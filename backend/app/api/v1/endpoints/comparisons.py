"""Deterministic brand and composition comparison endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ProductNotFoundError
from app.database.session import get_db
from app.repositories.interaction_repository import InteractionRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.comparison import ComparisonResponse
from app.services.comparison.engine import ComparisonEngine

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

    # Collect all active and inactive ingredient IDs to check cross-product drug interactions
    all_ingredient_ids = [c.ingredient_id for c in product_a.compositions] + [
        c.ingredient_id for c in product_b.compositions
    ]
    unique_ingredient_ids = list(set(all_ingredient_ids))

    interactions = await interaction_repo.find_interactions_for_ingredients(unique_ingredient_ids)

    # Execute deterministic comparison engine
    engine = ComparisonEngine()
    return engine.compare(product_a, product_b, interactions=interactions)
