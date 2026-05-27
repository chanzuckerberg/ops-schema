"""CLI entry point for the OPS schema validator."""

from __future__ import annotations

import argparse
import logging
import sys
import warnings
from pathlib import Path

# Suppress ResourceWarnings from unclosed aiohttp sessions/connectors emitted
# on GC by zarr/s3fs internals — not actionable from user code.
# Two paths: warnings.warn (filtered here) and loop.call_exception_handler
# (silenced via the asyncio logger).
warnings.filterwarnings("ignore", category=ResourceWarning, message="Unclosed.*")
logging.getLogger("asyncio").setLevel(logging.CRITICAL)


# File-based artifact types. Each entry: (description, module path, class name).
# Zarr artifacts are handled separately via the ops_validator.zarr framework.
ARTIFACT_TYPES = {
    "aggregated": (
        "Aggregated data (.h5ad)",
        "ops_validator.validators.aggregated_data",
        "AggregatedDataValidator",
    ),
    "cell-data": (
        "Cell data (.h5ad)",
        "ops_validator.validators.cell_data",
        "CellDataValidator",
    ),
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
        help="Path to the artifact or submission directory to validate. "
        "May be a local path or an s3://bucket/prefix URL.",
    )
    parser.add_argument(
        "--type",
        choices=list(ARTIFACT_TYPES.keys()) + ["zarr", "submission"],
        default=None,
        help=(
            "Artifact type to validate. Use 'zarr' for an OME-Zarr store, "
            "'submission' for a full submission directory. "
            "Auto-detected from path if omitted."
        ),
    )
    parser.add_argument(
        "--spec-version",
        default="ops-0.1",
        help="OPS spec version to validate Zarr stores against. Default: ops-0.1",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any SHOULD warnings are present in Zarr validation.",
    )

    args = parser.parse_args()

    is_remote = _is_remote_url(args.path)
    artifact_type = args.type

    # Remote URLs (s3://, etc.) only make sense for the Zarr framework — it
    # discovers stores and handles its own auth. Anything else requires a local
    # path we can stat and read with pathlib/yaml/csv/etc.
    if is_remote:
        if artifact_type in (None, "zarr"):
            sys.exit(
                _validate_zarr_single(
                    args.path, spec_version=args.spec_version, strict=args.strict
                )
            )
        print(
            f"ERROR: --type {artifact_type} requires a local path; got {args.path}",
            file=sys.stderr,
        )
        sys.exit(1)

    path = Path(args.path)
    if not path.exists():
        print(f"ERROR: Path does not exist: {path}", file=sys.stderr)
        sys.exit(1)

    if artifact_type == "submission" or (
        artifact_type is None and _is_submission_dir(path)
    ):
        sys.exit(_validate_submission(path, spec_version=args.spec_version))

    if artifact_type is None:
        artifact_type = _detect_type(path)
        if artifact_type is None:
            print(
                f"ERROR: Cannot auto-detect artifact type for {path}. "
                f"Use --type with one of: "
                f"{', '.join(list(ARTIFACT_TYPES.keys()) + ['zarr', 'submission'])}",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Auto-detected type: {artifact_type}")

    if artifact_type == "zarr":
        sys.exit(
            _validate_zarr_single(
                str(path), spec_version=args.spec_version, strict=args.strict
            )
        )

    # File-based artifact
    desc, module_path, class_name = ARTIFACT_TYPES[artifact_type]
    import importlib

    module = importlib.import_module(module_path)
    validator_class = getattr(module, class_name)

    validator = validator_class(path=path)
    validator.validate()
    print(validator.report())
    sys.exit(0 if validator.is_valid else 1)


def _is_remote_url(path_str: str) -> bool:
    """True for s3://, gs://, http(s)://, etc. — anything pathlib would mangle."""
    return "://" in path_str


def _is_submission_dir(path: Path) -> bool:
    """Check if path looks like a submission directory (has collection_metadata.yaml)."""
    return path.is_dir() and (path / "collection_metadata.yaml").exists()


def _detect_type(path: Path) -> str | None:
    """Attempt to auto-detect artifact type from file path."""
    name = path.name.lower()
    suffix = path.suffix.lower()

    if suffix == ".zarr" or (
        path.is_dir() and (path / "zarr.json").exists()
    ):
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


def _print_zarr_run(run, label: str | None = None) -> tuple[int, int, int]:
    """Print a ValidationRun in text form. Returns (n_pass, n_fail, n_warnings)."""
    from ops_validator.zarr.result import Severity

    if label:
        print(f"--- {label} ---")

    for r in run:
        status = "PASS" if r.passed else "FAIL"
        print(f"{status}  {r.node_path}")
        for issue in r.issues:
            prefix = "WARNING" if issue.severity == Severity.WARNING else "ERROR"
            print(f"  [{prefix}] {issue.message}")

    summary = run.summary
    warnings_count = sum(len(r.warnings) for r in run)
    print(
        f"\nValidated {summary.stores_validated} store(s) "
        f"({summary.level_zarr_jsons_validated} scale-level zarr.json files):"
    )
    print(f"  {summary.stores_passed} passed")
    print(f"  {summary.stores_failed} failed")
    print(f"  {warnings_count} warning(s)")
    print(f"  {summary.duration_seconds:.2f}s elapsed")
    return summary.stores_passed, summary.stores_failed, warnings_count


def _validate_zarr_single(
    path: Path, *, spec_version: str, strict: bool
) -> int:
    """Validate a single Zarr store path. Returns exit code."""
    from ops_validator.zarr import validate

    run = validate(str(path), spec_version=spec_version)
    _, n_fail, n_warn = _print_zarr_run(run)
    if n_fail > 0 or (strict and n_warn > 0):
        return 1
    return 0


def _validate_submission(submission_dir: Path, *, spec_version: str) -> int:
    """Validate all artifacts in a submission directory. Returns exit code."""
    import importlib

    from ops_validator.submission import check_ops_submission
    from ops_validator.zarr import validate as zarr_validate

    print(f"Validating submission directory: {submission_dir}\n")
    print("=" * 70)

    # 1. Submission directory layout check.
    print("\n--- Submission file structure ---")
    sub_result = check_ops_submission(submission_dir)
    for c in sub_result.checks:
        if c.exists:
            print(f"PASS  {c.path}")
        elif c.required:
            print(f"FAIL  {c.path}   [REQUIRED — missing]")
        else:
            print(f"SKIP  {c.path}   [OPTIONAL — missing]")
    n_missing = len(sub_result.missing_required)
    if n_missing:
        print(f"\n{n_missing} required file(s) missing.")
    else:
        print("\nAll required files present.")

    # 2. File-based per-artifact validation (existing pattern).
    collection_yaml = submission_dir / "collection_metadata.yaml"

    screen_dirs = [
        d
        for d in submission_dir.iterdir()
        if d.is_dir() and (d / "metadata").is_dir()
    ]

    artifacts: list[tuple[Path, str]] = []
    zarr_paths: list[Path] = []

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

        if (screen_dir / "cell_data.parquet").exists():
            artifacts.append((screen_dir / "cell_data.parquet", "cell-data"))

        for zarr_path in sorted(screen_dir.glob("*.zarr")):
            zarr_paths.append(zarr_path)

        vis_dir = screen_dir / "visualizations"
        if vis_dir.is_dir():
            for vis in sorted(vis_dir.iterdir()):
                if vis.is_dir():
                    h5ad = vis / "aggregated_data.h5ad"
                    if h5ad.exists():
                        artifacts.append((h5ad, "aggregated"))
                    for zarr_path in sorted(vis.glob("*.zarr")):
                        zarr_paths.append(zarr_path)

    if not artifacts and not zarr_paths and sub_result.passed:
        print("\nERROR: No artifacts found in submission directory.", file=sys.stderr)
        return 1

    print("\n" + "=" * 70)
    print("\n--- Per-artifact validation ---\n")

    all_passed = sub_result.passed
    results: list[tuple[str, str, bool, int, int]] = []

    for artifact_path, artifact_type in artifacts:
        _, module_path, class_name = ARTIFACT_TYPES[artifact_type]
        module = importlib.import_module(module_path)
        validator_class = getattr(module, class_name)

        validator = validator_class(path=artifact_path)
        validator.validate()
        passed = validator.is_valid
        n_errors = len(validator.errors)
        n_warnings = len(validator.warnings)

        if not passed:
            all_passed = False

        try:
            rel = artifact_path.relative_to(submission_dir)
        except ValueError:
            rel = artifact_path
        results.append((str(rel), artifact_type, passed, n_errors, n_warnings))

        if not passed:
            print(f"{'FAIL':>6}  {rel}")
            for err in validator.errors:
                print(f"        [ERROR] {err}")
        elif n_warnings > 0:
            print(f"{'WARN':>6}  {rel}  ({n_warnings} warnings)")
        else:
            print(f"{'PASS':>6}  {rel}")

    # 3. Zarr store validation through the new framework.
    if zarr_paths:
        print("\n--- Zarr image validation ---\n")
        for zarr_path in zarr_paths:
            try:
                rel = zarr_path.relative_to(submission_dir)
            except ValueError:
                rel = zarr_path
            run = zarr_validate(str(zarr_path), spec_version=spec_version)
            n_pass = run.summary.stores_passed
            n_fail = run.summary.stores_failed
            n_warn = sum(len(r.warnings) for r in run)
            passed = n_fail == 0
            if not passed:
                all_passed = False
                print(f"{'FAIL':>6}  {rel}  ({n_fail} failed of {n_fail + n_pass})")
                for r in run:
                    if not r.passed:
                        for err in r.errors:
                            print(f"        [ERROR] {r.node_path}: {err.message}")
            elif n_warn > 0:
                print(f"{'WARN':>6}  {rel}  ({n_warn} warnings)")
            else:
                print(f"{'PASS':>6}  {rel}")
            results.append((str(rel), "zarr", passed, n_fail, n_warn))

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
    if not sub_result.passed:
        print(f"  Submission layout: FAIL ({len(sub_result.missing_required)} missing)")
    print(f"\n  {'ALL PASSED' if all_passed else 'VALIDATION FAILED'}")
    print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    main()
