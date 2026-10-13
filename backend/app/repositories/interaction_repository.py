"""Repository handling Drug-Drug Interaction queries."""

from typing import List
from itertools import combinations
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.clinical import DrugInteraction


class InteractionRepository:
    """Encapsulates data operations for documented pairwise interactions."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_interactions_for_ingredients(self, ingredient_ids: List[str]) -> List[DrugInteraction]:
        """Queries documented interactions between any pair in the provided ingredient list."""
        if len(ingredient_ids) < 2:
            return []

        pairs = list(combinations(ingredient_ids, 2))
        conditions = []
        for id_a, id_b in pairs:
            conditions.append(
                (DrugInteraction.ingredient_a_id == id_a) & (DrugInteraction.ingredient_b_id == id_b)
            )
            conditions.append(
                (DrugInteraction.ingredient_a_id == id_b) & (DrugInteraction.ingredient_b_id == id_a)
            )

        stmt = (
            select(DrugInteraction)
            .where(or_(*conditions))
            .options(selectinload(DrugInteraction.source))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
