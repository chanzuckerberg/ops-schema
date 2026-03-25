"""Validator for perturbation_library.csv."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from ops_validator.gencode import gene_id_exists, gene_symbol_matches, reference_present
from ops_validator.models.perturbation_library import PerturbationLibraryRow
from ops_validator.validators.base import BaseValidator


class PerturbationLibraryValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", "perturbation_library.csv", f"File not found: {self.path}")
            return False

        try:
            df = pd.read_csv(self.path, dtype=str, keep_default_na=False)
        except Exception as e:
            self._error("PARSE", "perturbation_library.csv", f"Failed to read CSV: {e}")
            return False

        # Check required columns exist
        required_cols = {
            "perturbation_id", "gene_id", "gene_symbol", "barcode",
            "role", "protospacer_sequence", "protospacer_adjacent_motif",
        }
        missing = required_cols - set(df.columns)
        if missing:
            for col in sorted(missing):
                self._error("MISSING_COLUMN", "perturbation_library.csv", f"Missing required column: '{col}'")
            return False

        # Validate each row as a Pydantic model
        for idx, row in df.iterrows():
            row_dict = {k: (None if v == "" else v) for k, v in row.items()}
            try:
                PerturbationLibraryRow(**row_dict)
            except ValidationError as e:
                for err in e.errors():
                    field_path = ".".join(str(p) for p in err["loc"])
                    self._error(
                        "SCHEMA",
                        f"perturbation_library.csv :: row {idx} :: {field_path}",
                        err["msg"],
                    )

        # barcode uniqueness
        if "barcode" in df.columns:
            dupes = df["barcode"][df["barcode"].duplicated()]
            if len(dupes) > 0:
                self._error(
                    "PK",
                    "perturbation_library.csv :: barcode",
                    f"barcode must be unique (primary key). Found {len(dupes)} duplicate(s): "
                    f"{dupes.unique()[:5].tolist()}",
                )

        # Ensembl gene ID + symbol cross-check (if reference files present)
        if reference_present():
            targeting = df[df["role"] == "targeting"]
            for idx, row in targeting.iterrows():
                gid = row.get("gene_id", "")
                sym = row.get("gene_symbol", "")
                if gid and gid != "non-targeting":
                    if not gene_id_exists(gid):
                        self._error(
                            "ENSEMBL",
                            f"perturbation_library.csv :: row {idx} :: gene_id",
                            f"{gid!r} not found in Ensembl 110 reference.",
                        )
                    elif sym and not gene_symbol_matches(gid, sym):
                        self._warning(
                            "SYMBOL_MISMATCH",
                            f"perturbation_library.csv :: row {idx} :: gene_symbol",
                            f"gene_symbol {sym!r} does not match Ensembl 110 name for {gid!r}.",
                        )
        else:
            self._warning(
                "ENSEMBL_REF_MISSING",
                "perturbation_library.csv",
                "Ensembl reference not found — gene_id and gene_symbol checks skipped. "
                "Run `python scripts/prepare_references.py`.",
            )

        return self.is_valid
