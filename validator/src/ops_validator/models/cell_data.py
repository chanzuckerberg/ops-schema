"""
Schema definition for cell_data.parquet.

Validates a polars LazyFrame using lazy expressions so the parquet file does
not need to be fully materialized in memory. Column-presence and dtype checks
read parquet metadata only; per-row checks (null counts, regex, uniqueness)
are pushed down into the scan and aggregated in streaming mode.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import polars as pl

DtypeFamily = Literal["string", "integer", "float", "numeric"]


@dataclass
class ColumnSpec:
    name: str
    dtype_family: DtypeFamily
    required: bool = True
    description: str = ""


REQUIRED_COLUMNS: list[ColumnSpec] = [
    ColumnSpec("plate", "string", description="Plate identifier"),
    ColumnSpec("well_row", "string", description="Single uppercase letter"),
    ColumnSpec("well_col", "integer", description="Column integer"),
    ColumnSpec("tile", "integer", description="Field of view identifier"),
    ColumnSpec("x", "numeric", description="X centroid in pixels"),
    ColumnSpec("y", "numeric", description="Y centroid in pixels"),
    ColumnSpec("cell_uid", "string", description="Globally unique cell ID"),
    ColumnSpec("barcode", "string", description="Perturbation barcode (ACGT)"),
    ColumnSpec("perturbation_id", "string", description="FK to perturbation_library"),
]

OPTIONAL_COLUMNS = {"bounding_box", "cell_class", "global_x", "global_y"}


def _dtype_matches(actual: pl.DataType, family: DtypeFamily) -> bool:
    if family == "string":
        return actual == pl.Utf8 or actual == pl.String
    if family == "integer":
        return actual.is_integer()
    if family == "float":
        return actual.is_float()
    if family == "numeric":
        return actual.is_numeric()
    return False


def validate_dataframe_structure(
    lf: pl.LazyFrame, sample_limit: int | None = 5
) -> list[str]:
    """
    Validate the schema and per-row constraints of a cell_data parquet file
    via lazy polars expressions. Returns a list of error strings (empty = valid).

    sample_limit caps how many invalid examples are surfaced per check. Pass
    None to include every distinct invalid value (every duplicate cell_uid,
    every invalid well_row, etc.). The total count is always reported.
    """
    errors: list[str] = []

    schema = lf.collect_schema()

    present: list[ColumnSpec] = []
    for spec in REQUIRED_COLUMNS:
        if spec.name not in schema:
            errors.append(f"cell_data.parquet: missing required column '{spec.name}'")
            continue
        if not _dtype_matches(schema[spec.name], spec.dtype_family):
            errors.append(
                f"cell_data.parquet: column '{spec.name}' has dtype "
                f"{schema[spec.name]}; expected {spec.dtype_family}"
            )
            continue
        present.append(spec)

    if not present:
        return errors

    null_counts = (
        lf.select([pl.col(s.name).null_count().alias(s.name) for s in present])
        .collect(engine="streaming")
        .row(0, named=True)
    )
    for name, n_null in null_counts.items():
        if n_null:
            errors.append(
                f"cell_data.parquet: column '{name}' has {n_null} null value(s)"
            )

    if "well_row" in schema:
        _check_regex(lf, "well_row", r"^[A-Z]$",
                     "must be a single uppercase letter", sample_limit, errors)

    if "barcode" in schema:
        _check_regex(lf, "barcode", r"^[ACGT]+$",
                     "must contain only A, C, G, T", sample_limit, errors)

    if "cell_uid" in schema:
        n_dupes, dup_samples = _count_and_sample_duplicates(lf, "cell_uid", sample_limit)
        if n_dupes:
            errors.append(
                f"cell_data.parquet: 'cell_uid' must be globally unique. "
                f"Found {n_dupes} duplicate(s).{_format_samples(dup_samples, sample_limit)}"
            )

    return errors


def _check_regex(
    lf: pl.LazyFrame,
    column: str,
    pattern: str,
    requirement: str,
    sample_limit: int | None,
    errors: list[str],
) -> None:
    bad = lf.filter(~pl.col(column).str.contains(pattern))
    total = bad.select(pl.len()).collect(engine="streaming").item()
    if not total:
        return
    samples_q = bad.select(pl.col(column).unique())
    if sample_limit is not None:
        samples_q = samples_q.head(sample_limit)
    samples = samples_q.collect(engine="streaming")[column].to_list()
    errors.append(
        f"cell_data.parquet: '{column}' {requirement}. "
        f"Found {total} invalid value(s).{_format_samples(samples, sample_limit)}"
    )


def _count_and_sample_duplicates(
    lf: pl.LazyFrame, column: str, sample_limit: int | None
) -> tuple[int, list]:
    counts = (
        lf.select(
            pl.col(column).len().alias("total"),
            pl.col(column).n_unique().alias("unique"),
        )
        .collect(engine="streaming")
        .row(0, named=True)
    )
    n_dupes = counts["total"] - counts["unique"]
    if not n_dupes:
        return 0, []
    dup_q = (
        lf.group_by(column)
        .agg(pl.len().alias("count"))
        .filter(pl.col("count") > 1)
        .select(pl.col(column))
    )
    if sample_limit is not None:
        dup_q = dup_q.head(sample_limit)
    samples = dup_q.collect(engine="streaming")[column].to_list()
    return n_dupes, samples


def _format_samples(samples: list, sample_limit: int | None) -> str:
    if not samples:
        return ""
    if sample_limit is None or len(samples) < sample_limit:
        return f" Examples: {samples}"
    return f" Examples (first {sample_limit} shown): {samples}"
