"""OPS Data Standard Validator — v0.1.0

Two complementary validator surfaces:

1. Per-artifact file validators (BaseValidator-based) for YAML/CSV/Parquet/H5AD
   artifacts. Lazily imported so heavy optional dependencies aren't pulled in
   unless the matching validator is used:

       from ops_validator import CollectionValidator
       CollectionValidator(path).validate()

2. Zarr-image validation framework (Pydantic + ome-zarr-models) for OME-Zarr
   stores and HCS plates. Imported eagerly via the ``ops_validator.zarr``
   subpackage:

       from ops_validator import validate
       run = validate("s3://bucket/plate.ome.zarr")
"""

from ops_validator.zarr import (
    Issue,
    Severity,
    ValidationRun,
    ValidationSummary,
    ZarrNodeValidationResult,
    validate,
    validate_zarr_node,
)

__all__ = [
    # Per-artifact validators (lazy)
    "CollectionValidator",
    "ExperimentalValidator",
    "PerturbationLibraryValidator",
    "CellDataValidator",
    "AggregatedDataValidator",
    "FeatureDefinitionsValidator",
    "CrossArtifactValidator",
    # Zarr framework (eager)
    "validate",
    "validate_zarr_node",
    "ZarrNodeValidationResult",
    "ValidationSummary",
    "ValidationRun",
    "Issue",
    "Severity",
]


def __getattr__(name):
    """Lazy import per-artifact file validators only when accessed."""
    _VALIDATORS = {
        "CollectionValidator": "ops_validator.validators.collection",
        "ExperimentalValidator": "ops_validator.validators.experimental",
        "PerturbationLibraryValidator": "ops_validator.validators.perturbation_library",
        "CellDataValidator": "ops_validator.validators.cell_data",
        "AggregatedDataValidator": "ops_validator.validators.aggregated_data",
        "FeatureDefinitionsValidator": "ops_validator.validators.feature_definitions",
        "CrossArtifactValidator": "ops_validator.cross_artifact",
    }
    if name in _VALIDATORS:
        import importlib

        module = importlib.import_module(_VALIDATORS[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
