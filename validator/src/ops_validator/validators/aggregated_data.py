"""Validator for aggregated_data.h5ad."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ops_validator.gencode import reference_present, validate_var_index
from ops_validator.validators.base import BaseValidator

OPS_SCHEMA_VERSION = "0.1.0"


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
        # obs index must be perturbation_id
        if adata.obs.index.name not in (None, "perturbation_id"):
            self._warning(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                f"obs index name should be 'perturbation_id'. Got: {adata.obs.index.name!r}",
            )

        # perturbation_id values must not be null
        if adata.obs.index.isnull().any():
            self._error(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                "obs index (perturbation_id) contains null values.",
            )

        # perturbation_id values must be unique
        if adata.obs.index.duplicated().any():
            n = adata.obs.index.duplicated().sum()
            self._error(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                f"obs index (perturbation_id) must be unique. Found {n} duplicate(s).",
            )

    def _validate_var(self, adata) -> None:
        # var must have feature_name column
        if "feature_name" not in adata.var.columns:
            self._error(
                "VAR",
                "aggregated_data.h5ad :: var",
                "var must have a 'feature_name' column.",
            )

        # var index uniqueness
        if adata.var.index.duplicated().any():
            n = adata.var.index.duplicated().sum()
            self._error(
                "VAR",
                "aggregated_data.h5ad :: var.index",
                f"var index (feature_id) must be unique. Found {n} duplicate(s).",
            )

    def _validate_x(self, adata) -> None:
        if adata.X is None:
            self._error("X", "aggregated_data.h5ad :: X", "X matrix is missing.")
            return

        # X must be Float32
        try:
            import scipy.sparse as sp
            if sp.issparse(adata.X):
                dtype = adata.X.dtype
            else:
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
        # p_values and neg_log10_fdr, if present, must match X shape
        for layer_name in ("p_values", "neg_log10_fdr"):
            if layer_name in adata.layers:
                layer = adata.layers[layer_name]
                if layer.shape != adata.X.shape:
                    self._error(
                        "LAYER_SHAPE",
                        f"aggregated_data.h5ad :: layers['{layer_name}']",
                        f"Layer shape {layer.shape} must match X shape {adata.X.shape}.",
                    )

        # Recommend neg_log10_fdr when p_values is present
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
                    f"aggregated_data.h5ad :: uns",
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

        if "default_embedding" in adata.uns and "X_umap" in adata.obsm:
            default = adata.uns["default_embedding"]
            if default not in adata.obsm:
                self._error(
                    "DEFAULT_EMBEDDING",
                    "aggregated_data.h5ad :: uns['default_embedding']",
                    f"default_embedding {default!r} is not present in obsm. "
                    f"Available: {list(adata.obsm.keys())}",
                )
