"""Tests for Indian medicines dataset audit tool and composition parser benchmark (Prompt 2)."""

import csv
import json
from pathlib import Path
import pytest

from tools.audit_indian_medicines import (
    validate_schema_columns,
    is_suspicious_image_url,
    audit_dataset_file,
    render_markdown_audit_report,
    REQUIRED_COLUMNS,
)


def create_sample_csv(file_path: Path, rows: list) -> Path:
    """Helper creating a test CSV file."""
    fieldnames = REQUIRED_COLUMNS
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return file_path


# ============================================================================
# 1. Schema Column Validation
# ============================================================================

def test_validate_schema_columns_success():
    """Verifies that all 5 required columns are correctly recognized."""
    cols = ["name", "composition", "uses", "side_effects", "image_url"]
    is_valid, missing = validate_schema_columns(cols)
    assert is_valid is True
    assert len(missing) == 0


def test_validate_schema_columns_missing():
    """Verifies that missing columns are flagged with error details."""
    cols = ["name", "composition", "uses"]  # missing side_effects, image_url
    is_valid, missing = validate_schema_columns(cols)
    assert is_valid is False
    assert "side_effects" in missing
    assert "image_url" in missing


# ============================================================================
# 2. Image URL Quality Checks
# ============================================================================

def test_suspicious_image_url_detection():
    """Verifies detection of empty, non-https, or placeholder image links."""
    assert is_suspicious_image_url("") is True
    assert is_suspicious_image_url(None) is True
    assert is_suspicious_image_url("ftp://example.com/img.jpg") is True
    assert is_suspicious_image_url("https://example.com/placeholder.png") is True
    assert is_suspicious_image_url("https://example.com/default_image.jpg") is True

    # Valid https URL
    assert is_suspicious_image_url("https://onemg.gumlet.io/medicines/dolo.jpg") is False


# ============================================================================
# 3. Parsing Outcomes & Diagnostic Coverage Classification
# ============================================================================

def test_audit_dataset_file_classification(tmp_path: Path):
    """Verifies end-to-end classification into full extraction, partial extraction, and unparsed categories."""
    sample_rows = [
        # 1. Full Extraction with Strength: Known ingredient with strength and INN match
        {
            "name": "Dolo 650 Tablet",
            "composition": "Paracetamol (650mg)",
            "uses": "Fever, Pain relief",
            "side_effects": "Nausea, allergic reaction",
            "image_url": "https://onemg.gumlet.io/dolo.jpg",
        },
        # 2. Duplicate brand test: Same name as row 1
        {
            "name": "Dolo 650 Tablet",
            "composition": "Paracetamol (650mg)",
            "uses": "Headache",
            "side_effects": "None",
            "image_url": "https://onemg.gumlet.io/dolo_2.jpg",
        },
        # 3. Partial Extraction: Known ingredient but missing numeric strength
        {
            "name": "Generic Cetirizine Syrup",
            "composition": "Cetirizine Hydrochloride q.s.",
            "uses": "Allergies",
            "side_effects": "Drowsiness",
            "image_url": "https://onemg.gumlet.io/cetirizine.jpg",
        },
        # 4. Unparsed: Unrecognized molecule not in current dictionary
        {
            "name": "Exotic Herb Capsule",
            "composition": "Ashwagandha Extract (500mg)",
            "uses": "Stress relief",
            "side_effects": "Stomach upset",
            "image_url": "https://onemg.gumlet.io/ashwa.jpg",
        },
        # 5. Unparsed: Empty composition string
        {
            "name": "Empty Drug",
            "composition": "",
            "uses": "Unknown",
            "side_effects": "",
            "image_url": "placeholder.png",
        },
    ]

    csv_file = create_sample_csv(tmp_path / "test_medicines.csv", sample_rows)
    summary = audit_dataset_file(csv_file)

    assert summary["total_records_analyzed"] == 5
    assert summary["duplicate_name_count"] == 1
    assert summary["missing_fields"]["composition"] == 1
    assert summary["suspicious_image_url_count"] >= 1

    outcomes = summary["parser_outcomes"]
    assert outcomes["full_extraction_count"] >= 1
    assert outcomes["partial_extraction_count"] >= 1
    assert outcomes["unparsed_count"] >= 2

    # Verify failure log contains the unparsed row
    failures = summary["representative_failures"]
    assert any("Ashwagandha" in f["composition"] for f in failures)


# ============================================================================
# 4. Markdown Report Rendering
# ============================================================================

def test_render_markdown_audit_report(tmp_path: Path):
    """Verifies that markdown summary renders required sections, diagnostic disclaimers, and URL notices."""
    sample_rows = [
        {
            "name": "Calpol 500",
            "composition": "Paracetamol 500 mg",
            "uses": "Fever",
            "side_effects": "Nausea",
            "image_url": "https://example.com/calpol.jpg",
        }
    ]
    csv_file = create_sample_csv(tmp_path / "calpol.csv", sample_rows)
    summary = audit_dataset_file(csv_file)
    md = render_markdown_audit_report(summary)

    assert "# 📊 Indian Medicines Dataset Audit & Parser Diagnostic Coverage Report" in md
    assert "Schema & Data Quality Summary" in md
    assert "Composition Parser Outcomes & Diagnostic Coverage" in md
    assert "diagnostic parser coverage, not clinical accuracy" in md
    assert "Image URLs Unverified" in md

