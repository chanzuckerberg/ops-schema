"""
Maps OPS spec version strings to their root Pydantic model class.

Four registries exist:
  _REGISTRY                — image multiscale model per spec version
  _LABEL_REGISTRY          — label image model per spec version
  _PLATE_METADATA_REGISTRY — plate-root metadata validator fn per spec version
  _LABEL_METADATA_REGISTRY — label-group metadata validator fn per spec version

To add support for a new spec version:
  1. Create src/ops_validator/zarr/spec/vX_Y/models.py with the relevant model
     classes and optional validate_*_metadata functions.
  2. Add entries to the relevant registries below.
"""

from collections.abc import Callable

from pydantic import BaseModel

from ops_validator.zarr_validation.result import Issue
from ops_validator.zarr_validation.spec.v0_1.models import (
    OPSStoreSpecV0_1,
    validate_ops_label_metadata,
    validate_ops_plate_metadata,
)


class UnsupportedSpecVersionError(ValueError):
    def __init__(self, version: str, *, label: bool = False) -> None:
        registry = _LABEL_REGISTRY if label else _REGISTRY
        supported = sorted(registry)
        kind = "label " if label else ""
        super().__init__(
            f"OPS spec version '{version}' is not supported for {kind}validation. "
            f"Supported versions: {supported}"
        )


_REGISTRY: dict[str, type[BaseModel]] = {
    "ops-0.1": OPSStoreSpecV0_1,
}

# Label image model registry. None registered for v0.1: OPS label groups share
# the multiscale schema with image groups, so dispatch falls back to the main
# OPSStoreSpec; only the segmentation_metadata sidecar is checked separately.
_LABEL_REGISTRY: dict[str, type[BaseModel]] = {}

# Plate-root metadata validator registry: fn(raw_attrs) -> list[Issue]
_PLATE_METADATA_REGISTRY: dict[str, Callable[[dict], list[Issue]]] = {
    "ops-0.1": validate_ops_plate_metadata,
}

# Label-group metadata validator registry: fn(raw_attrs) -> list[Issue]
_LABEL_METADATA_REGISTRY: dict[str, Callable[[dict], list[Issue]]] = {
    "ops-0.1": validate_ops_label_metadata,
}


def get_model(spec_version: str) -> type[BaseModel]:
    """Return the OPSStoreSpec model class for the given spec version string."""
    if spec_version not in _REGISTRY:
        raise UnsupportedSpecVersionError(spec_version)
    return _REGISTRY[spec_version]


def get_label_model(spec_version: str) -> type[BaseModel]:
    """Return the OPS label model class for the given spec version string."""
    if spec_version not in _LABEL_REGISTRY:
        raise UnsupportedSpecVersionError(spec_version, label=True)
    return _LABEL_REGISTRY[spec_version]


def get_plate_metadata_validator(
    spec_version: str,
) -> Callable[[dict], list[Issue]] | None:
    """Return the plate-root metadata validator for this spec, or None."""
    return _PLATE_METADATA_REGISTRY.get(spec_version)


def get_label_metadata_validator(
    spec_version: str,
) -> Callable[[dict], list[Issue]] | None:
    """Return the label-group metadata validator for this spec, or None."""
    return _LABEL_METADATA_REGISTRY.get(spec_version)
