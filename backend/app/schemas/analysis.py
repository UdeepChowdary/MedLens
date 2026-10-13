"""Schemas for image analysis jobs, multidimensional confidence, and final reports."""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field
from .common import VerificationState
from .product import ProductReport, IngredientReport, SafetyProfile, EvidenceSourceSchema


class MultidimensionalConfidence(BaseModel):
    """Discrete, un-averaged confidence dimensions per Blueprint Section 08.4."""
    ocr_quality: float = Field(ge=0.0, le=1.0, description="Transcription reliability from OCR engine.")
    extraction_quality: float = Field(ge=0.0, le=1.0, description="Span detection and entity parsing calibration.")
    identity_confidence: float = Field(ge=0.0, le=1.0, description="Support for canonical INN match.")
    evidence_coverage: float = Field(ge=0.0, le=1.0, description="Ratio of claims grounded in consulted sources.")


class AnalysisCreateResponse(BaseModel):
    """Initial response returned upon image ingestion."""
    analysis_id: str = Field(description="Unique UUID tracking this analysis.")
    status: str = Field(default="received", description="Initial job lifecycle state.")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 creation timestamp."
    )


class AnalysisResponse(BaseModel):
    """Complete structured verification report."""
    analysis_id: str = Field(description="Unique UUID identifier.")
    status: VerificationState = Field(description="Explicit four-state verification result.")
    processing_time_ms: int = Field(ge=0, description="Total pipeline execution duration in milliseconds.")
    confidence: MultidimensionalConfidence = Field(description="Multidimensional confidence ratings.")
    product: ProductReport = Field(description="Top-level product identification.")
    active_ingredients: List[IngredientReport] = Field(default_factory=list, description="Active therapeutic agents.")
    inactive_ingredients: List[IngredientReport] = Field(default_factory=list, description="Inactive excipients and binders.")
    safety_profile: SafetyProfile = Field(description="Verified safety and contraindication indicators.")
    uncertainties: List[str] = Field(default_factory=list, description="Explicitly noted gaps, conflicts, or unread tokens.")
    audit_hash: str = Field(description="SHA-256 fingerprint of the image and pipeline execution.")
    sources: List[EvidenceSourceSchema] = Field(default_factory=list, description="All evidence sources consulted.")
    limitations: List[str] = Field(
        default_factory=lambda: [
            "MedLens provides informational packaging analysis only.",
            "This report is not a medical diagnosis, clinical advice, or prescription.",
            "Always consult a licensed physician or pharmacist for medical decisions."
        ],
        description="Mandatory legal and clinical scope limitations."
    )
