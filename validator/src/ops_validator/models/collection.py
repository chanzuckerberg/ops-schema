"""Pydantic model for collection_metadata.yaml"""

from __future__ import annotations

import re

from pydantic import BaseModel, field_validator, model_validator

DOI_PATTERN = re.compile(r"^https://doi\.org/10\.\d{4,9}/\S+$")


class CollectionMetadata(BaseModel):
    collection: CollectionBlock


class CollectionBlock(BaseModel):
    title: str
    publication_doi: str | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("collection.title must not be empty")
        return v

    @field_validator("publication_doi")
    @classmethod
    def doi_format(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not DOI_PATTERN.match(v):
            raise ValueError(
                f"collection.publication_doi must be a valid DOI URI "
                f"(e.g. 'https://doi.org/10.1016/j.cell.2022.12.009'), got: {v!r}"
            )
        return v
