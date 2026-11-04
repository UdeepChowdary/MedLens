"""Schemas for personalized health analysis and Bring-Your-Own-Key (BYOK) Gemini intelligence."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AllergyMatch(BaseModel):
    """Specific allergy risk evaluation."""
    allergen: str
    severity: str = Field(..., description="none | low | moderate | high")
    reaction_type: str = Field(..., description="e.g. IgE-mediated, cross-reactive class, direct match, excipient")
    explanation: str


class ConditionMatch(BaseModel):
    """Specific condition / chronic disease compatibility evaluation."""
    condition: str
    compatibility: str = Field(..., description="beneficial | compatible | caution | contraindicated")
    clinical_note: str


class PersonalizeRequest(BaseModel):
    """Input payload for personalizing a medicine analysis."""
    analysis_id: Optional[str] = None
    product_name: Optional[str] = None
    active_ingredients: List[str] = Field(default_factory=list)
    dosages: List[str] = Field(default_factory=list)
    manufacturer: Optional[str] = None
    user_allergies: List[str] = Field(default_factory=list)
    user_conditions: List[str] = Field(default_factory=list)
    gemini_api_key: Optional[str] = Field(None, description="Optional user-provided Gemini API key (BYOK)")


class PersonalizeResponse(BaseModel):
    """Structured clinical personalization output."""
    analysis_id: Optional[str] = None
    is_ai_enhanced: bool = Field(False, description="True if generated via Gemini AI; False if rule-based monograph match")
    model_name: Optional[str] = None
    overall_safety_rating: str = Field(..., description="safe | caution | high_risk | contraindicated")
    executive_summary: str
    allergy_matches: List[AllergyMatch] = Field(default_factory=list)
    condition_matches: List[ConditionMatch] = Field(default_factory=list)
    personalized_precautions: List[str] = Field(default_factory=list)
    tailored_dosage_advice: Optional[str] = None
    questions_for_doctor: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "MedLens Personalized Intelligence provides informational analysis only and does not substitute "
        "for professional medical diagnosis, advice, or prescription from a licensed healthcare provider."
    )


class VerifyKeyRequest(BaseModel):
    """Payload to test and validate a user-supplied Gemini API key."""
    gemini_api_key: str


class VerifyKeyResponse(BaseModel):
    """Result of Gemini API key validation."""
    valid: bool
    message: str
    model_tested: Optional[str] = None
