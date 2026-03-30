"""
Schema definition for cell_data.parquet.

Rather than a per-row Pydantic model (which would be slow for millions of cells),
the CellDataSchema class describes the expected column names and types.
The CellDataValidator uses this to validate the DataFrame as a whole.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

WELL_ROW_PATTERN = re.compile(r"^[A-Z]$")


@dataclass
class ColumnSpec:
    name: str
    dtype_check: type | tuple[type, ...]  # pandas dtype categories
    required: bool = True
    description: str = ""


REQUIRED_COLUMNS: list[ColumnSpec] = [
    ColumnSpec("plate", str, required=True, description="Plate identifier"),
    ColumnSpec("well_row", str, required=True, description="Single uppercase letter"),
    ColumnSpec("well_col", (int,), required=True, description="Column integer"),
    ColumnSpec("tile", (int,), required=True, description="Field of view identifier"),
    ColumnSpec("x", (float, int), required=True, description="X centroid in pixels"),
    ColumnSpec("y", (float, int), required=True, description="Y centroid in pixels"),
    ColumnSpec("cell_uid", (int,), required=True, description="Globally unique cell ID"),
    ColumnSpec("cell_seq_id", (int,), required=True, description="Per-well unique cell ID"),
    ColumnSpec("barcode", str, required=True, description="Perturbation barcode (ACGT)"),
    ColumnSpec("perturbation_id", str, required=True, description="FK to perturbation_library"),
]

OPTIONAL_COLUMNS = {"bounding_box", "cell_class", "global_x", "global_y"}


def validate_dataframe_structure(df: pd.DataFrame) -> list[str]:
    """
    Check that df has all required columns with expected dtype families.
    Returns a list of error strings (empty = valid structure).
    """
    errors: list[str] = []

    for spec in REQUIRED_COLUMNS:
        if spec.name not in df.columns:
            errors.append(f"cell_data.parquet: missing required column '{spec.name}'")
            continue

        col = df[spec.name]

        # Check for nulls in required columns
        if col.isnull().any():
            n_null = col.isnull().sum()
            errors.append(
                f"cell_data.parquet: column '{spec.name}' has {n_null} null value(s)"
            )

    # Validate well_row format
    if "well_row" in df.columns:
        invalid = df["well_row"][~df["well_row"].str.match(r"^[A-Z]$", na=False)]
        if len(invalid) > 0:
            errors.append(
                f"cell_data.parquet: 'well_row' must be a single uppercase letter. "
                f"Found {len(invalid)} invalid value(s): {invalid.unique()[:5].tolist()}"
            )

    # Validate barcode format
    if "barcode" in df.columns:
        invalid = df["barcode"][~df["barcode"].str.match(r"^[ACGT]+$", na=False)]
        if len(invalid) > 0:
            errors.append(
                f"cell_data.parquet: 'barcode' must contain only A, C, G, T. "
                f"Found {len(invalid)} invalid value(s)."
            )

    # cell_uid must be unique
    if "cell_uid" in df.columns:
        n_dupes = df["cell_uid"].duplicated().sum()
        if n_dupes > 0:
            errors.append(
                f"cell_data.parquet: 'cell_uid' must be globally unique. "
                f"Found {n_dupes} duplicate(s)."
            )

    # cell_seq_id must be unique within (plate, well_row, well_col)
    required_for_uniqueness = {"cell_seq_id", "plate", "well_row", "well_col"}
    if required_for_uniqueness.issubset(df.columns):
        dupes = df.duplicated(subset=["plate", "well_row", "well_col", "cell_seq_id"])
        if dupes.sum() > 0:
            errors.append(
                f"cell_data.parquet: 'cell_seq_id' must be unique within "
                f"(plate, well_row, well_col). Found {dupes.sum()} duplicate(s)."
            )

    return errors
