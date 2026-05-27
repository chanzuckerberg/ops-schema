"""Unit tests for the OPS v0.1 Zarr image spec Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ops_validator.zarr.spec.v0_1.models import (
    OPSChannelMetadata,
    OPSScaleLevelSpec,
    OPSSegmentationMetadata,
    OPSStoreSpecV0_1,
    validate_ops_label_metadata,
    validate_ops_plate_metadata,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _level(path: str, shape: list[int], **overrides) -> dict:
    """Build a minimal valid OPSScaleLevelSpec dict, with overrides."""
    base = {
        "path": path,
        "dtype": "uint16",
        "shape": shape,
        # Chunk: 1 t, 1 c, full spatial — ensures size >= 1 MB.
        "chunk_shape": [1, 1] + list(shape[2:]),
        "shard_shape": None,
        "codec_id": "zstd",
        "codec_level": 1,
        "index_codec_ids": None,
    }
    base.update(overrides)
    return base


def _store(axes: list[str], shapes: list[list[int]], **overrides) -> dict:
    """Build a minimal valid OPSStoreSpecV0_1 dict."""
    levels = [_level(str(i), s) for i, s in enumerate(shapes)]
    base = {
        "spec_version": "ops-0.1",
        "axes": axes,
        "multiscale_level_count": len(shapes),
        "levels": levels,
    }
    base.update(overrides)
    return base


def _five_level_shapes(
    base: list[int] = [1, 1, 16, 1024, 1024],
) -> list[list[int]]:
    """Build 5 power-of-two downsampled shapes from a base level-0 shape.

    Default base has Z=16 so the SHOULD spatial-downsampling rule (factor of 2)
    is satisfied for all three spatial dims across all 5 levels.
    """
    out = [list(base)]
    for _ in range(4):
        last = out[-1]
        out.append(
            [
                last[0],
                last[1],
                max(1, last[2] // 2),
                max(1, last[3] // 2),
                max(1, last[4] // 2),
            ]
        )
    return out


# ---------------------------------------------------------------------------
# OPSStoreSpecV0_1 — axes / levels
# ---------------------------------------------------------------------------


class TestStoreSpecAxes:
    def test_uppercase_axes_pass(self):
        OPSStoreSpecV0_1.model_validate(
            _store(["T", "C", "Z", "Y", "X"], _five_level_shapes())
        )

    def test_lowercase_axes_fail(self):
        with pytest.raises(ValidationError, match="uppercase"):
            OPSStoreSpecV0_1.model_validate(
                _store(["t", "c", "z", "y", "x"], _five_level_shapes())
            )

    def test_wrong_axes_order_fail(self):
        with pytest.raises(ValidationError):
            OPSStoreSpecV0_1.model_validate(
                _store(["T", "C", "X", "Y", "Z"], _five_level_shapes())
            )


class TestStoreSpecLevelCount:
    def test_five_levels_pass(self):
        OPSStoreSpecV0_1.model_validate(
            _store(["T", "C", "Z", "Y", "X"], _five_level_shapes())
        )

    def test_four_levels_fail(self):
        shapes = _five_level_shapes()[:4]
        with pytest.raises(ValidationError, match="Exactly 5"):
            OPSStoreSpecV0_1.model_validate(_store(["T", "C", "Z", "Y", "X"], shapes))

    def test_six_levels_fail(self):
        shapes = _five_level_shapes() + [[1, 1, 1, 32, 32]]
        with pytest.raises(ValidationError, match="Exactly 5"):
            OPSStoreSpecV0_1.model_validate(_store(["T", "C", "Z", "Y", "X"], shapes))


class TestStoreSpecDownsampling:
    def test_non_spatial_must_be_constant(self):
        shapes = _five_level_shapes()
        # Downsample channel between levels 0 and 1 — must be 1.
        shapes[1][1] = 2
        with pytest.raises(ValidationError, match="must be 1"):
            OPSStoreSpecV0_1.model_validate(_store(["T", "C", "Z", "Y", "X"], shapes))


# ---------------------------------------------------------------------------
# OPSScaleLevelSpec — sharding / index codecs
# ---------------------------------------------------------------------------


class TestIndexCodecs:
    # Shard time dim = TIME_SHARD_MIN_RECOMMENDED to keep the test focused on
    # crc32c behaviour without firing the unrelated time-shard SHOULD warning.
    def test_crc32c_present_passes(self):
        OPSScaleLevelSpec.model_validate(
            _level(
                "0",
                [1, 1, 16, 1024, 1024],
                shard_shape=[16, 1, 16, 1024, 1024],
                index_codec_ids=["bytes", "crc32c"],
            )
        )

    def test_crc32c_missing_fails(self):
        with pytest.raises(ValidationError, match="crc32c"):
            OPSScaleLevelSpec.model_validate(
                _level(
                    "0",
                    [1, 1, 16, 1024, 1024],
                    shard_shape=[16, 1, 16, 1024, 1024],
                    index_codec_ids=["bytes"],
                )
            )

    def test_no_sharding_skips_index_check(self):
        # shard_shape=None → index_codec_ids irrelevant
        OPSScaleLevelSpec.model_validate(
            _level("0", [1, 1, 16, 1024, 1024], shard_shape=None, index_codec_ids=None)
        )


class TestCodecAllowlist:
    def test_zstd_allowed(self):
        OPSScaleLevelSpec.model_validate(
            _level("0", [1, 1, 1, 1024, 1024], codec_id="zstd")
        )

    def test_gzip_rejected(self):
        with pytest.raises(ValidationError, match="not permitted"):
            OPSScaleLevelSpec.model_validate(
                _level("0", [1, 1, 1, 1024, 1024], codec_id="gzip")
            )


# ---------------------------------------------------------------------------
# Plate channel metadata
# ---------------------------------------------------------------------------


class TestPlateChannelMetadata:
    def _channel(self, **overrides) -> dict:
        base = {
            "name": "DAPI",
            "index": 0,
            "channel_type": "fluorescence",
            "description": "nuclear stain",
            "biological_annotation": {
                "biological_target": "DNA",
                "marker": "DAPI",
                "marker_type": "small molecule",
                "full_label": "DAPI stain",
            },
        }
        base.update(overrides)
        return base

    def test_fluorescence_with_bio_annotation_passes(self):
        OPSChannelMetadata.model_validate(self._channel())

    def test_fluorescence_without_bio_annotation_fails(self):
        with pytest.raises(ValidationError, match="biological_annotation is required"):
            OPSChannelMetadata.model_validate(
                self._channel(biological_annotation=None)
            )

    def test_labelfree_without_bio_annotation_passes(self):
        OPSChannelMetadata.model_validate(
            self._channel(channel_type="labelfree", biological_annotation=None)
        )

    def test_invalid_channel_type_fails(self):
        with pytest.raises(ValidationError, match="channel_type"):
            OPSChannelMetadata.model_validate(self._channel(channel_type="brightfield"))

    def test_validate_plate_metadata_missing_block(self):
        issues = validate_ops_plate_metadata({})
        assert len(issues) == 1
        assert "channels_metadata" in issues[0].message.lower()

    def test_validate_plate_metadata_ok(self):
        issues = validate_ops_plate_metadata(
            {"channels_metadata": [self._channel()]}
        )
        assert issues == []


# ---------------------------------------------------------------------------
# Label segmentation metadata
# ---------------------------------------------------------------------------


def _segmentation_metadata(**overrides) -> dict:
    base = {
        "label_name": "nuclei",
        "annotation_type": "instance",
        "is_ome_label": True,
        "source_channel": {"index": 0},
        "biological_annotation": {
            "biological_target": "nucleus",
            "marker": "DAPI",
            "marker_type": "small molecule",
            "full_label": "DAPI nuclear stain",
        },
        "segmentation": {
            "method": "cellpose",
            "version": "2.2",
            "stitching": False,
        },
        "statistics": {"n_cells": 12345},
    }
    base.update(overrides)
    return base


class TestSegmentationMetadata:
    def test_valid_segmentation_passes(self):
        OPSSegmentationMetadata.model_validate(_segmentation_metadata())

    def test_is_ome_label_false_fails(self):
        with pytest.raises(ValidationError, match="is_ome_label"):
            OPSSegmentationMetadata.model_validate(
                _segmentation_metadata(is_ome_label=False)
            )

    def test_validate_label_metadata_missing_block(self):
        issues = validate_ops_label_metadata({})
        assert len(issues) == 1
        assert "segmentation_metadata" in issues[0].message.lower()

    def test_validate_label_metadata_ok(self):
        issues = validate_ops_label_metadata(
            {"segmentation_metadata": _segmentation_metadata()}
        )
        assert issues == []

    def test_validate_label_metadata_missing_field(self):
        bad = _segmentation_metadata()
        del bad["statistics"]
        issues = validate_ops_label_metadata({"segmentation_metadata": bad})
        # Missing required field is surfaced via loc, not message.
        assert any("statistics" in str(i.loc) for i in issues)
