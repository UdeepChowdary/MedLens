"""Tests for Phase 4 rule-based extraction, BIO preprocessing, alignment, and evaluation."""

import json
from pathlib import Path
import pytest

from app.schemas.common import VerificationState
from app.services.extraction import (
    RuleBasedExtractor,
    ExtractionEvaluator,
    ClinicalTuple,
)
from tools.prepare_bio_dataset import (
    BIO_TAGS,
    CANONICAL_ENTITIES,
    LABEL2ID,
    ID2LABEL,
    tokenize_with_offsets,
    validate_alignment,
    convert_doc_to_bio,
)


@pytest.fixture
def extractor():
    return RuleBasedExtractor()


# ============================================================================
# 1. Rule-Based Extractor Tests
# ============================================================================

def test_extractor_single_ingredient(extractor):
    text = "Paracetamol Tablets IP 500 mg"
    res = extractor.extract(text)

    assert len(res.ingredients) == 1
    assert res.ingredients[0]["canonical_name"] == "Paracetamol"
    assert res.ingredients[0]["strength"]["numeric_value"] == 500.0
    assert res.ingredients[0]["strength"]["unit"] == "mg"
    assert res.dosage_form == "Tablet"
    assert res.verification_status == VerificationState.PARTIALLY_VERIFIED


def test_extractor_composition_header_and_basis(extractor):
    text = "Each uncoated tablet contains: Paracetamol IP 650 mg. Excipients q.s."
    res = extractor.extract(text)

    assert res.composition_header_found is True
    assert res.strength_basis == "per tablet"
    assert len(res.ingredients) == 1
    assert res.ingredients[0]["canonical_name"] == "Paracetamol"
    assert res.ingredients[0]["strength"]["numeric_value"] == 650.0
    assert res.ingredients[0]["strength"]["basis"] == "per tablet"
    assert res.verification_status == VerificationState.VERIFIED


def test_extractor_multi_ingredient_combination(extractor):
    text = (
        "Each film-coated tablet contains: Amoxicillin Trihydrate IP eq. to "
        "Amoxicillin 500 mg, Potassium Clavulanate IP eq. to Clavulanic Acid 125 mg."
    )
    res = extractor.extract(text)

    assert res.composition_header_found is True
    assert len(res.ingredients) == 2

    # Verify both active ingredients are identified with correct strengths
    names = [ing["canonical_name"] for ing in res.ingredients]
    assert "Amoxicillin" in names
    assert "Clavulanic Acid" in names

    amox = next(ing for ing in res.ingredients if ing["canonical_name"] == "Amoxicillin")
    clav = next(ing for ing in res.ingredients if ing["canonical_name"] == "Clavulanic Acid")

    assert amox["strength"]["numeric_value"] == 500.0
    assert clav["strength"]["numeric_value"] == 125.0
    assert res.verification_status == VerificationState.VERIFIED


def test_extractor_alias_mapping(extractor):
    text = "Acetaminophen 500 mg oral tablet"
    res = extractor.extract(text)

    assert len(res.ingredients) == 1
    assert res.ingredients[0]["canonical_name"] == "Paracetamol"
    assert res.ingredients[0]["raw_ingredient"].lower() == "acetaminophen"


def test_extractor_abstention_on_empty_text(extractor):
    res = extractor.extract("")
    assert res.verification_status == VerificationState.UNABLE_TO_VERIFY
    assert res.abstention_reason is not None


def test_extractor_abstention_on_unrecognized_ingredient(extractor):
    text = "Herbal wellness blend 500 mg per capsule"
    res = extractor.extract(text)

    assert res.verification_status == VerificationState.NEEDS_CONFIRMATION
    assert len(res.ingredients) == 0
    assert "No recognized active pharmaceutical ingredient" in res.abstention_reason


def test_extractor_missing_strength_triggers_confirmation(extractor):
    text = "Paracetamol Tablets IP without strength statement"
    res = extractor.extract(text)

    assert len(res.ingredients) == 1
    assert res.ingredients[0]["strength"] is None
    assert res.verification_status == VerificationState.NEEDS_CONFIRMATION


# ============================================================================
# 2. BIO Preprocessing and Token Alignment Tests
# ============================================================================

def test_bio_schema_completeness():
    assert len(CANONICAL_ENTITIES) == 11
    assert len(BIO_TAGS) == 23
    assert BIO_TAGS[0] == "O"

    for entity in CANONICAL_ENTITIES:
        b_tag = f"B-{entity}"
        i_tag = f"I-{entity}"
        assert b_tag in BIO_TAGS
        assert i_tag in BIO_TAGS
        assert ID2LABEL[LABEL2ID[b_tag]] == b_tag
        assert ID2LABEL[LABEL2ID[i_tag]] == i_tag


def test_tokenize_with_offsets():
    text = "Dolo 650. Each tablet contains: Paracetamol 650 mg."
    tokens = tokenize_with_offsets(text)

    assert len(tokens) > 0
    # Every token slice matches original text
    for tok, start, end in tokens:
        assert text[start:end] == tok


def test_alignment_validator_detects_mid_token_clip():
    text = "Paracetamol 500 mg"
    tokens = tokenize_with_offsets(text)
    # Clip start at char 2 ('racatamol') inside 'Paracetamol' [0, 11]
    invalid_entities = [
        {"label": "INGREDIENT", "raw_text": "racatamol", "char_span": [2, 11]}
    ]
    warnings = validate_alignment(text, tokens, invalid_entities)

    assert len(warnings) > 0
    warning_types = [w["type"] for w in warnings]
    assert "mid_token_clip_start" in warning_types or "text_mismatch" in warning_types


def test_alignment_validator_detects_slice_mismatch():
    text = "Paracetamol 500 mg"
    tokens = tokenize_with_offsets(text)
    invalid_entities = [
        {"label": "INGREDIENT", "raw_text": "Ibuprofen", "char_span": [0, 11]}
    ]
    warnings = validate_alignment(text, tokens, invalid_entities)

    assert any(w["type"] == "text_mismatch" for w in warnings)


def test_convert_doc_to_bio_priority_resolution():
    doc = {
        "transcription": "Paracetamol Tablets IP 500 mg",
        "image_metadata": {"image_id": "test-doc", "product_family": "paracetamol-generic"},
        "review_status": "verified_by_human",
        "entities": [
            # Coarse span overlapping fine-grained entities
            {"label": "PRODUCT_NAME", "raw_text": "Paracetamol Tablets IP 500 mg", "char_span": [0, 29]},
            {"label": "INGREDIENT", "raw_text": "Paracetamol", "char_span": [0, 11]},
            {"label": "DOSAGE_FORM", "raw_text": "Tablets", "char_span": [12, 19]},
            {"label": "SALT_FORM", "raw_text": "IP", "char_span": [20, 22]},
            {"label": "STRENGTH", "raw_text": "500 mg", "char_span": [23, 29]},
        ],
    }
    bio_res = convert_doc_to_bio(doc)

    assert bio_res["id"] == "test-doc"
    assert len(bio_res["alignment_warnings"]) == 0
    # Fine-grained INGREDIENT should win over PRODUCT_NAME
    assert bio_res["ner_labels"][0] == "B-INGREDIENT"
    assert bio_res["ner_labels"][1] == "B-DOSAGE_FORM"
    assert bio_res["ner_labels"][2] == "B-SALT_FORM"
    assert bio_res["ner_labels"][3] == "B-STRENGTH"
    assert bio_res["ner_labels"][4] == "I-STRENGTH"


# ============================================================================
# 3. Evaluation Metrics Harness Tests
# ============================================================================

def test_evaluator_strict_entity_metrics():
    gt = [[
        {"label": "INGREDIENT", "char_span": [0, 11]},
        {"label": "STRENGTH", "char_span": [12, 18]},
    ]]
    pred = [[
        {"label": "INGREDIENT", "char_span": [0, 11]},  # TP
        {"label": "STRENGTH", "char_span": [12, 19]},    # FP (off by 1 end) + FN
    ]]

    metrics, overall = ExtractionEvaluator.evaluate_entities(gt, pred)

    ing_metric = metrics["INGREDIENT"]
    assert ing_metric.true_positives == 1
    assert ing_metric.false_positives == 0
    assert ing_metric.precision == 1.0
    assert ing_metric.recall == 1.0
    assert ing_metric.f1 == 1.0

    str_metric = metrics["STRENGTH"]
    assert str_metric.true_positives == 0
    assert str_metric.false_positives == 1
    assert str_metric.false_negatives == 1
    assert str_metric.precision == 0.0
    assert str_metric.recall == 0.0


def test_evaluator_clinical_tuple_exact_matching():
    gt = [[
        ClinicalTuple(ingredient="Paracetamol", numeric_value=500.0, unit="mg", basis="per tablet"),
        ClinicalTuple(ingredient="Caffeine", numeric_value=30.0, unit="mg", basis="per tablet"),
    ]]
    pred = [[
        ClinicalTuple(ingredient="paracetamol", numeric_value=500.0, unit="mg", basis="per tablet"),
        # Wrong unit for caffeine (g instead of mg)
        ClinicalTuple(ingredient="caffeine", numeric_value=30.0, unit="g", basis="per tablet"),
    ]]

    tuple_metric = ExtractionEvaluator.evaluate_clinical_tuples(gt, pred)

    assert tuple_metric.total_ground_truth_tuples == 2
    assert tuple_metric.exact_matches == 1
    assert tuple_metric.false_negatives == 1
    assert tuple_metric.false_positives == 1
    assert tuple_metric.exact_tuple_accuracy == 0.5


def test_evaluator_abstention_rates():
    statuses = [
        VerificationState.VERIFIED,
        VerificationState.PARTIALLY_VERIFIED,
        VerificationState.NEEDS_CONFIRMATION,
        VerificationState.UNABLE_TO_VERIFY,
    ]
    correctness = [True, True, False, False]

    ab_metric = ExtractionEvaluator.evaluate_abstention(statuses, correctness)

    assert ab_metric.total_samples == 4
    assert ab_metric.abstained_samples == 2
    assert ab_metric.accepted_samples == 2
    assert ab_metric.abstention_rate == 0.5
    assert ab_metric.accepted_accuracy == 1.0


def test_evaluator_zero_division_safety():
    metrics, overall = ExtractionEvaluator.evaluate_entities([], [])
    assert overall.micro_precision == 0.0
    assert overall.micro_recall == 0.0
    assert overall.micro_f1 == 0.0

    t_metric = ExtractionEvaluator.evaluate_clinical_tuples([], [])
    assert t_metric.exact_tuple_accuracy == 0.0
    assert t_metric.f1 == 0.0


# ============================================================================
# 4. Dataset Integrity & Split Leakage Tests
# ============================================================================

def test_split_manifests_leakage_and_eligibility():
    splits_dir = Path(__file__).parent.parent / "data" / "splits"
    if not splits_dir.exists():
        pytest.skip("Splits directory not generated yet.")

    train_families = set(json.load(open(splits_dir / "train.json"))["product_families"])
    val_families = set(json.load(open(splits_dir / "val.json"))["product_families"])
    test_families = set(json.load(open(splits_dir / "test.json"))["product_families"])

    # Confirm strict zero leakage across splits
    assert not (train_families & val_families), "Leakage detected between train and val!"
    assert not (train_families & test_families), "Leakage detected between train and test!"
    assert not (val_families & test_families), "Leakage detected between val and test!"

    # Confirm synthetic fixtures are flagged ineligible for real training
    for split_name in ["train", "val", "test"]:
        manifest = json.load(open(splits_dir / f"{split_name}.json"))
        for img in manifest.get("images", []):
            if img.get("is_synthetic_fixture") or img.get("review_status") != "verified_by_human":
                assert img.get("eligible_for_real_training") is False, (
                    f"Image {img['image_id']} incorrectly marked eligible for real training!"
                )
