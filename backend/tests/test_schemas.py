"""Tests for Pydantic v2 data contracts and validation constraints."""

import pytest
from pydantic import ValidationError
from app.schemas.common import VerificationState, ComparisonOutcome
from app.schemas.product import StrengthSchema, ProductReport
from app.schemas.analysis import MultidimensionalConfidence
from app.schemas.comparison import ComparisonResponse, AttributeComparison


def test_strength_schema_valid() -> None:
    """Verifies that well-formed strengths pass validation."""
    strength = StrengthSchema(
        raw_text="650 mg per tablet",
        numeric_value=650.0,
        unit="mg",
        basis="per tablet",
    )
    assert strength.numeric_value == 650.0
    assert strength.unit == "mg"
    assert strength.basis == "per tablet"


def test_strength_schema_rejects_negative_value() -> None:
    """Verifies that non-positive dosage strength raises ValidationError."""
    with pytest.raises(ValidationError):
        StrengthSchema(
            raw_text="-500 mg",
            numeric_value=-500.0,
            unit="mg",
        )


def test_multidimensional_confidence_bounds() -> None:
    """Verifies that all confidence dimensions are clamped within [0.0, 1.0]."""
    conf = MultidimensionalConfidence(
        ocr_quality=0.95,
        extraction_quality=0.88,
        identity_confidence=0.99,
        evidence_coverage=0.90,
    )
    assert conf.ocr_quality == 0.95

    with pytest.raises(ValidationError):
        MultidimensionalConfidence(
            ocr_quality=1.2,  # Invalid: > 1.0
            extraction_quality=0.88,
            identity_confidence=0.99,
            evidence_coverage=0.90,
        )


def test_verification_states_conformance() -> None:
    """Verifies the four explicit states defined in Blueprint Section 07."""
    allowed_states = {
        VerificationState.VERIFIED,
        VerificationState.PARTIALLY_VERIFIED,
        VerificationState.NEEDS_CONFIRMATION,
        VerificationState.UNABLE_TO_VERIFY,
    }
    assert len(allowed_states) == 4
    assert VerificationState.VERIFIED.value == "verified"
    assert VerificationState.NEEDS_CONFIRMATION.value == "needs_confirmation"


def test_attribute_comparison_conformance() -> None:
    """Verifies deterministic comparison outcome enumeration."""
    attr = AttributeComparison(
        field="active_ingredients",
        result=ComparisonOutcome.MATCH,
        evidence=["PubChem:1983"],
    )
    assert attr.result == ComparisonOutcome.MATCH
    assert attr.result.value == "match"
