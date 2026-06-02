"""OPS Data Standard Validator — v0.1.0

Two complementary validator surfaces:

1. Per-artifact file validators (BaseValidator-based) for YAML/CSV/Parquet/H5AD
   artifacts:

       from ops_validator import CollectionValidator
       CollectionValidator(path).validate()

2. Zarr-image validation framework (Pydantic + ome-zarr-models) for OME-Zarr
   stores and HCS plates:

       from ops_validator import validate
       run = validate("s3://bucket/plate.ome.zarr")
"""

from ops_validator.validators.aggregated_data import AggregatedDataValidator
from ops_validator.validators.cell_data import CellDataValidator
from ops_validator.validators.collection import CollectionValidator
from ops_validator.validators.experimental import ExperimentalValidator
from ops_validator.validators.feature_definitions import FeatureDefinitionsValidator
from ops_validator.validators.perturbation_library import PerturbationLibraryValidator
from ops_validator.zarr_validation import (
    Issue,
    Severity,
    ValidationRun,
    ValidationSummary,
    ZarrNodeValidationResult,
    validate,
    validate_zarr_node,
)

__all__ = [
    # Per-artifact validators
    "CollectionValidator",
    "ExperimentalValidator",
    "PerturbationLibraryValidator",
    "CellDataValidator",
    "AggregatedDataValidator",
    "FeatureDefinitionsValidator",
    # Zarr framework
    "validate",
    "validate_zarr_node",
    "ZarrNodeValidationResult",
    "ValidationSummary",
    "ValidationRun",
    "Issue",
    "Severity",
]
