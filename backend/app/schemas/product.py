"""Schemas for normalized products, ingredients, safety profiles, and sources."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from .common import RoleType


class StrengthSchema(BaseModel):
    """Normalized dosage strength with numeric value, unit, and administration basis."""
    raw_text: str = Field(description="Verbatim strength string from the packaging.")
    numeric_value: Optional[float] = Field(default=None, description="Numeric magnitude, e.g. 500.0 or 0.05.")
    unit: str = Field(description="Unit of measurement, e.g. mg, g, mcg, ml, % w/v, q.s.")
    basis: Optional[str] = Field(default=None, description="Dose basis, e.g. 'per tablet', 'per 5 mL'.")

    @field_validator("numeric_value")
    @classmethod
    def validate_positive_numeric(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Strength numeric value must be strictly positive.")
        return v


class EvidenceSourceSchema(BaseModel):
    """Authoritative monograph evidence source citation."""
    name: str = Field(description="Provider name, e.g. 'National Library of Medicine / PubChem', 'openFDA'.")
    url: str = Field(description="Canonical URL to primary clinical monograph.")
    source_id: Optional[str] = Field(default=None, description="Identifier within provider namespace.")
    jurisdiction: Optional[str] = Field(default=None, description="Jurisdiction context, e.g. 'US', 'IN', 'WHO'.")
    retrieval_date: Optional[str] = Field(default=None, description="ISO-8601 retrieval timestamp.")


class IngredientReport(BaseModel):
    """Composition item breakdown presented in patient-facing and clinical reports."""
    canonical_name: str = Field(description="Normalized International Nonproprietary Name (INN).")
    raw_label_text: str = Field(description="Verbatim packaging string.")
    strength: StrengthSchema = Field(description="Parsed and validated strength tuple.")
    role: RoleType = Field(default=RoleType.ACTIVE, description="Active pharmaceutical agent vs excipient.")
    confidence: float = Field(ge=0.0, le=1.0, description="Normalized match confidence.")
    explanation: str = Field(description="Plain-language accessible explanation of physiological action.")
    therapeutic_purpose: str = Field(description="Specific medical rationale for inclusion in this medicine.")
    evidence_sources: List[EvidenceSourceSchema] = Field(default_factory=list, description="Traceable citations.")


class SafetyProfile(BaseModel):
    """Clinical safety indicators and contraindication warnings."""
    purpose_summary: str = Field(description="Summary of primary approved therapeutic uses.")
    precautions: List[str] = Field(default_factory=list, description="Usage guidelines, maximum daily intake, dietary notes.")
    contraindications: List[str] = Field(default_factory=list, description="Conditions under which medicine must not be used.")
    adverse_effects: List[str] = Field(default_factory=list, description="Common and serious documented side effects.")


class ProductReport(BaseModel):
    """Top-level identification of the scanned commercial product."""
    id: Optional[str] = Field(default=None, description="Unique product identifier if catalog matched.")
    detected_name: str = Field(description="Identified brand or generic product name.")
    dosage_form: str = Field(description="Physical presentation, e.g. Tablet, Capsule, Syrup.")
    manufacturer: Optional[str] = Field(default=None, description="Manufacturing pharmaceutical company.")
    is_verified: bool = Field(default=False, description="Whether product matches verified catalog.")
