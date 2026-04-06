"""Validator for collection_metadata.yaml."""

from __future__ import annotations

import yaml
from pydantic import ValidationError

from ops_validator.models.collection import CollectionMetadata
from ops_validator.validators.base import BaseValidator


class CollectionValidator(BaseValidator):
    def validate(self) -> bool:
        if not self.path.exists():
            self._error("MISSING", "collection_metadata.yaml", f"File not found: {self.path}")
            return False

        try:
            with open(self.path) as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self._error("PARSE", "collection_metadata.yaml", f"Failed to parse YAML: {e}")
            return False

        if not isinstance(data, dict):
            self._error("STRUCTURE", "collection_metadata.yaml", "File must be a YAML mapping")
            return False

        try:
            CollectionMetadata(**data)
        except ValidationError as e:
            for err in e.errors():
                field_path = ".".join(str(p) for p in err["loc"])
                self._error("SCHEMA", f"collection_metadata.yaml :: {field_path}", err["msg"])

        return self.is_valid
