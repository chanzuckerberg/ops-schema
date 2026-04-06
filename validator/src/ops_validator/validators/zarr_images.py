"""
Validator for {screen_name}.zarr (OPS plate store).

Walks all 7 hierarchy levels, validating group attributes with Pydantic models
and array specs with pydantic-zarr (following the DCA pattern).

Pending Item #8: annotation_type enum — all annotation_type values emit warnings,
not errors.
"""

from __future__ import annotations

from pathlib import Path

import zarr
from pydantic import ValidationError

from ops_validator.models.zarr_images import (
    OPSImageGroup,
    OPSLabelArray,
    OPSLabelGroup,
    OPSLabelsContainer,
    OPSPlateRoot,
    OPSResolutionArray,
    OPSWellGroup,
)
from ops_validator.validators.base import BaseValidator


class ZarrImagesValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", str(self.path), f"Zarr store not found: {self.path}")
            return False

        try:
            store = zarr.open_group(str(self.path), mode="r")
        except Exception as e:
            self._error("OPEN", str(self.path), f"Failed to open Zarr store: {e}")
            return False

        # Level 0: plate root
        plate_meta = self._validate_level0(store)
        if plate_meta is None:
            return False  # can't continue without plate metadata

        # Walk wells
        rows = plate_meta.ome.get("plate", {}).get("rows", [])
        cols = plate_meta.ome.get("plate", {}).get("columns", [])
        wells = plate_meta.ome.get("plate", {}).get("wells", [])
        channel_indices = {ch.index for ch in plate_meta.channels_metadata}

        for well in wells:
            well_path = well["path"]  # e.g. "A/1"
            self._validate_well(store, well_path, channel_indices)

        return self.is_valid

    # ------------------------------------------------------------------
    # Level 0
    # ------------------------------------------------------------------

    def _validate_level0(self, store: zarr.Group) -> OPSPlateRoot | None:
        attrs = dict(store.attrs)
        try:
            plate_meta = OPSPlateRoot(**attrs)
            return plate_meta
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L0", f"{self.path} :: {field_path}", err["msg"])
            return None

    # ------------------------------------------------------------------
    # Level 2: Well group
    # ------------------------------------------------------------------

    def _validate_well(
        self, store: zarr.Group, well_path: str, channel_indices: set[int]
    ) -> None:
        if well_path not in store:
            self._error("L2_MISSING", f"{well_path}", f"Well group not found: {well_path}")
            return

        well_group = store[well_path]
        attrs = dict(well_group.attrs)
        try:
            well_meta = OPSWellGroup(**attrs)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L2", f"{well_path} :: {field_path}", err["msg"])
            return

        # Walk image groups within the well
        images = well_meta.ome.get("well", {}).get("images", [])
        for image in images:
            image_path = f"{well_path}/{image['path']}"
            self._validate_image_group(store, image_path, channel_indices)

    # ------------------------------------------------------------------
    # Level 3: Image group (multiscales)
    # ------------------------------------------------------------------

    def _validate_image_group(
        self, store: zarr.Group, image_path: str, channel_indices: set[int]
    ) -> None:
        if image_path not in store:
            self._error("L3_MISSING", image_path, f"Image group not found: {image_path}")
            return

        image_group = store[image_path]
        attrs = dict(image_group.attrs)
        try:
            OPSImageGroup(**attrs)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L3", f"{image_path} :: {field_path}", err["msg"])

        # Level 4: resolution arrays (validate however many levels exist)
        multiscales = attrs.get("ome", {}).get("multiscales", [{}])
        n_levels = len(multiscales[0].get("datasets", [])) if multiscales else 1
        for res_level in range(n_levels):
            array_path = f"{image_path}/{res_level}"
            self._validate_resolution_array(store, array_path)

        # Level 5: labels container
        labels_path = f"{image_path}/labels"
        self._validate_labels_container(store, labels_path, image_path, channel_indices)

    # ------------------------------------------------------------------
    # Level 4: Resolution arrays
    # ------------------------------------------------------------------

    def _validate_resolution_array(self, store: zarr.Group, array_path: str) -> None:
        if array_path not in store:
            self._error(
                "L4_MISSING", array_path,
                f"Resolution array not found: {array_path}"
            )
            return

        try:
            zarr_array = store[array_path]
            OPSResolutionArray.from_zarr(zarr_array)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L4", f"{array_path} :: {field_path}", err["msg"])
        except Exception as e:
            self._error("L4", array_path, f"Failed to validate resolution array: {e}")

    # ------------------------------------------------------------------
    # Level 5: Labels container
    # ------------------------------------------------------------------

    def _validate_labels_container(
        self,
        store: zarr.Group,
        labels_path: str,
        image_path: str,
        channel_indices: set[int],
    ) -> None:
        if labels_path not in store:
            # Labels are not required if there are no segmentations
            self._warning(
                "L5_MISSING", labels_path,
                f"No labels container found at {labels_path}."
            )
            return

        labels_group = store[labels_path]
        attrs = dict(labels_group.attrs)
        try:
            labels_meta = OPSLabelsContainer(**attrs)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L5", f"{labels_path} :: {field_path}", err["msg"])
            return

        # Walk each label group (handle .zarr suffix on directory names)
        label_names = labels_meta.ome.get("labels", [])
        for label_name in label_names:
            label_path = f"{labels_path}/{label_name}"
            if label_path not in store:
                label_path = f"{labels_path}/{label_name}.zarr"
            self._validate_label_group(store, label_path, channel_indices)

    # ------------------------------------------------------------------
    # Level 6: Label group (per segmentation)
    # ------------------------------------------------------------------

    def _validate_label_group(
        self, store: zarr.Group, label_path: str, channel_indices: set[int]
    ) -> None:
        if label_path not in store:
            self._error("L6_MISSING", label_path, f"Label group not found: {label_path}")
            return

        label_group = store[label_path]
        attrs = dict(label_group.attrs)
        try:
            label_meta = OPSLabelGroup(**attrs)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L6", f"{label_path} :: {field_path}", err["msg"])
            return

        # Pending Item #8: annotation_type is warning-only
        annotation_type = label_meta.segmentation_metadata.annotation_type
        self._warning(
            "PENDING_8",
            f"{label_path} :: segmentation_metadata.annotation_type",
            f"annotation_type enum is not yet finalized (Pending Item #8). "
            f"Value {annotation_type!r} accepted with warning.",
        )

        # source_channel.index must match a channel in channels_metadata
        src_idx = label_meta.segmentation_metadata.source_channel.index
        if src_idx not in channel_indices:
            self._error(
                "SOURCE_CHANNEL",
                f"{label_path} :: segmentation_metadata.source_channel.index",
                f"source_channel.index {src_idx} does not match any "
                f"channels_metadata[].index at plate root. Valid indices: {sorted(channel_indices)}",
            )

        # Level 7: label resolution array
        label_array_path = f"{label_path}/0"
        self._validate_label_array(store, label_array_path)

    # ------------------------------------------------------------------
    # Level 7: Label resolution array
    # ------------------------------------------------------------------

    def _validate_label_array(self, store: zarr.Group, array_path: str) -> None:
        if array_path not in store:
            self._error("L7_MISSING", array_path, f"Label array not found: {array_path}")
            return

        try:
            zarr_array = store[array_path]
            OPSLabelArray.from_zarr(zarr_array)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("L7", f"{array_path} :: {field_path}", err["msg"])
        except Exception as e:
            self._error("L7", array_path, f"Failed to validate label array: {e}")
