"""Unit tests for the human-reviewed pilot dataset workflow (Prompt 3).

Covers:
- Schema validation (fields, uncertainty notes, image side)
- Character span validation (exact slice matching, out-of-bounds bounds checking)
- Image file linkage and cryptographic SHA-256 verification
- Group-aware dataset splitting with zero product family leakage
- Evaluation split eligibility (rejects unreviewed/synthetic items from test/val)
- Policy enforcement: synthetic illustrations cannot be marked as verified_by_human
- Human review queue detection of drafts, flagged items, and uncertainty
"""

import hashlib
import json
from pathlib import Path
import pytest

from app.schemas.dataset import (
    PackagingAnnotationDoc,
    ImageMetadata,
    ImageDimensions,
    ProvenanceMetadata,
    QualityFlags,
    EntityAnnotation,
    DatasetEntityLabel,
    PackagingType,
    ReviewStatus,
)
from tools.validate_dataset import (
    validate_annotation_file,
    validate_split_manifests,
    validate_dataset,
    compute_sha256,
)
from tools.split_dataset import split_dataset
from tools.review_queue import scan_review_queue, render_markdown_queue_report


# ============================================================================
# Helpers
# ============================================================================

def create_valid_test_doc(
    image_id: str = "img-test-01",
    file_name: str = "test_strip.jpg",
    product_family: str = "dolo-650",
    review_status: str = "verified_by_human",
    has_uncertainty: bool = False,
    uncertainty_notes: str = None,
    image_side: str = "back",
    raw_sha256: str = "a" * 64,
) -> dict:
    """Creates a valid annotation dictionary for testing."""
    transcription = "DOLO 650. Each tablet contains: Paracetamol IP 650 mg."
    return {
        "schema_version": "1.0.0",
        "image_metadata": {
            "image_id": image_id,
            "file_name": file_name,
            "format": "jpeg",
            "dimensions": {"width": 800, "height": 600},
            "sha256": raw_sha256,
            "packaging_type": "blister_foil",
            "image_side": image_side,
            "product_family": product_family,
            "brand_name": "Dolo 650",
            "manufacturer": "Micro Labs Ltd",
            "provenance": {
                "source": "MedLens Real Packaging Pilot",
                "license": "CC-BY-4.0",
                "annotator_id": "clinical-curator-01",
                "verified_by_human": (review_status == "verified_by_human"),
                "date_annotated": "2026-10-31T10:00:00Z",
                "notes": "Real physical blister back photograph under natural lighting.",
            },
        },
        "quality_flags": {
            "glare": False,
            "blur": False,
            "low_contrast": False,
            "small_text": False,
            "occlusion": False,
            "skew_angle": 0.0,
        },
        "transcription": transcription,
        "composition_text": "Each tablet contains: Paracetamol IP 650 mg.",
        "entities": [
            {
                "label": "BRAND",
                "raw_text": "DOLO 650",
                "normalized_value": "Dolo 650",
                "bbox": [50, 50, 150, 300],
                "char_span": [0, 8],
            },
            {
                "label": "INGREDIENT",
                "raw_text": "Paracetamol",
                "normalized_value": "Paracetamol",
                "bbox": [200, 50, 280, 250],
                "char_span": [32, 43],
            },
            {
                "label": "STRENGTH",
                "raw_text": "650 mg",
                "normalized_value": "650 mg",
                "bbox": [200, 260, 280, 350],
                "char_span": [47, 53],
            },
        ],
        "has_uncertainty": has_uncertainty,
        "uncertainty_notes": uncertainty_notes,
        "review_status": review_status,
    }


# ============================================================================
# 1. Schema Validation Tests
# ============================================================================

def test_packaging_annotation_doc_schema_instantiation():
    """Verifies that PackagingAnnotationDoc correctly validates all Prompt 3 fields."""
    raw = create_valid_test_doc()
    doc = PackagingAnnotationDoc(**raw)

    assert doc.image_metadata.image_id == "img-test-01"
    assert doc.image_metadata.image_side == "back"
    assert doc.composition_text == "Each tablet contains: Paracetamol IP 650 mg."
    assert doc.has_uncertainty is False
    assert doc.review_status == ReviewStatus.VERIFIED_BY_HUMAN
    assert len(doc.entities) == 3


def test_schema_rejects_missing_required_metadata(tmp_path: Path):
    """Verifies that validator catches missing image_id, sha256, or product_family."""
    raw = create_valid_test_doc()
    del raw["image_metadata"]["product_family"]

    bad_file = tmp_path / "missing_family.json"
    bad_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(bad_file, tmp_path, seen_hashes={}, check_image_exists=False)
    assert any(i.error_type == "MISSING_FIELD" and "product_family" in i.message for i in issues)


# ============================================================================
# 2. Character Span Validation Tests
# ============================================================================

def test_character_span_exact_match(tmp_path: Path):
    """Verifies that perfectly aligned character spans pass validation with 0 errors."""
    raw = create_valid_test_doc()
    test_file = tmp_path / "valid_spans.json"
    test_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(test_file, tmp_path, seen_hashes={}, check_image_exists=False)
    errors = [i for i in issues if i.severity == "ERROR"]
    assert len(errors) == 0


def test_character_span_text_mismatch_detected(tmp_path: Path):
    """Verifies that character spans pointing to wrong string slice are flagged."""
    raw = create_valid_test_doc()
    # Intentionally corrupt span: [0, 4] in "DOLO 650..." yields "DOLO", not "DOLO 650"
    raw["entities"][0]["char_span"] = [0, 4]

    bad_file = tmp_path / "mismatch_span.json"
    bad_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(bad_file, tmp_path, seen_hashes={}, check_image_exists=False)
    assert any(i.error_type == "CHAR_SPAN_TEXT_MISMATCH" for i in issues)


def test_character_span_out_of_bounds_detected(tmp_path: Path):
    """Verifies that character spans with end > transcription length are caught."""
    raw = create_valid_test_doc()
    # Out of bounds span: end index 999
    raw["entities"][0]["char_span"] = [0, 999]

    bad_file = tmp_path / "oob_span.json"
    bad_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(bad_file, tmp_path, seen_hashes={}, check_image_exists=False)
    assert any(i.error_type == "CHAR_SPAN_OUT_OF_BOUNDS" for i in issues)


# ============================================================================
# 3. Image Linkage & Cryptographic Hash Tests
# ============================================================================

def test_image_linkage_sha256_match(tmp_path: Path):
    """Verifies image linkage passes when physical image file matches declared SHA-256."""
    img_file = tmp_path / "sample_box.jpg"
    img_bytes = b"MEDLENS_AUTHENTIC_PACKAGING_PHOTO_BYTES"
    img_file.write_bytes(img_bytes)

    actual_sha = hashlib.sha256(img_bytes).hexdigest()
    raw = create_valid_test_doc(file_name="sample_box.jpg", raw_sha256=actual_sha)

    ann_file = tmp_path / "linked.json"
    ann_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(ann_file, tmp_path, seen_hashes={}, check_image_exists=True)
    errors = [i for i in issues if i.severity == "ERROR"]
    assert len(errors) == 0


def test_image_linkage_missing_image_file_detected(tmp_path: Path):
    """Verifies validator flags missing raw image files when checking image existence."""
    raw = create_valid_test_doc(file_name="nonexistent_strip.jpg")
    ann_file = tmp_path / "missing_img.json"
    ann_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(ann_file, tmp_path, seen_hashes={}, check_image_exists=True)
    assert any(i.error_type == "MISSING_IMAGE_FILE" for i in issues)


# ============================================================================
# 4. Product Family Leakage Prevention Tests
# ============================================================================

def test_group_aware_splitting_zero_product_family_leakage(tmp_path: Path):
    """Verifies that split_dataset guarantees 0% family leakage across train, val, and test."""
    ann_dir = tmp_path / "annotations"
    splits_dir = tmp_path / "splits"
    ann_dir.mkdir(parents=True)

    families = ["dolo-family", "calpol-family", "augmentin-family", "brufen-family", "cetirizine-family", "pan-d-family"]
    for idx, fam in enumerate(families):
        # Create 2 package photos per family
        for ver in ["strip_a", "box_b"]:
            doc = create_valid_test_doc(
                image_id=f"img-{fam}-{ver}",
                file_name=f"{fam}_{ver}.jpg",
                product_family=fam,
            )
            (ann_dir / f"img-{fam}-{ver}.json").write_text(json.dumps(doc), encoding="utf-8")

    summary = split_dataset(ann_dir, splits_dir, train_ratio=0.50, val_ratio=0.25, test_ratio=0.25, seed=42)

    assert summary["leakage_detected"] is False
    assert summary["total_product_families"] == 6

    # Load manifests and assert zero intersection
    train_data = json.loads((splits_dir / "train.json").read_text(encoding="utf-8"))
    val_data = json.loads((splits_dir / "val.json").read_text(encoding="utf-8"))
    test_data = json.loads((splits_dir / "test.json").read_text(encoding="utf-8"))

    train_f = set(train_data["product_families"])
    val_f = set(val_data["product_families"])
    test_f = set(test_data["product_families"])

    assert len(train_f & val_f) == 0, "Leakage between train and val!"
    assert len(train_f & test_f) == 0, "Leakage between train and test!"
    assert len(val_f & test_f) == 0, "Leakage between val and test!"


# ============================================================================
# 5. Evaluation Split Eligibility & Ground Truth Policy Tests
# ============================================================================

def test_evaluation_split_rejects_unreviewed_record(tmp_path: Path):
    """Verifies that validate_split_manifests rejects unreviewed drafts from evaluation splits."""
    ann_dir = tmp_path / "annotations"
    splits_dir = tmp_path / "splits"
    ann_dir.mkdir(parents=True)
    splits_dir.mkdir(parents=True)

    # Annotation in draft status
    draft_doc = create_valid_test_doc(image_id="img-draft-01", review_status="draft")
    (ann_dir / "img-draft-01.json").write_text(json.dumps(draft_doc), encoding="utf-8")

    # Put it in test split
    (splits_dir / "train.json").write_text(json.dumps({"product_families": [], "images": []}))
    (splits_dir / "val.json").write_text(json.dumps({"product_families": [], "images": []}))
    (splits_dir / "test.json").write_text(
        json.dumps({
            "product_families": ["dolo-650"],
            "images": [
                {
                    "annotation_file": "img-draft-01.json",
                    "image_id": "img-draft-01",
                    "product_family": "dolo-650",
                    "review_status": "draft",
                    "is_synthetic_fixture": False,
                }
            ],
        })
    )

    result = validate_split_manifests(splits_dir, ann_dir, require_human_verified=True)
    assert result["is_valid"] is False
    assert any(i["error_type"] == "UNREVIEWED_RECORD_IN_EVAL_SPLIT" for i in result["issues"])


def test_synthetic_illustration_cannot_be_verified_by_human(tmp_path: Path):
    """Verifies ground-truth policy: 3D illustrations cannot be marked as verified_by_human."""
    raw = create_valid_test_doc()
    # Mark as verified, but notes state it's a 3D generic illustration
    raw["review_status"] = "verified_by_human"
    raw["image_metadata"]["provenance"]["notes"] = (
        "FLAGGED: Source image is a 3D generic illustration lacking readable typography. Do NOT use as ground truth."
    )

    fake_file = tmp_path / "fake_illustration.json"
    fake_file.write_text(json.dumps(raw), encoding="utf-8")

    issues = validate_annotation_file(fake_file, tmp_path, seen_hashes={}, check_image_exists=False)
    assert any(i.error_type == "SYNTHETIC_CANNOT_BE_VERIFIED" for i in issues)


# ============================================================================
# 6. Human Review Queue Tests
# ============================================================================

def test_human_review_queue_detection(tmp_path: Path):
    """Verifies review_queue tool correctly surfaces drafts, flagged items, and uncertainty."""
    ann_dir = tmp_path / "annotations"
    ann_dir.mkdir(parents=True)

    # 1. Verified clean item
    doc_clean = create_valid_test_doc(image_id="img-clean", review_status="verified_by_human")
    (ann_dir / "img-clean.json").write_text(json.dumps(doc_clean), encoding="utf-8")

    # 2. Draft item
    doc_draft = create_valid_test_doc(image_id="img-draft", review_status="draft")
    (ann_dir / "img-draft.json").write_text(json.dumps(doc_draft), encoding="utf-8")

    # 3. Item with uncertainty flag
    doc_uncertain = create_valid_test_doc(
        image_id="img-uncertain",
        review_status="flagged_for_review",
        has_uncertainty=True,
        uncertainty_notes="Expiry date font worn off on foil fold.",
    )
    (ann_dir / "img-uncertain.json").write_text(json.dumps(doc_uncertain), encoding="utf-8")

    queue = scan_review_queue(ann_dir)

    assert queue["total_annotations"] == 3
    assert queue["verified_count"] == 1
    assert queue["pending_review_count"] == 2
    assert queue["draft_count"] == 1
    assert queue["flagged_count"] == 1
    assert queue["uncertain_count"] == 1

    md = render_markdown_queue_report(queue)
    assert "# 📋 MedLens Dataset Human Review Queue" in md
    assert "img-draft" in md
    assert "img-uncertain" in md
    assert "Expiry date font worn off" in md

