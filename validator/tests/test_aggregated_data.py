"""Tests for AggregatedDataValidator — standardized feature set enforcement."""

from __future__ import annotations

import numpy as np
import pytest

from ops_validator.validators.aggregated_data import (
    AggregatedDataValidator,
    _validate_feature_id_format,
    SHAPE_MEASUREMENTS,
    INTENSITY_MEASUREMENTS,
    VALID_COMPARTMENTS,
)


# ---------------------------------------------------------------------------
# Unit tests for _validate_feature_id_format
# ---------------------------------------------------------------------------

class TestFeatureIdFormat:
    # Valid shape features
    @pytest.mark.parametrize("feature_id", [
        "nucleus__shape__area",
        "cell__shape__eccentricity",
        "nucleus__shape__form_factor",
        "cell__shape__solidity",
    ])
    def test_valid_shape_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    # Valid intensity features
    @pytest.mark.parametrize("feature_id", [
        "nucleus__dna__mean",
        "cell__tubulin__integrated",
        "nucleus__gh2ax__mass_displacement",
        "cell__actin__mean_edge",
        "nucleus__gfp__std_edge",
        "cell__mcherry__mean_frac_0",
        "nucleus__dna__mean_frac_3",
    ])
    def test_valid_intensity_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    # Valid correlation features
    @pytest.mark.parametrize("feature_id", [
        "nucleus__correlation__dna_tubulin",
        "cell__correlation__actin_gh2ax",
        "nucleus__correlation__gfp_mcherry",
    ])
    def test_valid_correlation_features(self, feature_id):
        assert _validate_feature_id_format(feature_id) is None

    def test_wrong_compartment_returns_error(self):
        err = _validate_feature_id_format("cytoplasm__shape__area")
        assert err is not None
        assert "compartment" in err

    def test_invalid_shape_measurement_returns_error(self):
        err = _validate_feature_id_format("nucleus__shape__perimeter")
        assert err is not None
        assert "shape measurement" in err

    def test_invalid_intensity_measurement_returns_error(self):
        err = _validate_feature_id_format("nucleus__dna__variance")
        assert err is not None
        assert "intensity measurement" in err

    def test_correlation_missing_channel_pair_returns_error(self):
        err = _validate_feature_id_format("nucleus__correlation__dna")
        assert err is not None
        assert "channel pair" in err

    def test_wrong_number_of_parts_returns_error(self):
        err = _validate_feature_id_format("nucleus__shape")
        assert err is not None

    def test_czi_style_id_rejected(self):
        # Old-style IDs like "CellProfiler__AreaShape_Area__nucleus" don't belong in aggregated_data
        err = _validate_feature_id_format("CellProfiler__AreaShape_Area__nucleus")
        assert err is not None


# ---------------------------------------------------------------------------
# Integration tests via AggregatedDataValidator
# ---------------------------------------------------------------------------

def _make_h5ad(tmp_path, obs_index, var_index, var_columns=None, obs_columns=None, layers=None, obsm=None, uns=None):
    """Helper to write a minimal valid AnnData file."""
    import anndata as ad
    import pandas as pd

    n_obs = len(obs_index)
    n_var = len(var_index)

    X = np.zeros((n_obs, n_var), dtype=np.float32)
    obs = pd.DataFrame(index=obs_index)
    obs.index.name = "perturbation_id"
    if obs_columns:
        for col, vals in obs_columns.items():
            obs[col] = vals

    var_data = {"feature_name": [v.split("__")[-1] for v in var_index]}
    var_data["feature_type"] = ["shape" if "__shape__" in v else "correlation" if "__correlation__" in v else "intensity" for v in var_index]
    var_data["compartment"] = [v.split("__")[0] for v in var_index]
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
    "nucleus__shape__area",
    "cell__shape__eccentricity",
    "nucleus__dna__mean",
    "cell__tubulin__integrated",
    "nucleus__correlation__dna_tubulin",
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

    def test_invalid_feature_id_errors(self, tmp_path):
        bad_features = ["nucleus__shape__area", "CellProfiler__AreaShape_Area__nucleus"]
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, bad_features)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "VAR_FEATURE_ID" for i in v.errors)

    def test_invalid_shape_measurement_errors(self, tmp_path):
        bad_features = ["nucleus__shape__perimeter"]
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, bad_features)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "VAR_FEATURE_ID" for i in v.errors)

    def test_invalid_intensity_measurement_errors(self, tmp_path):
        bad_features = ["nucleus__dna__variance"]
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, bad_features)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "VAR_FEATURE_ID" for i in v.errors)

    def test_invalid_compartment_errors(self, tmp_path):
        bad_features = ["cytoplasm__shape__area"]
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, bad_features)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id in ("VAR_FEATURE_ID", "VAR_COMPARTMENT") for i in v.errors)

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
        import anndata as ad
        import pandas as pd
        n_obs, n_var = 3, 2
        X = np.zeros((n_obs, n_var), dtype=np.float32)
        obs = pd.DataFrame(index=["p1", "p2", "p3"])
        obs.index.name = "perturbation_id"
        # var with only feature_name — missing feature_type and compartment
        var = pd.DataFrame({"feature_name": ["a", "b"]}, index=["nucleus__shape__area", "cell__dna__mean"])
        var.index.name = "feature_id"
        adata = ad.AnnData(X=X, obs=obs, var=var,
                           obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
                           uns={"schema_version": "0.1.0", "default_embedding": "X_umap", "title": "T"})
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        error_messages = " ".join(i.message for i in v.errors)
        assert "feature_type" in error_messages
        assert "compartment" in error_messages

    def test_p_values_without_neg_log10_fdr_warns(self, tmp_path):
        import anndata as ad
        import pandas as pd
        n_obs, n_var = 3, len(VALID_FEATURES)
        path = _make_h5ad(tmp_path, VALID_PERTURBATIONS, VALID_FEATURES,
                          layers={"p_values": np.ones((n_obs, n_var), dtype=np.float32)})
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "NEG_LOG10_FDR" for i in v.warnings)

    def test_x_must_be_float32(self, tmp_path):
        import anndata as ad
        import pandas as pd
        n_obs, n_var = 3, len(VALID_FEATURES)
        X = np.zeros((n_obs, n_var), dtype=np.float64)  # wrong dtype
        obs = pd.DataFrame(index=VALID_PERTURBATIONS)
        obs.index.name = "perturbation_id"
        var_data = {
            "feature_name": [f.split("__")[-1] for f in VALID_FEATURES],
            "feature_type": ["shape" if "__shape__" in f else "correlation" if "__correlation__" in f else "intensity" for f in VALID_FEATURES],
            "compartment": [f.split("__")[0] for f in VALID_FEATURES],
        }
        var = pd.DataFrame(var_data, index=VALID_FEATURES)
        var.index.name = "feature_id"
        adata = ad.AnnData(X=X, obs=obs, var=var,
                           obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
                           uns={"schema_version": "0.1.0", "default_embedding": "X_umap", "title": "T"})
        path = tmp_path / "aggregated_data.h5ad"
        adata.write_h5ad(path)
        v = AggregatedDataValidator(path)
        v.validate()
        assert any(i.rule_id == "X_DTYPE" for i in v.errors)
