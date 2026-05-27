"""
Top-level runner: discover stores, run validation, return results.

Usage
-----
from ops_validator.zarr import validate

# Validate a single store directly (fast — no discovery):
results = validate("s3://my-bucket/datasets/plate.ome.zarr")

# Validate all stores found under a path (recursive discovery):
results = validate("s3://my-bucket/datasets/")

for r in results:
    print(r.node_path, "PASS" if r.passed else "FAIL")
    for issue in r.issues:
        print(f"  [{issue.severity.value.upper()}] {issue.message}")
"""

from __future__ import annotations

import time
from typing import Literal

from ops_validator.zarr.discovery import discover_zarr_stores, is_zarr_store
from ops_validator.zarr.registry import UnsupportedSpecVersionError, get_model
from ops_validator.zarr.result import (
    Issue,
    Severity,
    ValidationRun,
    ValidationSummary,
    ZarrNodeValidationResult,
)
from ops_validator.zarr.validator import validate_zarr_node

_DEFAULT_SPEC_VERSION = "ops-0.1"


def validate(
    path: str,
    spec_version: str = _DEFAULT_SPEC_VERSION,
    strategy: Literal["glob", "walk"] = "glob",
) -> ValidationRun:
    """
    Validate Zarr stores at or under `path`.

    - If `path` is itself a Zarr store root (contains zarr.json), validates it
      directly without any recursive discovery.
    - Otherwise, discovers all Zarr store roots under `path` and validates each.

    This means `path` can be the root of a single store, a subdirectory within a
    dataset, or any ancestor directory containing multiple stores.

    OME NGFF structural validation and OPS spec validation are performed in a
    single pass via open_ome_zarr().

    Parameters
    ----------
    path         : local path or s3://bucket/prefix — any level of the hierarchy
    spec_version : OPS spec version to validate against. Defaults to "ops-0.1".

    Returns
    -------
    ValidationRun — iterable collection of ZarrNodeValidationResult with summary metrics
    """
    stores = (
        [path.rstrip("/")]
        if is_zarr_store(path)
        else discover_zarr_stores(path, strategy=strategy)
    )
    stores_discovered = len(stores)
    results: list[ZarrNodeValidationResult] = []

    t0 = time.monotonic()

    for node_path in stores:
        try:
            ModelClass = get_model(spec_version)
        except UnsupportedSpecVersionError as exc:
            results.append(
                ZarrNodeValidationResult(
                    node_path=node_path,
                    spec_version=spec_version,
                    passed=False,
                    issues=[
                        Issue(
                            loc=("spec_version",),
                            message=str(exc),
                            severity=Severity.ERROR,
                        )
                    ],
                )
            )
            continue

        results.extend(validate_zarr_node(node_path, spec_version, ModelClass))

    duration = time.monotonic() - t0
    summary = ValidationSummary.from_results(
        results, duration_seconds=duration, stores_discovered=stores_discovered
    )
    return ValidationRun(path=path, results=results, summary=summary)
