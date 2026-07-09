"""Tests for cli.validate_structure and the typer entrypoint."""

from __future__ import annotations

from pathlib import Path

import pytest
from cloudpathlib import AnyPath

from ops_validator.cli import validate_structure


def _empty_file(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()


def _make_minimal_submission(root: Path, screen: str = "screen1", n_vizs: int = 1) -> Path:
    """Build the minimal OPS submission layout under `root`."""
    _empty_file(root / "collection_metadata.yaml")
    _empty_file(root / screen / "metadata" / "experimental_metadata.yaml")
    _empty_file(root / screen / "metadata" / "perturbation_library.csv")
    _empty_file(root / screen / "cell_data.parquet")
    (root / screen / f"{screen}.zarr").mkdir(parents=True, exist_ok=True)
    for i in range(n_vizs):
        vname = f"viz{i}"
        _empty_file(root / screen / "visualizations" / vname / "aggregated_data.h5ad")
        (root / screen / "visualizations" / vname / "examples.zarr").mkdir(parents=True, exist_ok=True)
    return root


class TestValidateStructure:
    def test_all_present_returns_empty(self, tmp_path):
        _make_minimal_submission(tmp_path)
        required = [
            "collection_metadata.yaml",
            "screen1/metadata/experimental_metadata.yaml",
            "screen1/metadata/perturbation_library.csv",
            "screen1/cell_data.parquet",
            "screen1/visualizations/viz0/aggregated_data.h5ad",
            "screen1/visualizations/viz0/examples.zarr",
        ]
        assert validate_structure(required, AnyPath(tmp_path)) == []

    def test_missing_file_reported(self, tmp_path):
        _make_minimal_submission(tmp_path)
        (tmp_path / "screen1" / "cell_data.parquet").unlink()
        required = ["collection_metadata.yaml", "screen1/cell_data.parquet"]
        missing = validate_structure(required, AnyPath(tmp_path))
        assert missing == ["screen1/cell_data.parquet"]

    def test_multiple_missing(self, tmp_path):
        # nothing exists under tmp_path yet
        required = ["a/b.yaml", "c.csv", "d/e/f.zarr"]
        missing = validate_structure(required, AnyPath(tmp_path))
        assert sorted(missing) == ["a/b.yaml", "c.csv", "d/e/f.zarr"]

    def test_empty_required_returns_empty(self, tmp_path):
        assert validate_structure([], AnyPath(tmp_path)) == []

    def test_directory_paths_are_accepted(self, tmp_path):
        # `.exists()` is true for both files and directories — validate_structure
        # doesn't distinguish. This matches the spec where examples.zarr is a
        # directory (zarr store), not a file.
        (tmp_path / "screen1" / "screen1.zarr").mkdir(parents=True)
        assert validate_structure(["screen1/screen1.zarr"], AnyPath(tmp_path)) == []


class TestValidatorFullFlow:
    """End-to-end-ish test of cli.validator() — synthetic tree, expects exit on structural fail."""

    def test_missing_collection_metadata_exits_nonzero(self, tmp_path, monkeypatch):
        from ops_validator.cli import validator

        # Build a screen but no collection_metadata.yaml
        _empty_file(tmp_path / "screen1" / "metadata" / "experimental_metadata.yaml")

        with pytest.raises(SystemExit) as exc:
            validator(AnyPath(tmp_path))
        assert exc.value.code == 1

    def test_zero_screens_exits_nonzero(self, tmp_path):
        from ops_validator.cli import validator

        _empty_file(tmp_path / "collection_metadata.yaml")
        # no screen subdir at all

        with pytest.raises(SystemExit) as exc:
            validator(AnyPath(tmp_path))
        assert exc.value.code == 1

    def test_multiple_screens_pass_structure(self, tmp_path):
        """validator() loops over every screen. Structural check passes when
        all screens have their required files; per-artifact validation runs
        once per screen."""
        from ops_validator.cli import validator

        _make_minimal_submission(tmp_path, screen="screen1")
        _make_minimal_submission(tmp_path, screen="screen2")
        # Empty placeholder files will fail per-artifact validation, but those
        # failures don't propagate to exit code in the current implementation.
        # We only assert the structural layer (which would sys.exit(1)) passes.
        validator(AnyPath(tmp_path))
