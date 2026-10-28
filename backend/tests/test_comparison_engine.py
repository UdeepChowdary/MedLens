"""Unit and integration tests for the deterministic medicine comparison engine (ML-042 to ML-046)."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.clinical import DrugInteraction, Source
from app.models.product import Ingredient, Product, ProductIngredient
from app.schemas.common import ComparisonOutcome
from app.services.comparison.engine import ComparisonEngine


def create_test_product(
    pid: str,
    brand_name: str,
    active_name: str,
    strength_num: float,
    strength_unit: str,
    dosage_form: str = "Tablet",
    route: str = "Oral",
    release_type: str = "Immediate Release",
    basis: str = "per tablet",
    excipients: list = None,
) -> Product:
    prod = Product(
        id=pid,
        brand_name=brand_name,
        manufacturer="Test Pharma Ltd",
        dosage_form=dosage_form,
        route=route,
        release_type=release_type,
    )

    ing = Ingredient(
        id=f"ing-{active_name.lower()}",
        preferred_name=active_name,
        drug_class="Analgesic",
    )

    comp = ProductIngredient(
        id=f"comp-{pid}-active",
        product_id=pid,
        ingredient_id=ing.id,
        raw_label_text=f"{active_name} {strength_num}{strength_unit}",
        strength_numeric=strength_num,
        strength_unit=strength_unit,
        strength_basis=basis,
        is_active=True,
    )
    comp.ingredient = ing
    prod.compositions = [comp]

    if excipients:
        for idx, exc_name in enumerate(excipients):
            exc_ing = Ingredient(
                id=f"ing-exc-{exc_name.lower().replace(' ', '-')}",
                preferred_name=exc_name,
                drug_class="Excipient",
            )
            exc_comp = ProductIngredient(
                id=f"comp-{pid}-exc-{idx}",
                product_id=pid,
                ingredient_id=exc_ing.id,
                raw_label_text=exc_name,
                strength_numeric=None,
                strength_unit="q.s.",
                strength_basis=basis,
                is_active=False,
            )
            exc_comp.ingredient = exc_ing
            prod.compositions.append(exc_comp)

    return prod


def test_identical_products_comparison():
    """ML-042, ML-043: Verifies identical active ingredient, strength, and formulation yield comparable status."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Paracip 500", "Paracetamol", 500.0, "mg")
    prod_b = create_test_product("p2", "Calpol 500", "Paracetamol", 500.0, "mg")

    res = engine.compare(prod_a, prod_b)

    assert res.comparison_status == "comparable"
    assert res.strength_delta is not None
    assert res.strength_delta.difference_detected is False
    assert res.strength_delta.numeric_delta == 0.0

    outcomes = {a.field: a.result for a in res.attributes}
    assert outcomes["active_ingredients"] == ComparisonOutcome.MATCH
    assert outcomes["strength"] == ComparisonOutcome.MATCH
    assert outcomes["dosage_form"] == ComparisonOutcome.MATCH
    assert outcomes["route"] == ComparisonOutcome.MATCH
    assert outcomes["release_type"] == ComparisonOutcome.MATCH


def test_strength_discrepancy_and_advisory():
    """ML-042: Verifies strength differences compute quantitative delta and attach dosage frequency warnings."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Dolo 650", "Paracetamol", 650.0, "mg")
    prod_b = create_test_product("p2", "Calpol 500", "Paracetamol", 500.0, "mg")

    res = engine.compare(prod_a, prod_b)

    assert res.comparison_status == "partially_comparable"
    assert res.strength_delta is not None
    assert res.strength_delta.difference_detected is True
    assert res.strength_delta.numeric_delta == 150.0
    assert res.strength_delta.unit == "mg"
    assert "150 mg higher" in res.strength_delta.warning

    outcomes = {a.field: a.result for a in res.attributes}
    assert outcomes["strength"] == ComparisonOutcome.DIFFERENCE


def test_unit_normalization_conversion():
    """ML-042: Verifies mathematical unit normalization (0.5 g normalized to 500 mg)."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Paracetamol 0.5g", "Paracetamol", 0.5, "g")
    prod_b = create_test_product("p2", "Paracetamol 500mg", "Paracetamol", 500.0, "mg")

    res = engine.compare(prod_a, prod_b)

    assert res.strength_delta is not None
    assert res.strength_delta.difference_detected is False
    assert res.strength_delta.numeric_delta == 0.0
    outcomes = {a.field: a.result for a in res.attributes}
    assert outcomes["strength"] == ComparisonOutcome.MATCH


def test_incompatible_dosage_basis():
    """ML-042: Verifies that differing administration bases (tablet vs per 5mL) are flagged as incomparable."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Calpol Tablet", "Paracetamol", 500.0, "mg", basis="per tablet")
    prod_b = create_test_product("p2", "Calpol Suspension", "Paracetamol", 250.0, "mg", dosage_form="Syrup", basis="per 5 mL")

    res = engine.compare(prod_a, prod_b)

    outcomes = {a.field: a.result for a in res.attributes}
    assert outcomes["strength"] == ComparisonOutcome.UNKNOWN
    assert res.strength_delta.difference_detected is True
    assert "basis discrepancy" in res.strength_delta.warning.lower()


def test_formulation_and_release_differences():
    """ML-043: Verifies release kinetics differences warn against chewing/crushing sustained-release tablets."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Metformin IR", "Metformin", 500.0, "mg", release_type="Immediate Release")
    prod_b = create_test_product("p2", "Metformin SR", "Metformin", 500.0, "mg", release_type="Sustained Release")

    res = engine.compare(prod_a, prod_b)

    outcomes = {a.field: a.result for a in res.attributes}
    assert outcomes["release_type"] == ComparisonOutcome.DIFFERENCE
    assert res.comparison_status == "partially_comparable"
    assert "Sustained" in [a.reason for a in res.attributes if a.field == "release_type"][0]


def test_excipient_analysis_and_allergen_alert():
    """ML-044: Verifies inactive excipient delta and flags known allergens (e.g. Lactose Monohydrate)."""
    engine = ComparisonEngine()
    prod_a = create_test_product(
        "p1", "Brand A", "Paracetamol", 500.0, "mg",
        excipients=["Lactose Monohydrate", "Magnesium Stearate"]
    )
    prod_b = create_test_product(
        "p2", "Brand B", "Paracetamol", 500.0, "mg",
        excipients=["Microcrystalline Cellulose", "Magnesium Stearate"]
    )

    res = engine.compare(prod_a, prod_b)

    assert any("Lactose Monohydrate" in diff for diff in res.excipient_differences)
    assert any("Microcrystalline Cellulose" in diff for diff in res.excipient_differences)
    assert any("Allergen Alert" in diff and "Lactose" in diff for diff in res.excipient_differences)


def test_excipient_honest_unavailable_reporting():
    """ML-044: Verifies honest reporting when excipient data is unavailable (zero hallucination)."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Brand A", "Paracetamol", 500.0, "mg", excipients=[])
    prod_b = create_test_product("p2", "Brand B", "Paracetamol", 500.0, "mg", excipients=[])

    res = engine.compare(prod_a, prod_b)

    assert len(res.excipient_differences) == 1
    assert "unavailable in the catalog" in res.excipient_differences[0]


def test_source_backed_drug_interaction():
    """ML-045: Verifies documented interaction reporting with severity and source citation."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Brufen 400", "Ibuprofen", 400.0, "mg")
    prod_b = create_test_product("p2", "Ecosprin 75", "Aspirin", 75.0, "mg")

    src = Source(
        id="src-nlm",
        source_name="National Library of Medicine / DailyMed",
        source_url="https://dailymed.nlm.nih.gov",
    )
    interaction = DrugInteraction(
        id="ix-1",
        ingredient_a_id="ing-ibuprofen",
        ingredient_b_id="ing-aspirin",
        severity="major",
        clinical_effect="Increased gastrointestinal bleeding risk and inhibition of aspirin cardioprotective antiplatelet effect.",
        source_id="src-nlm",
    )
    interaction.source = src

    res = engine.compare(prod_a, prod_b, interactions=[interaction])

    assert res.comparison_status == "conflicting"
    assert any("Clinical Interaction Alert [MAJOR]" in lim for lim in res.limitations)
    assert "National Library of Medicine / DailyMed" in res.sources


def test_negative_proof_interaction_coverage_wording():
    """ML-045: Verifies honest negative-proof coverage wording when no interactions are found."""
    engine = ComparisonEngine()
    prod_a = create_test_product("p1", "Dolo 650", "Paracetamol", 650.0, "mg")
    prod_b = create_test_product("p2", "Calpol 500", "Paracetamol", 500.0, "mg")

    res = engine.compare(prod_a, prod_b, interactions=[])

    honest_disclaimer = any("absence of a documented interaction" in lim for lim in res.limitations)
    assert honest_disclaimer is True


@pytest.mark.asyncio
async def test_api_comparisons_endpoint():
    """ML-046: Verifies POST /api/v1/comparisons integration with the live catalog database."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/comparisons",
            json={"product_id_a": "dolo-650", "product_id_b": "calpol-500"},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["comparison_status"] == "partially_comparable"
        assert data["medicine_a"]["name"] == "Dolo 650"
        assert data["medicine_b"]["name"] == "Calpol 500"
        assert data["strength_delta"]["numeric_delta"] == 150.0
        assert data["therapeutic_equivalence"]["status"] == "not_established"
        assert len(data["attributes"]) >= 4
