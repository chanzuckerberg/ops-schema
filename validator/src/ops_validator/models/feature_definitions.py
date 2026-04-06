"""Pydantic model for feature_definitions.csv (one model instance per row)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, field_validator


class FeatureDefinitionRow(BaseModel):
    feature_id: str
    feature_name: str
    feature_type: Literal[
        "shape", "intensity", "correlation", "texture", "granularity", "categorical"
    ]
    compartment: str | None = None
    channel: str | None = None
    unit: str | None = None
    software: str | None = None
    version: str | None = None

    @field_validator("feature_id")
    @classmethod
    def feature_id_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("feature_id must not be empty")
        return v

    @field_validator("feature_name")
    @classmethod
    def feature_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("feature_name must not be empty")
        return v

    @field_validator("compartment")
    @classmethod
    def compartment_valid(cls, v: str | None) -> str | None:
        # Any compartment name is valid (e.g., nucleus, cell, cytoplasm)
        if v is not None and not v.strip():
            raise ValueError("compartment must not be empty if provided")
        return v
