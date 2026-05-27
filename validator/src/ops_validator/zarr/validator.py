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

from typing import TYPE_CHECKING, Iterator

import pydantic
import zarr
from ome_zarr_models import open_ome_zarr
from ome_zarr_models.v05.hcs import HCS, WellGroupNotFoundError
from ome_zarr_models.v05.image import Image

from ops_validator.zarr.registry import (
    UnsupportedSpecVersionError,
    get_label_metadata_validator,
    get_label_model,
    get_model,
    get_plate_metadata_validator,
)
from ops_validator.zarr.result import Issue, Severity, ZarrNodeValidationResult
from ops_validator.zarr.zarr_node import ZarrNodeType, classify_group

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
    axes = [ax.name for ax in ms.axes]
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


def _iter_field_paths(hcs: HCS) -> Iterator[str]:
    """
    Yield field_path for every field declared in the plate.

    field_path is relative to the plate root, e.g. "D/4/r04c04f01_0".
    Well groups missing from disk are silently skipped (WellGroupNotFoundError).
    Field paths absent from well.members are also skipped.
    """
    for i, well_meta in enumerate(hcs.ome_attributes.plate.wells):
        try:
            well = hcs.get_well_group(i)
        except WellGroupNotFoundError:
            continue
        for img_meta in well.ome_attributes.well.images:
            if img_meta.path not in (well.members or {}):
                continue
            yield f"{well_meta.path}/{img_meta.path}"


def _check_plate_structure(
    hcs: HCS,
    node_path: str,
    ngff_version: str | None,
    spec_version: str,
    raw_plate_attrs: dict | None = None,
) -> ZarrNodeValidationResult:
    """
    Cross-field structural checks for an HCS plate.

    Returns a single ZarrNodeValidationResult for the plate root carrying
    issues that span multiple wells or fields. Per-field OPS array checks
    are handled separately by _validate_hcs_plate.

    ome-zarr-models gap
    -------------------
    HCSAttrs and WellAttrs both declare their sub-groups (wells and field
    images respectively) via get_optional_group_paths(). _from_zarr_v3
    catches FileNotFoundError for optional paths and silently skips them,
    so a declared well or field that is missing from disk does not cause
    open_ome_zarr() to raise. These missing-group cases must be checked
    here explicitly.

    Note: acquisition ID cross-references ARE validated by ome-zarr-models
    (HCS._check_valid_acquisitions), so that check is not repeated here.

    Checks
    ------
    MUST  — declared well has no group on disk
    MUST  — declared field has no group on disk
    SHOULD — axes not uniform across all fields
    SHOULD — level-0 chunk shape not uniform across all fields
    """
    issues: list[Issue] = []

    # MUST: every declared well exists on disk
    for i, well_meta in enumerate(hcs.ome_attributes.plate.wells):
        try:
            well = hcs.get_well_group(i)
        except WellGroupNotFoundError:
            issues.append(
                Issue(
                    loc=("plate", "wells", well_meta.path),
                    message=(
                        f"Well '{well_meta.path}' is declared in "
                        f"ome.plate.wells but has no group on disk"
                    ),
                    severity=Severity.ERROR,
                )
            )
            continue

        # MUST: every declared field exists on disk
        for img_meta in well.ome_attributes.well.images:
            if img_meta.path not in (well.members or {}):
                issues.append(
                    Issue(
                        loc=("plate", "wells", well_meta.path, img_meta.path),
                        message=(
                            f"Field '{well_meta.path}/{img_meta.path}' is declared in "
                            f"ome.well.images but has no group on disk"
                        ),
                        severity=Severity.ERROR,
                    )
                )

    # SHOULD: axes and level-0 chunk shape uniform across all fields
    seen_axes: list[tuple] = []
    seen_chunks: list[tuple] = []
    for field_path in _iter_field_paths(hcs):
        try:
            field_zarr_group = zarr.open_group(f"{node_path}/{field_path}", mode="r")
            field_img = open_ome_zarr(field_zarr_group)
            nd = _build_node_dict(field_img)
        except Exception:
            continue
        seen_axes.append(tuple(nd["axes"]))
        if nd["levels"]:
            seen_chunks.append(tuple(nd["levels"][0]["chunk_shape"]))

    if len(set(seen_axes)) > 1:
        issues.append(
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
        issues.append(
            Issue(
                loc=("plate", "chunk_shape"),
                message=(
                    f"Level-0 chunk shapes are not uniform across all "
                    f"plate fields: {set(seen_chunks)}"
                ),
                severity=Severity.WARNING,
            )
        )

    # Spec-specific plate root metadata validation (OPS channels_metadata)
    plate_meta_validator = get_plate_metadata_validator(spec_version)
    if plate_meta_validator and raw_plate_attrs is not None:
        issues.extend(plate_meta_validator(raw_plate_attrs))

    errors = [i for i in issues if i.severity == Severity.ERROR]
    return ZarrNodeValidationResult(
        node_path=node_path,
        spec_version=spec_version,
        passed=len(errors) == 0,
        ngff_version=ngff_version,
        issues=issues,
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
    ome_obj: HCS,
    ngff_version: str | None,
    spec_version: str,
    ModelClass: "type[BaseModel]",
    raw_plate_attrs: dict | None = None,
) -> list[ZarrNodeValidationResult]:
    """
    Run plate-level structural checks and per-field OPS validation.

    Returns one result for the plate root (structural issues) plus one
    result per field image.

    Note: each field is opened independently (zarr.open_group + open_ome_zarr),
    separate from the open_ome_zarr call in _check_plate_structure — two opens
    per field per validate() call.
    """
    results = [
        _check_plate_structure(
            ome_obj, node_path, ngff_version, spec_version, raw_plate_attrs
        )
    ]
    for field_path in _iter_field_paths(ome_obj):
        full_path = f"{node_path}/{field_path}"
        try:
            field_zarr_group = zarr.open_group(full_path, mode="r")
            dca = dict(field_zarr_group.attrs).get("dca")
            field_img = open_ome_zarr(field_zarr_group)
            node_dict = _build_node_dict(field_img)
        except Exception as exc:
            results.append(
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
                )
            )
            continue
        level_count = node_dict["multiscale_level_count"]
        node_dict["spec_version"] = spec_version
        node_dict["dca"] = dca
        try:
            ModelClass.model_validate(node_dict)
            results.append(
                ZarrNodeValidationResult(
                    node_path=full_path,
                    parent_path=node_path,
                    spec_version=spec_version,
                    passed=True,
                    ngff_version=ngff_version,
                    multiscale_level_count=level_count,
                )
            )
        except pydantic.ValidationError as exc:
            issues = _convert_errors(exc)
            errors = [i for i in issues if i.severity == Severity.ERROR]
            results.append(
                ZarrNodeValidationResult(
                    node_path=full_path,
                    parent_path=node_path,
                    spec_version=spec_version,
                    passed=len(errors) == 0,
                    ngff_version=ngff_version,
                    multiscale_level_count=level_count,
                    issues=issues,
                )
            )
    return results


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

    # Step 2: OME NGFF structural validation.
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

    # Step 4: dispatch by node type.
    if node_type == ZarrNodeType.HCS_PLATE:
        results = _validate_hcs_plate(
            node_path, ome_obj, ngff_version, spec_version, ModelClass, raw_attrs
        )
        for r in results:
            if r.node_type is None:
                r.node_type = node_type
        return results

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
