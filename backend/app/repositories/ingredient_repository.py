"""Repository handling Canonical Ingredient and Alias lookup queries."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Ingredient, IngredientAlias


class IngredientRepository:
    """Encapsulates data operations for chemical ingredients and alias resolution."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, ingredient_id: str) -> Optional[Ingredient]:
        """Fetches ingredient by primary key ID."""
        stmt = (
            select(Ingredient)
            .where(Ingredient.id == ingredient_id)
            .options(selectinload(Ingredient.aliases))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_canonical_by_alias(self, alias_text: str) -> Optional[Ingredient]:
        """Resolves alias string to canonical INN ingredient via verified aliases."""
        clean_alias = alias_text.strip().lower()
        stmt = (
            select(Ingredient)
            .join(IngredientAlias, Ingredient.id == IngredientAlias.ingredient_id)
            .where(
                (Ingredient.preferred_name.ilike(alias_text.strip()))
                | (IngredientAlias.normalized_alias == clean_alias)
                | (IngredientAlias.alias_text.ilike(alias_text.strip()))
            )
            .options(selectinload(Ingredient.aliases))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 10) -> List[Ingredient]:
        """Searches canonical ingredients by preferred name."""
        stmt = (
            select(Ingredient)
            .where(Ingredient.preferred_name.ilike(f"%{query}%"))
            .options(selectinload(Ingredient.aliases))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
