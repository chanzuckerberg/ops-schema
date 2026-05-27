"""OPS Zarr image validation framework.

Public API:

    from ops_validator.zarr import validate, validate_zarr_node

    run = validate("s3://bucket/plate.ome.zarr")
    for r in run:
        print(r.node_path, "PASS" if r.passed else "FAIL")
"""

from ops_validator.zarr.result import (
    Issue,
    Severity,
    ValidationRun,
    ValidationSummary,
    ZarrNodeValidationResult,
)
from ops_validator.zarr.runner import validate
from ops_validator.zarr.validator import validate_zarr_node

__all__ = [
    "validate",
    "validate_zarr_node",
    "ZarrNodeValidationResult",
    "ValidationSummary",
    "ValidationRun",
    "Issue",
    "Severity",
]
