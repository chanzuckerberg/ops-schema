"""
Validator for experimental_metadata.yaml.

Structural + format validation is handled by the Pydantic model.
Ontology term existence and ancestor checks are layered on here,
using lazy-loaded OBO parsers. If OBO files are not present,
ontology checks emit warnings instead of errors.
"""

from __future__ import annotations

import yaml
from pydantic import ValidationError

from ops_validator.models.experimental import ExperimentalMetadata
from ops_validator.ontology import get_parser, ontology_files_present
from ops_validator.validators.base import BaseValidator


class ExperimentalValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", "experimental_metadata.yaml", f"File not found: {self.path}")
            return False

        try:
            with open(self.path) as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self._error("PARSE", "experimental_metadata.yaml", f"Failed to parse YAML: {e}")
            return False

        if not isinstance(data, dict):
            self._error("STRUCTURE", "experimental_metadata.yaml", "File must be a YAML mapping")
            return False

        # Step 1: structural + format validation via Pydantic
        try:
            metadata = ExperimentalMetadata(**data)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("SCHEMA", f"experimental_metadata.yaml :: {field_path}", err["msg"])
            return False  # don't run ontology checks if structure is broken

        # Step 2: ontology term existence + ancestor checks (requires OBO files)
        if not ontology_files_present():
            self._warning(
                "ONTOLOGY_FILES_MISSING",
                "experimental_metadata.yaml",
                "OBO reference files not found — ontology term existence checks skipped. "
                "Run `python scripts/prepare_references.py` to enable full ontology validation.",
            )
            return self.is_valid

        self._validate_ontology_terms(metadata)
        return self.is_valid

    def _validate_ontology_terms(self, metadata: ExperimentalMetadata) -> None:
        exp = metadata.experiment

        # organism — already constrained to 3 values by the model, no OBO lookup needed

        # tissue_ontology_term_id
        tissue_type = exp.tissue_type
        tissue_term = exp.tissue_ontology_term_id

        if tissue_type == "cell line":
            cl_parser = get_parser("cellosaurus")
            if not cl_parser.term_exists(tissue_term):
                self._error(
                    "V-1b",
                    "experiment.tissue_ontology_term_id",
                    f"{tissue_term!r} is not a valid Cellosaurus term.",
                )
            elif cl_parser.is_deprecated(tissue_term):
                self._error(
                    "V-1b",
                    "experiment.tissue_ontology_term_id",
                    f"{tissue_term!r} is deprecated in Cellosaurus. Use a current term.",
                )

        elif tissue_type == "cell culture":
            cl_parser = get_parser("cl")
            if not cl_parser.term_exists(tissue_term):
                self._error(
                    "V-1",
                    "experiment.tissue_ontology_term_id",
                    f"{tissue_term!r} is not a valid CL term.",
                )
            elif cl_parser.is_deprecated(tissue_term):
                self._error(
                    "V-1",
                    "experiment.tissue_ontology_term_id",
                    f"{tissue_term!r} is deprecated in the Cell Ontology.",
                )

        elif tissue_type in ("tissue", "organoid"):
            uberon = get_parser("uberon")
            if not uberon.term_exists(tissue_term):
                self._error(
                    "V-2",
                    "experiment.tissue_ontology_term_id",
                    f"{tissue_term!r} is not a valid UBERON term.",
                )
            elif not uberon.is_descendant_of(tissue_term, "UBERON:0001062"):
                self._error(
                    "V-2",
                    "experiment.tissue_ontology_term_id",
                    f"{tissue_term!r} is not a descendant of UBERON:0001062 (anatomical entity).",
                )

        # disease_ontology_term_id
        disease_term = exp.disease_ontology_term_id
        if disease_term != "PATO:0000461":
            mondo = get_parser("mondo")
            if not mondo.term_exists(disease_term):
                self._error(
                    "DISEASE",
                    "experiment.disease_ontology_term_id",
                    f"{disease_term!r} is not a valid MONDO term.",
                )
            elif not mondo.is_descendant_of(disease_term, "MONDO:0000001"):
                self._error(
                    "DISEASE",
                    "experiment.disease_ontology_term_id",
                    f"{disease_term!r} is not a descendant of MONDO:0000001 (disease).",
                )

        # development_stage_ontology_term_id
        stage_term = exp.development_stage_ontology_term_id
        organism = exp.organism_ontology_term_id

        if stage_term != "na":
            if organism == "NCBITaxon:9606":
                hsapdv = get_parser("hsapdv")
                if not hsapdv.term_exists(stage_term):
                    self._error(
                        "V-3",
                        "experiment.development_stage_ontology_term_id",
                        f"{stage_term!r} is not a valid HsapDv term.",
                    )
                elif not hsapdv.is_descendant_of(stage_term, "HsapDv:0000001"):
                    self._error(
                        "V-3",
                        "experiment.development_stage_ontology_term_id",
                        f"{stage_term!r} is not a descendant of HsapDv:0000001 (life cycle).",
                    )
            elif organism == "NCBITaxon:10090":
                mmusdv = get_parser("mmusdv")
                if not mmusdv.term_exists(stage_term):
                    self._error(
                        "V-4",
                        "experiment.development_stage_ontology_term_id",
                        f"{stage_term!r} is not a valid MmusDv term.",
                    )
                elif not mmusdv.is_descendant_of(stage_term, "MmusDv:0000001"):
                    self._error(
                        "V-4",
                        "experiment.development_stage_ontology_term_id",
                        f"{stage_term!r} is not a descendant of MmusDv:0000001 (life cycle).",
                    )

        # assay_ontology_term_id
        assay_term = exp.assay_ontology_term_id
        efo = get_parser("efo")
        if not efo.term_exists(assay_term):
            self._error(
                "ASSAY",
                "experiment.assay_ontology_term_id",
                f"{assay_term!r} is not a valid EFO term.",
            )
        elif efo.is_deprecated(assay_term):
            self._error(
                "ASSAY",
                "experiment.assay_ontology_term_id",
                f"{assay_term!r} is deprecated in EFO.",
            )
