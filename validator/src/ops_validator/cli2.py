"""Next-generation OPS validator CLI.

Entry point only — validation dispatch is intentionally a stub.

Usage:
    ops-validate2 PATH [--type TYPE] [--spec-version VERSION]
"""

import argparse
import sys
from cloudpathlib import AnyPath
from pydantic import BaseModel
from ops_validator.validators import aggregated_data, cell_data, collection, experimental, feature_definitions, perturbation_library

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
        ok &= _run("cell_data", cell_data.CellDataValidator(path=self.cell_data))
        for viz in self.visualizations:
            ok &= _run(f"aggregated/{viz.id}", aggregated_data.AggregatedDataValidator(path=viz.aggregated_data))
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


def validate_structure(collection_root: AnyPath) -> OPSSubmissionStructure:
    # Placeholder for actual validation logic.
    print(f"Validating structure of: {collection_root}")

    errors = []
    structure = {
        "collection_root": collection_root
    }

    ## Check collection metadata
    if not (collection_root / "collection_metadata.yaml").is_file():
        errors.append(f"Missing expected collection_metadata.yaml file in collection root: {collection_root}")
    else:            
        structure["collection_metadata"] = collection_root / "collection_metadata.yaml"    
    
    for screen_name in collection_root.iterdir():
        if screen_name.name == "collection_metadata.yaml":
            continue

        if not screen_name.is_dir():
            errors.append(f"Expected directory for screen_name, found file: {screen_name}")
            continue
        structure["screen_name"] = screen_name

        ## Check metadata
        metadata = screen_name / "metadata"
        if not metadata.is_dir():
            errors.append(f"Expected directory for metadata, found file: {metadata}")
        else:
            for expected_file in [{"experimental_metadata": "experimental_metadata.yaml", "perturbation_metadata": "perturbation_library.csv", "feature_definitions": "feature_definitions.csv"}]:
                for key, filename in expected_file.items():
                    expected_path = metadata / filename
                    if not expected_path.is_file():
                        errors.append(f"Missing expected metadata file: {expected_path}")
                    else:
                        structure[key] = expected_path

        ## Check cell_data
        cell_data = screen_name / "cell_data.parquet"
        if not cell_data.is_file():
            errors.append(f"Missing expected cell_data file: {cell_data}")
        else:
            structure["cell_data"] = cell_data
        

        ## Check visualizations
        visualizations_dir = screen_name / "visualizations"
        if not visualizations_dir.is_dir():
            errors.append(f"Missing expected visualizations directory: {visualizations_dir}")
        else:
            visualizations = []
            for viz in visualizations_dir.iterdir():
                if not viz.is_dir():
                    errors.append(f"Expected directory for visualization, found file: {viz}")
                    continue
                viz_id = viz.name
                aggregated_data = viz / "aggregated_data.h5ad"
                if not aggregated_data.is_file():
                    errors.append(f"Missing expected aggregated_data file: {aggregated_data}")
                    continue
                examples = []
                examples_dir = viz / "examples"
                if not examples_dir.is_dir():
                    errors.append(f"Missing expected examples directory: {examples_dir}")
                    continue
                for example in examples_dir.iterdir():
                    examples.append(example)
                visualizations.append(
                    {"id": viz_id, "aggregated_data": aggregated_data, "examples": examples}
                )
            structure["visualizations"] = visualizations
        
        ## Check zarr files
        zarr_dir = list(screen_name.glob(f"{screen_name.name}*.zarr"))
        if len(zarr_dir) == 0:
            errors.append(f"Missing expected zarr file(s) for screen_name: {screen_name}")
        else:
            structure["zarr_files"] = zarr_dir
        
        
        print(errors)
    return OPSSubmissionStructure.model_validate(structure)

def validator(path: AnyPath):
    structure = validate_structure(path)
    structure.validate_ops()



def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ops-validate2",
        description="Validate OPS data artifacts (next-gen entry point).",
    )
    parser.add_argument(
        "path",
        type=AnyPath,
        help="Path to submission. Local path or s3://bucket/prefix URL.",
    )
    args = parser.parse_args()
    validator(args.path)



if __name__ == "__main__":
    main()
