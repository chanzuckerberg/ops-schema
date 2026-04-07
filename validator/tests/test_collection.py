"""Tests for CollectionValidator."""

import pytest
import yaml
from pathlib import Path

from ops_validator.validators.collection import CollectionValidator


def write_yaml(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "collection_metadata.yaml"
    p.write_text(yaml.dump(data))
    return p


def test_valid_collection_with_doi(tmp_path):
    p = write_yaml(tmp_path, {
        "collection": {
            "title": "My OPS Screen Collection",
            "publication_doi": "https://doi.org/10.1016/j.cell.2022.12.009",
        }
    })
    v = CollectionValidator(p)
    assert v.validate() is True
    assert v.is_valid


def test_valid_collection_no_doi(tmp_path):
    p = write_yaml(tmp_path, {
        "collection": {
            "title": "Unpublished Screen",
            "publication_doi": None,
        }
    })
    v = CollectionValidator(p)
    assert v.validate() is True


def test_invalid_doi_format(tmp_path):
    p = write_yaml(tmp_path, {
        "collection": {
            "title": "My Screen",
            "publication_doi": "10.1016/j.cell.2022.12.009",  # missing https://doi.org/
        }
    })
    v = CollectionValidator(p)
    assert v.validate() is False
    assert any("publication_doi" in e.field_path for e in v.errors)


def test_missing_title(tmp_path):
    p = write_yaml(tmp_path, {"collection": {"publication_doi": None}})
    v = CollectionValidator(p)
    assert v.validate() is False


def test_empty_title(tmp_path):
    p = write_yaml(tmp_path, {"collection": {"title": "   "}})
    v = CollectionValidator(p)
    assert v.validate() is False


def test_file_not_found(tmp_path):
    v = CollectionValidator(tmp_path / "nonexistent.yaml")
    assert v.validate() is False
    assert any("not found" in e.message.lower() for e in v.errors)
