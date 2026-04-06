"""CLI entry point for the OPS schema validator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ARTIFACT_TYPES = {
    "zarr": (
        "Zarr plate store (.zarr)",
        "ops_validator.validators.zarr_images",
        "ZarrImagesValidator",
    ),
    "aggregated": (
        "Aggregated data (.h5ad)",
        "ops_validator.validators.aggregated_data",
        "AggregatedDataValidator",
    ),
    "cell-data": ("Cell data (.h5ad)", "ops_validator.validators.cell_data", "CellDataValidator"),
    "collection": (
        "Collection metadata (.yaml)",
        "ops_validator.validators.collection",
        "CollectionValidator",
    ),
    "experimental": (
        "Experimental metadata (.yaml)",
        "ops_validator.validators.experimental",
        "ExperimentalValidator",
    ),
    "features": (
        "Feature definitions (.csv)",
        "ops_validator.validators.feature_definitions",
        "FeatureDefinitionsValidator",
    ),
    "perturbation": (
        "Perturbation library (.csv)",
        "ops_validator.validators.perturbation_library",
        "PerturbationLibraryValidator",
    ),
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
        help="Path to the artifact or submission directory to validate",
    )
    parser.add_argument(
        "--type",
        choices=list(ARTIFACT_TYPES.keys()) + ["submission"],
        default=None,
        help=(
            "Artifact type to validate. Use 'submission' for a full submission directory. "
            "Auto-detected from path if omitted."
        ),
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(f"ERROR: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)

    # If --type submission or auto-detected as submission directory, validate all
    artifact_type = args.type
    if artifact_type == "submission" or (artifact_type is None and _is_submission_dir(args.path)):
        sys.exit(_validate_submission(args.path))

    # Auto-detect type from file extension/name
    if artifact_type is None:
        artifact_type = _detect_type(args.path)
        if artifact_type is None:
            print(
                f"ERROR: Cannot auto-detect artifact type for {args.path}. "
                f"Use --type with one of: {', '.join(ARTIFACT_TYPES.keys())}, submission",
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


def _is_submission_dir(path: Path) -> bool:
    """Check if path looks like a submission directory (has collection_metadata.yaml)."""
    return path.is_dir() and (path / "collection_metadata.yaml").exists()


def _validate_submission(submission_dir: Path) -> int:
    """Validate all artifacts in a submission directory. Returns exit code."""
    import importlib

    print(f"Validating submission directory: {submission_dir}\n")
    print("=" * 70)

    collection_yaml = submission_dir / "collection_metadata.yaml"

    # Find screen directories (any subdir that has metadata/)
    screen_dirs = [d for d in submission_dir.iterdir() if d.is_dir() and (d / "metadata").is_dir()]

    # Build list of (path, type) pairs to validate
    artifacts: list[tuple[Path, str]] = []

    if collection_yaml.exists():
        artifacts.append((collection_yaml, "collection"))

    for screen_dir in sorted(screen_dirs):
        meta = screen_dir / "metadata"
        if (meta / "experimental_metadata.yaml").exists():
            artifacts.append((meta / "experimental_metadata.yaml", "experimental"))
        if (meta / "perturbation_library.csv").exists():
            artifacts.append((meta / "perturbation_library.csv", "perturbation"))
        if (meta / "feature_definitions.csv").exists():
            artifacts.append((meta / "feature_definitions.csv", "features"))

        # Cell data
        if (screen_dir / "cell_data.parquet").exists():
            artifacts.append((screen_dir / "cell_data.parquet", "cell-data"))

        # Zarr stores (plate-level)
        for zarr_path in sorted(screen_dir.glob("*.zarr")):
            artifacts.append((zarr_path, "zarr"))

        # Visualizations
        vis_dir = screen_dir / "visualizations"
        if vis_dir.is_dir():
            for vis in sorted(vis_dir.iterdir()):
                if vis.is_dir():
                    h5ad = vis / "aggregated_data.h5ad"
                    if h5ad.exists():
                        artifacts.append((h5ad, "aggregated"))

    if not artifacts:
        print("ERROR: No artifacts found in submission directory.", file=sys.stderr)
        return 1

    # Validate each artifact
    all_passed = True
    results: list[tuple[str, str, bool, int, int]] = []

    for artifact_path, artifact_type in artifacts:
        desc, module_path, class_name = ARTIFACT_TYPES[artifact_type]
        module = importlib.import_module(module_path)
        validator_class = getattr(module, class_name)

        validator = validator_class(path=artifact_path)
        validator.validate()
        passed = validator.is_valid
        n_errors = len(validator.errors)
        n_warnings = len(validator.warnings)

        if not passed:
            all_passed = False

        # Short relative path for display
        try:
            rel = artifact_path.relative_to(submission_dir)
        except ValueError:
            rel = artifact_path
        results.append((str(rel), artifact_type, passed, n_errors, n_warnings))

        # Print details for failures
        if not passed:
            print(f"\n{'FAIL':>6}  {rel}")
            for err in validator.errors:
                print(f"        [ERROR] {err}")
        elif n_warnings > 0:
            print(f"\n{'WARN':>6}  {rel}  ({n_warnings} warnings)")
        else:
            print(f"\n{'PASS':>6}  {rel}")

    # Summary table
    print("\n" + "=" * 70)
    print(f"\n{'SUMMARY':^70}\n")
    print(f"  {'Artifact':<50} {'Status':>8}")
    print(f"  {'-' * 50} {'-' * 8}")
    for rel, atype, passed, n_err, n_warn in results:
        status = "PASS" if passed else "FAIL"
        extra = f" ({n_warn}w)" if n_warn > 0 and passed else ""
        print(f"  {rel:<50} {status:>8}{extra}")

    n_pass = sum(1 for _, _, p, _, _ in results if p)
    n_fail = sum(1 for _, _, p, _, _ in results if not p)
    print(f"\n  {n_pass} passed, {n_fail} failed out of {len(results)} artifacts")
    print(f"\n  {'ALL PASSED' if all_passed else 'VALIDATION FAILED'}")
    print()

    return 0 if all_passed else 1


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
