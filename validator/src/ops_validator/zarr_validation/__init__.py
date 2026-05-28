"""OPS Zarr image validation framework.

Public API:

    from ops_validator.zarr_validation import validate, validate_zarr_node

    run = validate("s3://bucket/plate.ome.zarr")
    for r in run:
        print(r.node_path, "PASS" if r.passed else "FAIL")
"""

from ops_validator.zarr_validation.result import (
    Issue,
    Severity,
    ValidationRun,
    ValidationSummary,
    ZarrNodeValidationResult,
)
from ops_validator.zarr_validation.runner import validate
from ops_validator.zarr_validation.validator import validate_zarr_node

__all__ = [
    "validate",
    "validate_zarr_node",
    "ZarrNodeValidationResult",
    "ValidationSummary",
    "ValidationRun",
    "Issue",
    "Severity",
]
