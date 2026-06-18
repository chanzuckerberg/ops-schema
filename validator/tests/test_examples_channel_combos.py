"""Tests for examples.zarr channel_combos validation (shape + cross-leaf)."""

from __future__ import annotations

import json

from ops_validator.zarr_validation.examples import (
    check_display_channels,
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
                {
                    "name": "Phase2D",
                    "display_channels": ["Phase2D_labelfree"],
                    "priority": 1,
                },
                {"name": "5xUPRE", "display_channels": ["5xUPRE_GFP", "ER_mCherry"]},
            ]
        }
        assert validate_ops_examples_channel_combos_metadata(attrs) == []

    def test_duplicate_names_fail(self):
        attrs = {"channel_combos": [{"name": "A"}, {"name": "A"}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any(i.severity == Severity.ERROR for i in issues)
        assert any("unique" in i.message.lower() for i in issues)

    def test_negative_priority_fails(self):
        attrs = {"channel_combos": [{"name": "A", "priority": -1}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any("non-negative" in i.message.lower() for i in issues)

    def test_empty_name_fails(self):
        attrs = {"channel_combos": [{"name": "  "}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any(i.severity == Severity.ERROR for i in issues)

    def test_display_channels_optional(self):
        # Omitting display_channels (=> show all channels) is valid.
        attrs = {"channel_combos": [{"name": "A"}]}
        assert validate_ops_examples_channel_combos_metadata(attrs) == []

    def test_empty_display_channel_label_fails(self):
        attrs = {"channel_combos": [{"name": "A", "display_channels": ["ok", "  "]}]}
        issues = validate_ops_examples_channel_combos_metadata(attrs)
        assert any(i.severity == Severity.ERROR for i in issues)


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
# check_display_channels (pure cross-leaf rule)
# ---------------------------------------------------------------------------


class TestCheckDisplayChannels:
    def test_all_present_in_all_screens(self):
        combos = [{"name": "Phase2D", "display_channels": ["Phase2D_labelfree"]}]
        samples = {
            "Phase2D": [
                ("S1", frozenset({"Phase2D_labelfree", "GFP_a"})),
                ("S2", frozenset({"Phase2D_labelfree", "GFP_b"})),
            ]
        }
        assert check_display_channels(combos, samples) == []

    def test_multiple_labels_all_present(self):
        combos = [{"name": "C", "display_channels": ["a", "b"]}]
        samples = {"C": [("S1", frozenset({"a", "b", "c"}))]}
        assert check_display_channels(combos, samples) == []

    def test_missing_in_one_screen(self):
        combos = [{"name": "Phase2D", "display_channels": ["Phase2D_labelfree"]}]
        samples = {
            "Phase2D": [
                ("S1", frozenset({"Phase2D_labelfree"})),
                ("S2", frozenset({"only_other"})),
            ]
        }
        issues = check_display_channels(combos, samples)
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR
        assert "S2" in issues[0].message
        assert "Phase2D_labelfree" in issues[0].message

    def test_omitted_display_channels_skips_label_check(self):
        # All-channels combo: only needs a subdirectory (samples present); there
        # are no specific labels to verify.
        combos = [{"name": "A"}]
        samples = {"A": [("S1", frozenset({"whatever"}))]}
        assert check_display_channels(combos, samples) == []

    def test_combo_with_no_samples_errors(self):
        combos = [{"name": "Ghost", "display_channels": ["x"]}]
        issues = check_display_channels(combos, {"Ghost": []})
        assert len(issues) == 1
        assert "no matching subdirectory" in issues[0].message

    def test_malformed_entry_skipped(self):
        # Shape validator owns these; cross-leaf must not double-report.
        combos = [{"name": ""}, {"display_channels": ["x"]}]
        assert check_display_channels(combos, {}) == []


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
            channel_combos=[{"name": "Phase2D", "display_channels": ["Phase2D_labelfree"]}],
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
            channel_combos=[{"name": "Phase2D", "display_channels": ["p"]}],
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
            "channel_combos": [{"name": "A", "display_channels": ["DAPI"], "priority": 1}],
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

    def test_fail_when_display_channel_absent(self):
        raw = {"channel_combos": [{"name": "A", "display_channels": ["DAPI"]}]}
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
                {
                    "name": "Phase2D",
                    "display_channels": ["Phase2D_labelfree"],
                    "priority": 1,
                },
                {"name": "5xUPRE", "display_channels": ["5xUPRE_GFP"], "priority": 2},
            ],
            leaves=[
                ("Phase2D", "G1", "b1", 0, "S1", ["Phase2D_labelfree", "x_a"]),
                ("Phase2D", "G2", "b2", 0, "S2", ["Phase2D_labelfree", "x_b"]),
                ("5xUPRE", "G1", "b1", 0, "S1", ["5xUPRE_GFP", "ER_mCherry"]),
            ],
        )
        results = validate_examples_root(
            str(root),
            json.loads((root / "zarr.json").read_text())["attributes"],
            "ops-0.1",
        )
        assert results[0].passed, [i.message for i in results[0].issues]

    def test_integration_fail_display_channel_missing_in_one_screen(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[{"name": "Phase2D", "display_channels": ["Phase2D_labelfree"]}],
            leaves=[
                ("Phase2D", "G1", "b1", 0, "S1", ["Phase2D_labelfree"]),
                ("Phase2D", "G2", "b2", 0, "S2", ["something_else"]),
            ],
        )
        results = validate_examples_root(
            str(root),
            json.loads((root / "zarr.json").read_text())["attributes"],
            "ops-0.1",
        )
        assert not results[0].passed
        assert any("S2" in i.message for i in results[0].errors)

    def test_validate_zarr_node_routes_to_examples(self, tmp_path):
        root = _build_examples(
            tmp_path,
            channel_combos=[{"name": "Phase2D", "display_channels": ["Phase2D_labelfree"]}],
            leaves=[("Phase2D", "G1", "b1", 0, "S1", ["Phase2D_labelfree", "x"])],
        )
        results = validate_zarr_node(str(root), "ops-0.1")
        assert len(results) == 1
        assert results[0].node_type == ZarrNodeType.EXAMPLES_ROOT
        assert results[0].passed
