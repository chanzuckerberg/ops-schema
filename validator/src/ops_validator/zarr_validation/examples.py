"""
Validation for the example-images container's `channel_combos` metadata.

The `examples.zarr` container is a Zarr group whose root `zarr.json` MAY carry
an OPTIONAL `channel_combos` array — per channel combination, the representative
`primary_channel` (an OMERO label) and a display `priority`. Per
standards/ops/0.1.0/example-images.md, this artifact is NOT validated as an
OME-NGFF HCS store; only its `channel_combos` metadata is checked, in two parts:

  shape  (spec/v0_1/models.validate_ops_examples_channel_combos_metadata)
    - names non-empty + unique, primary_channel non-empty, priority >= 0

  cross-leaf  (this module)
    - every entry's `name` resolves to a {channel_combo} subdirectory
    - `primary_channel` is present in every leaf of that combo

A single combination MAY aggregate crops from multiple source screens whose
channel sets differ, so the primary MUST be common to all of them. The channel
set is uniform within a source screen, so the cross-leaf check samples one leaf
per distinct `source_screen` rather than reading every leaf.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable

import fsspec

from ops_validator.zarr_validation.registry import get_examples_metadata_validator
from ops_validator.zarr_validation.result import (
    Issue,
    Severity,
    ZarrNodeValidationResult,
)
from ops_validator.zarr_validation.zarr_node import ZarrNodeType

# A sampled leaf: (source_screen, set of channel labels present in that leaf).
LeafSample = tuple["str | None", frozenset]

# Sampler signature: (examples_root, combo_name) -> samples for that combo.
LeafSampler = Callable[[str, str], "list[LeafSample]"]

# Cap leaves visited per combo so a combo with millions of crops doesn't make
# validation unbounded. One leaf per distinct source_screen is sufficient (the
# channel set is uniform within a screen); this just bounds the search.
_MAX_LEAVES_PER_COMBO = 500


def labels_from_attrs(attrs: dict) -> list[str]:
    """Channel labels from a leaf zarr.json `attributes` dict.

    Accepts both layouts: OME-NGFF `ome.omero.channels[*].label` and the OPS
    data-portal `channels_metadata[*].name`.
    """
    omero = attrs.get("ome", {}).get("omero", {}).get("channels", [])
    if omero:
        return [c["label"] for c in omero if c.get("label")]
    channels_metadata = attrs.get("channels_metadata", [])
    return [c["name"] for c in channels_metadata if c.get("name")]


def check_primary_channels(
    channel_combos: Iterable[dict],
    samples_by_combo: dict[str, list[LeafSample]],
) -> list[Issue]:
    """Cross-leaf rule: every combo resolves to leaves, and `primary_channel`
    is present in each sampled (per-source-screen) leaf.

    `samples_by_combo[name]` is the leaf samples for that combo (one per
    distinct source_screen); an empty/missing list means the combo's
    subdirectory was absent or held no readable leaves.

    Pure function — I/O is done by the caller's sampler so the rule is unit
    testable without a store.
    """
    issues: list[Issue] = []
    for entry in channel_combos:
        name = entry.get("name")
        primary = entry.get("primary_channel")
        # Malformed entries are already reported by the shape validator.
        if not isinstance(name, str) or not name or not primary:
            continue

        samples = samples_by_combo.get(name) or []
        if not samples:
            issues.append(
                Issue(
                    loc=("channel_combos", name),
                    message=(
                        f"channel_combo '{name}' has no matching subdirectory "
                        f"(or no readable leaves) under the examples container"
                    ),
                    severity=Severity.ERROR,
                )
            )
            continue

        missing_screens = sorted(
            {str(screen) for screen, labels in samples if primary not in labels}
        )
        if missing_screens:
            issues.append(
                Issue(
                    loc=("channel_combos", name, "primary_channel"),
                    message=(
                        f"primary_channel '{primary}' for combo '{name}' is absent "
                        f"from leaf channels in source screen(s): {missing_screens}. "
                        f"It MUST be present in every leaf of the combo."
                    ),
                    severity=Severity.ERROR,
                )
            )
    return issues


def default_sample_leaves(
    examples_root: str,
    combo_name: str,
    *,
    max_leaves: int = _MAX_LEAVES_PER_COMBO,
) -> list[LeafSample]:
    """Sample one leaf per distinct `source_screen` under `{root}/{combo_name}`.

    Walks the combo subtree (depth is dataset-dependent — extra
    `observation_unit` columns add levels), treating any directory that
    contains a `zarr.json` as a leaf store. Reads each leaf's `zarr.json`
    attributes for `source_screen` + channel labels, keeping the first leaf
    seen per source_screen. Works for both local paths and `s3://` URLs via
    fsspec.
    """
    fs, root = fsspec.core.url_to_fs(examples_root)
    combo_path = f"{root.rstrip('/')}/{combo_name}"
    if not fs.exists(combo_path):
        return []

    by_screen: dict[str | None, frozenset] = {}
    stack = [combo_path]
    visited = 0
    while stack and visited < max_leaves:
        current = stack.pop()
        try:
            entries = fs.ls(current, detail=True)
        except FileNotFoundError:
            continue

        names = {e["name"].rstrip("/").rsplit("/", 1)[-1] for e in entries}
        is_leaf = "zarr.json" in names and current != combo_path
        if is_leaf:
            visited += 1
            try:
                raw = fs.cat(f"{current}/zarr.json")
                attrs = json.loads(raw).get("attributes", {})
            except (FileNotFoundError, ValueError):
                continue
            screen = attrs.get("source_screen")
            by_screen.setdefault(screen, frozenset(labels_from_attrs(attrs)))
            continue

        # Not a leaf — descend into child directories.
        stack.extend(e["name"] for e in entries if e["type"] == "directory")

    return list(by_screen.items())


def validate_examples_root(
    node_path: str,
    raw_attrs: dict,
    spec_version: str,
    *,
    sample_leaves: LeafSampler | None = None,
) -> list[ZarrNodeValidationResult]:
    """Validate the `channel_combos` metadata on an examples container root.

    Runs the shape validator (registry) then the cross-leaf primary-channel
    check. `sample_leaves` is injectable for testing; it defaults to
    `default_sample_leaves`. Returns a single result tagged EXAMPLES_ROOT.
    """
    issues: list[Issue] = []

    shape_validator = get_examples_metadata_validator(spec_version)
    if shape_validator is not None:
        issues.extend(shape_validator(raw_attrs))

    combos = raw_attrs.get("channel_combos", [])
    sampler = sample_leaves or default_sample_leaves
    samples_by_combo: dict[str, list[LeafSample]] = {}
    if isinstance(combos, list):
        for entry in combos:
            name = entry.get("name") if isinstance(entry, dict) else None
            if isinstance(name, str) and name and name not in samples_by_combo:
                samples_by_combo[name] = sampler(node_path, name)
        issues.extend(check_primary_channels(combos, samples_by_combo))

    ome = raw_attrs.get("ome")
    ngff_version = str(ome.get("version")) if isinstance(ome, dict) else None
    errors = [i for i in issues if i.severity == Severity.ERROR]
    return [
        ZarrNodeValidationResult(
            node_path=node_path,
            spec_version=spec_version,
            passed=len(errors) == 0,
            ngff_version=ngff_version,
            issues=issues,
            node_type=ZarrNodeType.EXAMPLES_ROOT,
        )
    ]
