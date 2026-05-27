"""
OPS submission structure validator.

Checks that all required (and optional) files exist at the expected paths
within an OPS collection root, following the directory layout defined in
standards/ops/0.1.0/schema.md.

Expected structure
------------------
{collection_root}/
├── collection_metadata.yaml                 REQUIRED
└── {screen_name}/                           one directory per experiment
    ├── metadata/
    │   ├── experimental_metadata.yaml       REQUIRED
    │   ├── perturbation_library.csv         REQUIRED
    │   └── feature_definitions.csv          OPTIONAL
    ├── cell_data.parquet                    REQUIRED
    ├── visualizations/
    │   └── {visualization_id}/              one directory per visualization
    │       ├── aggregated_data.h5ad         REQUIRED
    │       └── examples.zarr                REQUIRED
    └── {screen_name}.zarr                   REQUIRED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class OPSFileCheck:
    """Result of a single file/directory existence check."""

    path: str  # path relative to the collection root
    required: bool  # True = REQUIRED by spec; False = OPTIONAL
    exists: bool


@dataclass
class OPSSubmissionResult:
    """Aggregated result for a full collection root check."""

    root: str
    checks: list[OPSFileCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.exists for c in self.checks if c.required)

    @property
    def missing_required(self) -> list[OPSFileCheck]:
        return [c for c in self.checks if c.required and not c.exists]

    @property
    def missing_optional(self) -> list[OPSFileCheck]:
        return [c for c in self.checks if not c.required and not c.exists]


def check_ops_submission(root: str | Path) -> OPSSubmissionResult:
    """
    Walk *root* as an OPS collection root and check each required/optional path.

    Screen directories are any non-hidden immediate subdirectories of *root*.
    The zarr store for each screen is expected at ``{screen_name}/{screen_name}.zarr``.
    Visualization directories are any subdirectories of ``{screen_name}/visualizations/``.
    """
    r = Path(root)
    result = OPSSubmissionResult(root=str(r))

    def _check(rel: str, *, required: bool) -> None:
        result.checks.append(OPSFileCheck(rel, required, (r / rel).exists()))

    # --- Collection level ---
    _check("collection_metadata.yaml", required=True)

    # --- Screen directories (any non-hidden immediate subdirectory) ---
    try:
        screen_dirs = sorted(
            d for d in r.iterdir() if d.is_dir() and not d.name.startswith(".")
        )
    except OSError:
        screen_dirs = []

    for sd in screen_dirs:
        sn = sd.name

        _check(f"{sn}/metadata/experimental_metadata.yaml", required=True)
        _check(f"{sn}/metadata/perturbation_library.csv", required=True)
        _check(f"{sn}/metadata/feature_definitions.csv", required=False)
        _check(f"{sn}/cell_data.parquet", required=True)
        _check(f"{sn}/{sn}.zarr", required=True)

        viz_dir = sd / "visualizations"
        if not viz_dir.is_dir():
            # No visualizations/ directory at all
            result.checks.append(
                OPSFileCheck(f"{sn}/visualizations/", required=True, exists=False)
            )
            continue

        viz_subdirs = sorted(d for d in viz_dir.iterdir() if d.is_dir())
        if not viz_subdirs:
            # visualizations/ exists but is empty
            result.checks.append(
                OPSFileCheck(
                    f"{sn}/visualizations/*/aggregated_data.h5ad",
                    required=True,
                    exists=False,
                )
            )
            result.checks.append(
                OPSFileCheck(
                    f"{sn}/visualizations/*/examples.zarr", required=True, exists=False
                )
            )
            continue

        for viz in viz_subdirs:
            vid = viz.name
            _check(f"{sn}/visualizations/{vid}/aggregated_data.h5ad", required=True)
            _check(f"{sn}/visualizations/{vid}/examples.zarr", required=True)

    return result
