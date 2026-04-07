"""Tests for PerturbationLibraryValidator."""

from pathlib import Path

import pandas as pd

from ops_validator.validators.perturbation_library import PerturbationLibraryValidator

VALID_ROW = {
    "perturbation_id": "BRCA2",
    "gene_id": "ENSG00000139618",
    "barcode": "ACGTACGT",
    "role": "targeting",
    "control_type": "",
    "protospacer_sequence": "ACGTACGTACGTACGT",
    "protospacer_adjacent_motif": "3' NGG",
    "sgrna_target_locus": "",
}

VALID_CONTROL_ROW = {
    "perturbation_id": "non-targeting-1",
    "gene_id": "non-targeting",
    "barcode": "TTTTAAAA",
    "role": "control",
    "control_type": "non-targeting",
    "protospacer_sequence": "ACGTACGTACGTACGT",
    "protospacer_adjacent_motif": "3' NGG",
    "sgrna_target_locus": "",
}


def write_csv(tmp_path: Path, rows: list[dict]) -> Path:
    p = tmp_path / "perturbation_library.csv"
    pd.DataFrame(rows).to_csv(p, index=False)
    return p


def test_valid_library(tmp_path):
    p = write_csv(tmp_path, [VALID_ROW, VALID_CONTROL_ROW])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert v.is_valid, v.report()


def test_perturbation_id_na_rejected(tmp_path):
    row = {**VALID_ROW, "perturbation_id": "na"}
    p = write_csv(tmp_path, [row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid
    assert any("na" in e.message for e in v.errors)


def test_invalid_barcode(tmp_path):
    row = {**VALID_ROW, "barcode": "ACGTXYZ"}
    p = write_csv(tmp_path, [row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid


def test_duplicate_barcode(tmp_path):
    row2 = {**VALID_CONTROL_ROW, "barcode": "ACGTACGT"}  # same as VALID_ROW
    p = write_csv(tmp_path, [VALID_ROW, row2])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid
    assert any("duplicate" in e.message.lower() for e in v.errors)


def test_control_missing_control_type(tmp_path):
    row = {**VALID_CONTROL_ROW, "control_type": ""}
    p = write_csv(tmp_path, [VALID_ROW, row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid


def test_targeting_with_control_type(tmp_path):
    row = {**VALID_ROW, "control_type": "non-targeting"}
    p = write_csv(tmp_path, [row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid


def test_invalid_gene_id_format(tmp_path):
    row = {**VALID_ROW, "gene_id": "BRCA2"}  # not an Ensembl ID
    p = write_csv(tmp_path, [row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid


def test_protospacer_too_short(tmp_path):
    row = {**VALID_ROW, "protospacer_sequence": "ACGT"}  # < 14 chars
    p = write_csv(tmp_path, [row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid


def test_invalid_pam_format(tmp_path):
    row = {**VALID_ROW, "protospacer_adjacent_motif": "NGG"}  # missing "3' " prefix
    p = write_csv(tmp_path, [row])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid


def test_blank_gene_id_targeting_row_is_error(tmp_path):
    row = {**VALID_ROW, "gene_id": ""}
    p = write_csv(tmp_path, [row, VALID_CONTROL_ROW])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid
    assert any("GENE_ID_BLANK" in e.rule_id for e in v.errors)


def test_gene_id_not_in_gencode_is_error(tmp_path):
    row = {**VALID_ROW, "gene_id": "ENSG99999999999"}
    p = write_csv(tmp_path, [row, VALID_CONTROL_ROW])
    v = PerturbationLibraryValidator(p)
    v.validate()
    assert not v.is_valid
    assert any("GENCODE" in e.rule_id for e in v.errors)


