"""Next-generation OPS validator CLI.

Entry point only — validation dispatch is intentionally a stub.

Usage:
    ops-validate2 PATH [--type TYPE] [--spec-version VERSION]
"""

import logging
import sys
import warnings

import typer
from cloudpathlib import AnyPath
from pydantic import BaseModel

app = typer.Typer(add_completion=False)

from ops_validator.validators import aggregated_data, cell_data, collection, experimental, feature_definitions, perturbation_library
from ops_validator.zarr_validation import validate as validate_zarr

# Suppress ResourceWarnings from unclosed aiohttp sessions/connectors emitted
# on GC by zarr/s3fs internals — not actionable from user code.
# Two paths: warnings.warn (filtered here) and loop.call_exception_handler
# (silenced via the asyncio logger).
warnings.filterwarnings("ignore", category=ResourceWarning, message="Unclosed.*")
logging.getLogger("asyncio").setLevel(logging.CRITICAL)


class OPSVisualizations(BaseModel):
    id: str
    aggregated_data: AnyPath
    examples: list[AnyPath]

class OPSSubmissionStructure(BaseModel):
    collection_root: AnyPath
    collection_metadata: AnyPath
    screen_name: AnyPath
    experimental_metadata: AnyPath
    perturbation_metadata: AnyPath
    feature_definitions: AnyPath | None
    cell_data: AnyPath
    visualizations: list[OPSVisualizations]
    zarr_files: list[AnyPath]

    def validate_ops(self) -> bool:
        ok = True
        ok &= _run("collection", collection.CollectionValidator(path=self.collection_metadata))
        ok &= _run("experimental", experimental.ExperimentalValidator(path=self.experimental_metadata))
        ok &= _run("perturbation", perturbation_library.PerturbationLibraryValidator(path=self.perturbation_metadata))
        if self.feature_definitions is not None:
            ok &= _run("features", feature_definitions.FeatureDefinitionsValidator(path=self.feature_definitions))
        ok &= _run("cell_data", cell_data.CellDataValidator(path=self.cell_data, sample_limit=None))
        for viz in self.visualizations:
            ok &= _run(f"aggregated/{viz.id}", aggregated_data.AggregatedDataValidator(path=viz.aggregated_data))
        for zarr_path in self.zarr_files:
            ok &= _run_zarr(f"zarr/{zarr_path.name}", zarr_path)
        return ok


def _run(label: str, validator) -> bool:
    """Run a per-artifact validator and print PASS/FAIL with any errors."""
    validator.validate()
    if validator.is_valid:
        nw = len(validator.warnings)
        suffix = f" ({nw} warnings)" if nw else ""
        print(f"  PASS  {label}{suffix}")
    else:
        print(f"  FAIL  {label}  ({len(validator.errors)} errors, {len(validator.warnings)} warnings)")
        for err in validator.errors:
            print(f"        {err}")
    return validator.is_valid


def _run_zarr(label: str, path: AnyPath) -> bool:
    """Run zarr-store validation and print PASS/FAIL per discovered store."""
    run = validate_zarr(str(path))
    for r in run:
        if r.passed:
            nw = len(r.warnings)
            suffix = f" ({nw} warnings)" if nw else ""
            print(f"  PASS  {r.node_path}{suffix}")
        else:
            print(f"  FAIL  {r.node_path}  ({len(r.errors)} errors)")
            for err in r.errors:
                print(f"        {err.message}")
    s = run.summary
    total = s.stores_passed + s.stores_failed
    print(f"  [{label}] {s.stores_passed} passed, {s.stores_failed} failed of {total}, {s.duration_seconds:.1f}s")
    return s.stores_failed == 0


def validate_structure(required: list[str], root: AnyPath) -> list[str]:
    """Return entries from `required` (relative paths) that don't exist under `root`."""
    return [p for p in required if not (root / p).exists()]


def validator(path: AnyPath):
    print(f"Validating structure of: {path}")
    screens = sorted(c for c in path.iterdir() if c.is_dir())
    if len(screens) != 1:
        print(f"  STRUCT  expected 1 screen dir; found {len(screens)}")
        sys.exit(1)
    s = screens[0]
    vis_root = s / "visualizations"
    vizs = sorted(c for c in vis_root.iterdir() if c.is_dir()) if vis_root.is_dir() else []
    zarrs = sorted(s.glob("*.zarr"))

    required = [
        "collection_metadata.yaml",
        f"{s.name}/metadata/experimental_metadata.yaml",
        f"{s.name}/metadata/perturbation_library.csv",
        f"{s.name}/cell_data.parquet",
        *(f"{s.name}/visualizations/{v.name}/aggregated_data.h5ad" for v in vizs),
    ]
    missing = validate_structure(required, path)
    for m in missing:
        print(f"  STRUCT  missing: {m}")
    if not zarrs:
        print(f"  STRUCT  no *.zarr in {s.name}")
    if missing or not zarrs:
        sys.exit(1)

    feat = s / "metadata/feature_definitions.csv"
    OPSSubmissionStructure.model_validate({
        "collection_root": path,
        "collection_metadata": path / "collection_metadata.yaml",
        "screen_name": s,
        "experimental_metadata": s / "metadata/experimental_metadata.yaml",
        "perturbation_metadata": s / "metadata/perturbation_library.csv",
        "feature_definitions": feat if feat.is_file() else None,
        "cell_data": s / "cell_data.parquet",
        "visualizations": [
            {"id": v.name, "aggregated_data": v / "aggregated_data.h5ad", "examples": []}
            for v in vizs
        ],
        "zarr_files": zarrs,
    }).validate_ops()



@app.command()
def _cli(
    path: str = typer.Argument(..., help="Path to submission or single artifact"),
    type_: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help=(
            "Artifact type. One of: collection, experimental, perturbation, "
            "features, cell-data, aggregated, zarr. "
            "If omitted, PATH is treated as a full submission directory."
        ),
    ),
) -> None:
    p = AnyPath(path)
    if type_ is None:
        validator(p)
        return
    if type_ == "collection":
        ok = _run(type_, collection.CollectionValidator(path=p))
    elif type_ == "experimental":
        ok = _run(type_, experimental.ExperimentalValidator(path=p))
    elif type_ == "perturbation":
        ok = _run(type_, perturbation_library.PerturbationLibraryValidator(path=p))
    elif type_ == "features":
        ok = _run(type_, feature_definitions.FeatureDefinitionsValidator(path=p))
    elif type_ == "cell-data":
        ok = _run(type_, cell_data.CellDataValidator(path=p))
    elif type_ == "aggregated":
        ok = _run(type_, aggregated_data.AggregatedDataValidator(path=p))
    elif type_ == "zarr":
        ok = _run_zarr(f"zarr/{p.name}", p)
    else:
        typer.echo(f"Unknown --type {type_!r}", err=True)
        raise typer.Exit(2)
    raise typer.Exit(0 if ok else 1)


def main() -> None:
    """Entry point — typer parses argv."""
    app()



if __name__ == "__main__":
    main()
