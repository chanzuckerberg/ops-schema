"""
Pydantic models for OPS Data Standard v0.1 zarr image validation.

Rules are derived from standards/ops/0.1.0/zarr-images.md.

Array storage rules (OPSStoreSpecV0_1 / OPSScaleLevelSpec):
  - Axes must be uppercase ["T", "C", "Z", "Y", "X"]
  - Exactly 5 resolution levels required (full res → 16x downsampled)
  - Sharding is RECOMMENDED (not MUST) — per-tile stores use flat chunking
  - sharding_indexed index_codecs MUST include 'crc32c'
  - Chunk/shard size limits and compression rules are the same as DCA v0.1

Metadata rules validated via validate_ops_plate_metadata / validate_ops_label_metadata:
  - Plate root: channels_metadata[].channel_type, .name, .index, .description
  - Plate root: channels_metadata[].biological_annotation required for
    fluorescence and predicted channels
  - Label group: segmentation_metadata (label_name, annotation_type, is_ome_label,
    source_channel, biological_annotation, segmentation, statistics)

MUST violations → raise ValueError without a prefix → classified as ERROR.
SHOULD violations → raise ValueError prefixed "[SHOULD]" → classified as WARNING.
"""

from __future__ import annotations

import math
from typing import Literal

import numpy as np
import pydantic
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from ops_validator.zarr.constants import (
    ALLOWED_CODECS,
    CHUNK_MIN_BYTES,
    CHUNK_REC_BYTES,
    DOWNSAMPLING_FACTOR_RECOMMENDED,
    LABEL_DTYPE_RECOMMENDED,
    NON_SPATIAL_AXES,
    RAW_DTYPES_RECOMMENDED,
    RECOMMENDED_CODEC,
    RECOMMENDED_LEVEL_MAX,
    SHARD_MAX_BYTES,
    SHARD_REC_BYTES,
    SPATIAL_SHARD_MAX_RECOMMENDED,
    TC_CHUNK_RECOMMENDED,
    TIME_SHARD_MIN_RECOMMENDED,
    _nbytes,
)
from ops_validator.zarr.result import Issue, Severity

AXES_REQUIRED = ["T", "C", "Z", "Y", "X"]
MULTISCALE_LEVEL_COUNT_REQUIRED = 5  # full res → 16x downsampled
INDEX_CODECS_REQUIRED = {"crc32c"}


class OPSScaleLevelSpec(BaseModel):
    """
    Validates one scale level (one Zarr array) inside an OPS multiscale store.

    Fields populated by validator._build_node_dict() + _extract_level()
    (which includes index_codec_ids for sharded arrays).
    """

    model_config = ConfigDict(extra="allow")

    path: str
    dtype: str
    shape: list[int]
    chunk_shape: list[int]
    shard_shape: list[int] | None = None
    codec_id: str
    codec_level: int | None = None
    index_codec_ids: list[str] | None = None

    @field_validator("codec_id")
    @classmethod
    def codec_must_be_allowed(cls, v: str) -> str:
        normalized = v.lower()
        if normalized not in ALLOWED_CODECS:
            raise ValueError(
                f"Codec '{v}' is not permitted; must be one of {sorted(ALLOWED_CODECS)}"
            )
        return normalized

    @model_validator(mode="after")
    def check_chunk_size(self) -> "OPSScaleLevelSpec":
        nbytes = _nbytes(self.chunk_shape, self.dtype)
        total_nbytes = _nbytes(self.shape, self.dtype)
        kb = nbytes / 1024

        if nbytes < CHUNK_MIN_BYTES and nbytes < total_nbytes:
            raise ValueError(
                f"Uncompressed chunk size {kb:.0f} KB is below the required 512 KB minimum "
                f"(chunk_shape={self.chunk_shape}, dtype={self.dtype})"
            )

        if nbytes < CHUNK_REC_BYTES and nbytes < total_nbytes:
            raise ValueError(
                f"[SHOULD] Uncompressed chunk size {kb:.0f} KB is below the recommended "
                f"1 MB (chunk_shape={self.chunk_shape}, dtype={self.dtype})"
            )

        return self

    @model_validator(mode="after")
    def check_chunk_shape_recommendations(self) -> "OPSScaleLevelSpec":
        _t, c, _z, _y, _x = self.chunk_shape

        warnings: list[str] = []
        if c != TC_CHUNK_RECOMMENDED:
            warnings.append(
                f"[SHOULD] Channel chunk size should be {TC_CHUNK_RECOMMENDED}; got {c}"
            )
        if warnings:
            raise ValueError("\n".join(warnings))
        return self

    @model_validator(mode="after")
    def check_shard_size(self) -> "OPSScaleLevelSpec":
        """
        Shard size checks for OPS. Sharding is recommended for merged-well stores
        but flat chunking is acceptable for per-tile stores, so the 1 GB MUST
        requirement from DCA does not apply here — all size limits are SHOULD.
        """
        if self.shard_shape is None:
            return self

        shard_bytes = _nbytes(self.shard_shape, self.dtype)

        # MUST: < 5 TB
        if shard_bytes >= SHARD_MAX_BYTES:
            raise ValueError(
                f"Uncompressed shard size {shard_bytes / 1024**4:.1f} TB must be < 5 TB"
            )

        warnings: list[str] = []

        # SHOULD: < 5 GB
        if shard_bytes > SHARD_REC_BYTES:
            warnings.append(
                f"[SHOULD] Uncompressed shard size {shard_bytes / 1024**3:.1f} GB "
                f"exceeds the recommended 5 GB"
            )

        _t, _c, z, y, x = self.shard_shape
        for dim_name, dim_val in (("z", z), ("y", y), ("x", x)):
            if dim_val > SPATIAL_SHARD_MAX_RECOMMENDED:
                warnings.append(
                    f"[SHOULD] Shard size in {dim_name} ({dim_val}) exceeds "
                    f"the recommended maximum of {SPATIAL_SHARD_MAX_RECOMMENDED}"
                )

        if _t < TIME_SHARD_MIN_RECOMMENDED:
            warnings.append(
                f"[SHOULD] Time shard size ({_t}) is below the recommended "
                f"minimum of {TIME_SHARD_MIN_RECOMMENDED}"
            )

        if warnings:
            raise ValueError("\n".join(warnings))
        return self

    @model_validator(mode="after")
    def check_index_codecs(self) -> "OPSScaleLevelSpec":
        """When sharding_indexed is used, index_codecs MUST include 'crc32c'."""
        if self.shard_shape is None or self.index_codec_ids is None:
            return self
        missing = INDEX_CODECS_REQUIRED - set(self.index_codec_ids)
        if missing:
            raise ValueError(
                f"sharding_indexed index_codecs must include {sorted(missing)}; "
                f"got {self.index_codec_ids}"
            )
        return self

    @model_validator(mode="after")
    def check_compression_recommendation(self) -> "OPSScaleLevelSpec":
        warnings: list[str] = []
        dtype_kind = np.dtype(self.dtype).kind

        if dtype_kind in ("u", "i"):
            if self.codec_id == "blosc":
                warnings.append(
                    "[SHOULD] Integer data should use zstd (not blosc) for compression"
                )
            if (
                self.codec_id == RECOMMENDED_CODEC
                and self.codec_level is not None
                and self.codec_level > RECOMMENDED_LEVEL_MAX
            ):
                warnings.append(
                    f"[SHOULD] Compression level {self.codec_level} exceeds the recommended "
                    f"maximum of {RECOMMENDED_LEVEL_MAX}"
                )
        elif dtype_kind == "f":
            if self.codec_id == "blosc":
                warnings.append(
                    "[SHOULD] Float data should use byte shuffle + zstd (not blosc)"
                )
            if (
                self.codec_id == RECOMMENDED_CODEC
                and self.codec_level is not None
                and self.codec_level > RECOMMENDED_LEVEL_MAX
            ):
                warnings.append(
                    f"[SHOULD] Compression level {self.codec_level} exceeds the recommended "
                    f"maximum of {RECOMMENDED_LEVEL_MAX}"
                )

        if warnings:
            raise ValueError("\n".join(warnings))
        return self

    @model_validator(mode="after")
    def check_dtype_recommendation(self) -> "OPSScaleLevelSpec":
        normalized = str(np.dtype(self.dtype))
        if (
            normalized not in RAW_DTYPES_RECOMMENDED
            and normalized != LABEL_DTYPE_RECOMMENDED
        ):
            raise ValueError(
                f"[SHOULD] dtype '{self.dtype}' is unusual; raw arrays should use "
                f"uint8 or uint16, label arrays should use uint32"
            )
        return self


class OPSStoreSpecV0_1(BaseModel):
    """
    Root OPS v0.1 model. Validates a full multiscale Zarr store against the
    OPS Data Standard zarr-images.md specification.

    Call OPSStoreSpecV0_1.model_validate(data) where data is the dict
    produced by validator._build_node_dict().
    """

    model_config = ConfigDict(extra="allow")

    spec_version: Literal["ops-0.1"]
    axes: list[str]
    multiscale_level_count: int
    levels: list[OPSScaleLevelSpec]

    @field_validator("axes")
    @classmethod
    def axes_must_be_TCZYX(cls, v: list[str]) -> list[str]:
        if v != AXES_REQUIRED:
            raise ValueError(
                f"Axes must be {AXES_REQUIRED} (uppercase, per OME-NGFF v0.5); got {v}. "
                "All datasets must be 5D with dimensions in T, C, Z, Y, X order."
            )
        return v

    @field_validator("multiscale_level_count")
    @classmethod
    def must_have_5_levels(cls, v: int) -> int:
        if v != MULTISCALE_LEVEL_COUNT_REQUIRED:
            raise ValueError(
                f"Exactly {MULTISCALE_LEVEL_COUNT_REQUIRED} resolution levels are required "
                f"(full resolution through 16x downsampled); found {v}"
            )
        return v

    @model_validator(mode="after")
    def check_downsampling_factors(self) -> "OPSStoreSpecV0_1":
        if len(self.levels) < 2:
            return self

        axes_lower = [a.lower() for a in AXES_REQUIRED]
        must_errors: list[str] = []
        should_warnings: list[str] = []

        for i in range(len(self.levels) - 1):
            coarse = self.levels[i].shape
            fine = self.levels[i + 1].shape

            for dim_idx, dim_name in enumerate(axes_lower):
                coarse_dim = coarse[dim_idx]
                fine_dim = fine[dim_idx]

                if fine_dim == 0:
                    continue

                factor = coarse_dim / fine_dim

                if dim_name in NON_SPATIAL_AXES:
                    if coarse_dim != fine_dim:
                        must_errors.append(
                            f"Level {i}→{i+1}: downsampling factor for '{dim_name.upper()}' "
                            f"must be 1 (got {coarse_dim}/{fine_dim}={factor:.2f})"
                        )
                else:
                    if not math.isclose(
                        factor, DOWNSAMPLING_FACTOR_RECOMMENDED, rel_tol=0.05
                    ):
                        should_warnings.append(
                            f"[SHOULD] Level {i}→{i+1}: downsampling "
                            f"factor for '{dim_name.upper()}' "
                            f"should be {DOWNSAMPLING_FACTOR_RECOMMENDED} "
                            f"(got {coarse_dim}/{fine_dim}≈{factor:.2f})"
                        )

        all_issues = must_errors + should_warnings
        if all_issues:
            raise ValueError("\n".join(all_issues))

        return self


# ---------------------------------------------------------------------------
# Label group metadata — segmentation_metadata
# ---------------------------------------------------------------------------


class _OPSSegmentationSourceChannel(BaseModel):
    model_config = ConfigDict(extra="allow")
    index: int


class _OPSSegmentationBioAnnotation(BaseModel):
    model_config = ConfigDict(extra="allow")
    biological_target: str
    marker: str
    marker_type: str
    full_label: str


class _OPSSegmentationInfo(BaseModel):
    model_config = ConfigDict(extra="allow")
    method: str
    version: str
    stitching: bool | str  # False = no stitching; string = stitching method name
    parameters: dict | None = None


class _OPSSegmentationStatistics(BaseModel):
    model_config = ConfigDict(extra="allow")
    n_cells: int


class OPSSegmentationMetadata(BaseModel):
    """segmentation_metadata block required at every OPS label group."""

    model_config = ConfigDict(extra="allow")

    label_name: str
    annotation_type: str
    is_ome_label: bool
    source_channel: _OPSSegmentationSourceChannel
    biological_annotation: _OPSSegmentationBioAnnotation
    segmentation: _OPSSegmentationInfo
    statistics: _OPSSegmentationStatistics
    description: str | None = None

    @field_validator("is_ome_label")
    @classmethod
    def is_ome_label_must_be_true(cls, v: bool) -> bool:
        if not v:
            raise ValueError(
                "is_ome_label must be true for OME-NGFF compliant label arrays"
            )
        return v


class _OPSLabelSpec(BaseModel):
    model_config = ConfigDict(extra="allow")
    segmentation_metadata: OPSSegmentationMetadata


# ---------------------------------------------------------------------------
# Plate root metadata — channels_metadata
# (Defined after _OPSSegmentationBioAnnotation so the type is concrete at class
# build time rather than relying on PEP 563 forward references.)
# ---------------------------------------------------------------------------

VALID_CHANNEL_TYPES = frozenset(
    {"fluorescence", "chromogenic", "labelfree", "predicted"}
)
_CHANNELS_REQUIRING_BIO_ANNOTATION = frozenset({"fluorescence", "predicted"})


class OPSChannelMetadata(BaseModel):
    """One entry in channels_metadata at the plate root."""

    model_config = ConfigDict(extra="allow")

    name: str
    index: int
    channel_type: str
    description: str
    biological_annotation: _OPSSegmentationBioAnnotation | None = None
    fluorophore: str | None = None
    excitation_wavelength_nm: float | None = None
    emission_wavelength_nm: float | None = None
    antibody_catalog_id: str | None = None

    @field_validator("channel_type")
    @classmethod
    def channel_type_must_be_valid(cls, v: str) -> str:
        if v not in VALID_CHANNEL_TYPES:
            raise ValueError(
                f"channel_type must be one of {sorted(VALID_CHANNEL_TYPES)}; got '{v}'"
            )
        return v

    @model_validator(mode="after")
    def biological_annotation_required(self) -> "OPSChannelMetadata":
        if (
            self.channel_type in _CHANNELS_REQUIRING_BIO_ANNOTATION
            and not self.biological_annotation
        ):
            raise ValueError(
                f"biological_annotation is required when channel_type='{self.channel_type}'"
            )
        return self


class _OPSPlateChannelsSpec(BaseModel):
    model_config = ConfigDict(extra="allow")
    channels_metadata: list[OPSChannelMetadata]


# ---------------------------------------------------------------------------
# Public validation functions — called by registry → validator
# ---------------------------------------------------------------------------


def _pydantic_to_issues(exc: pydantic.ValidationError) -> list[Issue]:
    """Convert a pydantic.ValidationError to list[Issue] without importing validator."""
    _SHOULD = "[SHOULD]"
    issues: list[Issue] = []
    for error in exc.errors(include_url=False):
        loc = tuple(error.get("loc", ()))
        raw_msg: str = error.get("msg", "")
        if raw_msg.startswith("Value error, "):
            raw_msg = raw_msg[len("Value error, ") :]
        for line in raw_msg.splitlines():
            line = line.strip()
            if not line:
                continue
            sev = Severity.WARNING if line.startswith(_SHOULD) else Severity.ERROR
            msg = line[len(_SHOULD) :].strip() if sev == Severity.WARNING else line
            issues.append(Issue(loc=loc, message=msg, severity=sev))
    return issues


def validate_ops_plate_metadata(raw_attrs: dict) -> list[Issue]:
    """
    Validate channels_metadata at the HCS plate root against the OPS spec.

    Called by validator._check_plate_structure when spec_version == "ops-0.1".
    """
    if "channels_metadata" not in raw_attrs:
        return [
            Issue(
                loc=("channels_metadata",),
                message="channels_metadata is required at the plate root",
                severity=Severity.ERROR,
            )
        ]
    try:
        _OPSPlateChannelsSpec.model_validate(
            {"channels_metadata": raw_attrs["channels_metadata"]}
        )
        return []
    except pydantic.ValidationError as exc:
        return _pydantic_to_issues(exc)


def validate_ops_label_metadata(raw_attrs: dict) -> list[Issue]:
    """
    Validate segmentation_metadata at an OPS label group.

    Called by validator.validate_zarr_node for IMAGE_LABEL nodes when
    spec_version == "ops-0.1".
    """
    if "segmentation_metadata" not in raw_attrs:
        return [
            Issue(
                loc=("segmentation_metadata",),
                message="segmentation_metadata is required at OPS label groups",
                severity=Severity.ERROR,
            )
        ]
    try:
        _OPSLabelSpec.model_validate(
            {"segmentation_metadata": raw_attrs["segmentation_metadata"]}
        )
        return []
    except pydantic.ValidationError as exc:
        return _pydantic_to_issues(exc)
