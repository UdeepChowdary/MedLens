"""Service health and liveness probe endpoint."""

from typing import Dict
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=Dict[str, str])
def check_health() -> Dict[str, str]:
    """Returns application health, environment mode, and API status."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
    }
