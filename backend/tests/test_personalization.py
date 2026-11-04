"""Unit tests for personalized analysis service and BYOK Gemini API integration."""

import pytest
from app.schemas.personalization import PersonalizeRequest, VerifyKeyRequest
from app.services.personalization_service import PersonalizationService


def test_rule_based_personalization_allergy_conflict():
    """Confirms rule-based matching flags a direct allergy conflict."""
    service = PersonalizationService()
    req = PersonalizeRequest(
        product_name="Pan 40",
        active_ingredients=["Pantoprazole"],
        dosages=["40 mg"],
        user_allergies=["Pantoprazole", "Penicillin"],
        user_conditions=["GERD"],
    )
    result = service.personalize(req)
    assert result.is_ai_enhanced is False
    assert result.overall_safety_rating == "contraindicated"
    assert len(result.allergy_matches) == 2
    pan_match = next(m for m in result.allergy_matches if m.allergen == "Pantoprazole")
    assert pan_match.severity == "high"
    assert "ALERT" in pan_match.explanation


def test_rule_based_personalization_beneficial_condition():
    """Confirms rule-based matching identifies beneficial indication for GERD."""
    service = PersonalizationService()
    req = PersonalizeRequest(
        product_name="Pan 40",
        active_ingredients=["Pantoprazole"],
        dosages=["40 mg"],
        user_allergies=["Sulfa"],
        user_conditions=["GERD", "Hypertension"],
    )
    result = service.personalize(req)
    assert result.overall_safety_rating == "safe"
    gerd_match = next(m for m in result.condition_matches if m.condition == "GERD")
    assert gerd_match.compatibility == "beneficial"
    assert "Therapeutically indicated" in gerd_match.clinical_note


def test_rule_based_personalization_condition_caution():
    """Confirms rule-based matching raises caution for renal or osteoporosis conditions with PPI."""
    service = PersonalizationService()
    req = PersonalizeRequest(
        product_name="Pan 40",
        active_ingredients=["Pantoprazole"],
        dosages=["40 mg"],
        user_allergies=[],
        user_conditions=["Chronic Kidney Disease", "Osteoporosis"],
    )
    result = service.personalize(req)
    assert result.overall_safety_rating == "caution"
    assert any(m.compatibility == "caution" for m in result.condition_matches)


def test_verify_gemini_key_empty():
    """Empty key immediately returns valid=False."""
    service = PersonalizationService()
    res = service.verify_gemini_key("")
    assert res.valid is False
    assert "empty" in res.message


def test_verify_gemini_key_invalid():
    """Invalid dummy key returns clean user-facing failure message."""
    service = PersonalizationService()
    res = service.verify_gemini_key("invalid_dummy_gemini_key_12345")
    assert res.valid is False
    assert "Invalid Gemini API key" in res.message or "Could not verify" in res.message
