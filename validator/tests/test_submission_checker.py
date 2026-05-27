"""Tests for the OPS submission directory checker."""

from __future__ import annotations

from pathlib import Path

from ops_validator.submission import check_ops_submission


def _write(p: Path, content: str = "") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def _mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Empty / missing root
# ---------------------------------------------------------------------------


def test_empty_dir_fails_collection_check(tmp_path):
    result = check_ops_submission(tmp_path)
    assert not result.passed
    missing = {c.path for c in result.missing_required}
    assert "collection_metadata.yaml" in missing


# ---------------------------------------------------------------------------
# Complete submission
# ---------------------------------------------------------------------------


def test_complete_submission_passes(tmp_path):
    root = tmp_path
    screen = root / "screen_a"
    _write(root / "collection_metadata.yaml", "title: test")
    _write(screen / "metadata" / "experimental_metadata.yaml", "x: 1")
    _write(screen / "metadata" / "perturbation_library.csv", "barcode\n")
    _write(screen / "cell_data.parquet")
    _mkdir(screen / "screen_a.zarr")
    _mkdir(screen / "visualizations" / "v1")
    _write(screen / "visualizations" / "v1" / "aggregated_data.h5ad")
    _mkdir(screen / "visualizations" / "v1" / "examples.zarr")

    result = check_ops_submission(root)
    assert result.passed
    assert result.missing_required == []


# ---------------------------------------------------------------------------
# Optional file behaviour
# ---------------------------------------------------------------------------


def test_optional_feature_definitions_does_not_fail(tmp_path):
    root = tmp_path
    screen = root / "screen_a"
    _write(root / "collection_metadata.yaml")
    _write(screen / "metadata" / "experimental_metadata.yaml")
    _write(screen / "metadata" / "perturbation_library.csv")
    _write(screen / "cell_data.parquet")
    _mkdir(screen / "screen_a.zarr")
    _mkdir(screen / "visualizations" / "v1")
    _write(screen / "visualizations" / "v1" / "aggregated_data.h5ad")
    _mkdir(screen / "visualizations" / "v1" / "examples.zarr")

    result = check_ops_submission(root)
    assert result.passed
    # feature_definitions.csv missing as optional
    optional = {c.path for c in result.missing_optional}
    assert any("feature_definitions.csv" in p for p in optional)


# ---------------------------------------------------------------------------
# Missing required files
# ---------------------------------------------------------------------------


def test_missing_zarr_store_reported(tmp_path):
    root = tmp_path
    screen = root / "screen_a"
    _write(root / "collection_metadata.yaml")
    _write(screen / "metadata" / "experimental_metadata.yaml")
    _write(screen / "metadata" / "perturbation_library.csv")
    _write(screen / "cell_data.parquet")
    _mkdir(screen / "visualizations" / "v1")
    _write(screen / "visualizations" / "v1" / "aggregated_data.h5ad")
    _mkdir(screen / "visualizations" / "v1" / "examples.zarr")
    # No screen_a.zarr

    result = check_ops_submission(root)
    assert not result.passed
    assert any("screen_a.zarr" in c.path for c in result.missing_required)


def test_missing_visualizations_dir_reported(tmp_path):
    root = tmp_path
    screen = root / "screen_a"
    _write(root / "collection_metadata.yaml")
    _write(screen / "metadata" / "experimental_metadata.yaml")
    _write(screen / "metadata" / "perturbation_library.csv")
    _write(screen / "cell_data.parquet")
    _mkdir(screen / "screen_a.zarr")
    # No visualizations/ at all

    result = check_ops_submission(root)
    assert not result.passed
    assert any("visualizations/" in c.path for c in result.missing_required)


def test_empty_visualizations_dir_reports_globbed_paths(tmp_path):
    root = tmp_path
    screen = root / "screen_a"
    _write(root / "collection_metadata.yaml")
    _write(screen / "metadata" / "experimental_metadata.yaml")
    _write(screen / "metadata" / "perturbation_library.csv")
    _write(screen / "cell_data.parquet")
    _mkdir(screen / "screen_a.zarr")
    _mkdir(screen / "visualizations")  # empty

    result = check_ops_submission(root)
    assert not result.passed
    missing = {c.path for c in result.missing_required}
    assert any("aggregated_data.h5ad" in p for p in missing)
    assert any("examples.zarr" in p for p in missing)


# ---------------------------------------------------------------------------
# Multiple screens
# ---------------------------------------------------------------------------


def test_multiple_screens(tmp_path):
    root = tmp_path
    _write(root / "collection_metadata.yaml")
    for name in ["screen_a", "screen_b"]:
        s = root / name
        _write(s / "metadata" / "experimental_metadata.yaml")
        _write(s / "metadata" / "perturbation_library.csv")
        _write(s / "cell_data.parquet")
        _mkdir(s / f"{name}.zarr")
        _mkdir(s / "visualizations" / "v1")
        _write(s / "visualizations" / "v1" / "aggregated_data.h5ad")
        _mkdir(s / "visualizations" / "v1" / "examples.zarr")

    result = check_ops_submission(root)
    assert result.passed
    # Each screen contributes its zarr path
    paths = {c.path for c in result.checks}
    assert "screen_a/screen_a.zarr" in paths
    assert "screen_b/screen_b.zarr" in paths


def test_hidden_dirs_ignored(tmp_path):
    root = tmp_path
    _write(root / "collection_metadata.yaml")
    _mkdir(root / ".git")  # should not be treated as a screen

    result = check_ops_submission(root)
    # collection_metadata.yaml is the only requirement; passes
    assert result.passed
    # No screen-level checks were emitted for .git
    paths = {c.path for c in result.checks}
    assert not any(".git" in p for p in paths)
