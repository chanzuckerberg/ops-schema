"""Validator for perturbation_library.csv."""

from __future__ import annotations

import pandas as pd
from pydantic import ValidationError

from ops_validator.gencode import gene_id_exists, gene_symbol_matches
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
            "perturbation_id",
            "gene_id",
            "gene_symbol",
            "barcode",
            "role",
            "protospacer_sequence",
            "protospacer_adjacent_motif",
        }
        missing = required_cols - set(df.columns)
        if missing:
            for col in sorted(missing):
                self._error(
                    "MISSING_COLUMN",
                    "perturbation_library.csv",
                    f"Missing required column: '{col}'",
                )
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

        # Strict gene_id requirement: every targeting row MUST have a gene_id
        targeting = df[df["role"] == "targeting"]
        if len(targeting) > 0:
            blank_gene_id = targeting["gene_id"].isin(["", "nan"]) | targeting["gene_id"].isna()
            blank_rows = targeting.index[blank_gene_id].tolist()
            for row_idx in blank_rows:
                self._error(
                    "GENE_ID_BLANK",
                    f"perturbation_library.csv :: row {row_idx} :: gene_id",
                    "gene_id MUST be a valid GENCODE v48 Ensembl gene ID for targeting rows.",
                )

        # GENCODE gene ID + symbol cross-check
        for idx, row in targeting.iterrows():
            gid = row.get("gene_id", "")
            sym = row.get("gene_symbol", "")
            if not gid or gid in ("", "non-targeting"):
                continue
            if not gene_id_exists(gid):
                self._error(
                    "GENCODE",
                    f"perturbation_library.csv :: row {idx} :: gene_id",
                    f"{gid!r} not found in GENCODE v48 reference.",
                )
            elif sym and not gene_symbol_matches(gid, sym):
                self._warning(
                    "SYMBOL_MISMATCH",
                    f"perturbation_library.csv :: row {idx} :: gene_symbol",
                    f"gene_symbol {sym!r} does not match GENCODE v48 name for {gid!r}.",
                )

        return self.is_valid
