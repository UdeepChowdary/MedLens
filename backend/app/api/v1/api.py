"""Router aggregation for API v1."""

from fastapi import APIRouter
from app.api.v1.endpoints import health, analyses, products, comparisons, interactions

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System & Health"])
api_router.include_router(analyses.router, prefix="/analyses", tags=["Analyses"])
api_router.include_router(products.router, prefix="/products", tags=["Products Catalog"])
api_router.include_router(comparisons.router, prefix="/comparisons", tags=["Comparisons"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["Interactions"])
