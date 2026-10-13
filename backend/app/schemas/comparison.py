"""Schemas for deterministic brand and composition comparison."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from .common import ComparisonOutcome


class StrengthDelta(BaseModel):
    """Magnitude and clinical advisory of strength discrepancy."""
    difference_detected: bool = Field(description="True if numeric strengths differ.")
    numeric_delta: Optional[float] = Field(default=None, description="Difference in primary active strength (A - B).")
    unit: Optional[str] = Field(default=None, description="Unit of measurement.")
    warning: Optional[str] = Field(default=None, description="Clinical advisory regarding dosage frequency implications.")


class AttributeComparison(BaseModel):
    """Per-field comparison outcome per Blueprint Section 09."""
    field: str = Field(description="Attribute compared, e.g. 'active_ingredients', 'strength', 'release_type'.")
    result: ComparisonOutcome = Field(description="Deterministic result: match, difference, unknown, conflict.")
    evidence: List[str] = Field(default_factory=list, description="Identifiers of sources supporting the evaluation.")
    reason: Optional[str] = Field(default=None, description="Explanation when result is unknown or in conflict.")


class ComparisonResponse(BaseModel):
    """Structured dual-product comparison result."""
    comparison_status: str = Field(description="Overall comparability status, e.g. 'comparable', 'partially_comparable'.")
    medicine_a: Dict[str, Any] = Field(description="Identification and status of Medicine A.")
    medicine_b: Dict[str, Any] = Field(description="Identification and status of Medicine B.")
    attributes: List[AttributeComparison] = Field(description="Per-field attribute comparison outcomes.")
    strength_delta: Optional[StrengthDelta] = Field(default=None, description="Strength difference analysis.")
    excipient_differences: List[str] = Field(default_factory=list, description="Inactive binder and preservative variances.")
    therapeutic_equivalence: Dict[str, str] = Field(
        default_factory=lambda: {"status": "not_established", "note": "Requires product-specific regulatory bioequivalence filing."},
        description="Equivalence status; never declared equivalent without explicit regulatory proof."
    )
    limitations: List[str] = Field(default_factory=list, description="Limitations of comparison coverage.")
    sources: List[str] = Field(default_factory=list, description="Source identifiers utilized.")
