"""OPS Data Standard Validator — v0.1.0

Validators are imported lazily to avoid pulling in heavy optional dependencies.
Use: ``from ops_validator.validators.zarr_images import ZarrImagesValidator``
"""

__all__ = [
    "CollectionValidator",
    "ExperimentalValidator",
    "PerturbationLibraryValidator",
    "CellDataValidator",
    "AggregatedDataValidator",
    "FeatureDefinitionsValidator",
    "ZarrImagesValidator",
    "CrossArtifactValidator",
]


def __getattr__(name):
    """Lazy import validators only when accessed."""
    _VALIDATORS = {
        "CollectionValidator": "ops_validator.validators.collection",
        "ExperimentalValidator": "ops_validator.validators.experimental",
        "PerturbationLibraryValidator": "ops_validator.validators.perturbation_library",
        "CellDataValidator": "ops_validator.validators.cell_data",
        "AggregatedDataValidator": "ops_validator.validators.aggregated_data",
        "FeatureDefinitionsValidator": "ops_validator.validators.feature_definitions",
        "ZarrImagesValidator": "ops_validator.validators.zarr_images",
        "CrossArtifactValidator": "ops_validator.cross_artifact",
    }
    if name in _VALIDATORS:
        import importlib

        module = importlib.import_module(_VALIDATORS[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
