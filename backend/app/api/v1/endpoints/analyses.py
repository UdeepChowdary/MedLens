"""Analysis lifecycle endpoints: image intake and report retrieval."""

import uuid
from typing import Optional
from fastapi import APIRouter, File, UploadFile, status
from app.core.config import settings
from app.core.errors import ImageValidationError, AnalysisNotFoundError
from app.schemas.analysis import AnalysisCreateResponse, AnalysisResponse
from app.schemas.common import VerificationState
from app.schemas.product import ProductReport, SafetyProfile
from app.schemas.analysis import MultidimensionalConfidence

router = APIRouter()

# Allowed image MIME types per Blueprint Section 05
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("", response_model=AnalysisCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_analysis(
    file: UploadFile = File(..., description="Medicine packaging image (JPEG, PNG, WebP)")
) -> AnalysisCreateResponse:
    """Accepts and validates medicine label packaging photo, returning tracking ID."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ImageValidationError(
            message=f"Unsupported file format '{file.content_type}'. Must be JPEG, PNG, or WebP.",
            details={"content_type": file.content_type, "allowed": list(ALLOWED_MIME_TYPES)},
        )

    # Read bytes to validate max size
    contents = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise ImageValidationError(
            message=f"File size {len(contents)} bytes exceeds maximum {settings.MAX_UPLOAD_SIZE_MB}MB limit.",
            details={"file_size_bytes": len(contents), "max_bytes": max_bytes},
        )

    analysis_id = str(uuid.uuid4())
    return AnalysisCreateResponse(analysis_id=analysis_id, status="received")


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(analysis_id: str) -> AnalysisResponse:
    """Retrieves verified report or current processing state for an analysis ID."""
    # In Phase 1, demonstrative fixture is returned for 'demo-scan'; others raise 404
    if analysis_id != "demo-scan":
        raise AnalysisNotFoundError(analysis_id=analysis_id)

    return AnalysisResponse(
        analysis_id="demo-scan",
        status=VerificationState.VERIFIED,
        processing_time_ms=1850,
        confidence=MultidimensionalConfidence(
            ocr_quality=0.96,
            extraction_quality=0.95,
            identity_confidence=0.98,
            evidence_coverage=0.92,
        ),
        product=ProductReport(
            detected_name="Dolo 650",
            dosage_form="Tablet",
            manufacturer="Micro Labs Ltd",
            is_verified=True,
        ),
        active_ingredients=[],
        inactive_ingredients=[],
        safety_profile=SafetyProfile(
            purpose_summary="Symptomatic relief of fever and mild-to-moderate pain.",
            precautions=["Do not exceed maximum daily dose of 4000mg."],
            contraindications=["Severe hepatic impairment or active liver disease."],
            adverse_effects=["Nausea", "Allergic skin rash"],
        ),
        uncertainties=[],
        audit_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        sources=[],
    )
