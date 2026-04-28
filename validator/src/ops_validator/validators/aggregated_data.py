"""Validator for aggregated_data.h5ad."""

from __future__ import annotations

import re

import numpy as np

from ops_validator.validators.base import BaseValidator

OPS_SCHEMA_VERSION = "0.1.0"

# ---------------------------------------------------------------------------
# Standardized feature set (Vesuvius-derived)
# Feature ID formats (single-underscore separated):
#   Shape:       {compartment}_{measurement}
#   Intensity:   {compartment}_{channel}_{measurement}
#   Correlation: {compartment}_correlation_{channel_a}_{channel_b}
# ---------------------------------------------------------------------------

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
        # --- aggregate_id index ---
        if adata.obs.index.name not in (None, "aggregate_id"):
            self._warning(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                f"obs index name should be 'aggregate_id'. Got: {adata.obs.index.name!r}",
            )

        if adata.obs.index.isnull().any():
            self._error(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                "obs index (aggregate_id) contains null values.",
            )

        if adata.obs.index.duplicated().any():
            n = adata.obs.index.duplicated().sum()
            self._error(
                "OBS_INDEX",
                "aggregated_data.h5ad :: obs.index",
                f"obs index (aggregate_id) must be unique. Found {n} duplicate(s).",
            )

        # --- n_cells column (RECOMMENDED) ---
        if "n_cells" in adata.obs.columns:
            n_cells = adata.obs["n_cells"]
            if not np.issubdtype(n_cells.dtype, np.integer):
                self._error(
                    "OBS_N_CELLS",
                    "aggregated_data.h5ad :: obs['n_cells']",
                    f"obs['n_cells'] must be an integer dtype. Got: {n_cells.dtype}",
                )
            else:
                negative_mask = n_cells < 0
                if negative_mask.any():
                    n = int(negative_mask.sum())
                    sample = adata.obs.index[negative_mask][:3].tolist()
                    self._error(
                        "OBS_N_CELLS",
                        "aggregated_data.h5ad :: obs['n_cells']",
                        f"obs['n_cells'] must be non-negative. "
                        f"Found {n} negative value(s). Sample aggregate_id(s): {sample}",
                    )

        # --- perturbation_id FK column ---
        if "perturbation_id" not in adata.obs.columns:
            self._error(
                "OBS_PERTURBATION_ID",
                "aggregated_data.h5ad :: obs",
                "obs must contain a 'perturbation_id' column (FK to perturbation_library.csv).",
            )
        else:
            perturbation_id = adata.obs["perturbation_id"]
            invalid_mask = perturbation_id.isnull() | (perturbation_id.astype(str).str.strip() == "")
            if invalid_mask.any():
                n = invalid_mask.sum()
                sample = adata.obs.index[invalid_mask][:3].tolist()
                self._error(
                    "OBS_PERTURBATION_ID",
                    "aggregated_data.h5ad :: obs",
                    f"obs['perturbation_id'] must not contain null or empty values. "
                    f"Found {n} invalid row(s). Sample aggregate_id(s): {sample}",
                )

        # --- observation_unit columns must exist in obs ---
        observation_unit = adata.uns.get("observation_unit")
        if observation_unit is not None:
            if isinstance(observation_unit, np.ndarray):
                unit_cols = observation_unit.tolist()
            elif isinstance(observation_unit, (list, tuple)):
                unit_cols = list(observation_unit)
            else:
                self._error(
                    "UNS_OBSERVATION_UNIT",
                    "aggregated_data.h5ad :: uns['observation_unit']",
                    "uns['observation_unit'] must be a list of obs column name strings.",
                )
                return

            if not unit_cols:
                self._error(
                    "UNS_OBSERVATION_UNIT",
                    "aggregated_data.h5ad :: uns['observation_unit']",
                    "uns['observation_unit'] must not be empty.",
                )
                return

            if not all(isinstance(c, str) and c.strip() for c in unit_cols):
                self._error(
                    "UNS_OBSERVATION_UNIT",
                    "aggregated_data.h5ad :: uns['observation_unit']",
                    "uns['observation_unit'] must contain only non-empty strings.",
                )
                return

            if len(set(unit_cols)) != len(unit_cols):
                self._error(
                    "UNS_OBSERVATION_UNIT",
                    "aggregated_data.h5ad :: uns['observation_unit']",
                    "uns['observation_unit'] contains duplicate column name(s); each "
                    "obs column name must appear only once.",
                )
                return

            for col in unit_cols:
                if col not in adata.obs.columns:
                    self._error(
                        "OBS_OBSERVATION_UNIT",
                        "aggregated_data.h5ad :: obs",
                        f"Column '{col}' declared in uns['observation_unit'] "
                        f"is missing from obs.",
                    )

            # --- validate aggregate_id is reconstructable ---
            present_cols = [c for c in unit_cols if c in adata.obs.columns]
            if len(present_cols) == len(unit_cols):
                reconstructed = adata.obs[present_cols].astype(str).agg("|".join, axis=1)
                mismatches = adata.obs.index.astype(str) != reconstructed.values
                if mismatches.any():
                    n = mismatches.sum()
                    sample = adata.obs.index[mismatches][:3].tolist()
                    self._error(
                        "OBS_AGGREGATE_ID",
                        "aggregated_data.h5ad :: obs.index",
                        f"aggregate_id does not match concatenation of "
                        f"observation_unit columns for {n} row(s). "
                        f"Sample: {sample}",
                    )

    def _validate_var(self, adata) -> None:
        # Required var columns
        for col in ("feature_name", "feature_type", "compartment"):
            if col not in adata.var.columns:
                self._error(
                    "VAR_COLUMNS",
                    "aggregated_data.h5ad :: var",
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

        # Validate each feature_id conforms to the standardized feature format
        for feature_id in adata.var.index:
            err = _validate_feature_id_format(str(feature_id))
            if err:
                self._error("VAR_FEATURE_ID", "aggregated_data.h5ad :: var.index", err)

        # feature_type values must be from the standardized set
        if "feature_type" in adata.var.columns:
            valid_types = {"shape", "intensity", "correlation"}
            invalid = adata.var["feature_type"][~adata.var["feature_type"].isin(valid_types)]
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
                        f"{key} has shape {emb.shape}; expected (n_obs, 2).",
                    )

    def _validate_uns(self, adata) -> None:
        for key in ("observation_unit", "schema_version", "default_embedding", "title"):
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

        if "neg_log10_fdr_threshold" in adata.uns:
            threshold = adata.uns["neg_log10_fdr_threshold"]
            try:
                threshold_value = float(threshold)
            except (TypeError, ValueError):
                self._error(
                    "NEG_LOG10_FDR_THRESHOLD",
                    "aggregated_data.h5ad :: uns['neg_log10_fdr_threshold']",
                    f"neg_log10_fdr_threshold must be a float. Got: {threshold!r}",
                )
            else:
                if not np.isfinite(threshold_value) or threshold_value <= 0:
                    self._error(
                        "NEG_LOG10_FDR_THRESHOLD",
                        "aggregated_data.h5ad :: uns['neg_log10_fdr_threshold']",
                        f"neg_log10_fdr_threshold must be a positive finite float "
                        f"(in −log₁₀(FDR) units, e.g., 1.30103 for FDR = 0.05). "
                        f"Got: {threshold_value}",
                    )
