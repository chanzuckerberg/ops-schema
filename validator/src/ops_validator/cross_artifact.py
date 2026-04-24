"""
Cross-artifact validation.

Checks FK integrity and consistency across all submitted artifacts.
Run after all individual artifact validators have passed.
"""

from __future__ import annotations

from pathlib import Path

import anndata as ad
import pandas as pd

from ops_validator.validators.base import BaseValidator, ValidationIssue


class CrossArtifactValidator(BaseValidator):
    """
    Validates relationships between artifacts in a single experiment directory.

    Expected layout:
        {experiment_dir}/
            metadata/
                perturbation_library.csv
                feature_definitions.csv (optional)
            cell_data.parquet
            visualizations/
                {viz_id}/
                    aggregated_data.h5ad
    """

    def __init__(self, experiment_dir: str | Path):
        super().__init__(experiment_dir)
        self._lib_df: pd.DataFrame | None = None
        self._cell_df: pd.DataFrame | None = None
        self._adata: ad.AnnData | None = None
        self._feat_df: pd.DataFrame | None = None

    def validate(self) -> bool:
        base = self.path

        lib_path = base / "metadata" / "perturbation_library.csv"
        cell_path = base / "cell_data.parquet"
        feat_path = base / "metadata" / "feature_definitions.csv"

        # Find all aggregated_data.h5ad files under visualizations/
        viz_dir = base / "visualizations"
        h5ad_paths = list(viz_dir.glob("*/aggregated_data.h5ad")) if viz_dir.exists() else []

        # Load files (silently skip if missing — individual validators catch that)
        if lib_path.exists():
            try:
                self._lib_df = pd.read_csv(lib_path, dtype=str, keep_default_na=False)
            except Exception as e:
                self._error("LOAD", str(lib_path), f"Could not load perturbation_library.csv: {e}")

        if cell_path.exists():
            try:
                self._cell_df = pd.read_parquet(cell_path)
            except Exception as e:
                self._error("LOAD", str(cell_path), f"Could not load cell_data.parquet: {e}")

        if feat_path.exists():
            try:
                self._feat_df = pd.read_csv(feat_path, dtype=str, keep_default_na=False)
            except Exception:
                pass  # optional file; feature_definitions validator handles this

        # Run cross-checks
        if self._lib_df is not None and self._cell_df is not None:
            self._check_barcode_fk()
            self._check_perturbation_id_fk_cell()

        for h5ad_path in h5ad_paths:
            try:
                adata = ad.read_h5ad(h5ad_path)
            except Exception as e:
                self._error("LOAD", str(h5ad_path), f"Could not load aggregated_data.h5ad: {e}")
                continue

            if self._lib_df is not None:
                self._check_perturbation_id_fk_aggregated(adata, h5ad_path)
                self._check_v12_control_present(adata, h5ad_path)

            if self._feat_df is not None:
                self._check_var_vs_feature_definitions(adata, h5ad_path)

        if self._lib_df is not None and self._cell_df is not None and h5ad_paths:
            for h5ad_path in h5ad_paths:
                try:
                    adata = ad.read_h5ad(h5ad_path)
                    self._check_perturbation_id_consistency(adata, h5ad_path)
                    self._check_v14_n_cells_matches_cell_data(adata, h5ad_path)
                except Exception:
                    pass

        return self.is_valid

    def _check_barcode_fk(self) -> None:
        """All barcode values in cell_data must exist in perturbation_library."""
        lib_barcodes = set(self._lib_df["barcode"].dropna())
        cell_barcodes = set(self._cell_df["barcode"].dropna().astype(str))
        orphans = cell_barcodes - lib_barcodes
        if orphans:
            sample = sorted(orphans)[:5]
            self._error(
                "FK_BARCODE",
                "cell_data.parquet :: barcode",
                f"{len(orphans)} barcode value(s) in cell_data.parquet not found in "
                f"perturbation_library.csv. Sample: {sample}",
            )

    def _check_perturbation_id_fk_cell(self) -> None:
        """All perturbation_id values in cell_data must exist in perturbation_library."""
        lib_ids = set(self._lib_df["perturbation_id"].dropna())
        cell_ids = set(self._cell_df["perturbation_id"].dropna().astype(str))
        orphans = cell_ids - lib_ids
        if orphans:
            sample = sorted(orphans)[:5]
            self._error(
                "FK_PERTURBATION_ID_CELL",
                "cell_data.parquet :: perturbation_id",
                f"{len(orphans)} perturbation_id value(s) in cell_data.parquet not found in "
                f"perturbation_library.csv. Sample: {sample}",
            )

    def _check_perturbation_id_fk_aggregated(
        self, adata: ad.AnnData, h5ad_path: Path
    ) -> None:
        """All perturbation_id values in aggregated_data obs must exist in perturbation_library."""
        if "perturbation_id" not in adata.obs.columns:
            self._error(
                "FK_PERTURBATION_ID_AGG",
                f"{h5ad_path} :: obs.perturbation_id",
                "perturbation_id column missing from aggregated_data obs.",
            )
            return
        lib_ids = set(self._lib_df["perturbation_id"].dropna())
        agg_ids = set(adata.obs["perturbation_id"].dropna().astype(str))
        orphans = agg_ids - lib_ids
        if orphans:
            sample = sorted(orphans)[:5]
            self._error(
                "FK_PERTURBATION_ID_AGG",
                f"{h5ad_path} :: obs.perturbation_id",
                f"{len(orphans)} perturbation_id value(s) in aggregated_data.h5ad not found in "
                f"perturbation_library.csv. Sample: {sample}",
            )

    def _check_v12_control_present(
        self, adata: ad.AnnData, h5ad_path: Path
    ) -> None:
        """V-12: at least one perturbation_id in aggregated obs must map to a control row."""
        if "perturbation_id" not in adata.obs.columns:
            return
        if "role" not in self._lib_df.columns:
            return
        control_ids = set(
            self._lib_df.loc[self._lib_df["role"] == "control", "perturbation_id"].dropna()
        )
        agg_ids = set(adata.obs["perturbation_id"].dropna().astype(str))
        if not agg_ids & control_ids:
            self._error(
                "V12_CONTROL_PRESENT",
                f"{h5ad_path} :: obs.perturbation_id",
                "No perturbation_id in aggregated_data.h5ad obs maps to a control row "
                "in perturbation_library.csv. At least one control is required (V-12).",
            )

    def _check_perturbation_id_consistency(
        self, adata: ad.AnnData, h5ad_path: Path
    ) -> None:
        """perturbation_id set in cell_data must match perturbation_id column in aggregated_data."""
        if self._cell_df is None:
            return
        if "perturbation_id" not in adata.obs.columns:
            return
        cell_ids = set(self._cell_df["perturbation_id"].dropna().astype(str))
        agg_ids = set(adata.obs["perturbation_id"].dropna().astype(str))
        only_in_cell = cell_ids - agg_ids
        only_in_agg = agg_ids - cell_ids
        if only_in_cell:
            self._warning(
                "PERTURBATION_ID_CONSISTENCY",
                f"{h5ad_path} :: obs.perturbation_id",
                f"{len(only_in_cell)} perturbation_id(s) in cell_data not in aggregated_data obs. "
                f"Sample: {sorted(only_in_cell)[:5]}",
            )
        if only_in_agg:
            self._warning(
                "PERTURBATION_ID_CONSISTENCY",
                f"{h5ad_path} :: obs.perturbation_id",
                f"{len(only_in_agg)} perturbation_id(s) in aggregated_data obs not in cell_data. "
                f"Sample: {sorted(only_in_agg)[:5]}",
            )

    def _check_v14_n_cells_matches_cell_data(
        self, adata: ad.AnnData, h5ad_path: Path
    ) -> None:
        """V-14: obs['n_cells'] must equal the count of rows in cell_data.parquet
        whose observation_unit column values match each aggregate row.
        """
        if self._cell_df is None:
            return
        if "n_cells" not in adata.obs.columns:
            return

        observation_unit = adata.uns.get("observation_unit")
        if observation_unit is None:
            return
        if hasattr(observation_unit, "tolist"):
            unit_cols = list(observation_unit.tolist())
        else:
            unit_cols = list(observation_unit)
        if not unit_cols:
            return

        missing = [c for c in unit_cols if c not in self._cell_df.columns]
        if missing:
            self._warning(
                "V14_N_CELLS",
                f"{h5ad_path} :: obs['n_cells']",
                f"Cannot verify n_cells against cell_data.parquet: observation_unit "
                f"column(s) {missing} not present in cell_data.parquet.",
            )
            return

        cell_counts = (
            self._cell_df.groupby([self._cell_df[c].astype(str) for c in unit_cols])
            .size()
            .to_dict()
        )

        mismatches = []
        for aggregate_id, row in adata.obs[unit_cols + ["n_cells"]].iterrows():
            key_values = tuple(str(row[c]) for c in unit_cols)
            key = key_values[0] if len(key_values) == 1 else key_values
            expected = int(cell_counts.get(key, 0))
            actual = int(row["n_cells"])
            if expected != actual:
                mismatches.append((aggregate_id, actual, expected))

        if mismatches:
            sample = [
                f"{agg_id!r}: n_cells={actual}, cell_data rows={expected}"
                for agg_id, actual, expected in mismatches[:3]
            ]
            self._error(
                "V14_N_CELLS",
                f"{h5ad_path} :: obs['n_cells']",
                f"{len(mismatches)} row(s) where obs['n_cells'] does not match the "
                f"count of rows in cell_data.parquet with matching observation_unit "
                f"values. Sample: {sample}",
            )

    def _check_var_vs_feature_definitions(
        self, adata: ad.AnnData, h5ad_path: Path
    ) -> None:
        """All feature_ids in aggregated_data var must be documented in feature_definitions.

        feature_definitions.csv covers the full lab feature universe and will contain
        many features not in aggregated_data var — that is expected and not flagged.
        Only undocumented aggregated_data features (var IDs missing from feature_definitions)
        are warned about.
        """
        if self._feat_df is None or "feature_id" not in self._feat_df.columns:
            return
        feat_ids = set(self._feat_df["feature_id"].dropna())
        var_ids = set(adata.var.index.dropna().astype(str))
        undocumented = var_ids - feat_ids
        if undocumented:
            self._warning(
                "VAR_VS_FEATURES",
                f"{h5ad_path} :: var.index",
                f"{len(undocumented)} feature_id(s) in aggregated_data var are not documented "
                f"in feature_definitions.csv. Sample: {sorted(undocumented)[:5]}",
            )
