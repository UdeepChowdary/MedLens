"""Deterministic brand and composition comparison endpoints."""

from typing import Dict, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ProductNotFoundError
from app.database.session import get_db
from app.repositories.product_repository import ProductRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.comparison import (
    ComparisonResponse,
    AttributeComparison,
    StrengthDelta,
)
from app.schemas.common import ComparisonOutcome

router = APIRouter()


class ComparisonRequest(BaseModel):
    """Request payload comparing two identified products."""
    product_id_a: str = Field(description="First product ID, e.g. 'dolo-650'")
    product_id_b: str = Field(description="Second product ID, e.g. 'calpol-500'")


@router.post("", response_model=ComparisonResponse)
async def compare_products(
    payload: ComparisonRequest,
    db: AsyncSession = Depends(get_db),
) -> ComparisonResponse:
    """Performs deterministic composition comparison between two products backed by relational database."""
    product_repo = ProductRepository(db)
    interaction_repo = InteractionRepository(db)

    product_a = await product_repo.get_by_id(payload.product_id_a)
    if not product_a:
        raise ProductNotFoundError(product_id=payload.product_id_a)

    product_b = await product_repo.get_by_id(payload.product_id_b)
    if not product_b:
        raise ProductNotFoundError(product_id=payload.product_id_b)

    # Extract active ingredients
    active_a = [c for c in product_a.compositions if c.is_active]
    active_b = [c for c in product_b.compositions if c.is_active]

    map_a = {c.ingredient_id: c for c in active_a}
    map_b = {c.ingredient_id: c for c in active_b}

    shared_ids = set(map_a.keys()) & set(map_b.keys())
    sources = ["PubChem:Monographs", "Regulatory:CuratedCatalog"]

    attributes: List[AttributeComparison] = []

    # 1. Active Ingredients Comparison
    if set(map_a.keys()) == set(map_b.keys()):
        evidence_list = [f"PubChem:{c.ingredient.chemical_identifier or c.ingredient.preferred_name}" for c in active_a]
        attributes.append(
            AttributeComparison(
                field="active_ingredients",
                result=ComparisonOutcome.MATCH,
                evidence=evidence_list,
                reason="Identical canonical active ingredient profile.",
            )
        )
    else:
        attributes.append(
            AttributeComparison(
                field="active_ingredients",
                result=ComparisonOutcome.DIFFERENCE,
                evidence=[f"{c.ingredient.preferred_name}" for c in active_a + active_b],
                reason=f"Differing active ingredients between {product_a.brand_name} and {product_b.brand_name}.",
            )
        )

    # 2. Strength Comparison & Delta Computation
    strength_delta_obj: StrengthDelta = None
    if shared_ids:
        # Evaluate primary shared active ingredient
        primary_id = list(shared_ids)[0]
        comp_a = map_a[primary_id]
        comp_b = map_b[primary_id]

        str_a = comp_a.strength_numeric or 0.0
        str_b = comp_b.strength_numeric or 0.0
        diff = abs(str_a - str_b)

        if diff > 0:
            attributes.append(
                AttributeComparison(
                    field="strength",
                    result=ComparisonOutcome.DIFFERENCE,
                    evidence=[f"Packaging:{product_a.brand_name}", f"Packaging:{product_b.brand_name}"],
                    reason=f"{product_a.brand_name} ({str_a:g}{comp_a.strength_unit}) vs {product_b.brand_name} ({str_b:g}{comp_b.strength_unit}) ({diff:g}{comp_a.strength_unit} discrepancy)",
                )
            )
            strength_delta_obj = StrengthDelta(
                difference_detected=True,
                numeric_delta=diff,
                unit=comp_a.strength_unit,
                warning=f"Product A ({product_a.brand_name}) contains {diff:g}{comp_a.strength_unit} higher active {comp_a.ingredient.preferred_name} per dose than Product B ({product_b.brand_name}).",
            )
        else:
            attributes.append(
                AttributeComparison(
                    field="strength",
                    result=ComparisonOutcome.MATCH,
                    evidence=[f"Packaging:{product_a.brand_name}", f"Packaging:{product_b.brand_name}"],
                    reason="Equivalent active ingredient nominal strength.",
                )
            )
            strength_delta_obj = StrengthDelta(
                difference_detected=False,
                numeric_delta=0.0,
                unit=comp_a.strength_unit,
                warning="Active strengths are quantitatively identical.",
            )
    else:
        attributes.append(
            AttributeComparison(
                field="strength",
                result=ComparisonOutcome.UNKNOWN,
                reason="Cannot compute quantitative strength delta across distinct chemical active moieties.",
            )
        )

    # 3. Dosage Form Comparison
    if product_a.dosage_form.lower() == product_b.dosage_form.lower():
        attributes.append(
            AttributeComparison(
                field="dosage_form",
                result=ComparisonOutcome.MATCH,
                evidence=["PackageLeaflet"],
                reason=f"Both presentations are formulated as {product_a.dosage_form}.",
            )
        )
    else:
        attributes.append(
            AttributeComparison(
                field="dosage_form",
                result=ComparisonOutcome.DIFFERENCE,
                evidence=["PackageLeaflet"],
                reason=f"{product_a.brand_name} ({product_a.dosage_form}) vs {product_b.brand_name} ({product_b.dosage_form}).",
            )
        )

    # 4. Check Pairwise Interactions if co-administered
    combined_ingredient_ids = list(set(map_a.keys()) | set(map_b.keys()))
    interactions = await interaction_repo.find_interactions_for_ingredients(combined_ingredient_ids)
    interaction_warnings = [
        f"Interaction detected ({i.severity}): {i.clinical_effect}" for i in interactions
    ]

    # 5. Overall comparability status
    if set(map_a.keys()) == set(map_b.keys()):
        if strength_delta_obj and not strength_delta_obj.difference_detected:
            status = "comparable"
        else:
            status = "partially_comparable"
    else:
        status = "different_compositions"

    limitations = [
        "Comparison is based on registered catalog label composition and regulatory monographs.",
        "Consult a licensed medical practitioner or registered pharmacist before any brand substitution.",
    ]
    if interaction_warnings:
        limitations.extend(interaction_warnings)

    return ComparisonResponse(
        comparison_status=status,
        medicine_a={"product_id": product_a.id, "name": product_a.brand_name, "manufacturer": product_a.manufacturer},
        medicine_b={"product_id": product_b.id, "name": product_b.brand_name, "manufacturer": product_b.manufacturer},
        attributes=attributes,
        strength_delta=strength_delta_obj,
        excipient_differences=[
            f"Excipients for {product_a.brand_name} and {product_b.brand_name} may differ in inactive binders, dyes, and coatings."
        ],
        therapeutic_equivalence={
            "status": "not_established",
            "note": "Bioequivalence cannot be asserted without product-specific in-vivo bioequivalence filings.",
        },
        limitations=limitations,
        sources=sources,
    )
