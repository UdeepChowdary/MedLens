"""API endpoints for personalized clinical health analysis and BYOK Gemini API validation."""

import json
from typing import Dict, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.repositories.analysis_repository import AnalysisRepository
from app.schemas.personalization import (
    PersonalizeRequest,
    PersonalizeResponse,
    VerifyKeyRequest,
    VerifyKeyResponse,
)
from app.services.personalization_service import PersonalizationService

router = APIRouter()


@router.post("", response_model=PersonalizeResponse)
async def personalize_analysis(
    request: PersonalizeRequest,
    db: AsyncSession = Depends(get_db),
) -> PersonalizeResponse:
    """Evaluates a medication against patient allergies and medical conditions.
    
    If an optional Gemini API key is provided, invokes Gemini for deep clinical cross-reactivity
    and tailored patient guidance; otherwise falls back to deterministic pharmacopeia rules.
    """
    product_context: Dict[str, str] = {}

    if request.analysis_id:
        repo = AnalysisRepository(db)
        record = await repo.get_by_id(request.analysis_id)
        if record and record.report_json:
            try:
                data = json.loads(record.report_json)
                product_context["name"] = data.get("product", {}).get("detected_name", "")
                product_context["manufacturer"] = data.get("product", {}).get("manufacturer", "")
                actives = data.get("active_ingredients", [])
                if actives and isinstance(actives, list):
                    first_act = actives[0]
                    product_context["active_ingredient"] = first_act.get("canonical_name", "")
                    strength = first_act.get("strength", {})
                    product_context["dosage"] = strength.get("raw_text", "")
                    # Append all actives if request didn't specify them
                    if not request.active_ingredients:
                        request.active_ingredients = [act.get("canonical_name", "") for act in actives if act.get("canonical_name")]
                    if not request.dosages:
                        request.dosages = [act.get("strength", {}).get("raw_text", "") for act in actives if act.get("strength", {}).get("raw_text")]
            except Exception:
                pass

    service = PersonalizationService()
    return service.personalize(request=request, product_context=product_context)


@router.post("/verify-key", response_model=VerifyKeyResponse)
async def verify_gemini_key(
    request: VerifyKeyRequest,
) -> VerifyKeyResponse:
    """Live validation of a user-supplied Gemini API key."""
    service = PersonalizationService()
    return service.verify_gemini_key(api_key=request.gemini_api_key)
