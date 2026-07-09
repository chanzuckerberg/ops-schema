"""Tests for the polars-backed CellDataValidator + validate_dataframe_structure."""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from ops_validator.models.cell_data import validate_dataframe_structure
from ops_validator.validators.cell_data import CellDataValidator


def _valid_frame(n: int = 4) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "plate": ["P1"] * n,
            "well_row": [chr(ord("A") + i) for i in range(n)],
            "well_col": list(range(1, n + 1)),
            "tile": list(range(10, 10 + n)),
            "x": [float(i) for i in range(n)],
            "y": [float(i) for i in range(n)],
            "cell_uid": [f"P1_{chr(ord('A') + i)}_{i}" for i in range(n)],
            "barcode": ["ACGT", "ACGTACGT", "AAAA", "GGGG"][:n],
            "perturbation_id": [f"pid{i}" for i in range(n)],
        }
    )


def _write_parquet(tmp_path: Path, df: pl.DataFrame, name: str = "cell_data.parquet") -> Path:
    p = tmp_path / name
    df.write_parquet(p)
    return p


class TestValidatorHappyPath:
    def test_valid_file_passes(self, tmp_path):
        p = _write_parquet(tmp_path, _valid_frame())
        v = CellDataValidator(path=p)
        assert v.validate() is True
        assert v.errors == []
        assert v.warnings == []

    def test_missing_file_errors(self, tmp_path):
        v = CellDataValidator(path=tmp_path / "does_not_exist.parquet")
        assert v.validate() is False
        assert len(v.errors) == 1
        assert v.errors[0].rule_id == "MISSING"


class TestValidatorSchemaFailures:
    def test_missing_required_column(self, tmp_path):
        df = _valid_frame().drop("cell_uid")
        v = CellDataValidator(path=_write_parquet(tmp_path, df))
        v.validate()
        assert any("cell_uid" in e.message for e in v.errors)

    def test_wrong_dtype_for_plate(self, tmp_path):
        # plate is required to be string; write as Int64 to trigger dtype error
        df = _valid_frame().with_columns(
            pl.Series("plate", list(range(_valid_frame().height)), dtype=pl.Int64)
        )
        v = CellDataValidator(path=_write_parquet(tmp_path, df))
        v.validate()
        assert any("plate" in e.message and "dtype" in e.message for e in v.errors)

    def test_null_in_required_column(self, tmp_path):
        df = _valid_frame().with_columns(
            pl.Series("perturbation_id", ["pid0", None, "pid2", "pid3"])
        )
        v = CellDataValidator(path=_write_parquet(tmp_path, df))
        v.validate()
        assert any("perturbation_id" in e.message and "null" in e.message for e in v.errors)


class TestValidatorContentFailures:
    def test_invalid_well_row(self, tmp_path):
        df = _valid_frame().with_columns(pl.Series("well_row", ["A", "b", "C", "D"]))
        v = CellDataValidator(path=_write_parquet(tmp_path, df))
        v.validate()
        msgs = " ".join(e.message for e in v.errors)
        assert "well_row" in msgs and "single uppercase letter" in msgs

    def test_invalid_barcode(self, tmp_path):
        df = _valid_frame().with_columns(
            pl.Series("barcode", ["ACGT", "ACGN", "AAAA", "GGGG"])
        )
        v = CellDataValidator(path=_write_parquet(tmp_path, df))
        v.validate()
        msgs = " ".join(e.message for e in v.errors)
        assert "barcode" in msgs and "A, C, G, T" in msgs

    def test_duplicate_cell_uid(self, tmp_path):
        df = _valid_frame().with_columns(
            pl.Series("cell_uid", ["dup", "dup", "u3", "u4"])
        )
        v = CellDataValidator(path=_write_parquet(tmp_path, df))
        v.validate()
        msgs = " ".join(e.message for e in v.errors)
        assert "cell_uid" in msgs and "duplicate" in msgs


class TestSampleLimit:
    def _bad_frame(self, n_unique_bad: int = 8) -> pl.DataFrame:
        """50 rows, n_unique_bad distinct invalid well_row values, all in cell_uid duplicates."""
        n = 50
        bad_letters = [chr(ord("a") + i) for i in range(n_unique_bad)]
        return pl.DataFrame(
            {
                "plate": ["P1"] * n,
                "well_row": [bad_letters[i % n_unique_bad] for i in range(n)],
                "well_col": list(range(n)),
                "tile": list(range(n)),
                "x": [float(i) for i in range(n)],
                "y": [float(i) for i in range(n)],
                "cell_uid": [f"dup_{i % 4}" for i in range(n)],
                "barcode": ["ACGT"] * n,
                "perturbation_id": ["pid"] * n,
            }
        )

    def test_default_caps_sample_to_5(self, tmp_path):
        df = self._bad_frame(n_unique_bad=8)
        lf = pl.scan_parquet(_write_parquet(tmp_path, df))
        errors = validate_dataframe_structure(lf, sample_limit=5)
        well_row_err = next(e for e in errors if "well_row" in e)
        # Total count uses ALL bad rows; sample lists only the cap.
        assert "Found 50 invalid value(s)" in well_row_err
        assert "first 5 shown" in well_row_err

    def test_none_shows_all_distinct_samples(self, tmp_path):
        df = self._bad_frame(n_unique_bad=8)
        lf = pl.scan_parquet(_write_parquet(tmp_path, df))
        errors = validate_dataframe_structure(lf, sample_limit=None)
        well_row_err = next(e for e in errors if "well_row" in e)
        # No "first N shown" suffix when uncapped
        assert "first" not in well_row_err.lower()
        # All 8 distinct lowercase letters should appear in the examples list
        for letter in "abcdefgh":
            assert f"'{letter}'" in well_row_err
