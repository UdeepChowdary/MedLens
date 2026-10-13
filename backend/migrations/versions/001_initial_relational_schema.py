"""001_initial_relational_schema

Revision ID: 001_initial_relational_schema
Revises: 
Create Date: 2026-10-13 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_initial_relational_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Sources
    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_name", sa.String(length=150), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("jurisdiction", sa.String(length=50), nullable=False),
        sa.Column("retrieval_date", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # 2. Products
    op.create_table(
        "products",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("brand_name", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("dosage_form", sa.String(length=100), nullable=False),
        sa.Column("route", sa.String(length=50), nullable=False),
        sa.Column("release_type", sa.String(length=50), nullable=False),
        sa.Column("country_code", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_brand_name"), "products", ["brand_name"], unique=False)

    # 3. Canonical Ingredients
    op.create_table(
        "ingredients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("preferred_name", sa.String(length=255), nullable=False),
        sa.Column("chemical_identifier", sa.String(length=100), nullable=True),
        sa.Column("drug_class", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("standard_mechanism", sa.Text(), nullable=True),
        sa.Column("max_daily_dose_mg", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingredients_preferred_name"), "ingredients", ["preferred_name"], unique=True)

    # 4. Product Ingredients
    op.create_table(
        "product_ingredients",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("product_id", sa.String(length=36), nullable=False),
        sa.Column("ingredient_id", sa.String(length=36), nullable=False),
        sa.Column("raw_label_text", sa.String(length=255), nullable=False),
        sa.Column("strength_numeric", sa.Float(), nullable=True),
        sa.Column("strength_unit", sa.String(length=50), nullable=False),
        sa.Column("strength_basis", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "ingredient_id", "is_active", name="uq_product_ingredient_role"),
    )

    # 5. Ingredient Aliases
    op.create_table(
        "ingredient_aliases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ingredient_id", sa.String(length=36), nullable=False),
        sa.Column("alias_text", sa.String(length=255), nullable=False),
        sa.Column("normalized_alias", sa.String(length=255), nullable=False),
        sa.Column("alias_type", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ingredient_aliases_alias_text"), "ingredient_aliases", ["alias_text"], unique=False)
    op.create_index(op.f("ix_ingredient_aliases_normalized_alias"), "ingredient_aliases", ["normalized_alias"], unique=False)

    # 6. Clinical Information
    op.create_table(
        "clinical_information",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("subject_type", sa.String(length=50), nullable=False),
        sa.Column("subject_id", sa.String(length=36), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clinical_information_subject_id"), "clinical_information", ["subject_id"], unique=False)

    # 7. Drug Interactions
    op.create_table(
        "drug_interactions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("ingredient_a_id", sa.String(length=36), nullable=False),
        sa.Column("ingredient_b_id", sa.String(length=36), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("clinical_effect", sa.Text(), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["ingredient_a_id"], ["ingredients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["ingredient_b_id"], ["ingredients.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_drug_interactions_ingredient_a_id"), "drug_interactions", ["ingredient_a_id"], unique=False)
    op.create_index(op.f("ix_drug_interactions_ingredient_b_id"), "drug_interactions", ["ingredient_b_id"], unique=False)

    # 8. Analyses
    op.create_table(
        "analyses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("image_sha256", sa.String(length=64), nullable=False),
        sa.Column("processing_time_ms", sa.Integer(), nullable=False),
        sa.Column("confidence_aggregate", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analyses_image_sha256"), "analyses", ["image_sha256"], unique=False)

    # 9. Extracted Entities
    op.create_table(
        "extracted_entities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("raw_text", sa.String(length=255), nullable=False),
        sa.Column("normalized_candidate", sa.String(length=255), nullable=True),
        sa.Column("bbox_json", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("verification_status", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 10. Analysis Sources
    op.create_table(
        "analysis_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("analysis_id", sa.String(length=36), nullable=False),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("query_metadata", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["analysis_id"], ["analyses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # 11. Model Versions
    op.create_table(
        "model_versions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("model_id", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("artifact_location", sa.Text(), nullable=False),
        sa.Column("evaluation_summary", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("model_versions")
    op.drop_table("analysis_sources")
    op.drop_table("extracted_entities")
    op.drop_index(op.f("ix_analyses_image_sha256"), table_name="analyses")
    op.drop_table("analyses")
    op.drop_index(op.f("ix_drug_interactions_ingredient_b_id"), table_name="drug_interactions")
    op.drop_index(op.f("ix_drug_interactions_ingredient_a_id"), table_name="drug_interactions")
    op.drop_table("drug_interactions")
    op.drop_index(op.f("ix_clinical_information_subject_id"), table_name="clinical_information")
    op.drop_table("clinical_information")
    op.drop_index(op.f("ix_ingredient_aliases_normalized_alias"), table_name="ingredient_aliases")
    op.drop_index(op.f("ix_ingredient_aliases_alias_text"), table_name="ingredient_aliases")
    op.drop_table("ingredient_aliases")
    op.drop_table("product_ingredients")
    op.drop_index(op.f("ix_ingredients_preferred_name"), table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_index(op.f("ix_products_brand_name"), table_name="products")
    op.drop_table("products")
    op.drop_table("sources")
