"""
Pydantic models for the OPS Zarr plate store hierarchy.

Levels 4 and 7 use pydantic-zarr (ArraySpec) following the DCA pattern.
Levels 0, 2, 3, 5, 6 validate the zarr group attributes directly as Pydantic models.
"""

from __future__ import annotations

from functools import reduce
from operator import mul
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator
from pydantic_zarr.v3 import ArraySpec, NamedConfig, RegularChunkingConfig

ALLOWED_COMPRESSION_CODECS = ("blosc", "zstd", "lz4", "numcodecs.blosc", "numcodecs.zstd", "numcodecs.lz4")
CHANNEL_TYPES = {"fluorescence", "chromogenic", "labelfree", "predicted"}


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class OmePlateAcquisition(BaseModel):
    id: int


class OmePlateRow(BaseModel):
    name: str


class OmePlateColumn(BaseModel):
    name: str


class OmePlateWell(BaseModel):
    path: str
    rowIndex: int
    columnIndex: int


class OmePlateMetadata(BaseModel):
    version: str
    name: str
    field_count: int
    acquisitions: list[OmePlateAcquisition]
    rows: list[OmePlateRow]
    columns: list[OmePlateColumn]
    wells: list[OmePlateWell]


class BiologicalAnnotation(BaseModel):
    biological_target: str
    marker: str
    marker_type: str
    full_label: str


class ChannelMetadata(BaseModel):
    name: str
    index: int
    channel_type: str
    description: str
    biological_annotation: BiologicalAnnotation | None = None
    fluorophore: str | None = None
    excitation_wavelength_nm: float | None = None
    emission_wavelength_nm: float | None = None
    antibody_catalog_id: str | None = None

    @field_validator("channel_type")
    @classmethod
    def validate_channel_type(cls, v: str) -> str:
        if v not in CHANNEL_TYPES:
            raise ValueError(
                f"channel_type must be one of {sorted(CHANNEL_TYPES)}. Got: {v!r}"
            )
        return v

    @model_validator(mode="after")
    def biological_annotation_required(self) -> ChannelMetadata:
        if self.channel_type in ("fluorescence", "predicted"):
            if self.biological_annotation is None:
                raise ValueError(
                    f"biological_annotation is required for channel_type "
                    f"'{self.channel_type}' (channel '{self.name}')"
                )
        return self


# ---------------------------------------------------------------------------
# Level 0: Plate Root
# ---------------------------------------------------------------------------

class OPSPlateRoot(BaseModel):
    """Validates zarr attributes at {screen_name}.zarr/"""
    ome: dict  # full OME plate block; parsed into OmePlateMetadata below
    channels_metadata: list[ChannelMetadata]

    @model_validator(mode="after")
    def validate_ome_plate(self) -> OPSPlateRoot:
        OmePlateMetadata(**self.ome.get("plate", {}))
        return self

    @model_validator(mode="after")
    def channel_indices_unique_and_sequential(self) -> OPSPlateRoot:
        indices = [ch.index for ch in self.channels_metadata]
        if sorted(indices) != list(range(len(indices))):
            raise ValueError(
                f"channels_metadata[].index must be 0-based sequential integers. "
                f"Got: {indices}"
            )
        return self


# ---------------------------------------------------------------------------
# Level 2: Well Group
# ---------------------------------------------------------------------------

class OmeWellImage(BaseModel):
    path: str
    acquisition: int


class OmeWellMetadata(BaseModel):
    images: list[OmeWellImage]


class OPSWellGroup(BaseModel):
    """Validates zarr attributes at {screen_name}.zarr/{row}/{col}/"""
    ome: dict

    @model_validator(mode="after")
    def validate_ome_well(self) -> OPSWellGroup:
        OmeWellMetadata(**self.ome.get("well", {}))
        return self


# ---------------------------------------------------------------------------
# Level 3: Image Group (Multiscales)
# ---------------------------------------------------------------------------

class CoordinateTransformation(BaseModel):
    type: Literal["scale"]
    scale: list[float]


class MultiscaleDataset(BaseModel):
    path: str
    coordinateTransformations: list[CoordinateTransformation]


class MultiscaleAxis(BaseModel):
    name: str
    type: str
    unit: str | None = None


class MultiscaleEntry(BaseModel):
    name: str
    axes: list[MultiscaleAxis]
    datasets: list[MultiscaleDataset]
    downsamplingMethod: str | None = None  # RECOMMENDED

    @model_validator(mode="after")
    def five_resolution_levels(self) -> MultiscaleEntry:
        if len(self.datasets) != 5:
            raise ValueError(
                f"multiscales must have exactly 5 resolution levels (full through 16x). "
                f"Got {len(self.datasets)}."
            )
        return self

    @model_validator(mode="after")
    def axes_tcxyz(self) -> MultiscaleEntry:
        names = [ax.name for ax in self.axes]
        if names != ["T", "C", "Z", "Y", "X"]:
            raise ValueError(
                f"multiscales axes must be ['T', 'C', 'Z', 'Y', 'X'] "
                f"(uppercase, per OME-NGFF v0.5). Got: {names}"
            )
        return self

    @model_validator(mode="after")
    def axis_unit_rules(self) -> MultiscaleEntry:
        """Unit is required for space/time axes; must be absent for channel axes."""
        for ax in self.axes:
            if ax.type == "channel" and ax.unit is not None:
                raise ValueError(
                    f"Channel axis '{ax.name}' must not have a unit (no physical unit). "
                    f"Got: {ax.unit!r}"
                )
            if ax.type in ("space", "time") and ax.unit is None:
                raise ValueError(
                    f"Axis '{ax.name}' (type='{ax.type}') must have a unit."
                )
        return self


class OPSImageGroup(BaseModel):
    """Validates zarr attributes at {screen_name}.zarr/{row}/{col}/0/"""
    ome: dict

    @model_validator(mode="after")
    def validate_multiscales(self) -> OPSImageGroup:
        entries = self.ome.get("multiscales", [])
        if not entries:
            raise ValueError("ome.multiscales is required at Level 3")
        for entry in entries:
            MultiscaleEntry(**entry)
        return self


# ---------------------------------------------------------------------------
# Level 4: Resolution Arrays (extends DCA DCAZarr pattern)
# ---------------------------------------------------------------------------

class OPSRegularChunkingConfig(RegularChunkingConfig):
    chunk_shape: Annotated[list[int], Field(min_length=5, max_length=5)]


OPSRegularChunking = NamedConfig[Literal["regular"], OPSRegularChunkingConfig]


class OPSResolutionArray(ArraySpec):
    """
    Validates Level 4 Zarr arrays: [T, C, Z, Y, X] shape, sharding, codecs.
    Follows the DCA DCAZarr pattern exactly.
    """
    model_config = ConfigDict(extra="allow")

    shape: Annotated[list[int], Field(min_length=5, max_length=5)]
    chunk_grid: OPSRegularChunking

    @classmethod
    def from_zarr(cls, zarr_array, **kwargs):
        context = kwargs.get("pydantic_context", {})
        model = super().from_zarr(zarr_array)
        return cls.model_validate(model.__dict__, context=context)

    @field_validator("codecs", mode="after")
    @classmethod
    def validate_sharding(cls, codecs: list[NamedConfig], info: ValidationInfo) -> list[NamedConfig]:
        found_sharding = any(c["name"] == "sharding_indexed" for c in codecs)
        if not found_sharding:
            raise ValueError(
                "Level 4 array MUST use sharding_indexed codec. No sharding codec found."
            )
        return codecs

    @field_validator("codecs", mode="after")
    @classmethod
    def validate_compression(cls, codecs: list[NamedConfig], info: ValidationInfo) -> list[NamedConfig]:
        for codec in codecs:
            if codec["name"] == "sharding_indexed":
                chunk_codecs = codec.get("configuration", {}).get("codecs", [])
                codec_names = [c["name"] for c in chunk_codecs]
                final = codec_names[-1] if codec_names else ""
                if not any(
                    final == allowed or final == f"numcodecs.{allowed.split('.')[-1]}"
                    for allowed in ("blosc", "zstd", "lz4")
                ):
                    raise ValueError(
                        f"Level 4 array inner codec SHOULD be zstd (blosc/zstd and lz4 accepted). "
                        f"Got: {final!r}"
                    )
                # index_codecs must include crc32c
                index_codecs = codec.get("configuration", {}).get("index_codecs", [])
                index_names = [c["name"] for c in index_codecs]
                if "crc32c" not in index_names:
                    raise ValueError(
                        f"Level 4 array index_codecs must include 'crc32c'. Got: {index_names}"
                    )
        return codecs


# ---------------------------------------------------------------------------
# Level 5: Labels Container
# ---------------------------------------------------------------------------

class OPSLabelsContainer(BaseModel):
    """Validates zarr attributes at {screen_name}.zarr/{row}/{col}/0/labels/"""
    ome: dict

    @model_validator(mode="after")
    def validate_labels_list(self) -> OPSLabelsContainer:
        labels = self.ome.get("labels")
        if labels is None:
            raise ValueError("ome.labels is required at Level 5 (labels container)")
        if not isinstance(labels, list):
            raise ValueError("ome.labels must be a list of label group names")
        return self


# ---------------------------------------------------------------------------
# Level 6: Label Group (per segmentation)
# ---------------------------------------------------------------------------

class SourceChannel(BaseModel):
    index: int


class SegmentationParams(BaseModel):
    method: str
    version: str
    stitching: bool | str  # False = no stitching; string = method name (e.g. "hybrid_iou")
    parameters: dict[str, Any] | None = None


class SegmentationStatistics(BaseModel):
    n_cells: int


class SegmentationMetadata(BaseModel):
    label_name: str
    annotation_type: str  # warning-only — Pending Item #8
    is_ome_label: Literal[True]
    source_channel: SourceChannel
    biological_annotation: BiologicalAnnotation
    segmentation: SegmentationParams
    statistics: SegmentationStatistics
    description: str | None = None


class OPSLabelGroup(BaseModel):
    """Validates zarr attributes at {screen_name}.zarr/{row}/{col}/0/labels/{seg_name}/"""
    segmentation_metadata: SegmentationMetadata


# ---------------------------------------------------------------------------
# Level 7: Label Resolution Array
# ---------------------------------------------------------------------------

class OPSLabelArray(ArraySpec):
    """Validates Level 7 label arrays."""
    model_config = ConfigDict(extra="allow")

    shape: Annotated[list[int], Field(min_length=5, max_length=5)]
    chunk_grid: OPSRegularChunking

    @classmethod
    def from_zarr(cls, zarr_array, **kwargs):
        context = kwargs.get("pydantic_context", {})
        model = super().from_zarr(zarr_array)
        return cls.model_validate(model.__dict__, context=context)

    @field_validator("codecs", mode="after")
    @classmethod
    def validate_sharding(cls, codecs: list[NamedConfig], info: ValidationInfo) -> list[NamedConfig]:
        found_sharding = any(c["name"] == "sharding_indexed" for c in codecs)
        if not found_sharding:
            raise ValueError(
                "Level 7 label array MUST use sharding_indexed codec."
            )
        return codecs
