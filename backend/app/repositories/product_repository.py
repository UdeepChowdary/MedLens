"""Repository handling Product and ProductIngredient database queries."""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductIngredient
from app.models.clinical import ClinicalInformation


class ProductRepository:
    """Encapsulates data operations for products and their formulations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: str) -> Optional[Product]:
        """Fetches product by ID or normalized slug with eager loading."""
        stmt = (
            select(Product)
            .where(
                (Product.id == product_id)
                | (Product.brand_name.ilike(product_id.replace("-", " ")))
            )
            .options(
                selectinload(Product.compositions).selectinload(ProductIngredient.ingredient)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_brand_name(self, brand_name: str) -> Optional[Product]:
        """Exact match lookup on brand name."""
        stmt = (
            select(Product)
            .where(Product.brand_name.ilike(brand_name))
            .options(
                selectinload(Product.compositions).selectinload(ProductIngredient.ingredient)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, query: str, limit: int = 10) -> List[Product]:
        """Performs case-insensitive search on brand names and active ingredient names."""
        from app.models.product import Ingredient
        stmt = (
            select(Product)
            .outerjoin(Product.compositions)
            .outerjoin(ProductIngredient.ingredient)
            .where(
                (Product.brand_name.ilike(f"%{query}%"))
                | (Ingredient.preferred_name.ilike(f"%{query}%"))
            )
            .options(
                selectinload(Product.compositions).selectinload(ProductIngredient.ingredient)
            )
            .distinct()
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_clinical_info(self, product_id: str, ingredient_ids: List[str]) -> List[ClinicalInformation]:
        """Fetches clinical monographs associated with product or its ingredients."""
        subject_ids = [product_id] + ingredient_ids
        stmt = (
            select(ClinicalInformation)
            .where(ClinicalInformation.subject_id.in_(subject_ids))
            .options(selectinload(ClinicalInformation.source))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
