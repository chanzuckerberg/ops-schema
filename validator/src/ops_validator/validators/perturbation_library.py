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

        # Check blank gene_id thresholds among targeting rows
        targeting = df[df["role"] == "targeting"]
        if len(targeting) > 0:
            blank_gene_id = targeting["gene_id"].isin(["", "nan"]) | targeting["gene_id"].isna()
            n_blank = blank_gene_id.sum()
            pct_blank = n_blank / len(targeting)
            if pct_blank > 0.5:
                self._error(
                    "GENE_ID_BLANK",
                    "perturbation_library.csv :: gene_id",
                    f"{n_blank}/{len(targeting)} ({pct_blank:.0%}) targeting rows have blank "
                    f"gene_id. More than 50% blank is not allowed.",
                )
            elif pct_blank > 0.2:
                self._warning(
                    "GENE_ID_BLANK",
                    "perturbation_library.csv :: gene_id",
                    f"{n_blank}/{len(targeting)} ({pct_blank:.0%}) targeting rows have blank "
                    f"gene_id. Consider resolving more gene IDs against Ensembl 110.",
                )

        # Ensembl gene ID + symbol cross-check (if reference files present)
        if reference_present():
            for idx, row in targeting.iterrows():
                gid = row.get("gene_id", "")
                sym = row.get("gene_symbol", "")
                if not gid or gid in ("", "non-targeting"):
                    continue
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
