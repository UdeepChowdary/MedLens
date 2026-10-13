"""Tests for database models, repositories, and clinical knowledge base."""

import pytest
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import Base
from app.database.seed import seed_database
from app.models.product import Product, ProductIngredient, Ingredient
from app.models.analysis import Analysis, ExtractedEntityModel
from app.repositories.product_repository import ProductRepository
from app.repositories.ingredient_repository import IngredientRepository
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.analysis_repository import AnalysisRepository


def test_schema_table_names():
    """Verifies that all 11 required relational entities are defined on metadata."""
    expected_tables = {
        "products",
        "ingredients",
        "product_ingredients",
        "ingredient_aliases",
        "sources",
        "clinical_information",
        "drug_interactions",
        "analyses",
        "extracted_entities",
        "analysis_sources",
        "model_versions",
    }
    actual_tables = set(Base.metadata.tables.keys())
    for t in expected_tables:
        assert t in actual_tables, f"Missing table {t} in metadata"


async def test_seeder_idempotency(db_session: AsyncSession):
    """Verifies running the clinical seeder repeatedly produces zero duplicate inserts."""
    repeat_counts = await seed_database(db_session)
    assert repeat_counts["sources"] == 0
    assert repeat_counts["ingredients"] == 0
    assert repeat_counts["aliases"] == 0
    assert repeat_counts["products"] == 0
    assert repeat_counts["interactions"] == 0


async def test_product_repository_queries(db_session: AsyncSession):
    """Tests ProductRepository retrieval and cross-ingredient search."""
    repo = ProductRepository(db_session)

    # 1. Fetch by ID
    dolo = await repo.get_by_id("dolo-650")
    assert dolo is not None
    assert dolo.brand_name == "Dolo 650"
    assert dolo.dosage_form == "Tablet"
    assert len(dolo.compositions) == 1
    assert dolo.compositions[0].strength_numeric == 650.0
    assert dolo.compositions[0].ingredient.preferred_name == "Paracetamol"

    # 2. Search by brand name
    brand_results = await repo.search("dolo")
    assert len(brand_results) >= 1
    assert any(p.id == "dolo-650" for p in brand_results)

    # 3. Search by active ingredient (Paracetamol) finds both Dolo and Calpol
    ingredient_results = await repo.search("paracetamol")
    product_names = [p.brand_name for p in ingredient_results]
    assert "Dolo 650" in product_names
    assert "Calpol 500" in product_names


async def test_ingredient_repository_alias_resolution(db_session: AsyncSession):
    """Tests normalization from commercial & pharmacopeial synonyms to canonical INN."""
    repo = IngredientRepository(db_session)

    # US synonym
    ing_us = await repo.find_canonical_by_alias("Acetaminophen")
    assert ing_us is not None
    assert ing_us.preferred_name == "Paracetamol"

    # Abbreviation
    ing_abbr = await repo.find_canonical_by_alias("APAP")
    assert ing_abbr is not None
    assert ing_abbr.preferred_name == "Paracetamol"

    # Pharmacopeial salt notation
    ing_ip = await repo.find_canonical_by_alias("Paracetamol IP")
    assert ing_ip is not None
    assert ing_ip.preferred_name == "Paracetamol"

    # Non-existent alias
    ing_none = await repo.find_canonical_by_alias("CompletelyUnknownMolecule")
    assert ing_none is None


async def test_interaction_repository_pair_matching(db_session: AsyncSession):
    """Tests querying documented pairwise interactions between ingredients."""
    repo = InteractionRepository(db_session)

    # Documented pair: Paracetamol + Ibuprofen
    interactions = await repo.find_interactions_for_ingredients(["ing-paracetamol", "ing-ibuprofen"])
    assert len(interactions) == 1
    assert interactions[0].severity == "minor"
    assert "renal" in interactions[0].clinical_effect.lower()

    # Documented synergistic pair: Amoxicillin + Clavulanic Acid
    amox_interactions = await repo.find_interactions_for_ingredients(["ing-amoxicillin", "ing-clavulanic-acid"])
    assert len(amox_interactions) == 1
    assert "synergistic" in amox_interactions[0].clinical_effect.lower()

    # Single ingredient returns no interaction
    single_res = await repo.find_interactions_for_ingredients(["ing-paracetamol"])
    assert len(single_res) == 0

    # No documented interaction in pair
    empty_res = await repo.find_interactions_for_ingredients(["ing-paracetamol", "ing-cetirizine"])
    assert len(empty_res) == 0


async def test_clinical_monograph_retrieval(db_session: AsyncSession):
    """Tests retrieving clinical claims for a product and its ingredients."""
    repo = ProductRepository(db_session)
    clinical_info = await repo.get_clinical_info("dolo-650", ["ing-paracetamol"])

    assert len(clinical_info) >= 4
    categories = {c.category for c in clinical_info}
    assert "purpose" in categories
    assert "precaution" in categories
    assert "contraindication" in categories
    assert "adverse_effect" in categories

    # Sources are eagerly loaded
    for item in clinical_info:
        assert item.source is not None
        assert item.source.source_url.startswith("http")


async def test_analysis_repository_persistence(db_session: AsyncSession):
    """Tests persisting and retrieving an analysis audit record with extracted entities."""
    repo = AnalysisRepository(db_session)

    job_id = f"test-job-{uuid.uuid4().hex[:8]}"
    analysis = Analysis(
        id=job_id,
        status="completed",
        image_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        processing_time_ms=420,
        confidence_aggregate=0.94,
        model_version="test-model-v1",
    )
    saved = await repo.create(analysis)
    assert saved.id == job_id

    entity = ExtractedEntityModel(
        id=f"ent-{uuid.uuid4().hex[:8]}",
        analysis_id=job_id,
        entity_type="brand_name",
        raw_text="DOLO 650",
        normalized_candidate="Dolo 650",
        confidence=0.98,
        verification_status="verified",
    )
    await repo.add_entities([entity])
    db_session.expire_all()

    fetched = await repo.get_by_id(job_id)
    assert fetched is not None
    assert len(fetched.entities) == 1
    assert fetched.entities[0].raw_text == "DOLO 650"
    assert fetched.entities[0].confidence == 0.98


async def test_foreign_key_cascade(db_session: AsyncSession):
    """Tests foreign key cascading deletion on product and its compositions."""
    temp_id = f"temp-prod-{uuid.uuid4().hex[:6]}"
    temp_prod = Product(
        id=temp_id,
        brand_name="Temporary Drug",
        dosage_form="Capsule",
    )
    db_session.add(temp_prod)
    await db_session.flush()

    comp = ProductIngredient(
        product_id=temp_id,
        ingredient_id="ing-paracetamol",
        raw_label_text="Paracetamol 250 mg",
        strength_numeric=250.0,
        strength_unit="mg",
    )
    db_session.add(comp)
    await db_session.commit()

    # Verify inserted
    saved_comp = await db_session.scalar(
        select(ProductIngredient).where(ProductIngredient.product_id == temp_id)
    )
    assert saved_comp is not None

    # Delete parent
    await db_session.delete(temp_prod)
    await db_session.commit()

    # Child composition must be automatically deleted
    cascaded_comp = await db_session.scalar(
        select(ProductIngredient).where(ProductIngredient.product_id == temp_id)
    )
    assert cascaded_comp is None
