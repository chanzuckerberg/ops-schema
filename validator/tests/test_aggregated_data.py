"""Tests for AggregatedDataValidator — standardized feature set enforcement."""

from __future__ import annotations

import numpy as np
import anndata as ad
import pandas as pd
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
    @pytest.mark.parametrize(
        "feature_id",
        [
            "nucleus_area",
            "cell_eccentricity",
            "nucleus_form_factor",
            "cell_solidity",
        ],
    )
    def test_valid_shape_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    # Valid intensity features: {compartment}_{channel}_{measurement}
    @pytest.mark.parametrize(
        "feature_id",
        [
            "nucleus_DAPI_mean",
            "cell_COXIV_integrated",
            "nucleus_GH2AX_mass_displacement",
            "cell_WGA_mean_edge",
            "nucleus_GFP_std_edge",
            "cell_MCHERRY_mean_frac_0",
            "nucleus_DAPI_mean_frac_3",
        ],
    )
    def test_valid_intensity_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    # Valid correlation features: {compartment}_correlation_{channel_a}_{channel_b}
    @pytest.mark.parametrize(
        "feature_id",
        [
            "nucleus_correlation_CENPA_DAPI",
            "cell_correlation_COXIV_WGA",
            "nucleus_correlation_GFP_MCHERRY",
        ],
    )
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
):
    """Helper to write a minimal valid AnnData file."""
    n_obs = len(obs_index)
    n_var = len(var_index)

    X = np.zeros((n_obs, n_var), dtype=x_dtype)
    obs = pd.DataFrame(index=obs_index)
    obs.index.name = "perturbation_id"
    if obs_columns:
        for col, vals in obs_columns.items():
            obs[col] = vals

    var_data = {"feature_name": [v.split("_", 1)[-1] for v in var_index]}
    var_data["feature_type"] = [
        "shape"
        if len(v.split("_")) == 2
        else "correlation"
        if "_correlation_" in v
        else "intensity"
        for v in var_index
    ]
    var_data["compartment"] = [v.split("_", 1)[0] for v in var_index]
    if var_columns:
        var_data.update(var_columns)
    var = pd.DataFrame(var_data, index=var_index)
    var.index.name = "feature_id"

    _obsm = {"X_umap": np.zeros((n_obs, 2), dtype=np.float32)}
    if obsm:
        _obsm.update(obsm)

    _uns = {"schema_version": "0.1.0", "default_embedding": "X_umap", "title": "Test"}
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

    def test_valid_cell_cycle_phase(self, tmp_path):
        obs_cols = {"cell_cycle_phase": ["interphase", "mitotic", "interphase"]}
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, VALID_FEATURES, obs_columns=obs_cols)
        v = AggregatedDataValidator(path)
        assert v.validate() is True
        assert len(v.errors) == 0

    def test_invalid_cell_cycle_phase_errors(self, tmp_path):
        obs_cols = {"cell_cycle_phase": ["interphase", "prophase", "interphase"]}
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, VALID_FEATURES, obs_columns=obs_cols)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "OBS_CELL_CYCLE" for i in v.errors)

    def test_missing_required_var_columns_errors(self, tmp_path):
        n_obs, n_var = 3, 2
        X = np.zeros((n_obs, n_var), dtype=np.float32)
        obs = pd.DataFrame(index=["p1", "p2", "p3"])
        obs.index.name = "perturbation_id"
        # var with only feature_name — missing feature_type and compartment
        var = pd.DataFrame(
            {"feature_name": ["a", "b"]}, index=["nucleus_area", "cell_DAPI_mean"]
        )
        var.index.name = "feature_id"
        adata = ad.AnnData(
            X=X,
            obs=obs,
            var=var,
            obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
            uns={"schema_version": "0.1.0", "default_embedding": "X_umap", "title": "T"},
        )
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        error_messages = " ".join(i.message for i in v.errors)
        assert "feature_type" in error_messages
        assert "compartment" in error_messages

    def test_p_values_without_neg_log10_fdr_warns(self, tmp_path):
        n_obs, n_var = 3, len(VALID_FEATURES)
        path = _make_h5ad(
            tmp_path,
            VALID_PERTURBATIONS,
            VALID_FEATURES,
            layers={"p_values": np.ones((n_obs, n_var), dtype=np.float32)},
        )
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "NEG_LOG10_FDR" for i in v.warnings)

    def test_x_must_be_float32(self, tmp_path):
        path = _make_h5ad(
            tmp_path, VALID_PERTURBATIONS, VALID_FEATURES, x_dtype=np.float64
        )
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "X_DTYPE" for i in v.errors)
