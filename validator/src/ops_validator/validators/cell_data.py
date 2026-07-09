"""Validator for cell_data.parquet.

Uses polars `scan_parquet` so the file is streamed lazily rather than fully
materialized. Accepts local paths and remote URLs (s3://, gs://, http(s)://).
Credentials, when needed, come from the environment via polars' built-in
object_store integration.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
from cloudpathlib import CloudPath

from ops_validator.models.cell_data import validate_dataframe_structure
from ops_validator.validators.base import BaseValidator


class CellDataValidator(BaseValidator):
    def __init__(
        self,
        path: str | Path | CloudPath,
        sample_limit: int | None = 5,
    ):
        """sample_limit caps invalid-example output per check; None means no cap."""
        super().__init__(path)
        self.sample_limit = sample_limit

    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", "cell_data.parquet", f"File not found: {self.path}")
            return False

        source = self.path.as_uri() if isinstance(self.path, CloudPath) else str(self.path)

        try:
            lf = pl.scan_parquet(source)
        except Exception as e:
            self._error("PARSE", "cell_data.parquet", f"Failed to open Parquet: {e}")
            return False

        try:
            for msg in validate_dataframe_structure(lf, sample_limit=self.sample_limit):
                self._error("SCHEMA", "cell_data.parquet", msg)
        except Exception as e:
            self._error("PARSE", "cell_data.parquet", f"Failed to scan Parquet: {e}")
            return False

        return self.is_valid
