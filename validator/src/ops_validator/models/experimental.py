"""
Pydantic model for experimental_metadata.yaml.

Implements all ontology validation rules V-1 through V-5 from the OPS schema.
Ontology checks are skipped with a warning if reference OBO files are not present.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, field_validator, model_validator

# V-5: allowed organism term IDs in v0.1.0
ALLOWED_ORGANISMS = {
    "NCBITaxon:9606": "Homo sapiens",
    "NCBITaxon:10090": "Mus musculus",
    "NCBITaxon:7955": "Danio rerio",
}

CELLOSAURUS_PATTERN = re.compile(r"^CVCL_[0-9A-Z]+$")

# V-1: forbidden CL terms for cell culture
FORBIDDEN_CL_TERMS = {"CL:0000255", "CL:0000257", "CL:0000548"}


class ISSChannel(BaseModel):
    name: str
    laser_wavelength_nm: int
    exposure_time_ms: int


class ExperimentBlock(BaseModel):
    screen_title: str
    pseudobulk: list[str] | None = None
    crop_seq_anndata: str | None = None
    organism_ontology_term_id: str
    organism: str | None = None  # system-annotated; validated post-load
    tissue_ontology_term_id: str
    tissue: str | None = None  # system-annotated
    tissue_type: Literal["tissue", "organoid", "cell culture", "cell line"]
    disease_ontology_term_id: str
    disease: str | None = None  # system-annotated
    development_stage_ontology_term_id: str
    development_stage: str | None = None  # system-annotated
    assay_ontology_term_id: str
    assay: str | None = None  # system-annotated

    @field_validator("organism_ontology_term_id")
    @classmethod
    def validate_organism(cls, v: str) -> str:
        if v not in ALLOWED_ORGANISMS:
            raise ValueError(
                f"organism_ontology_term_id must be one of "
                f"{sorted(ALLOWED_ORGANISMS.keys())} (v0.1.0). Got: {v!r}"
            )
        return v

    @field_validator("screen_title")
    @classmethod
    def screen_title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("experiment.screen_title must not be empty")
        return v


class CellularBlock(BaseModel):
    growth_conditions: str
    plate_type: str
    seeding: SeedingBlock | None = None
    induction: InductionBlock | None = None


class SeedingBlock(BaseModel):
    density_cells_cm2: int | None = None


class InductionBlock(BaseModel):
    duration: str | None = None


class LibraryBlock(BaseModel):
    vector: str
    gene_selection: str | None = None
    positive_controls: str | list[str] | None = None
    negative_controls: str | list[str] | None = None


class ISSBlock(BaseModel):
    cycles: int | None = None
    objective: str | None = None
    chemistry: str | None = None
    channels: list[ISSChannel] | None = None


class PhenotypeBlock(BaseModel):
    objective: str
    exposure_time_ms: list[int]


class MicroscopeBlock(BaseModel):
    system: str


class PipelineBlock(BaseModel):
    github: str
    version: float | str


class ExperimentalMetadata(BaseModel):
    experiment: ExperimentBlock
    cellular: CellularBlock
    library: LibraryBlock
    iss: ISSBlock | None = None
    phenotype: PhenotypeBlock
    microscope: MicroscopeBlock
    pipeline: PipelineBlock

    # Ontology validators are called by the ExperimentalValidator (not here)
    # because they require lazy-loaded OBO parsers. The model validates
    # structure and basic format; the validator layer adds ontology checks.

    @model_validator(mode="after")
    def validate_cell_line_development_stage(self) -> ExperimentalMetadata:
        """V-1b: cell line tissue_type → development_stage must be 'na'."""
        if self.experiment.tissue_type == "cell line":
            if self.experiment.development_stage_ontology_term_id != "na":
                raise ValueError(
                    "experiment.development_stage_ontology_term_id must be 'na' "
                    "when tissue_type is 'cell line' (V-1b)"
                )
        return self

    @model_validator(mode="after")
    def validate_cell_line_tissue_format(self) -> ExperimentalMetadata:
        """V-1b: cell line → tissue_ontology_term_id must be CVCL_XXXXX format."""
        if self.experiment.tissue_type == "cell line":
            term = self.experiment.tissue_ontology_term_id
            if not CELLOSAURUS_PATTERN.match(term):
                raise ValueError(
                    f"tissue_ontology_term_id must be a Cellosaurus CVCL_XXXXX term "
                    f"when tissue_type is 'cell line' (V-1b). Got: {term!r}"
                )
        return self

    @model_validator(mode="after")
    def validate_cell_culture_tissue_format(self) -> ExperimentalMetadata:
        """V-1: cell culture → tissue_ontology_term_id must be a CL term."""
        if self.experiment.tissue_type == "cell culture":
            term = self.experiment.tissue_ontology_term_id
            if not term.startswith("CL:"):
                raise ValueError(
                    f"tissue_ontology_term_id must be a CL term when tissue_type "
                    f"is 'cell culture' (V-1). Got: {term!r}"
                )
            if term in FORBIDDEN_CL_TERMS:
                raise ValueError(
                    f"tissue_ontology_term_id {term!r} is a forbidden CL term (V-1). "
                    f"Forbidden: {sorted(FORBIDDEN_CL_TERMS)}"
                )
        return self

    @model_validator(mode="after")
    def validate_tissue_organoid_format(self) -> ExperimentalMetadata:
        """V-2: tissue/organoid → tissue_ontology_term_id must be UBERON term."""
        if self.experiment.tissue_type in ("tissue", "organoid"):
            term = self.experiment.tissue_ontology_term_id
            if not term.startswith("UBERON:"):
                raise ValueError(
                    f"tissue_ontology_term_id must be a UBERON term when tissue_type "
                    f"is 'tissue' or 'organoid' (V-2). Got: {term!r}"
                )
        return self

    @model_validator(mode="after")
    def validate_disease_format(self) -> ExperimentalMetadata:
        """disease_ontology_term_id must be PATO:0000461 or a MONDO term."""
        term = self.experiment.disease_ontology_term_id
        if term != "PATO:0000461" and not term.startswith("MONDO:"):
            raise ValueError(
                f"disease_ontology_term_id must be 'PATO:0000461' (normal) or a "
                f"MONDO term. Got: {term!r}"
            )
        return self

    @model_validator(mode="after")
    def validate_development_stage_format(self) -> ExperimentalMetadata:
        """V-3/V-4: check development_stage prefix matches organism."""
        organism = self.experiment.organism_ontology_term_id
        term = self.experiment.development_stage_ontology_term_id

        if term == "na":
            return self

        if organism == "NCBITaxon:9606":
            if not term.startswith("HsapDv:"):
                raise ValueError(
                    f"development_stage_ontology_term_id must be a HsapDv term "
                    f"for Homo sapiens (V-3). Got: {term!r}"
                )
        elif organism == "NCBITaxon:10090":
            if not term.startswith("MmusDv:"):
                raise ValueError(
                    f"development_stage_ontology_term_id must be a MmusDv term "
                    f"for Mus musculus (V-4). Got: {term!r}"
                )
        return self

    @model_validator(mode="after")
    def validate_assay_format(self) -> ExperimentalMetadata:
        """assay_ontology_term_id must be an EFO term."""
        term = self.experiment.assay_ontology_term_id
        if not term.startswith("EFO:"):
            raise ValueError(
                f"assay_ontology_term_id must be an EFO term (e.g. 'EFO:0022605'). Got: {term!r}"
            )
        return self
