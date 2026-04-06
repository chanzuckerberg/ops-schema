"""Tests for FeatureDefinitionsValidator and FeatureDefinitionRow model."""

from __future__ import annotations

import textwrap

import pytest

from ops_validator.models.feature_definitions import FeatureDefinitionRow
from ops_validator.validators.feature_definitions import FeatureDefinitionsValidator

# ---------------------------------------------------------------------------
# FeatureDefinitionRow model
# ---------------------------------------------------------------------------


class TestFeatureDefinitionRowModel:
    def test_valid_shape_row(self):
        row = FeatureDefinitionRow(
            feature_id="nucleus__shape__area",
            feature_name="Nucleus Area",
            feature_type="shape",
            compartment="nucleus",
        )
        assert row.feature_type == "shape"
        assert row.compartment == "nucleus"

    def test_valid_intensity_row(self):
        row = FeatureDefinitionRow(
            feature_id="cell__dna__mean",
            feature_name="Cell DNA Mean Intensity",
            feature_type="intensity",
            compartment="cell",
            channel="dna",
        )
        assert row.channel == "dna"

    def test_valid_correlation_row(self):
        row = FeatureDefinitionRow(
            feature_id="nucleus__correlation__dna_tubulin",
            feature_name="Nucleus DNA-Tubulin Correlation",
            feature_type="correlation",
            compartment="nucleus",
        )
        assert row.feature_type == "correlation"

    def test_valid_texture_row(self):
        row = FeatureDefinitionRow(
            feature_id="my_custom_texture_feature",
            feature_name="Custom Texture",
            feature_type="texture",
        )
        assert row.feature_type == "texture"

    def test_valid_granularity_row(self):
        row = FeatureDefinitionRow(
            feature_id="my_granularity_feature",
            feature_name="Custom Granularity",
            feature_type="granularity",
        )
        assert row.feature_type == "granularity"

    def test_valid_categorical_row(self):
        row = FeatureDefinitionRow(
            feature_id="cell_class",
            feature_name="Cell Class",
            feature_type="categorical",
        )
        assert row.feature_type == "categorical"

    def test_rejects_old_morphology_type(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="feature_type"):
            FeatureDefinitionRow(
                feature_id="some_feature",
                feature_name="Some Feature",
                feature_type="morphology",  # old value — removed from spec
            )

    def test_rejects_invalid_compartment(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="compartment"):
            FeatureDefinitionRow(
                feature_id="bad__shape__area",
                feature_name="Bad",
                feature_type="shape",
                compartment="cytoplasm",  # not a valid compartment
            )

    def test_optional_fields_default_to_none(self):
        row = FeatureDefinitionRow(
            feature_id="f1",
            feature_name="Feature 1",
            feature_type="shape",
        )
        assert row.compartment is None
        assert row.channel is None
        assert row.unit is None
        assert row.software is None
        assert row.version is None

    def test_rejects_empty_feature_id(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError, match="feature_id must not be empty"):
            FeatureDefinitionRow(
                feature_id="   ",
                feature_name="Something",
                feature_type="shape",
            )


# ---------------------------------------------------------------------------
# FeatureDefinitionsValidator
# ---------------------------------------------------------------------------


class TestFeatureDefinitionsValidator:
    def test_missing_file_emits_recommended_warning(self, tmp_path):
        v = FeatureDefinitionsValidator(tmp_path / "feature_definitions.csv")
        result = v.validate()
        assert result is True
        assert len(v.errors) == 0
        assert any(i.rule_id == "RECOMMENDED_MISSING" for i in v.warnings)

    def test_valid_csv(self, tmp_path):
        csv = tmp_path / "feature_definitions.csv"
        csv.write_text(
            textwrap.dedent("""\
            feature_id,feature_name,feature_type,compartment,channel
            nucleus__shape__area,Nucleus Area,shape,nucleus,
            cell__dna__mean,Cell DNA Mean,intensity,cell,dna
            nucleus__correlation__dna_tubulin,DNA-Tubulin Correlation,correlation,nucleus,
        """)
        )
        v = FeatureDefinitionsValidator(csv)
        assert v.validate() is True
        assert len(v.errors) == 0

    def test_missing_required_columns(self, tmp_path):
        csv = tmp_path / "feature_definitions.csv"
        csv.write_text("feature_id,feature_name\nf1,Feature 1\n")
        v = FeatureDefinitionsValidator(csv)
        v.validate()
        assert any("feature_type" in i.message for i in v.errors)

    def test_invalid_feature_type_rejected(self, tmp_path):
        csv = tmp_path / "feature_definitions.csv"
        csv.write_text(
            textwrap.dedent("""\
            feature_id,feature_name,feature_type
            f1,Feature 1,morphology
        """)
        )
        v = FeatureDefinitionsValidator(csv)
        v.validate()
        assert len(v.errors) > 0

    def test_duplicate_feature_id_rejected(self, tmp_path):
        csv = tmp_path / "feature_definitions.csv"
        csv.write_text(
            textwrap.dedent("""\
            feature_id,feature_name,feature_type
            nucleus__shape__area,Nucleus Area,shape
            nucleus__shape__area,Nucleus Area Dup,shape
        """)
        )
        v = FeatureDefinitionsValidator(csv)
        v.validate()
        assert any(i.rule_id == "PK" for i in v.errors)

    def test_lab_features_beyond_viz_set_are_valid(self, tmp_path):
        """feature_definitions.csv may contain features not in aggregated_data — that's expected."""
        csv = tmp_path / "feature_definitions.csv"
        csv.write_text(
            textwrap.dedent("""\
            feature_id,feature_name,feature_type,compartment,channel,software
            nucleus__shape__area,Nucleus Area,shape,nucleus,,CellProfiler
            my_custom_texture_1,Custom Texture Feature,texture,,,CustomPipeline
            my_custom_texture_2,Another Custom Feature,granularity,,,CustomPipeline
            cell_class_label,Cell Class,categorical,,,ClassifierV2
        """)
        )
        v = FeatureDefinitionsValidator(csv)
        assert v.validate() is True
        assert len(v.errors) == 0
