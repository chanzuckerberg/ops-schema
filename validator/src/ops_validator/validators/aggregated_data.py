"""Validator for aggregated_data.h5ad."""

from __future__ import annotations

import re

import numpy as np

from ops_validator.gencode import reference_present, validate_var_index
from ops_validator.validators.base import BaseValidator

OPS_SCHEMA_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Standardized feature set (Vesuvius-derived)
# Feature ID format: {compartment}__{channel_or_type}__{measurement}
# ---------------------------------------------------------------------------

VALID_COMPARTMENTS = {"nucleus", "cell"}

SHAPE_MEASUREMENTS = {"area", "eccentricity", "form_factor", "solidity"}

INTENSITY_MEASUREMENTS = {
    "mean", "integrated", "mass_displacement",
    "mean_edge", "std_edge", "mean_frac_0", "mean_frac_3",
}

# Feature IDs follow: {compartment}__{channel_or_type}__{measurement}
_FEATURE_ID_RE = re.compile(r"^(?P<compartment>[^_][^_]*)__(?P<middle>[^_][^_]*)__(?P<measurement>.+)$")


def _validate_feature_id_format(feature_id: str) -> str | None:
    """Return an error string if the feature_id does not conform to the standardized format,
    or None if it is valid."""
    m = _FEATURE_ID_RE.match(feature_id)
    if not m:
        return (
            f"feature_id {feature_id!r} does not match the required format "
            f"'{{compartment}}__{{channel_or_type}}__{{measurement}}'."
        )
    compartment = m.group("compartment")
    middle = m.group("middle")
    measurement = m.group("measurement")

    if compartment not in VALID_COMPARTMENTS:
        return (
            f"feature_id {feature_id!r}: compartment must be one of "
            f"{sorted(VALID_COMPARTMENTS)}. Got: {compartment!r}."
        )

    if middle == "shape":
        if measurement not in SHAPE_MEASUREMENTS:
            return (
                f"feature_id {feature_id!r}: shape measurement must be one of "
                f"{sorted(SHAPE_MEASUREMENTS)}. Got: {measurement!r}."
            )
    elif middle == "correlation":
        # channel pair: any two non-empty names separated by underscore are valid
        if "_" not in measurement:
            return (
                f"feature_id {feature_id!r}: correlation feature must encode a channel pair "
                f"as '{{channel_a}}_{{channel_b}}'. Got: {measurement!r}."
            )
    else:
        # middle is a channel name; measurement must be a valid intensity measurement
        if measurement not in INTENSITY_MEASUREMENTS:
            return (
                f"feature_id {feature_id!r}: intensity measurement must be one of "
                f"{sorted(INTENSITY_MEASUREMENTS)}. Got: {measurement!r}."
            )
    return None


class AggregatedDataValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", "aggregated_data.h5ad", f"File not found: {self.path}")
            return False

        try:
            import anndata as ad
            adata = ad.read_h5ad(self.path)
        except Exception as e:
            self._error("PARSE", "aggregated_data.h5ad", f"Failed to read h5ad: {e}")
            return False

        self._validate_obs(adata)
        self._validate_var(adata)
        self._validate_x(adata)
        self._validate_layers(adata)
        self._validate_obsm(adata)
        self._validate_uns(adata)

        return self.is_valid

    def _validate_obs(self, adata) -> None:
        if adata.obs.index.name not in (None, "perturbation_id"):
            self._warning(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                f"obs index name should be 'perturbation_id'. Got: {adata.obs.index.name!r}",
            )

        if adata.obs.index.isnull().any():
            self._error(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                "obs index (perturbation_id) contains null values.",
            )

        if adata.obs.index.duplicated().any():
            n = adata.obs.index.duplicated().sum()
            self._error(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                f"obs index (perturbation_id) must be unique. Found {n} duplicate(s).",
            )

        # cell_cycle_phase, if present, must be "interphase" or "mitotic"
        if "cell_cycle_phase" in adata.obs.columns:
            invalid = adata.obs["cell_cycle_phase"][
                ~adata.obs["cell_cycle_phase"].isin({"interphase", "mitotic"})
            ]
            if len(invalid) > 0:
                self._error(
                    "OBS_CELL_CYCLE",
                    "aggregated_data.h5ad :: obs.cell_cycle_phase",
                    f"cell_cycle_phase must be 'interphase' or 'mitotic'. "
                    f"Found invalid value(s): {invalid.unique()[:5].tolist()}",
                )

    def _validate_var(self, adata) -> None:
        # Required var columns
        for col in ("feature_name", "feature_type", "compartment"):
            if col not in adata.var.columns:
                self._error(
                    "VAR_COLUMNS",
                    f"aggregated_data.h5ad :: var",
                    f"var must have a '{col}' column.",
                )

        # var index uniqueness
        if adata.var.index.duplicated().any():
            n = adata.var.index.duplicated().sum()
            self._error(
                "VAR_INDEX",
                "aggregated_data.h5ad :: var.index",
                f"var index (feature_id) must be unique. Found {n} duplicate(s).",
            )

        # Validate each feature_id conforms to the standardized Vesuvius feature format
        for feature_id in adata.var.index:
            err = _validate_feature_id_format(str(feature_id))
            if err:
                self._error("VAR_FEATURE_ID", f"aggregated_data.h5ad :: var.index", err)

        # feature_type values must be from the standardized set
        if "feature_type" in adata.var.columns:
            valid_types = {"shape", "intensity", "correlation"}
            invalid = adata.var["feature_type"][
                ~adata.var["feature_type"].isin(valid_types)
            ]
            if len(invalid) > 0:
                self._error(
                    "VAR_FEATURE_TYPE",
                    "aggregated_data.h5ad :: var.feature_type",
                    f"feature_type must be one of {sorted(valid_types)}. "
                    f"Found invalid value(s): {invalid.unique()[:5].tolist()}",
                )

        # compartment values must be valid
        if "compartment" in adata.var.columns:
            invalid = adata.var["compartment"][
                ~adata.var["compartment"].isin(VALID_COMPARTMENTS)
            ]
            if len(invalid) > 0:
                self._error(
                    "VAR_COMPARTMENT",
                    "aggregated_data.h5ad :: var.compartment",
                    f"compartment must be one of {sorted(VALID_COMPARTMENTS)}. "
                    f"Found invalid value(s): {invalid.unique()[:5].tolist()}",
                )

    def _validate_x(self, adata) -> None:
        if adata.X is None:
            self._error("X", "aggregated_data.h5ad :: X", "X matrix is missing.")
            return

        try:
            import scipy.sparse as sp
            dtype = adata.X.dtype
        except Exception:
            dtype = None

        if dtype is not None and dtype != np.float32:
            self._error(
                "X_DTYPE",
                "aggregated_data.h5ad :: X",
                f"X must be Float32. Got: {dtype}",
            )

    def _validate_layers(self, adata) -> None:
        for layer_name in ("p_values", "neg_log10_fdr"):
            if layer_name in adata.layers:
                layer = adata.layers[layer_name]
                if layer.shape != adata.X.shape:
                    self._error(
                        "LAYER_SHAPE",
                        f"aggregated_data.h5ad :: layers['{layer_name}']",
                        f"Layer shape {layer.shape} must match X shape {adata.X.shape}.",
                    )

        if "p_values" in adata.layers and "neg_log10_fdr" not in adata.layers:
            self._warning(
                "NEG_LOG10_FDR",
                "aggregated_data.h5ad :: layers",
                "p_values layer is present but neg_log10_fdr is missing. "
                "neg_log10_fdr is RECOMMENDED when p_values is present.",
            )

    def _validate_obsm(self, adata) -> None:
        if "X_umap" not in adata.obsm:
            self._error(
                "OBSM",
                "aggregated_data.h5ad :: obsm",
                "obsm must contain 'X_umap' (required 2D UMAP embedding).",
            )
        else:
            umap = adata.obsm["X_umap"]
            if umap.shape[1] != 2:
                self._error(
                    "OBSM_UMAP",
                    "aggregated_data.h5ad :: obsm['X_umap']",
                    f"X_umap must have shape (n_perturbations, 2). Got shape: {umap.shape}",
                )

    def _validate_uns(self, adata) -> None:
        for key in ("schema_version", "default_embedding", "title"):
            if key not in adata.uns:
                self._error(
                    "UNS",
                    "aggregated_data.h5ad :: uns",
                    f"uns must contain '{key}'.",
                )

        if "schema_version" in adata.uns:
            ver = adata.uns["schema_version"]
            if ver != OPS_SCHEMA_VERSION:
                self._warning(
                    "SCHEMA_VERSION",
                    "aggregated_data.h5ad :: uns['schema_version']",
                    f"schema_version is {ver!r}; expected {OPS_SCHEMA_VERSION!r}.",
                )

        if "default_embedding" in adata.uns:
            default = adata.uns["default_embedding"]
            if default not in adata.obsm:
                self._error(
                    "DEFAULT_EMBEDDING",
                    "aggregated_data.h5ad :: uns['default_embedding']",
                    f"default_embedding {default!r} is not present in obsm. "
                    f"Available: {list(adata.obsm.keys())}",
                )
