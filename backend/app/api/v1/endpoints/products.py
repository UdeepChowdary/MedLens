"""Product catalog search and detail lookup endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ProductNotFoundError
from app.database.session import get_db
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductReport

router = APIRouter()


def _to_product_report(product: Product) -> ProductReport:
    """Maps Product ORM entity to API ProductReport schema."""
    return ProductReport(
        id=product.id,
        detected_name=product.brand_name,
        dosage_form=product.dosage_form,
        manufacturer=product.manufacturer,
        is_verified=(product.status == "approved"),
    )


@router.get("/search", response_model=List[ProductReport])
async def search_products(
    q: str = Query(..., min_length=2, description="Product brand or salt query"),
    db: AsyncSession = Depends(get_db),
) -> List[ProductReport]:
    """Searches canonical products catalog by query string against brand and active ingredients."""
    repo = ProductRepository(db)
    products = await repo.search(q)
    return [_to_product_report(p) for p in products]


@router.get("/{product_id}", response_model=ProductReport)
async def get_product(
    product_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProductReport:
    """Retrieves normalized product record by ID or normalized brand slug."""
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id)
    if not product:
        raise ProductNotFoundError(product_id=product_id)
    return _to_product_report(product)
