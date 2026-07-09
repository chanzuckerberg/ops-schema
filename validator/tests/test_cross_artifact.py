"""Tests for CrossArtifactValidator — FK integrity and consistency across artifacts."""

from __future__ import annotations

import anndata as ad
import numpy as np
import pandas as pd

from ops_validator.validators.cross_artifact import CrossArtifactValidator

# ---------------------------------------------------------------------------
# Fixture builders — a fully consistent experiment that each test mutates.
# ---------------------------------------------------------------------------


def _default_lib() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"perturbation_id": "pert_001", "barcode": "ACGT", "role": "targeting"},
            {"perturbation_id": "pert_002", "barcode": "TTTT", "role": "targeting"},
            {"perturbation_id": "ctrl_001", "barcode": "GGGG", "role": "control"},
        ]
    )


def _default_cell() -> pd.DataFrame:
    rows = (
        [{"barcode": "ACGT", "perturbation_id": "pert_001"}] * 3
        + [{"barcode": "TTTT", "perturbation_id": "pert_002"}] * 2
        + [{"barcode": "GGGG", "perturbation_id": "ctrl_001"}] * 2
    )
    return pd.DataFrame(rows)


def _default_feat() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"feature_id": "nucleus_area", "feature_name": "area", "feature_type": "shape"},
            {
                "feature_id": "cell_DAPI_mean",
                "feature_name": "DAPI mean",
                "feature_type": "intensity",
            },
            {"feature_id": "cell_unused", "feature_name": "unused", "feature_type": "shape"},
        ]
    )


def _make_agg(
    perturbation_ids=("pert_001", "pert_002", "ctrl_001"),
    n_cells=(3, 2, 2),
    var_ids=("nucleus_area", "cell_DAPI_mean"),
    observation_unit=("perturbation_id",),
) -> ad.AnnData:
    obs = pd.DataFrame(
        {"perturbation_id": list(perturbation_ids), "n_cells": list(n_cells)}
    )
    obs.index = [f"agg{i}" for i in range(len(perturbation_ids))]
    obs.index.name = "aggregate_id"
    var = pd.DataFrame(index=list(var_ids))
    var.index.name = "feature_id"
    X = np.zeros((len(obs), len(var)), dtype=np.float32)
    return ad.AnnData(X=X, obs=obs, var=var, uns={"observation_unit": list(observation_unit)})


def _write(base, lib=None, cell=None, feat=None, agg="default"):
    """Write an experiment layout under `base`. Pass None to omit an artifact."""
    meta = base / "metadata"
    meta.mkdir(parents=True, exist_ok=True)
    if lib is not None:
        lib.to_csv(meta / "perturbation_library.csv", index=False)
    if cell is not None:
        cell.to_parquet(base / "cell_data.parquet", index=False)
    if feat is not None:
        feat.to_csv(meta / "feature_definitions.csv", index=False)
    if agg is not None:
        adata = _make_agg() if isinstance(agg, str) else agg
        vdir = base / "visualizations" / "viz1"
        vdir.mkdir(parents=True, exist_ok=True)
        adata.write_h5ad(vdir / "aggregated_data.h5ad")
    return base


def _validate(base):
    v = CrossArtifactValidator(experiment_dir=base)
    v.validate()
    return v


def _rule_ids(issues):
    return {i.rule_id for i in issues}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCrossArtifactValidator:
    def test_all_consistent_passes(self, tmp_path):
        _write(tmp_path, lib=_default_lib(), cell=_default_cell(), feat=_default_feat())
        v = _validate(tmp_path)
        assert v.is_valid
        assert v.errors == []
        assert v.warnings == []

    def test_orphan_barcode_in_cell_errors(self, tmp_path):
        cell = pd.concat(
            [_default_cell(), pd.DataFrame([{"barcode": "CCCC", "perturbation_id": "pert_001"}])],
            ignore_index=True,
        )
        _write(tmp_path, lib=_default_lib(), cell=cell, feat=_default_feat())
        v = _validate(tmp_path)
        assert not v.is_valid
        assert "FK_BARCODE" in _rule_ids(v.errors)

    def test_orphan_perturbation_id_in_cell_errors(self, tmp_path):
        cell = pd.concat(
            [_default_cell(), pd.DataFrame([{"barcode": "ACGT", "perturbation_id": "pert_999"}])],
            ignore_index=True,
        )
        _write(tmp_path, lib=_default_lib(), cell=cell, feat=_default_feat())
        v = _validate(tmp_path)
        assert "FK_PERTURBATION_ID_CELL" in _rule_ids(v.errors)

    def test_orphan_perturbation_id_in_aggregated_errors(self, tmp_path):
        agg = _make_agg(
            perturbation_ids=("pert_001", "pert_002", "ctrl_001", "pert_999"),
            n_cells=(3, 2, 2, 0),
        )
        _write(tmp_path, lib=_default_lib(), cell=_default_cell(), feat=_default_feat(), agg=agg)
        v = _validate(tmp_path)
        assert "FK_PERTURBATION_ID_AGG" in _rule_ids(v.errors)

    def test_missing_control_errors(self, tmp_path):
        lib = _default_lib()
        lib.loc[lib["perturbation_id"] == "ctrl_001", "role"] = "targeting"
        _write(tmp_path, lib=lib, cell=_default_cell(), feat=_default_feat())
        v = _validate(tmp_path)
        assert "V12_CONTROL_PRESENT" in _rule_ids(v.errors)

    def test_n_cells_mismatch_errors(self, tmp_path):
        agg = _make_agg(n_cells=(99, 2, 2))  # pert_001 should be 3
        _write(tmp_path, lib=_default_lib(), cell=_default_cell(), feat=_default_feat(), agg=agg)
        v = _validate(tmp_path)
        assert "V14_N_CELLS" in _rule_ids(v.errors)

    def test_undocumented_feature_warns_only(self, tmp_path):
        agg = _make_agg(var_ids=("nucleus_area", "cell_DAPI_mean", "cell_mystery"))
        _write(tmp_path, lib=_default_lib(), cell=_default_cell(), feat=_default_feat(), agg=agg)
        v = _validate(tmp_path)
        assert v.is_valid  # warning, not error
        assert "VAR_VS_FEATURES" in _rule_ids(v.warnings)

    def test_perturbation_id_consistency_warns(self, tmp_path):
        # Library + cell_data carry pert_003, but it's absent from aggregated obs.
        lib = pd.concat(
            [
                _default_lib(),
                pd.DataFrame(
                    [{"perturbation_id": "pert_003", "barcode": "AAAA", "role": "targeting"}]
                ),
            ],
            ignore_index=True,
        )
        cell = pd.concat(
            [_default_cell(), pd.DataFrame([{"barcode": "AAAA", "perturbation_id": "pert_003"}])],
            ignore_index=True,
        )
        _write(tmp_path, lib=lib, cell=cell, feat=_default_feat())
        v = _validate(tmp_path)
        assert v.is_valid  # consistency mismatch is a warning
        assert "PERTURBATION_ID_CONSISTENCY" in _rule_ids(v.warnings)

    def test_missing_artifacts_skipped(self, tmp_path):
        # Only the library present — no cross-checks have both sides, so it passes.
        _write(tmp_path, lib=_default_lib(), cell=None, feat=None, agg=None)
        v = _validate(tmp_path)
        assert v.is_valid
        assert v.errors == []

    def test_feature_definitions_optional(self, tmp_path):
        # No feature_definitions.csv → var-vs-features check is skipped, still valid.
        _write(tmp_path, lib=_default_lib(), cell=_default_cell(), feat=None)
        v = _validate(tmp_path)
        assert v.is_valid
        assert "VAR_VS_FEATURES" not in _rule_ids(v.warnings)
