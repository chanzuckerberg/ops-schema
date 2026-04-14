"""Tests for CrossArtifactValidator."""

from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import pytest

from ops_validator.cross_artifact import CrossArtifactValidator

VALID_FEATURES = [
    "nucleus_area",
    "cell_eccentricity",
    "nucleus_DAPI_mean",
]


def _make_experiment(
    tmp_path: Path,
    lib_rows: list[dict],
    agg_perturbation_ids: list[str],
) -> Path:
    """Build a minimal experiment directory with library + one aggregated_data.h5ad."""
    base = tmp_path / "experiment"
    meta_dir = base / "metadata"
    viz_dir = base / "visualizations" / "viz1"
    meta_dir.mkdir(parents=True)
    viz_dir.mkdir(parents=True)

    lib_df = pd.DataFrame(lib_rows)
    lib_df.to_csv(meta_dir / "perturbation_library.csv", index=False)

    n_obs = len(agg_perturbation_ids)
    n_var = len(VALID_FEATURES)
    obs = pd.DataFrame(
        {"perturbation_id": agg_perturbation_ids},
        index=agg_perturbation_ids,
    )
    obs.index.name = "aggregate_id"
    var = pd.DataFrame(
        {
            "feature_name": [f.split("_", 1)[-1] for f in VALID_FEATURES],
            "feature_type": ["shape", "shape", "intensity"],
            "compartment": [f.split("_", 1)[0] for f in VALID_FEATURES],
        },
        index=VALID_FEATURES,
    )
    var.index.name = "feature_id"
    adata = ad.AnnData(
        X=np.zeros((n_obs, n_var), dtype=np.float32),
        obs=obs,
        var=var,
        obsm={"X_umap": np.zeros((n_obs, 2), dtype=np.float32)},
        uns={
            "observation_unit": "perturbation_id",
            "schema_version": "0.1.0",
            "default_embedding": "X_umap",
            "title": "Test",
        },
    )
    adata.write_h5ad(viz_dir / "aggregated_data.h5ad")
    return base


def _lib_row(perturbation_id: str, role: str, control_type: str = "") -> dict:
    return {
        "perturbation_id": perturbation_id,
        "gene_id": "non-targeting" if role == "control" else "ENSG00000000001",
        "barcode": perturbation_id.replace("_", "").upper().ljust(4, "A")[:8] + "ACGT",
        "role": role,
        "control_type": control_type,
        "protospacer_sequence": "ACGTACGTACGTACGT",
        "protospacer_adjacent_motif": "3' NGG",
    }


class TestV12ControlPresent:
    def test_passes_with_control(self, tmp_path):
        base = _make_experiment(
            tmp_path,
            lib_rows=[
                _lib_row("tgt_1", "targeting"),
                _lib_row("ctrl_1", "control", "non-targeting"),
            ],
            agg_perturbation_ids=["tgt_1", "ctrl_1"],
        )
        v = CrossArtifactValidator(base)
        v.validate()
        v12_errors = [e for e in v.errors if e.rule_id == "V12_CONTROL_PRESENT"]
        assert len(v12_errors) == 0

    def test_fails_without_control(self, tmp_path):
        base = _make_experiment(
            tmp_path,
            lib_rows=[
                _lib_row("tgt_1", "targeting"),
                _lib_row("tgt_2", "targeting"),
                _lib_row("ctrl_1", "control", "non-targeting"),
            ],
            agg_perturbation_ids=["tgt_1", "tgt_2"],
        )
        v = CrossArtifactValidator(base)
        v.validate()
        v12_errors = [e for e in v.errors if e.rule_id == "V12_CONTROL_PRESENT"]
        assert len(v12_errors) == 1

    def test_passes_with_only_controls(self, tmp_path):
        base = _make_experiment(
            tmp_path,
            lib_rows=[
                _lib_row("ctrl_1", "control", "non-targeting"),
                _lib_row("ctrl_2", "control", "intergenic"),
            ],
            agg_perturbation_ids=["ctrl_1", "ctrl_2"],
        )
        v = CrossArtifactValidator(base)
        v.validate()
        v12_errors = [e for e in v.errors if e.rule_id == "V12_CONTROL_PRESENT"]
        assert len(v12_errors) == 0
