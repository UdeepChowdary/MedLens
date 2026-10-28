"""Tests for INN normalization pipeline."""

import pytest
from app.services.normalization.inn_normalizer import INNNormalizer
from app.schemas.common import VerificationState


@pytest.fixture
def normalizer():
    # Curated alias map for isolated testing
    alias_map = {
        "paracetamol": ("Paracetamol", "ing-paracetamol"),
        "paracetamol ip": ("Paracetamol", "ing-paracetamol"),
        "acetaminophen": ("Paracetamol", "ing-paracetamol"),
        "apap": ("Paracetamol", "ing-paracetamol"),
        "ibuprofen": ("Ibuprofen", "ing-ibuprofen"),
        "ibuprofen ip": ("Ibuprofen", "ing-ibuprofen"),
        "amoxicillin": ("Amoxicillin", "ing-amoxicillin"),
        "amoxicillin trihydrate": ("Amoxicillin", "ing-amoxicillin"),
        "amoxycillin": ("Amoxicillin", "ing-amoxicillin"),
        "cetirizine": ("Cetirizine", "ing-cetirizine"),
        "cetirizine hydrochloride": ("Cetirizine", "ing-cetirizine"),
        "metformin": ("Metformin", "ing-metformin"),
        "metformin hydrochloride": ("Metformin", "ing-metformin"),
    }
    return INNNormalizer(alias_map)


def test_exact_alias_lookup(normalizer):
    res = normalizer.normalize("paracetamol ip")
    assert res.canonical_name == "Paracetamol"
    assert res.verification_state == VerificationState.VERIFIED
    assert res.match_method == "exact_alias"
    assert res.match_score == 1.0


def test_case_insensitivity(normalizer):
    res = normalizer.normalize("PARACETAMOL IP")
    assert res.canonical_name == "Paracetamol"
    assert res.verification_state == VerificationState.VERIFIED


def test_pharmacopeial_suffix_handling(normalizer):
    # 'Amoxicillin IP' has suffix IP; normalizer handles it
    res = normalizer.normalize("Amoxicillin IP")
    assert res.canonical_name == "Amoxicillin"
    assert res.verification_state == VerificationState.VERIFIED


def test_typo_variant_mapping(normalizer):
    res = normalizer.normalize("Amoxycillin")
    assert res.canonical_name == "Amoxicillin"
    assert res.verification_state == VerificationState.VERIFIED


def test_salt_form_preservation(normalizer):
    res = normalizer.normalize("Cetirizine Hydrochloride")
    assert res.canonical_name == "Cetirizine"
    assert res.verification_state == VerificationState.VERIFIED
    assert res.salt_form_preserved is not None
    assert "hydrochloride" in res.salt_form_preserved.lower()


def test_unknown_ingredient_abstains(normalizer):
    res = normalizer.normalize("Xylophenamine")
    assert res.verification_state == VerificationState.UNABLE_TO_VERIFY
    assert res.canonical_name is None
    assert res.abstention_reason is not None


def test_empty_string_handling(normalizer):
    res = normalizer.normalize("")
    assert res.verification_state == VerificationState.UNABLE_TO_VERIFY
    assert res.canonical_name is None

