"""Validator for feature_definitions.csv (RECOMMENDED artifact)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from ops_validator.models.feature_definitions import FeatureDefinitionRow
from ops_validator.validators.base import BaseValidator


class FeatureDefinitionsValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            # feature_definitions.csv is RECOMMENDED
            self._warning(
                "RECOMMENDED_MISSING",
                "feature_definitions.csv",
                "feature_definitions.csv not found. This file is RECOMMENDED and SHOULD "
                "document all features present in cell_data.parquet, including lab-specific "
                "and extended features beyond the standardized visualization set.",
            )
            return True

        try:
            df = pd.read_csv(self.path, dtype=str, keep_default_na=False)
        except Exception as e:
            self._error("PARSE", "feature_definitions.csv", f"Failed to read CSV: {e}")
            return False

        required_cols = {"feature_id", "feature_name", "feature_type"}
        missing = required_cols - set(df.columns)
        if missing:
            for col in sorted(missing):
                self._error("MISSING_COLUMN", "feature_definitions.csv", f"Missing required column: '{col}'")
            return False

        for idx, row in df.iterrows():
            row_dict = {k: (None if v == "" else v) for k, v in row.items()}
            try:
                FeatureDefinitionRow(**row_dict)
            except ValidationError as e:
                for err in e.errors():
                    field_path = ".".join(str(p) for p in err["loc"])
                    self._error(
                        "SCHEMA",
                        f"feature_definitions.csv :: row {idx} :: {field_path}",
                        err["msg"],
                    )

        # feature_id uniqueness
        if "feature_id" in df.columns:
            dupes = df["feature_id"][df["feature_id"].duplicated()]
            if len(dupes) > 0:
                self._error(
                    "PK",
                    "feature_definitions.csv :: feature_id",
                    f"feature_id must be unique. Found {len(dupes)} duplicate(s): "
                    f"{dupes.unique()[:5].tolist()}",
                )

        return self.is_valid
