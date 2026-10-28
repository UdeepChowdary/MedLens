"""Tests for multidimensional confidence scoring engine."""

from app.services.scoring.confidence import (
    ScoringInput,
    compute_confidence,
    determine_verification_state,
)
from app.schemas.common import VerificationState


def test_perfect_scan_confidence():
    inp = ScoringInput(
        ocr_word_count=50,
        ocr_low_confidence_tokens=1,
        ocr_engine_reported_score=0.98,
        image_quality_flag=True,
        ingredients_detected=1,
        ingredients_with_strength=1,
        composition_header_found=True,
        identity_match_method="exact_alias",
        identity_match_score=1.0,
        total_claims=4,
        claims_with_source=4,
    )
    conf = compute_confidence(inp)
    assert conf.ocr_quality >= 0.90
    assert conf.extraction_quality >= 0.90
    assert conf.identity_confidence >= 0.95
    assert conf.evidence_coverage == 1.0

    state = determine_verification_state(conf)
    assert state == VerificationState.VERIFIED


def test_blurry_image_penalizes_ocr():
    inp = ScoringInput(
        ocr_engine_reported_score=0.95,
        image_quality_flag=False,  # Blurry!
    )
    conf = compute_confidence(inp)
    assert conf.ocr_quality < 0.50


def test_unverified_when_no_identity_match():
    inp = ScoringInput(
        ocr_engine_reported_score=0.99,
        image_quality_flag=True,
        ingredients_detected=1,
        ingredients_with_strength=1,
        identity_match_method="none",
        identity_match_score=0.0,
    )
    conf = compute_confidence(inp)
    assert conf.identity_confidence == 0.0

    state = determine_verification_state(conf)
    assert state == VerificationState.UNABLE_TO_VERIFY


def test_confidence_values_bounded():
    # Extreme input values
    inp = ScoringInput(
        ocr_word_count=100,
        ocr_low_confidence_tokens=200,  # aberrant
        ocr_engine_reported_score=1.5,   # aberrant
        identity_match_score=2.0,
        total_claims=1,
        claims_with_source=10,
    )
    conf = compute_confidence(inp)
    assert 0.0 <= conf.ocr_quality <= 1.0
    assert 0.0 <= conf.extraction_quality <= 1.0
    assert 0.0 <= conf.identity_confidence <= 1.0
    assert 0.0 <= conf.evidence_coverage <= 1.0


def test_multidimensional_fields_are_distinct():
    inp = ScoringInput(
        ocr_word_count=20,
        ocr_engine_reported_score=0.70,
        image_quality_flag=True,
        ingredients_detected=2,
        ingredients_with_strength=1,
        identity_match_method="fuzzy_high",
        identity_match_score=0.90,
        total_claims=5,
        claims_with_source=2,
    )
    conf = compute_confidence(inp)
    # Assert dimensions are independent, not collapsed to a single average
    assert conf.ocr_quality != conf.extraction_quality

