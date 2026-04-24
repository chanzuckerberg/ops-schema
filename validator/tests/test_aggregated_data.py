"""Tests for AggregatedDataValidator — standardized feature set enforcement."""

from __future__ import annotations

import numpy as np
import pytest

from ops_validator.validators.aggregated_data import (
    AggregatedDataValidator,
    _validate_feature_id_format,
)


# ---------------------------------------------------------------------------
# Unit tests for _validate_feature_id_format
# ---------------------------------------------------------------------------

class TestFeatureIdFormat:
    # Valid shape features: {compartment}_{measurement}
    @pytest.mark.parametrize("feature_id", [
        "nucleus_area",
        "cell_eccentricity",
        "nucleus_form_factor",
        "cell_solidity",
    ])
    def test_valid_shape_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    # Valid intensity features: {compartment}_{channel}_{measurement}
    @pytest.mark.parametrize("feature_id", [
        "nucleus_DAPI_mean",
        "cell_COXIV_integrated",
        "nucleus_GH2AX_mass_displacement",
        "cell_WGA_mean_edge",
        "nucleus_GFP_std_edge",
        "cell_MCHERRY_mean_frac_0",
        "nucleus_DAPI_mean_frac_3",
    ])
    def test_valid_intensity_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    # Valid correlation features: {compartment}_correlation_{channel_a}_{channel_b}
    @pytest.mark.parametrize("feature_id", [
        "nucleus_correlation_CENPA_DAPI",
        "cell_correlation_COXIV_WGA",
        "nucleus_correlation_GFP_MCHERRY",
    ])
    def test_valid_correlation_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None


# ---------------------------------------------------------------------------
# Integration tests via AggregatedDataValidator
# ---------------------------------------------------------------------------

def _make_h5ad(
    tmp_path,
    obs_index,
    var_index,
    var_columns=None,
    obs_columns=None,
    layers=None,
    obsm=None,
    uns=None,
    x_dtype=np.float32,
    observation_unit=None,
    perturbation_ids=None,
):
    """Helper to write a minimal valid AnnData file."""
    import anndata as ad
    import pandas as pd

    if observation_unit is None:
        observation_unit = ["perturbation_id"]

    n_obs = len(obs_index)
    n_var = len(var_index)

    X = np.zeros((n_obs, n_var), dtype=x_dtype)
    obs = pd.DataFrame(index=obs_index)
    obs.index.name = "aggregate_id"

    if perturbation_ids is not None:
        obs["perturbation_id"] = perturbation_ids
    else:
        obs["perturbation_id"] = obs_index

    for col_idx, col in enumerate(observation_unit):
        if col not in obs.columns:
            if len(observation_unit) == 1:
                obs[col] = obs_index
            else:
                obs[col] = [str(idx).split("|")[col_idx] if "|" in str(idx) else idx for idx in obs_index]

    if obs_columns:
        for col, vals in obs_columns.items():
            obs[col] = vals

    var_data = {"feature_name": [v.split("_", 1)[-1] for v in var_index]}
    var_data["feature_type"] = ["shape" if len(v.split("_")) == 2 else "correlation" if "_correlation_" in v else "intensity" for v in var_index]
    var_data["compartment"] = [v.split("_", 1)[0] for v in var_index]
    if var_columns:
        var_data.update(var_columns)
    var = pd.DataFrame(var_data, index=var_index)
    var.index.name = "feature_id"

    _obsm = {"X_umap": np.zeros((n_obs, 2), dtype=np.float32)}
    if obsm:
        _obsm.update(obsm)

    _uns = {
        "observation_unit": observation_unit,
        "schema_version": "0.1.0",
        "default_embedding": "X_umap",
        "title": "Test",
    }
    if uns:
        _uns.update(uns)

    adata = ad.AnnData(X=X, obs=obs, var=var, obsm=_obsm, uns=_uns)
    if layers:
        for k, v in layers.items():
            adata.layers[k] = v

    path = tmp_path / "aggregated_data.h5ad"
    adata.write_h5ad(path)
    return path


VALID_FEATURES = [
    "nucleus_area",
    "cell_eccentricity",
    "nucleus_DAPI_mean",
    "cell_COXIV_integrated",
    "nucleus_correlation_DAPI_COXIV",
]
VALID_PERTURBATIONS = ["pert_001", "pert_002", "pert_003"]


class TestAggregatedDataValidator:
    def test_valid_file_passes(self, tmp_path):
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, VALID_FEATURES)
        v = AggregatedDataValidator(path)
        assert v.validate() is True
        assert len(v.errors) == 0

    def test_missing_file_errors(self, tmp_path):
        v = AggregatedDataValidator(tmp_path / "aggregated_data.h5ad")
        assert v.validate() is False
        assert any(i.rule_id == "MISSING" for i in v.errors)

    def test_guide_level_observation_unit(self, tmp_path):
        barcodes = ["ACGT", "TGCA", "GGCC"]
        path = _make_h5ad(
            tmp_path,
            barcodes,
            VALID_FEATURES,
            observation_unit=["barcode"],
            perturbation_ids=["gene_A", "gene_A", "gene_B"],
        )
        v = AggregatedDataValidator(path)
        assert v.validate() is True
        assert len(v.errors) == 0

    def test_multi_column_observation_unit(self, tmp_path):
        obs_index = ["gene_A|mitotic", "gene_A|interphase", "gene_B|mitotic"]
        path = _make_h5ad(
            tmp_path,
            obs_index,
            VALID_FEATURES,
            observation_unit=["perturbation_id", "cell_cycle_phase"],
            perturbation_ids=["gene_A", "gene_A", "gene_B"],
            obs_columns={
                "cell_cycle_phase": ["mitotic", "interphase", "mitotic"],
            },
        )
        v = AggregatedDataValidator(path)
        assert v.validate() is True
        assert len(v.errors) == 0

    def test_missing_observation_unit_column_errors(self, tmp_path):
        import anndata as ad
        import pandas as pd

        n_obs, n_var = 3, len(VALID_FEATURES)
        X = np.zeros((n_obs, n_var), dtype=np.float32)
        obs = pd.DataFrame(
            {"perturbation_id": VALID_PERTURBATIONS},
            index=VALID_PERTURBATIONS,
        )
        obs.index.name = "aggregate_id"
        var_data = {
            "feature_name": [v.split("_", 1)[-1] for v in VALID_FEATURES],
            "feature_type": ["shape" if len(v.split("_")) == 2 else "correlation" if "_correlation_" in v else "intensity" for v in VALID_FEATURES],
            "compartment": [v.split("_", 1)[0] for v in VALID_FEATURES],
        }
        var = pd.DataFrame(var_data, index=VALID_FEATURES)
        var.index.name = "feature_id"
        adata = ad.AnnData(
            X=X, obs=obs, var=var,
            obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
            uns={"observation_unit": ["perturbation_id", "cell_cycle_phase"],
                 "schema_version": "0.1.0", "default_embedding": "X_umap", "title": "T"},
        )
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_OBSERVATION_UNIT" for i in v.errors)

    def test_aggregate_id_mismatch_errors(self, tmp_path):
        import anndata as ad
        import pandas as pd

        n_obs, n_var = 2, len(VALID_FEATURES)
        X = np.zeros((n_obs, n_var), dtype=np.float32)
        obs = pd.DataFrame(
            {"perturbation_id": ["g1", "g2"], "barcode": ["ACGT", "TGCA"]},
            index=["WRONG_ID", "ALSO_WRONG"],
        )
        obs.index.name = "aggregate_id"
        var_data = {
            "feature_name": [v.split("_", 1)[-1] for v in VALID_FEATURES],
            "feature_type": ["shape" if len(v.split("_")) == 2 else "correlation" if "_correlation_" in v else "intensity" for v in VALID_FEATURES],
            "compartment": [v.split("_", 1)[0] for v in VALID_FEATURES],
        }
        var = pd.DataFrame(var_data, index=VALID_FEATURES)
        var.index.name = "feature_id"
        adata = ad.AnnData(
            X=X, obs=obs, var=var,
            obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
            uns={"observation_unit": ["barcode"], "schema_version": "0.1.0",
                 "default_embedding": "X_umap", "title": "T"},
        )
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_AGGREGATE_ID" for i in v.errors)

    def test_duplicate_aggregate_id_errors(self, tmp_path):
        path = _make_h5ad(
            tmp_path,
            obs_index=["dup", "dup", "unique"],
            var_index=VALID_FEATURES,
        )
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_INDEX" for i in v.errors)

    def test_missing_perturbation_id_column_errors(self, tmp_path):
        import anndata as ad
        import pandas as pd

        n_obs, n_var = 2, len(VALID_FEATURES)
        X = np.zeros((n_obs, n_var), dtype=np.float32)
        obs = pd.DataFrame(
            {"gene_id": ["ENSG001", "ENSG002"]},
            index=["ENSG001", "ENSG002"],
        )
        obs.index.name = "aggregate_id"
        var_data = {
            "feature_name": [v.split("_", 1)[-1] for v in VALID_FEATURES],
            "feature_type": ["shape" if len(v.split("_")) == 2 else "correlation" if "_correlation_" in v else "intensity" for v in VALID_FEATURES],
            "compartment": [v.split("_", 1)[0] for v in VALID_FEATURES],
        }
        var = pd.DataFrame(var_data, index=VALID_FEATURES)
        var.index.name = "feature_id"
        adata = ad.AnnData(
            X=X, obs=obs, var=var,
            obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
            uns={"observation_unit": ["gene_id"], "schema_version": "0.1.0",
                 "default_embedding": "X_umap", "title": "T"},
        )
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_PERTURBATION_ID" for i in v.errors)

    def test_missing_required_var_columns_errors(self, tmp_path):
        import anndata as ad
        import pandas as pd
        n_obs, n_var = 3, 2
        X = np.zeros((n_obs, n_var), dtype=np.float32)
        obs = pd.DataFrame(
            {"perturbation_id": ["p1", "p2", "p3"]},
            index=["p1", "p2", "p3"],
        )
        obs.index.name = "aggregate_id"

        var = pd.DataFrame({"feature_name": ["a", "b"]}, index=["nucleus_area", "cell_DAPI_mean"])
        var.index.name = "feature_id"
        adata = ad.AnnData(X=X, obs=obs, var=var,
                           obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
                           uns={"observation_unit": ["perturbation_id"], "schema_version": "0.1.0",
                                "default_embedding": "X_umap", "title": "T"})
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        error_messages = " ".join(i.message for i in v.errors)
        assert "feature_type" in error_messages
        assert "compartment" in error_messages

    def test_p_values_without_neg_log10_fdr_warns(self, tmp_path):
        n_obs, n_var = 3, len(VALID_FEATURES)
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
                          layers={"p_values": np.ones((n_obs, n_var), dtype=np.float32)})
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "NEG_LOG10_FDR" for i in v.warnings)

    def test_x_must_be_float32(self, tmp_path):
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, VALID_FEATURES, x_dtype=np.float64)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "X_DTYPE" for i in v.errors)

    def test_n_cells_valid(self, tmp_path):
        path = _make_h5ad(
            tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
            obs_columns={"n_cells": np.array([10, 20, 30], dtype=np.int64)},
        )
        v = AggregatedDataValidator(path)
        assert v.validate() is True
        assert not any(i.rule_id == "OBS_N_CELLS" for i in v.errors)

    def test_n_cells_negative_errors(self, tmp_path):
        path = _make_h5ad(
            tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
            obs_columns={"n_cells": np.array([10, -5, 30], dtype=np.int64)},
        )
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_N_CELLS" for i in v.errors)

    def test_n_cells_non_integer_errors(self, tmp_path):
        path = _make_h5ad(
            tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
            obs_columns={"n_cells": np.array([10.5, 20.0, 30.0], dtype=np.float64)},
        )
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_N_CELLS" for i in v.errors)

    def test_neg_log10_fdr_threshold_valid(self, tmp_path):
        path = _make_h5ad(
            tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
            uns={"neg_log10_fdr_threshold": 1.30103},
        )
        v = AggregatedDataValidator(path)
        assert v.validate() is True
        assert not any(i.rule_id == "NEG_LOG10_FDR_THRESHOLD" for i in v.errors)

    def test_neg_log10_fdr_threshold_non_positive_errors(self, tmp_path):
        path = _make_h5ad(
            tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
            uns={"neg_log10_fdr_threshold": 0.0},
        )
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "NEG_LOG10_FDR_THRESHOLD" for i in v.errors)
