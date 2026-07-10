"""
Generic, version-agnostic Zarr-store validator.

Flow for one Zarr store:
  1. zarr.open_group()            — open store, read raw ome and dca attrs
  2. open_ome_zarr()              — OME NGFF structural validation (raises on failure)
  3. classify_group()             — determine ZarrNodeType, enforce mutual exclusivity
  4. Dispatch by node type:
       IMAGE        → _validate_image()       (OPSStoreSpec model)
       IMAGE_LABEL  → _validate_image_label() (OPS label model, optional)
       HCS_PLATE    → _validate_hcs_plate() (plate structural checks
                                            + per-field images)
       LABELS_LIST  → _validate_labels_list() (no arrays — pass immediately)
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING

import pydantic
import zarr
from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v05.image import Image

from ops_validator.zarr_validation.examples import validate_examples_root
from ops_validator.zarr_validation.registry import (
    UnsupportedSpecVersionError,
    get_label_metadata_validator,
    get_label_model,
    get_model,
    get_plate_metadata_validator,
)
from ops_validator.zarr_validation.result import Issue, Severity, ZarrNodeValidationResult
from ops_validator.zarr_validation.zarr_node import ZarrNodeType, classify_group

if TYPE_CHECKING:
    from pydantic import BaseModel
    from pydantic_zarr.v3 import ArraySpec


# ---------------------------------------------------------------------------
# Store metadata extraction
# ---------------------------------------------------------------------------


def _get_compression(codecs: tuple | list) -> tuple[str | None, int | None]:
    """
    Walk a codec chain (list/tuple of dicts) and return (codec_id, level) for
    the first compression codec found.  Recurses into sharding_indexed inner codecs.

    Each codec dict has the shape: {'name': str, 'configuration': dict}
    where 'configuration' is optional (e.g. bytes codec has no configuration).
    """
    for codec in codecs:
        name = codec.get("name", "")
        cfg = codec.get("configuration") or {}

        if name == "sharding_indexed":
            return _get_compression(cfg.get("codecs", ()))

        if name == "blosc":
            return "blosc", cfg.get("clevel")

        if name == "zstd":
            return "zstd", cfg.get("level")

        if name == "gzip":
            return "gzip", cfg.get("level")

    return None, None


def _extract_level(path: str, spec: "ArraySpec") -> dict:
    """
    Extract spec-relevant metadata from one pydantic_zarr ArraySpec.

    In zarr v3 with sharding:
      - spec.chunk_grid['configuration']['chunk_shape']  → outer shard (write unit)
      - codecs[0]['configuration']['chunk_shape']        → inner chunk (read unit)
      - compression lives inside the sharding codec's inner codecs

    Without sharding:
      - spec.chunk_grid['configuration']['chunk_shape']  → chunk shape
      - compression is in codecs directly
    """
    codecs = spec.codecs  # tuple of dicts
    shard_shape = tuple(spec.chunk_grid["configuration"]["chunk_shape"])

    index_codec_ids = None
    if codecs and codecs[0].get("name") == "sharding_indexed":
        cfg = codecs[0]["configuration"]
        chunk_shape = tuple(cfg["chunk_shape"])
        inner_codecs = cfg.get("codecs", ())
        index_codec_ids = [c.get("name", "") for c in cfg.get("index_codecs", ())]
    else:
        chunk_shape = shard_shape
        shard_shape = None
        inner_codecs = codecs

    codec_id, codec_level = _get_compression(inner_codecs)
    return {
        "path": path,
        "dtype": str(spec.data_type),
        "shape": list(spec.shape),
        "chunk_shape": list(chunk_shape),
        "shard_shape": list(shard_shape) if shard_shape else None,
        "codec_id": codec_id or "none",
        "codec_level": codec_level,
        "index_codec_ids": index_codec_ids,
    }


def _build_node_dict(img: Image) -> dict:
    """
    Build the dict that OPSStoreSpec.model_validate() expects from an
    ome_zarr_models Image (or compatible multiscale group).
    """
    ms = img.ome_attributes.multiscales[0]
    axes = [{"name": ax.name, "type": ax.type, "unit": ax.unit} for ax in ms.axes]
    levels = []
    shapes = []
    for ds in ms.datasets:
        spec = img.members[ds.path]
        levels.append(_extract_level(ds.path, spec))
        shapes.append(list(spec.shape))
    return {
        "axes": axes,
        "multiscale_level_count": len(ms.datasets),
        "levels": levels,
        "array_shapes": shapes,
    }


# ---------------------------------------------------------------------------
# HCS plate traversal
# ---------------------------------------------------------------------------


def _gather_plate_fields(
    node_path: str,
    plate_wells: list[dict],
    plate_acquisitions: "list[dict] | None" = None,
) -> "tuple[list[Issue], list[str]]":
    """
    Open each declared well zarr.json once and return:
      - issues for wells / fields that fail per-well traversal checks
      - field paths for all declared fields that exist on disk

    Uses raw zarr attrs rather than ome-zarr-models Well objects to avoid
    Well.from_zarr(), which eagerly opens all Image sub-groups via
    get_optional_group_paths() — O(N_fields) sequential I/O calls.

    Checks (raised as ERRORs)
    -------------------------
    MUST — every declared well has a group on disk
    MUST — every declared field has a group on disk
    MUST — field acquisition ID must be in plate.acquisitions (if acquisitions
           are declared); only checked for fields that exist on disk
    """
    issues: list[Issue] = []
    field_paths: list[str] = []

    valid_aq_ids: set[int] | None = None
    if plate_acquisitions is not None:
        valid_aq_ids = {
            aq["id"]
            for aq in plate_acquisitions
            if isinstance(aq.get("id"), int) and aq["id"] >= 0
        }

    for well_meta in plate_wells:
        well_path = well_meta["path"]
        try:
            well_group = zarr.open_group(f"{node_path}/{well_path}", mode="r")
        except Exception:
            issues.append(
                Issue(
                    loc=("plate", "wells", well_path),
                    message=(
                        f"Well '{well_path}' is declared in "
                        f"ome.plate.wells but has no group on disk"
                    ),
                    severity=Severity.ERROR,
                )
            )
            continue

        well_ome = dict(well_group.attrs).get("ome", {})
        well_images = well_ome.get("well", {}).get("images", [])
        try:
            well_keys = set(well_group.keys())
        except Exception:
            well_keys = set()

        for img_meta in well_images:
            img_path = img_meta.get("path", "")
            if not img_path:
                continue
            if img_path not in well_keys:
                issues.append(
                    Issue(
                        loc=("plate", "wells", well_path, img_path),
                        message=(
                            f"Field '{well_path}/{img_path}' is declared in "
                            f"ome.well.images but has no group on disk"
                        ),
                        severity=Severity.ERROR,
                    )
                )
                continue
            field_paths.append(f"{well_path}/{img_path}")
            aq_id = img_meta.get("acquisition")
            if (
                valid_aq_ids is not None
                and aq_id is not None
                and aq_id not in valid_aq_ids
            ):
                issues.append(
                    Issue(
                        loc=("plate", "wells", well_path, img_path, "acquisition"),
                        message=(
                            f"Acquisition ID {aq_id!r} for field "
                            f"'{well_path}/{img_path}' is not in "
                            f"ome.plate.acquisitions: {sorted(valid_aq_ids)}"
                        ),
                        severity=Severity.ERROR,
                    )
                )

    return issues, field_paths


def _validate_field(
    node_path: str,
    field_path: str,
    spec_version: str,
    ngff_version: str | None,
    ModelClass: "type[BaseModel]",
) -> "tuple[ZarrNodeValidationResult, tuple | None, tuple | None]":
    """
    Open and validate one HCS field image.

    Returns (result, axes, level-0 chunk_shape). axes and chunk_shape are
    None when the field could not be opened, so the caller can skip them
    in uniformity accumulation.
    """
    full_path = f"{node_path}/{field_path}"
    try:
        field_zarr_group = zarr.open_group(full_path, mode="r")
        dca = dict(field_zarr_group.attrs).get("dca")
        field_img = open_ome_zarr(field_zarr_group)
        node_dict = _build_node_dict(field_img)
    except Exception as exc:
        return (
            ZarrNodeValidationResult(
                node_path=full_path,
                parent_path=node_path,
                spec_version=spec_version,
                passed=False,
                ngff_version=ngff_version,
                issues=[
                    Issue(
                        loc=("plate", field_path, "metadata_extraction"),
                        message=str(exc),
                        severity=Severity.ERROR,
                    )
                ],
            ),
            None,
            None,
        )

    axes = tuple(ax["name"] for ax in node_dict["axes"])
    chunk_shape = (
        tuple(node_dict["levels"][0]["chunk_shape"]) if node_dict["levels"] else None
    )
    level_count = node_dict["multiscale_level_count"]
    node_dict["spec_version"] = spec_version
    node_dict["dca"] = dca
    try:
        ModelClass.model_validate(node_dict)
        return (
            ZarrNodeValidationResult(
                node_path=full_path,
                parent_path=node_path,
                spec_version=spec_version,
                passed=True,
                ngff_version=ngff_version,
                multiscale_level_count=level_count,
            ),
            axes,
            chunk_shape,
        )
    except pydantic.ValidationError as exc:
        issues = _convert_errors(exc)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        return (
            ZarrNodeValidationResult(
                node_path=full_path,
                parent_path=node_path,
                spec_version=spec_version,
                passed=len(errors) == 0,
                ngff_version=ngff_version,
                multiscale_level_count=level_count,
                issues=issues,
            ),
            axes,
            chunk_shape,
        )


# ---------------------------------------------------------------------------
# Pydantic error conversion
# ---------------------------------------------------------------------------

_SHOULD_MARKER = "[SHOULD]"


def _convert_errors(exc: pydantic.ValidationError) -> list[Issue]:
    """
    Convert a pydantic.ValidationError into a list of Issue objects.

    Validators in the spec models prefix SHOULD-level messages with "[SHOULD]".
    Everything else is treated as a MUST violation (ERROR severity).

    A single ValueError can contain multiple newline-separated messages (used
    when a model validator accumulates several SHOULD warnings).  Each line
    becomes its own Issue.
    """
    issues: list[Issue] = []

    for error in exc.errors(include_url=False):
        loc = tuple(error.get("loc", ()))
        raw_msg: str = error.get("msg", "")

        # Pydantic prefixes user messages with "Value error, " — strip it.
        if raw_msg.startswith("Value error, "):
            raw_msg = raw_msg[len("Value error, ") :]

        for line in raw_msg.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(_SHOULD_MARKER):
                issues.append(
                    Issue(
                        loc=loc,
                        message=line[len(_SHOULD_MARKER) :].strip(),
                        severity=Severity.WARNING,
                    )
                )
            else:
                issues.append(Issue(loc=loc, message=line, severity=Severity.ERROR))

    return issues


# ---------------------------------------------------------------------------
# Per-node-type validation helpers
# ---------------------------------------------------------------------------


def _validate_image(
    node_path: str,
    ome_obj: Image,
    ngff_version: str | None,
    spec_version: str,
    ModelClass: "type[BaseModel]",
    *,
    dca: object,
    parent_path: str | None = None,
) -> list[ZarrNodeValidationResult]:
    """
    Run spec validation for one image or label image multiscale group.

    Used directly for IMAGE nodes and called per-field by _validate_hcs_plate.
    The caller supplies the appropriate ModelClass (image or label) and the
    raw `dca` attrs dict to inject (None for label groups). The OPS spec
    models do not consume the `dca` field directly but accept it via
    extra="allow".
    """
    try:
        node_dict = _build_node_dict(ome_obj)
    except Exception as exc:
        return [
            ZarrNodeValidationResult(
                node_path=node_path,
                parent_path=parent_path,
                spec_version=spec_version,
                passed=False,
                ngff_version=ngff_version,
                issues=[
                    Issue(
                        loc=("metadata_extraction",),
                        message=str(exc),
                        severity=Severity.ERROR,
                    )
                ],
            )
        ]

    level_count = node_dict["multiscale_level_count"]
    node_dict["spec_version"] = spec_version
    node_dict["dca"] = dca

    try:
        ModelClass.model_validate(node_dict)
        return [
            ZarrNodeValidationResult(
                node_path=node_path,
                parent_path=parent_path,
                spec_version=spec_version,
                passed=True,
                ngff_version=ngff_version,
                multiscale_level_count=level_count,
            )
        ]
    except pydantic.ValidationError as exc:
        issues = _convert_errors(exc)
        errors = [i for i in issues if i.severity == Severity.ERROR]
        return [
            ZarrNodeValidationResult(
                node_path=node_path,
                parent_path=parent_path,
                spec_version=spec_version,
                passed=len(errors) == 0,
                ngff_version=ngff_version,
                multiscale_level_count=level_count,
                issues=issues,
            )
        ]


def _validate_hcs_plate(
    node_path: str,
    raw_attrs: dict,
    ngff_version: str | None,
    spec_version: str,
    ModelClass: "type[BaseModel]",
) -> list[ZarrNodeValidationResult]:
    """
    Run plate-level structural checks and per-field OPS validation.

    Returns one result for the plate root (structural issues) plus one
    result per field image. Fields are validated concurrently via a thread
    pool — each field's I/O is independent.

    `raw_attrs` is the full plate-root attrs dict from zarr_group.attrs
    (carries both `ome.plate` and top-level OPS keys like `channels_metadata`).
    We work from this dict rather than an ome-zarr-models HCS object to avoid
    HCS.from_zarr(), which recursively opens all well and field sub-groups
    at construction time.

    Checks
    ------
    MUST   — declared well has a group on disk (via _gather_plate_fields)
    MUST   — declared field has a group on disk (via _gather_plate_fields)
    MUST   — field acquisition ID is in plate.acquisitions
    SHOULD — axes uniform across all fields
    SHOULD — level-0 chunk shape uniform across all fields
    + spec-specific OPS plate metadata validation (channels_metadata)
    """
    raw_plate_attrs = raw_attrs.get("ome", {}).get("plate", {})

    gather_issues, field_paths = _gather_plate_fields(
        node_path,
        raw_plate_attrs.get("wells", []),
        raw_plate_attrs.get("acquisitions"),
    )

    plate_meta_validator = get_plate_metadata_validator(spec_version)
    schema_issues: list[Issue] = []
    if plate_meta_validator is not None:
        schema_issues = plate_meta_validator(raw_attrs)

    plate_issues = schema_issues + gather_issues

    seen_axes: list[tuple] = []
    seen_chunks: list[tuple] = []
    field_results: list[ZarrNodeValidationResult] = []

    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                _validate_field, node_path, fp, spec_version, ngff_version, ModelClass
            ): fp
            for fp in field_paths
        }
        for future in as_completed(futures):
            result, axes, chunk_shape = future.result()
            field_results.append(result)
            if axes is not None:
                seen_axes.append(axes)
            if chunk_shape is not None:
                seen_chunks.append(chunk_shape)

    if len(set(seen_axes)) > 1:
        plate_issues.append(
            Issue(
                loc=("plate", "axes"),
                message=(
                    f"Axes are not uniform across all plate fields: "
                    f"{set(seen_axes)}"
                ),
                severity=Severity.WARNING,
            )
        )

    if len(set(seen_chunks)) > 1:
        plate_issues.append(
            Issue(
                loc=("plate", "chunk_shape"),
                message=(
                    f"Level-0 chunk shapes are not uniform across all "
                    f"plate fields: {set(seen_chunks)}"
                ),
                severity=Severity.WARNING,
            )
        )

    errors = [i for i in plate_issues if i.severity == Severity.ERROR]
    plate_result = ZarrNodeValidationResult(
        node_path=node_path,
        spec_version=spec_version,
        passed=len(errors) == 0,
        ngff_version=ngff_version,
        issues=plate_issues,
    )

    return [plate_result] + field_results


def _validate_labels_list(
    node_path: str,
    ngff_version: str | None,
    spec_version: str,
) -> list[ZarrNodeValidationResult]:
    """LABELS_LIST groups carry no arrays — pass immediately."""
    return [
        ZarrNodeValidationResult(
            node_path=node_path,
            spec_version=spec_version,
            passed=True,
            ngff_version=ngff_version,
        )
    ]


# ---------------------------------------------------------------------------
# Core per-store validation — dispatcher
# ---------------------------------------------------------------------------


def validate_zarr_node(
    node_path: str,
    spec_version: str = "ops-0.1",
    ModelClass: "type[BaseModel] | None" = None,
) -> list[ZarrNodeValidationResult]:
    """
    Run full validation (NGFF structural + OPS spec) for one store.

    Returns one result for standalone image stores, or one result per field
    image for HCS plates.

    Parameters
    ----------
    node_path:    local path or s3:// URL to the Zarr store root
    spec_version: OPS spec version string, e.g. "ops-0.1"
    ModelClass:   the OPSStoreSpec class for this version; resolved from the
                  registry if not provided
    """
    if ModelClass is None:
        ModelClass = get_model(spec_version)

    # Step 1: open group and read raw ome attrs before ome-zarr-models dispatch.
    # This is required because ome-zarr-models uses extra="allow" on BaseOMEAttrs
    # and would silently accept a group with both 'plate' and 'multiscales'.
    try:
        zarr_group = zarr.open_group(node_path, mode="r")
        raw_attrs = dict(zarr_group.attrs)
        raw_ome_attrs = raw_attrs.get("ome", {})
        raw_dca_attrs = raw_attrs.get("dca")
    except Exception as exc:
        return [
            ZarrNodeValidationResult(
                node_path=node_path,
                spec_version=spec_version,
                passed=False,
                issues=[
                    Issue(
                        loc=("store_open",), message=str(exc), severity=Severity.ERROR
                    )
                ],
            )
        ]

    # Step 1.5: examples-images container. A group carrying a top-level
    # `channel_combos` attribute is the examples.zarr root. Per the OPS spec
    # (example-images.md) this artifact is NOT an OME-NGFF/HCS store —
    # validators MUST NOT apply HCS checks — so route it to the channel_combos
    # validator and skip the NGFF structural + node-type dispatch below.
    if "channel_combos" in raw_attrs:
        return validate_examples_root(node_path, raw_attrs, spec_version)

    # Step 1a: HCS fast path — bypass open_ome_zarr for plates.
    # open_ome_zarr on an HCS root calls HCS.from_zarr(), which recursively
    # opens every well via Well.from_zarr(), which in turn opens every field
    # image via Image.from_zarr() — O(N_fields) sequential I/O calls before
    # any validation. We detect the plate from raw attrs and validate
    # directly from the metadata dict, parallelizing per-field validation
    # inside _validate_hcs_plate.
    if "plate" in raw_ome_attrs and "multiscales" not in raw_ome_attrs:
        ngff_version = str(raw_ome_attrs.get("version", "0.5"))
        results: list[ZarrNodeValidationResult] = _validate_hcs_plate(
            node_path, raw_attrs, ngff_version, spec_version, ModelClass
        )
        for r in results:
            if r.node_type is None:
                r.node_type = ZarrNodeType.HCS_PLATE
        return results

    # Step 2: OME NGFF structural validation (non-HCS stores).
    try:
        ome_obj = open_ome_zarr(zarr_group)  # pass already-opened group — no double I/O
    except Exception as exc:
        return [
            ZarrNodeValidationResult(
                node_path=node_path,
                spec_version=spec_version,
                passed=False,
                issues=[
                    Issue(
                        loc=("ngff_validation",),
                        message=str(exc),
                        severity=Severity.ERROR,
                    )
                ],
            )
        ]

    ngff_version = str(ome_obj.ome_zarr_version)

    # Step 3: classify node type, catching ambiguous ome attrs.
    try:
        node_type = classify_group(node_path, ome_obj, raw_ome_attrs)
    except ValueError as exc:
        return [
            ZarrNodeValidationResult(
                node_path=node_path,
                spec_version=spec_version,
                passed=False,
                ngff_version=ngff_version,
                issues=[
                    Issue(
                        loc=("node_classification",),
                        message=str(exc),
                        severity=Severity.ERROR,
                    )
                ],
            )
        ]

    # Step 4: dispatch by node type. HCS plates were handled by the Step 1a
    # fast path above; if classify_group still returns HCS_PLATE here the
    # root didn't carry a 'plate' attr (shouldn't happen), so fall through.
    if node_type == ZarrNodeType.LABELS_LIST:
        results = _validate_labels_list(node_path, ngff_version, spec_version)
        for r in results:
            if r.node_type is None:
                r.node_type = node_type
        return results

    if node_type == ZarrNodeType.IMAGE_LABEL:
        try:
            LabelModelClass = get_label_model(spec_version)
        except UnsupportedSpecVersionError:
            # OPS label-array model not registered for this version — skip arrays
            # with an informational warning. The segmentation_metadata sidecar is
            # still validated below.
            results = [
                ZarrNodeValidationResult(
                    node_path=node_path,
                    spec_version=spec_version,
                    passed=True,
                    ngff_version=ngff_version,
                    issues=[
                        Issue(
                            loc=("label_validation",),
                            message=(
                                f"OPS label array validation is not yet supported for "
                                f"spec version '{spec_version}'. "
                                f"Label arrays were not checked."
                            ),
                            severity=Severity.WARNING,
                        )
                    ],
                )
            ]
        else:
            results = _validate_image(
                node_path,
                ome_obj,
                ngff_version,
                spec_version,
                LabelModelClass,
                dca=None,
            )
        # Spec-specific label group metadata validation (OPS segmentation_metadata)
        label_meta_validator = get_label_metadata_validator(spec_version)
        if label_meta_validator and results:
            label_meta_issues = label_meta_validator(raw_attrs)
            if label_meta_issues:
                r = results[0]
                r.issues.extend(label_meta_issues)
                r.passed = not any(i.severity == Severity.ERROR for i in r.issues)
        for r in results:
            if r.node_type is None:
                r.node_type = node_type
        return results

    # IMAGE
    results = _validate_image(
        node_path, ome_obj, ngff_version, spec_version, ModelClass, dca=raw_dca_attrs
    )
    for r in results:
        if r.node_type is None:
            r.node_type = node_type
    return results
