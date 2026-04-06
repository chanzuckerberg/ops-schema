"""CLI entry point for the OPS schema validator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ARTIFACT_TYPES = {
    "zarr": ("Zarr plate store (.zarr)", "ops_validator.validators.zarr_images", "ZarrImagesValidator"),
    "aggregated": ("Aggregated data (.h5ad)", "ops_validator.validators.aggregated_data", "AggregatedDataValidator"),
    "cell-data": ("Cell data (.h5ad)", "ops_validator.validators.cell_data", "CellDataValidator"),
    "collection": ("Collection metadata (.yaml)", "ops_validator.validators.collection", "CollectionValidator"),
    "experimental": ("Experimental metadata (.yaml)", "ops_validator.validators.experimental", "ExperimentalValidator"),
    "features": ("Feature definitions (.csv)", "ops_validator.validators.feature_definitions", "FeatureDefinitionsValidator"),
    "perturbation": ("Perturbation library (.csv)", "ops_validator.validators.perturbation_library", "PerturbationLibraryValidator"),
}


def main() -> None:
    """Run OPS schema validation from the command line."""
    parser = argparse.ArgumentParser(
        prog="ops-validate",
        description="Validate OPS data artifacts against the OPS Data Standard v0.1.0",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to the artifact to validate",
    )
    parser.add_argument(
        "--type",
        choices=list(ARTIFACT_TYPES.keys()),
        default=None,
        help="Artifact type to validate (auto-detected from path if omitted)",
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"ERROR: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    # Auto-detect type from file extension/name
    artifact_type = args.type
    if artifact_type is None:
        artifact_type = _detect_type(args.path)
        if artifact_type is None:
            print(
                f"ERROR: Cannot auto-detect artifact type for {args.path}. "
                f"Use --type with one of: {', '.join(ARTIFACT_TYPES.keys())}",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Auto-detected type: {artifact_type}")

    # Import and run validator
    desc, module_path, class_name = ARTIFACT_TYPES[artifact_type]
    import importlib
    module = importlib.import_module(module_path)
    validator_class = getattr(module, class_name)

    validator = validator_class(path=args.path)
    validator.validate()
    print(validator.report())
    sys.exit(0 if validator.is_valid else 1)


def _detect_type(path: Path) -> str | None:
    """Attempt to auto-detect artifact type from file path."""
    name = path.name.lower()
    suffix = path.suffix.lower()

    if suffix == ".zarr" or path.is_dir() and any(path.glob("*/zarr.json")):
        return "zarr"
    if name == "aggregated_data.h5ad":
        return "aggregated"
    if name.endswith("singlecell.h5ad") or name == "cell_data.h5ad":
        return "cell-data"
    if name == "collection_metadata.yaml":
        return "collection"
    if name == "experimental_metadata.yaml":
        return "experimental"
    if name == "feature_definitions.csv":
        return "features"
    if name == "perturbation_library.csv":
        return "perturbation"

    return None


if __name__ == "__main__":
    main()
