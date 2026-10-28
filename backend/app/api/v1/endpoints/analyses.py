"""Analysis lifecycle endpoints: image intake and report retrieval."""

import uuid
from typing import Optional
from fastapi import APIRouter, File, UploadFile, status
from app.core.config import settings
from app.core.errors import ImageValidationError, AnalysisNotFoundError
from app.schemas.analysis import AnalysisCreateResponse, AnalysisResponse
from app.schemas.common import VerificationState
from app.schemas.product import (
    ProductReport,
    SafetyProfile,
    IngredientReport,
    StrengthSchema,
    EvidenceSourceSchema,
)
from app.schemas.common import RoleType
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
    # Demonstrative fixture is returned for 'demo-scan'; others raise 404 until OCR/worker pipeline
    if analysis_id != "demo-scan":
        raise AnalysisNotFoundError(analysis_id=analysis_id)

    pubchem_source = EvidenceSourceSchema(
        name="National Library of Medicine / PubChem",
        url="https://pubchem.ncbi.nlm.nih.gov/compound/1983",
        source_id="1983",
        jurisdiction="GLOBAL",
    )
    openfda_source = EvidenceSourceSchema(
        name="openFDA Drug Product Labels",
        url="https://open.fda.gov/apis/drug/label/",
        source_id="openfda-paracetamol",
        jurisdiction="US",
    )

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
            id="dolo-650",
            detected_name="Dolo 650",
            dosage_form="Tablet",
            manufacturer="Micro Labs Ltd",
            is_verified=True,
        ),
        active_ingredients=[
            IngredientReport(
                canonical_name="Paracetamol (Acetaminophen)",
                raw_label_text="Paracetamol IP 650 mg",
                strength=StrengthSchema(
                    raw_text="650 mg",
                    numeric_value=650.0,
                    unit="mg",
                    basis="per tablet",
                ),
                role=RoleType.ACTIVE,
                confidence=0.98,
                explanation="An analgesic and antipyretic agent that reduces pain signals in the nervous system and lowers body temperature by central prostaglandin inhibition.",
                therapeutic_purpose="Symptomatic relief of mild-to-moderate pain and reduction of fever.",
                evidence_sources=[pubchem_source, openfda_source],
            )
        ],
        inactive_ingredients=[
            IngredientReport(
                canonical_name="Maize Starch",
                raw_label_text="Maize Starch q.s.",
                strength=StrengthSchema(raw_text="q.s.", unit="q.s."),
                role=RoleType.INACTIVE,
                confidence=0.95,
                explanation="Binder and disintegrant helping the tablet maintain cohesion and disintegrate in the gastric tract.",
                therapeutic_purpose="Tablet binding agent; non-therapeutic.",
                evidence_sources=[],
            ),
            IngredientReport(
                canonical_name="Povidone K30",
                raw_label_text="Povidone K30 q.s.",
                strength=StrengthSchema(raw_text="q.s.", unit="q.s."),
                role=RoleType.INACTIVE,
                confidence=0.92,
                explanation="Polymer vehicle used as a granulating binder.",
                therapeutic_purpose="Tablet cohesion; non-therapeutic.",
                evidence_sources=[],
            ),
            IngredientReport(
                canonical_name="Magnesium Stearate",
                raw_label_text="Magnesium Stearate q.s.",
                strength=StrengthSchema(raw_text="q.s.", unit="q.s."),
                role=RoleType.INACTIVE,
                confidence=0.96,
                explanation="Lubricant preventing powder adherence to die punches during mechanical compression.",
                therapeutic_purpose="Manufacturing lubricant; non-therapeutic.",
                evidence_sources=[],
            ),
        ],
        safety_profile=SafetyProfile(
            purpose_summary="Symptomatic relief of fever and mild-to-moderate pain. Not a substitute for ongoing medical evaluation.",
            precautions=[
                "Do not exceed maximum daily dose of 4000mg to avoid liver injury.",
                "Avoid concurrent alcohol intake as it potentiates hepatotoxicity risk.",
                "Consult a physician if febrile symptoms persist beyond 3 days.",
            ],
            contraindications=[
                "Known hypersensitivity to paracetamol.",
                "Severe hepatic impairment or active liver disease.",
            ],
            adverse_effects=["Nausea", "Allergic skin rash", "Hepatotoxicity (in overdose)"],
        ),
        uncertainties=[],
        audit_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        sources=[pubchem_source, openfda_source],
    )
