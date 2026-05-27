"""Unit tests for the Zarr framework dispatcher (mock-based)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ops_validator.zarr.result import Severity
from ops_validator.zarr.validator import (
    _extract_level,
    _get_compression,
    validate_zarr_node,
)
from ops_validator.zarr.zarr_node import ZarrNodeType


def make_array_spec(shape, chunk_shape, codecs, dtype="uint16"):
    spec = MagicMock()
    spec.shape = shape
    spec.data_type = dtype
    spec.chunk_grid = {"configuration": {"chunk_shape": list(chunk_shape)}}
    spec.codecs = codecs
    return spec


# ---------------------------------------------------------------------------
# _get_compression
# ---------------------------------------------------------------------------


class TestGetCompression:
    def test_zstd(self):
        assert _get_compression([{"name": "zstd", "configuration": {"level": 3}}]) == (
            "zstd",
            3,
        )

    def test_blosc(self):
        assert _get_compression(
            [{"name": "blosc", "configuration": {"clevel": 5}}]
        ) == ("blosc", 5)

    def test_empty(self):
        assert _get_compression([]) == (None, None)

    def test_sharding_recurses(self):
        codecs = [
            {
                "name": "sharding_indexed",
                "configuration": {
                    "chunk_shape": [128, 128, 128],
                    "codecs": [
                        {"name": "bytes", "configuration": {}},
                        {"name": "zstd", "configuration": {"level": 1}},
                    ],
                },
            }
        ]
        assert _get_compression(codecs) == ("zstd", 1)


# ---------------------------------------------------------------------------
# _extract_level
# ---------------------------------------------------------------------------


class TestExtractLevel:
    def test_no_sharding(self):
        spec = make_array_spec(
            shape=[1, 1, 256, 512, 512],
            chunk_shape=[1, 1, 128, 128, 128],
            codecs=[{"name": "zstd", "configuration": {"level": 3}}],
        )
        result = _extract_level("0", spec)
        assert result["chunk_shape"] == [1, 1, 128, 128, 128]
        assert result["shard_shape"] is None
        assert result["index_codec_ids"] is None

    def test_sharding_extracts_inner_chunk_and_index_codecs(self):
        codecs = [
            {
                "name": "sharding_indexed",
                "configuration": {
                    "chunk_shape": [1, 1, 64, 64, 64],
                    "codecs": [{"name": "zstd", "configuration": {"level": 1}}],
                    "index_codecs": [
                        {"name": "bytes", "configuration": {}},
                        {"name": "crc32c", "configuration": {}},
                    ],
                },
            }
        ]
        spec = make_array_spec(
            shape=[1, 1, 512, 1024, 1024],
            chunk_shape=[1, 1, 256, 512, 512],
            codecs=codecs,
        )
        result = _extract_level("0", spec)
        assert result["shard_shape"] == [1, 1, 256, 512, 512]
        assert result["chunk_shape"] == [1, 1, 64, 64, 64]
        assert result["index_codec_ids"] == ["bytes", "crc32c"]


# ---------------------------------------------------------------------------
# validate_zarr_node dispatcher — IMAGE_LABEL branch
# ---------------------------------------------------------------------------


class TestImageLabelNodeNoModelButHasMetadata:
    """No label model is registered for ops-0.1 (label arrays share the image
    schema in v0.1 — only segmentation_metadata is checked). The dispatcher
    should still run the label metadata validator and combine its issues with
    the warning that arrays were skipped."""

    def _run(self, monkeypatch, segmentation_metadata):
        mock_group = MagicMock()
        attrs = {"ome": {}}
        if segmentation_metadata is not None:
            attrs["segmentation_metadata"] = segmentation_metadata
        mock_group.attrs = attrs

        monkeypatch.setattr(
            "ops_validator.zarr.validator.zarr.open_group",
            lambda *a, **kw: mock_group,
        )
        mock_ome = MagicMock()
        mock_ome.ome_zarr_version = "0.5"
        monkeypatch.setattr(
            "ops_validator.zarr.validator.open_ome_zarr",
            lambda *a, **kw: mock_ome,
        )
        monkeypatch.setattr(
            "ops_validator.zarr.validator.classify_group",
            lambda *a, **kw: ZarrNodeType.IMAGE_LABEL,
        )
        MockModel = MagicMock()
        return validate_zarr_node(
            "/fake/label", spec_version="ops-0.1", ModelClass=MockModel
        )

    def test_missing_segmentation_metadata_is_error(self, monkeypatch):
        results = self._run(monkeypatch, segmentation_metadata=None)
        errors = [
            i for r in results for i in r.issues if i.severity == Severity.ERROR
        ]
        assert errors
        assert any("segmentation_metadata" in e.message.lower() for e in errors)
        assert not results[0].passed

    def test_valid_segmentation_metadata_passes(self, monkeypatch):
        segmentation = {
            "label_name": "nuclei",
            "annotation_type": "instance",
            "is_ome_label": True,
            "source_channel": {"index": 0},
            "biological_annotation": {
                "biological_target": "nucleus",
                "marker": "DAPI",
                "marker_type": "small molecule",
                "full_label": "DAPI",
            },
            "segmentation": {
                "method": "cellpose",
                "version": "2.2",
                "stitching": False,
            },
            "statistics": {"n_cells": 42},
        }
        results = self._run(monkeypatch, segmentation_metadata=segmentation)
        assert results[0].passed
        # Warning issued that the label array model isn't registered.
        warnings = [i for i in results[0].issues if i.severity == Severity.WARNING]
        assert warnings


# ---------------------------------------------------------------------------
# Node type stamping
# ---------------------------------------------------------------------------


class TestNodeTypeStamping:
    def test_image_node_stamped(self, monkeypatch):
        mock_group = MagicMock()
        mock_group.attrs = {"ome": {}}
        monkeypatch.setattr(
            "ops_validator.zarr.validator.zarr.open_group",
            lambda *a, **kw: mock_group,
        )
        mock_ome = MagicMock()
        mock_ome.ome_zarr_version = "0.5"
        monkeypatch.setattr(
            "ops_validator.zarr.validator.open_ome_zarr",
            lambda *a, **kw: mock_ome,
        )
        monkeypatch.setattr(
            "ops_validator.zarr.validator.classify_group",
            lambda *a, **kw: ZarrNodeType.IMAGE,
        )
        monkeypatch.setattr(
            "ops_validator.zarr.validator._build_node_dict",
            lambda *a, **kw: {
                "axes": ["T", "C", "Z", "Y", "X"],
                "levels": [],
                "multiscale_level_count": 0,
                "array_shapes": [],
            },
        )
        MockModel = MagicMock()
        results = validate_zarr_node(
            "/fake/img", spec_version="ops-0.1", ModelClass=MockModel
        )
        assert all(r.node_type == ZarrNodeType.IMAGE for r in results)
