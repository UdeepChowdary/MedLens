"""Tests for dataset schema validation, duplicate detection, leakage-free splitting, and reporting."""

import json
import tempfile
from pathlib import Path
import pytest

from app.schemas.dataset import (
    PackagingAnnotationDoc,
    EntityAnnotation,
    DatasetEntityLabel,
    PackagingType,
)
from tools.validate_dataset import (
    validate_dataset,
    validate_strength_text,
    validate_annotation_file,
)
from tools.split_dataset import split_dataset
from tools.generate_dataset_report import generate_statistics, render_markdown_report
from tools.annotate import initialize_annotation, add_entity_to_annotation

# Dynamically anchored data directory paths (works from repo root, backend dir, or CI)
BASE_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ANN_DIR = BASE_DATA_DIR / "annotations"
RAW_DIR = BASE_DATA_DIR / "raw"
SPLITS_DIR = BASE_DATA_DIR / "splits"


def test_valid_dataset_passes_validation():
    """Verifies that all baseline annotations in data/annotations pass validation."""
    result = validate_dataset(ANN_DIR, RAW_DIR, check_image_exists=True)

    assert result["is_valid"] is True
    assert result["total_files"] >= 5
    assert result["error_count"] == 0
    assert result["valid_files"] == result["total_files"]


def test_validate_strength_units():
    """Verifies medical unit parser accepts valid units and rejects malformed tokens."""
    # Valid
    valid_cases = ["500 mg", "650mg", "10 mg", "0.5 g", "125 mcg", "5 ml", "0.5% w/v", "q.s."]
    for case in valid_cases:
        is_val, unit = validate_strength_text(case)
        assert is_val is True, f"Failed for valid case: {case}"

    # Invalid
    invalid_cases = ["500", "500 unknown_unit", "invalid_text", "500 mgg", "20 xyz"]
    for case in invalid_cases:
        is_val, _ = validate_strength_text(case)
        assert is_val is False, f"Should have failed for invalid case: {case}"


def test_validation_detects_out_of_bounds_bbox(tmp_path: Path):
    """Verifies that bounding boxes with invalid coordinates are flagged with errors."""
    sample_path = ANN_DIR / "img-dolo-650-blister.json"
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Corrupt bbox: ymax > 1000
    data["entities"][0]["bbox"] = [100, 100, 1050, 500]

    bad_file = tmp_path / "bad_bbox.json"
    with open(bad_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    seen = {}
    issues = validate_annotation_file(bad_file, RAW_DIR, seen, check_image_exists=False)
    err_types = [i.error_type for i in issues]
    assert "BBOX_OUT_OF_BOUNDS" in err_types


def test_validation_detects_duplicate_image_hashes(tmp_path: Path):
    """Verifies that two annotations pointing to the same image hash are caught as duplicates."""
    sample_path = ANN_DIR / "img-dolo-650-blister.json"
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    file_a = tmp_path / "ann_a.json"
    file_b = tmp_path / "ann_b.json"

    with open(file_a, "w", encoding="utf-8") as f:
        json.dump(data, f)
    with open(file_b, "w", encoding="utf-8") as f:
        json.dump(data, f)

    seen = {}
    issues_a = validate_annotation_file(file_a, RAW_DIR, seen, check_image_exists=False)
    issues_b = validate_annotation_file(file_b, RAW_DIR, seen, check_image_exists=False)

    assert len(issues_a) == 0
    assert any(i.error_type == "DUPLICATE_IMAGE_HASH" for i in issues_b)


def test_leakage_free_dataset_splitting(tmp_path: Path):
    """Verifies that dataset splitting ensures zero product family leakage between train, val, and test."""
    ann_dir = ANN_DIR
    out_dir = tmp_path / "splits"

    summary = split_dataset(
        ann_dir,
        out_dir,
        train_ratio=0.60,
        val_ratio=0.20,
        test_ratio=0.20,
        seed=123,
    )

    assert summary["leakage_detected"] is False
    assert summary["total_images"] >= 5

    # Check manifest files exist and are valid JSON
    train_manifest = json.loads((out_dir / "train.json").read_text(encoding="utf-8"))
    val_manifest = json.loads((out_dir / "val.json").read_text(encoding="utf-8"))
    test_manifest = json.loads((out_dir / "test.json").read_text(encoding="utf-8"))

    train_fams = set(train_manifest["product_families"])
    val_fams = set(val_manifest["product_families"])
    test_fams = set(test_manifest["product_families"])

    # Strict isolation assertion
    assert len(train_fams & val_fams) == 0, "Train and Val share product families!"
    assert len(train_fams & test_fams) == 0, "Train and Test share product families!"
    assert len(val_fams & test_fams) == 0, "Val and Test share product families!"


def test_dataset_report_statistics_generation():
    """Verifies aggregating statistics and rendering markdown report."""
    ann_dir = ANN_DIR
    splits_dir = SPLITS_DIR

    stats = generate_statistics(ann_dir, splits_dir)
    assert stats["total_images"] >= 5
    assert stats["total_annotated_entities"] >= 30
    assert "BRAND" in stats["entity_distribution"]
    assert "INGREDIENT" in stats["entity_distribution"]
    assert "STRENGTH" in stats["entity_distribution"]

    md = render_markdown_report(stats)
    assert "# 📊 MedLens Medicine Label Dataset Quality Report" in md
    assert "Unique Product Families" in md


def test_annotation_tool_workflow(tmp_path: Path):
    """Verifies CLI helper initializes a new annotation draft from image and adds entity."""
    img_file = RAW_DIR / "dolo_650_blister.jpg"
    out_dir = tmp_path / "annotations"

    created = initialize_annotation(
        image_path=img_file,
        output_dir=out_dir,
        product_family="test-brand",
        brand_name="Test Brand",
        packaging_type="blister_foil",
    )
    assert created.exists()

    # Add entity token
    add_entity_to_annotation(
        annotation_path=created,
        label="BRAND",
        raw_text="Test Brand",
        bbox=(100, 100, 200, 500),
    )

    with open(created, "r", encoding="utf-8") as f:
        saved = json.load(f)

    assert len(saved["entities"]) == 1
    assert saved["entities"][0]["label"] == "BRAND"
    assert saved["entities"][0]["raw_text"] == "Test Brand"
    assert saved["image_metadata"]["dimensions"]["width"] == 260
