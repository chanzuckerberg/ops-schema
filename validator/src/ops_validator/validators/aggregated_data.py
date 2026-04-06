"""Validator for aggregated_data.h5ad."""

from __future__ import annotations

import re

import numpy as np

from ops_validator.validators.base import BaseValidator

OPS_SCHEMA_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Standardized feature set (Vesuvius-derived)
# Feature ID format: {compartment}__{channel_or_type}__{measurement}
# ---------------------------------------------------------------------------

# No restriction on compartment names — labs may use any compartment.
VALID_COMPARTMENTS = None

SHAPE_MEASUREMENTS = {"area", "eccentricity", "form_factor", "solidity"}

INTENSITY_MEASUREMENTS = {
    "mean", "integrated", "mass_displacement",
    "mean_edge", "std_edge", "mean_frac_0", "mean_frac_3",
}

# Feature IDs follow: {compartment}_{measurement} or {compartment}_{channel}_{measurement}
# Single underscore separator. Any compartment name is valid.
_FEATURE_ID_RE = re.compile(r"^(?P<compartment>[a-zA-Z]+)_(?P<rest>.+)$")


def _validate_feature_id_format(feature_id: str) -> str | None:
    """Return an error string if the feature_id does not conform to the standardized format,
    or None if it is valid."""
    m = _FEATURE_ID_RE.match(feature_id)
    if not m:
        return (
            f"feature_id {feature_id!r} does not match the required format "
            f"'{{compartment}}_{{measurement}}' or '{{compartment}}_{{channel}}_{{measurement}}'."
        )
    # Feature ID is valid if it starts with a compartment and has at least one measurement
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

        # compartment column should exist and have non-empty values
        if "compartment" in adata.var.columns:
            empty = adata.var["compartment"].isna() | (adata.var["compartment"] == "")
            if empty.any():
                self._warning(
                    "VAR_COMPARTMENT",
                    "aggregated_data.h5ad :: var.compartment",
                    f"{empty.sum()} features have empty compartment values.",
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
        # At least one 2D embedding must be present (X_umap, X_phate, X_tsne, etc.)
        embedding_keys = [k for k in adata.obsm if k.startswith("X_")]
        if not embedding_keys:
            self._error(
                "OBSM",
                "aggregated_data.h5ad :: obsm",
                "obsm must contain at least one 2D embedding (e.g., X_umap, X_phate, X_tsne).",
            )
        else:
            for key in embedding_keys:
                emb = adata.obsm[key]
                if emb.shape[1] != 2:
                    self._warning(
                        "OBSM_SHAPE",
                        f"aggregated_data.h5ad :: obsm['{key}']",
                        f"{key} has shape {emb.shape}; expected (n_perturbations, 2).",
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
