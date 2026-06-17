"""Tests for examples.zarr channel_combos validation (shape + cross-leaf)."""

from __future__ import annotations

import json

from ops_validator.zarr_validation.examples import (
    check_primary_channels,
    default_sample_leaves,
    labels_from_attrs,
    validate_examples_root,
)
from ops_validator.zarr_validation.result import Severity
from ops_validator.zarr_validation.spec.v0_1.models import (
    validate_ops_examples_channel_combos_metadata,
)
from ops_validator.zarr_validation.validator import validate_zarr_node
from ops_validator.zarr_validation.zarr_node import ZarrNodeType


# ---------------------------------------------------------------------------
# Shape validation (validate_ops_examples_channel_combos_metadata)
# ---------------------------------------------------------------------------


class TestShape:
    def test_absent_is_ok(self):
        assert validate_ops_examples_channel_combos_metadata({}) == []

    def test_valid_passes(self):
        attrs = {
            "channel_combos": [
                {"name": "Phase2D", "primary_channel": "Phase2D_labelfree", "priority": 1},
                {"name": "5xUPRE", "primary_channel": "5xUPRE_GFP"},
            ]
        }
        assert validate_ops_examples_channel_combos_metadata(attrs) == []

    def test_duplicate_names_fail(self):
        attrs = {
            "channel_combos": [
                {"name": "A", "primary_channel": "x"},
                {"name": "A", "primary_channel": "y"},
            ]
        }
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any(i.severity == Severity.ERROR for i in issues)
        assert any("unique" in i.message.lower() for i in issues)

    def test_negative_priority_fails(self):
        attrs = {"channel_combos": [{"name": "A", "primary_channel": "x", "priority": -1}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any("non-negative" in i.message.lower() for i in issues)

    def test_empty_name_fails(self):
        attrs = {"channel_combos": [{"name": "  ", "primary_channel": "x"}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any(i.severity == Severity.ERROR for i in issues)

    def test_missing_primary_fails(self):
        attrs = {"channel_combos": [{"name": "A"}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any(i.severity == Severity.ERROR for i in issues)

    def test_priority_optional(self):
        attrs = {"channel_combos": [{"name": "A", "primary_channel": "x"}]}
        assert validate_ops_examples_channel_combos_metadata(attrs) == []


# ---------------------------------------------------------------------------
# labels_from_attrs
# ---------------------------------------------------------------------------


class TestLabelsFromAttrs:
    def test_omero(self):
        attrs = {"ome": {"omero": {"channels": [{"label": "DAPI"}, {"label": "GFP"}]}}}
        assert labels_from_attrs(attrs) == ["DAPI", "GFP"]

    def test_channels_metadata_fallback(self):
        attrs = {"channels_metadata": [{"name": "DAPI"}, {"name": "GFP"}]}
        assert labels_from_attrs(attrs) == ["DAPI", "GFP"]

    def test_empty(self):
        assert labels_from_attrs({}) == []


# ---------------------------------------------------------------------------
# check_primary_channels (pure cross-leaf rule)
# ---------------------------------------------------------------------------


class TestCheckPrimaryChannels:
    def test_present_in_all_screens(self):
        combos = [{"name": "Phase2D", "primary_channel": "Phase2D_labelfree"}]
        samples = {
            "Phase2D": [
                ("S1", frozenset({"Phase2D_labelfree", "GFP_a"})),
                ("S2", frozenset({"Phase2D_labelfree", "GFP_b"})),
            ]
        }
        assert check_primary_channels(combos, samples) == []

    def test_missing_in_one_screen(self):
        combos = [{"name": "Phase2D", "primary_channel": "Phase2D_labelfree"}]
        samples = {
            "Phase2D": [
                ("S1", frozenset({"Phase2D_labelfree"})),
                ("S2", frozenset({"only_other"})),
            ]
        }
        issues = check_primary_channels(combos, samples)
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR
        assert "S2" in issues[0].message
        assert "Phase2D_labelfree" in issues[0].message

    def test_combo_with_no_samples_errors(self):
        combos = [{"name": "Ghost", "primary_channel": "x"}]
        issues = check_primary_channels(combos, {"Ghost": []})
        assert len(issues) == 1
        assert "no matching subdirectory" in issues[0].message

    def test_malformed_entry_skipped(self):
        # Shape validator owns these; cross-leaf must not double-report.
        combos = [{"name": "", "primary_channel": "x"}, {"name": "A"}]
        assert check_primary_channels(combos, {}) == []


# ---------------------------------------------------------------------------
# Local fixture helpers
# ---------------------------------------------------------------------------


def _write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def _build_examples(tmp_path, channel_combos, leaves):
    """leaves: iterable of (combo, pert, barcode, idx, source_screen, [labels])."""
    root = tmp_path / "examples.zarr"
    _write_json(
        root / "zarr.json",
        {
            "zarr_format": 3,
            "node_type": "group",
            "attributes": {
                "ome": {"version": "0.5"},
                "dca_examples_version": "0.1",
                "channel_combos": channel_combos,
            },
        },
    )
    for combo, pert, barcode, idx, screen, labels in leaves:
        leaf = root / combo / pert / barcode / f"{idx}.zarr"
        _write_json(
            leaf / "zarr.json",
            {
                "zarr_format": 3,
                "node_type": "group",
                "attributes": {
                    "source_screen": screen,
                    "ome": {
                        "version": "0.5",
                        "omero": {"channels": [{"label": x} for x in labels]},
                    },
                },
            },
        )
    return root


# ---------------------------------------------------------------------------
# default_sample_leaves (real local-fs walk)
# ---------------------------------------------------------------------------


class TestDefaultSampleLeaves:
    def test_dedups_by_source_screen(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[{"name": "Phase2D", "primary_channel": "Phase2D_labelfree"}],
            leaves=[
                ("Phase2D", "GENE1", "bc1", 0, "S1", ["Phase2D_labelfree", "GFP_a"]),
                ("Phase2D", "GENE1", "bc1", 1, "S1", ["Phase2D_labelfree", "GFP_a"]),
                ("Phase2D", "GENE2", "bc2", 0, "S2", ["Phase2D_labelfree", "GFP_b"]),
            ],
        )
        samples = default_sample_leaves(str(root), "Phase2D")
        screens = {s for s, _ in samples}
        assert screens == {"S1", "S2"}

    def test_missing_combo_returns_empty(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[{"name": "Phase2D", "primary_channel": "p"}],
            leaves=[("Phase2D", "G", "b", 0, "S1", ["p"])],
        )
        assert default_sample_leaves(str(root), "DoesNotExist") == []


# ---------------------------------------------------------------------------
# validate_examples_root (orchestrator) + end-to-end via validate_zarr_node
# ---------------------------------------------------------------------------


class TestValidateExamplesRoot:
    def test_pass_with_injected_sampler(self):
        raw = {
            "ome": {"version": "0.5"},
            "channel_combos": [{"name": "A", "primary_channel": "DAPI", "priority": 1}],
        }
        results = validate_examples_root(
            "mem://examples.zarr",
            raw,
            "ops-0.1",
            sample_leaves=lambda root, combo: [("S1", frozenset({"DAPI"}))],
        )
        assert len(results) == 1
        assert results[0].passed
        assert results[0].node_type == ZarrNodeType.EXAMPLES_ROOT

    def test_fail_when_primary_absent(self):
        raw = {"channel_combos": [{"name": "A", "primary_channel": "DAPI"}]}
        results = validate_examples_root(
            "mem://examples.zarr",
            raw,
            "ops-0.1",
            sample_leaves=lambda root, combo: [("S1", frozenset({"GFP"}))],
        )
        assert not results[0].passed
        assert any("DAPI" in i.message for i in results[0].errors)

    def test_integration_pass(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[
                {"name": "Phase2D", "primary_channel": "Phase2D_labelfree", "priority": 1},
                {"name": "5xUPRE", "primary_channel": "5xUPRE_GFP", "priority": 2},
            ],
            leaves=[
                ("Phase2D", "G1", "b1", 0, "S1", ["Phase2D_labelfree", "x_a"]),
                ("Phase2D", "G2", "b2", 0, "S2", ["Phase2D_labelfree", "x_b"]),
                ("5xUPRE", "G1", "b1", 0, "S1", ["5xUPRE_GFP", "ER_mCherry"]),
            ],
        )
        results = validate_examples_root(
            str(root), json.loads((root / "zarr.json").read_text())["attributes"], "ops-0.1"
        )
        assert results[0].passed, [i.message for i in results[0].issues]

    def test_integration_fail_primary_missing_in_one_screen(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[{"name": "Phase2D", "primary_channel": "Phase2D_labelfree"}],
            leaves=[
                ("Phase2D", "G1", "b1", 0, "S1", ["Phase2D_labelfree"]),
                ("Phase2D", "G2", "b2", 0, "S2", ["something_else"]),
            ],
        )
        results = validate_examples_root(
            str(root), json.loads((root / "zarr.json").read_text())["attributes"], "ops-0.1"
        )
        assert not results[0].passed
        assert any("S2" in i.message for i in results[0].errors)

    def test_validate_zarr_node_routes_to_examples(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[{"name": "Phase2D", "primary_channel": "Phase2D_labelfree"}],
            leaves=[("Phase2D", "G1", "b1", 0, "S1", ["Phase2D_labelfree", "x"])],
        )
        results = validate_zarr_node(str(root), "ops-0.1")
        assert len(results) == 1
        assert results[0].node_type == ZarrNodeType.EXAMPLES_ROOT
        assert results[0].passed
