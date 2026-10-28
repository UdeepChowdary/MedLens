"""Interaction checking endpoint: queries curated drug-drug interactions by ingredient IDs."""

from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.interaction import InteractionReport

router = APIRouter()


class InteractionCheckRequest(BaseModel):
    """Request for interaction lookup by ingredient IDs."""
    ingredient_ids: List[str] = Field(
        min_length=2,
        description="List of canonical ingredient IDs to check pairwise interactions for."
    )


@router.post("/check", response_model=List[InteractionReport])
async def check_interactions(
    payload: InteractionCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> List[InteractionReport]:
    """
    Returns documented drug-drug interaction evidence for the specified ingredients.
    
    IMPORTANT: An empty result means 'no record found in consulted sources', 
    NOT 'no interaction exists'. Coverage limitations are always in effect.
    """
    repo = InteractionRepository(db)
    interactions = await repo.find_interactions_for_ingredients(payload.ingredient_ids)
    
    return [
        InteractionReport(
            ingredient_a=i.ingredient_a_id,
            ingredient_b=i.ingredient_b_id,
            severity=i.severity,
            clinical_effect=i.clinical_effect,
            source_id=i.source_id,
            coverage_note="Interaction record sourced from curated pharmaceutical monographs. "
                         "Absence of a record does not imply absence of interaction.",
        )
        for i in interactions
    ]

