"""Pydantic model for perturbation_library.csv (one model instance per row)."""

from __future__ import annotations

import re
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

BARCODE_PATTERN = re.compile(r"^[ACGT]+$")
PROTOSPACER_PATTERN = re.compile(r"^[ACGT]{14,22}$")
ENSEMBL_PATTERN = re.compile(r"^ENSG\d+$")

# IUPAC nucleotide ambiguity codes
IUPAC_CHARS = set("ABCDGHKMNRSTVWY")
PAM_PATTERN = re.compile(r"^3' [ABCDGHKMNRSTVWY]+$")

LOCUS_PATTERN = re.compile(
    r"^(\d+|X|Y|MT|[0-9A-Za-z_]+):\d+-\d+\([+-]\)$"
)


class PerturbationLibraryRow(BaseModel):
    perturbation_id: str
    gene_id: str | None = None
    gene_symbol: str
    barcode: Annotated[str, Field(pattern=r"^[ACGT]+$")]
    role: Literal["targeting", "control"]
    control_type: Literal["non-targeting", "intergenic"] | None = None
    protospacer_sequence: Annotated[str, Field(min_length=14, max_length=22)]
    protospacer_adjacent_motif: str
    sgrna_target_locus: str | None = None
    derived_gene_id: str | None = None
    derived_gene_name: str | None = None

    @field_validator("perturbation_id")
    @classmethod
    def perturbation_id_not_na(cls, v: str) -> str:
        if v.lower() == "na":
            raise ValueError("perturbation_id MUST NOT be 'na'")
        if not v.strip():
            raise ValueError("perturbation_id must not be empty")
        return v

    @field_validator("gene_id")
    @classmethod
    def gene_id_format(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if v == "non-targeting":
            return v
        if not ENSEMBL_PATTERN.match(v):
            raise ValueError(
                f"gene_id must be a version-stripped Ensembl gene ID "
                f"(e.g. 'ENSG00000186092'), 'non-targeting', or empty. Got: {v!r}"
            )
        return v

    @field_validator("gene_symbol")
    @classmethod
    def gene_symbol_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("gene_symbol must not be empty")
        return v

    @field_validator("protospacer_sequence")
    @classmethod
    def protospacer_acgt_only(cls, v: str) -> str:
        if not BARCODE_PATTERN.match(v):
            raise ValueError(
                f"protospacer_sequence must contain only A, C, G, T. Got: {v!r}"
            )
        return v

    @field_validator("protospacer_adjacent_motif")
    @classmethod
    def pam_format(cls, v: str) -> str:
        if not PAM_PATTERN.match(v):
            raise ValueError(
                f"protospacer_adjacent_motif must be formatted as \"3' MOTIF\" using "
                f"IUPAC codes (e.g. \"3' NGG\"). Got: {v!r}"
            )
        return v

    @field_validator("sgrna_target_locus")
    @classmethod
    def locus_format(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not LOCUS_PATTERN.match(v):
            raise ValueError(
                f"sgrna_target_locus must use format 'CHROM:START-END(STRAND)' "
                f"with ENSEMBL-style chromosome identifiers (e.g. '7:117548628-117548650(+)'). "
                f"Got: {v!r}"
            )
        return v

    @field_validator("derived_gene_id")
    @classmethod
    def derived_gene_id_format(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not ENSEMBL_PATTERN.match(v):
            raise ValueError(
                f"derived_gene_id must be a version-stripped Ensembl ID. Got: {v!r}"
            )
        return v

    @model_validator(mode="after")
    def control_type_consistency(self) -> PerturbationLibraryRow:
        """V-10/V-11: control_type present iff role == 'control'."""
        if self.role == "control" and self.control_type is None:
            raise ValueError(
                "control_type is required when role is 'control' (V-10)"
            )
        if self.role == "targeting" and self.control_type is not None:
            raise ValueError(
                "control_type must not be present when role is 'targeting' (V-11)"
            )
        return self

    @model_validator(mode="after")
    def control_gene_id(self) -> PerturbationLibraryRow:
        """Controls must have gene_id == 'non-targeting'."""
        if self.role == "control" and self.gene_id not in ("non-targeting", None):
            raise ValueError(
                f"gene_id must be 'non-targeting' for control guides. Got: {self.gene_id!r}"
            )
        return self
