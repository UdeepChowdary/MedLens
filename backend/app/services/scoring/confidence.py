"""Multidimensional confidence scoring engine per Blueprint Section 08.4."""

from dataclasses import dataclass
from typing import List, Optional
from app.schemas.analysis import MultidimensionalConfidence
from app.schemas.common import VerificationState


@dataclass
class ScoringInput:
    """Input signals for confidence computation."""
    # OCR signals
    ocr_word_count: int = 0
    ocr_low_confidence_tokens: int = 0  # tokens with engine confidence < 0.7
    ocr_engine_reported_score: float = 1.0
    image_quality_flag: bool = True  # True = OK, False = blurry/poor
    
    # Extraction signals
    ingredients_detected: int = 0
    ingredients_with_strength: int = 0
    composition_header_found: bool = False
    
    # Identity signals  
    identity_match_method: str = "none"  # exact_alias, exact_raw, fuzzy_high, fuzzy_medium, none
    identity_match_score: float = 0.0
    
    # Evidence signals
    total_claims: int = 0
    claims_with_source: int = 0


# Weights per Blueprint Section 08.4 formula
W_OCR = 0.30
W_MATCH = 0.40
W_SOURCE = 0.30

# Thresholds
THRESHOLD_VERIFIED = 0.90
THRESHOLD_PARTIALLY_VERIFIED = 0.70


def compute_ocr_quality(inp: ScoringInput) -> float:
    """OCR quality dimension: transcription fidelity."""
    score = inp.ocr_engine_reported_score
    
    if not inp.image_quality_flag:
        score *= 0.5  # Severe penalty for blurry/poor images
    
    if inp.ocr_word_count > 0:
        low_conf_ratio = inp.ocr_low_confidence_tokens / inp.ocr_word_count
        score *= (1.0 - low_conf_ratio * 0.5)
    
    return max(0.0, min(1.0, score))


def compute_extraction_quality(inp: ScoringInput) -> float:
    """Extraction quality: how well entities were detected."""
    if inp.ingredients_detected == 0:
        return 0.0
    
    strength_ratio = (
        inp.ingredients_with_strength / inp.ingredients_detected
        if inp.ingredients_detected > 0 else 0.0
    )
    header_bonus = 0.05 if inp.composition_header_found else 0.0
    score = (strength_ratio * 0.90) + header_bonus
    return max(0.0, min(1.0, score))


def compute_identity_confidence(inp: ScoringInput) -> float:
    """Identity confidence: support for the canonical INN match."""
    method_scores = {
        "exact_alias": 0.99,
        "exact_raw": 0.97,
        "fuzzy_high": 0.85,
        "fuzzy_medium": 0.72,
        "fuzzy_no_match": 0.30,
        "fuzzy_low": 0.25,
        "none": 0.0,
    }
    base = method_scores.get(inp.identity_match_method, 0.0)
    # Blend with the raw score for fuzzy methods
    if inp.identity_match_method.startswith("fuzzy"):
        return max(0.0, min(1.0, (base + inp.identity_match_score) / 2.0))
    return base


def compute_evidence_coverage(inp: ScoringInput) -> float:
    """Evidence coverage: fraction of claims backed by a source."""
    if inp.total_claims == 0:
        return 0.50  # Neutral: no claims to verify yet
    ratio = inp.claims_with_source / inp.total_claims
    return max(0.0, min(1.0, ratio))


def compute_confidence(inp: ScoringInput) -> MultidimensionalConfidence:
    """Computes all four confidence dimensions. Never averages into a single score."""
    return MultidimensionalConfidence(
        ocr_quality=round(compute_ocr_quality(inp), 3),
        extraction_quality=round(compute_extraction_quality(inp), 3),
        identity_confidence=round(compute_identity_confidence(inp), 3),
        evidence_coverage=round(compute_evidence_coverage(inp), 3),
    )


def determine_verification_state(conf: MultidimensionalConfidence) -> VerificationState:
    """
    Maps multidimensional confidence to an explicit 4-state verification result.
    Per blueprint: high OCR quality must never compensate for an unsupported identity.
    """
    weighted = (
        W_OCR * conf.ocr_quality
        + W_MATCH * conf.identity_confidence
        + W_SOURCE * conf.evidence_coverage
    )
    
    # Identity confidence is the critical gate
    if conf.identity_confidence < 0.50:
        return VerificationState.UNABLE_TO_VERIFY
    
    if weighted >= THRESHOLD_VERIFIED and conf.extraction_quality >= 0.80:
        return VerificationState.VERIFIED
    elif weighted >= THRESHOLD_PARTIALLY_VERIFIED:
        return VerificationState.PARTIALLY_VERIFIED
    elif conf.identity_confidence >= 0.70:
        return VerificationState.NEEDS_CONFIRMATION
    else:
        return VerificationState.UNABLE_TO_VERIFY

