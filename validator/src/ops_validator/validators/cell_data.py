"""Validator for cell_data.parquet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ops_validator.models.cell_data import validate_dataframe_structure
from ops_validator.validators.base import BaseValidator


class CellDataValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", "cell_data.parquet", f"File not found: {self.path}")
            return False

        try:
            df = pd.read_parquet(self.path)
        except Exception as e:
            self._error("PARSE", "cell_data.parquet", f"Failed to read Parquet: {e}")
            return False

        for msg in validate_dataframe_structure(df):
            self._error("SCHEMA", "cell_data.parquet", msg)

        return self.is_valid
