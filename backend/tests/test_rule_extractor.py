"""Tests for deterministic rule-based ingredient extractor."""

from app.services.extraction.rule_baseline import RuleBasedExtractor
from app.schemas.common import VerificationState


def test_standard_composition_extraction():
    extractor = RuleBasedExtractor()
    text = "Each film-coated tablet contains: Paracetamol IP 500 mg"
    res = extractor.extract(text)

    assert res.verification_status == VerificationState.VERIFIED
    assert res.composition_header_found is True
    assert res.dosage_form == "Film-coated Tablet"
    assert len(res.ingredients) == 1
    assert res.ingredients[0]["canonical_name"] == "Paracetamol"
    assert res.ingredients[0]["strength"]["numeric_value"] == 500.0
    assert res.ingredients[0]["strength"]["unit"] == "mg"


def test_multi_ingredient_extraction():
    extractor = RuleBasedExtractor()
    text = "Each uncoated tablet contains: Ibuprofen 400 mg Paracetamol 325 mg"
    res = extractor.extract(text)

    assert len(res.ingredients) == 2
    names = {ing["canonical_name"] for ing in res.ingredients}
    assert "Ibuprofen" in names
    assert "Paracetamol" in names


def test_no_composition_header_yields_partially_verified():
    extractor = RuleBasedExtractor()
    text = "Paracetamol 500 mg"
    res = extractor.extract(text)

    assert res.verification_status == VerificationState.PARTIALLY_VERIFIED
    assert res.composition_header_found is False
    assert len(res.ingredients) == 1


def test_unrecognized_ingredient_needs_confirmation():
    extractor = RuleBasedExtractor()
    text = "Each tablet contains: UnknownChemical 10 mg"
    res = extractor.extract(text)

    assert res.verification_status == VerificationState.NEEDS_CONFIRMATION
    assert len(res.ingredients) == 0
    assert res.abstention_reason is not None


def test_empty_text_abstains():
    extractor = RuleBasedExtractor()
    res = extractor.extract("")

    assert res.verification_status == VerificationState.UNABLE_TO_VERIFY
    assert res.abstention_reason is not None

