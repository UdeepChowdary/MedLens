"""Unit tests for the pretrained OCR benchmark suite (Prompt 4).

Covers:
- Character Error Rate (CER) and Word Error Rate (WER) edit distance algorithms
- Strict eligibility filtering (rejects drafts, unverified records, and 3D illustrations)
- Explicit handling of unavailable OCR engines without silent mock substitution
- Isolated synthetic test fixture execution
- Markdown benchmark report rendering and required disclaimers
"""

import json
from pathlib import Path
import pytest
from PIL import Image

from tools.benchmark_ocr import (
    levenshtein_distance,
    calculate_cer,
    calculate_wer,
    compute_text_metrics,
    is_eligible_real_packaging_annotation,
    load_benchmark_candidates,
    run_ocr_benchmark,
    render_markdown_ocr_benchmark,
)
from app.services.ocr.base import BaseOCREngine
from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox


# ============================================================================
# 1. Edit Distance & Text Metric Tests
# ============================================================================

def test_levenshtein_distance_exact_match():
    """Verifies edit distance between identical sequences is zero."""
    assert levenshtein_distance("PARACETAMOL", "PARACETAMOL") == 0
    assert levenshtein_distance([], []) == 0
    assert levenshtein_distance(["dolo", "650"], ["dolo", "650"]) == 0


def test_levenshtein_distance_operations():
    """Verifies single insertions, deletions, and substitutions."""
    # 1 substitution ('a' -> 'o')
    assert levenshtein_distance("cat", "cot") == 1
    # 1 deletion ('e' removed)
    assert levenshtein_distance("Paracetamol", "Paracetmol") == 1
    # 1 insertion ('s' added)
    assert levenshtein_distance("tablet", "tablets") == 1


def test_calculate_cer_and_wer_metrics():
    """Verifies CER and WER computations across standard and degraded strings."""
    ref = "Dolo 650 Tablet"

    # Exact match
    assert calculate_cer(ref, ref) == 0.0
    assert calculate_wer(ref, ref) == 0.0

    # 1 character typo in 15 characters: "Dolo 550 Tablet"
    cer = calculate_cer(ref, "Dolo 550 Tablet")
    assert round(cer, 3) == round(1 / 15, 3)

    # 1 word substitution in 3 words
    wer = calculate_wer(ref, "Dolo 500 Tablet")
    assert round(wer, 3) == round(1 / 3, 3)

    # Case normalization check
    assert calculate_cer(ref, "dolo 650 tablet", normalize=True) == 0.0
    assert calculate_wer(ref, "dolo 650 tablet", normalize=True) == 0.0


def test_compute_text_metrics_comprehensive():
    """Verifies complete metric dictionary payload."""
    ref = "Augmentin 625 Duo"
    hyp = "Augmentin 625 Duo."
    metrics = compute_text_metrics(reference=ref, hypothesis=hyp)

    assert metrics["exact_match_raw"] is False  # trailing dot
    assert metrics["exact_match_normalized"] is False
    assert metrics["raw_cer"] > 0.0
    assert metrics["reference_char_count"] == len(ref)


# ============================================================================
# 2. Eligibility & Ground Truth Filtering Tests
# ============================================================================

def test_eligibility_filter_accepts_verified_real_package():
    """Verifies that human-verified authentic packaging annotations are accepted."""
    doc = {
        "schema_version": "1.0.0",
        "image_metadata": {
            "image_id": "img-paracetamol-500-box",
            "file_name": "paracetamol_500_box.jpg",
            "product_family": "paracetamol-generic-500",
            "provenance": {
                "source": "MedLens Real Archive",
                "verified_by_human": True,
                "notes": "Verified against physical packaging photo pixels.",
            },
        },
        "review_status": "verified_by_human",
        "transcription": "Paracetamol Tablets IP 500 mg",
    }
    is_eligible, reason = is_eligible_real_packaging_annotation(doc)
    assert is_eligible is True
    assert "Eligible" in reason


def test_eligibility_filter_rejects_synthetic_illustration():
    """Verifies that annotations flagged as 3D illustrations are disqualified."""
    doc = {
        "schema_version": "1.0.0",
        "image_metadata": {
            "image_id": "img-dolo-650-blister",
            "file_name": "dolo_650_blister.jpg",
            "product_family": "dolo-650",
            "provenance": {
                "source": "MedLens Reference",
                "verified_by_human": False,
                "notes": "Source image is a 3D generic illustration. Do NOT use as ground truth.",
            },
        },
        "review_status": "flagged_for_review",
        "transcription": "Dolo 650. Each uncoated tablet contains...",
    }
    is_eligible, reason = is_eligible_real_packaging_annotation(doc)
    assert is_eligible is False
    assert "requires verified_by_human" in reason or "illustration" in reason


def test_eligibility_filter_rejects_unreviewed_draft():
    """Verifies that unreviewed drafts are excluded from evaluation splits."""
    doc = {
        "schema_version": "1.0.0",
        "image_metadata": {
            "image_id": "img-draft",
            "file_name": "draft.jpg",
            "product_family": "test-family",
            "provenance": {"verified_by_human": False},
        },
        "review_status": "draft",
        "transcription": "Some text",
    }
    is_eligible, reason = is_eligible_real_packaging_annotation(doc)
    assert is_eligible is False


# ============================================================================
# 3. Engine Availability & Benchmark Scoring Tests
# ============================================================================

def test_unavailable_engine_explicitly_reported_without_mock_substitution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Verifies that missing OCR engines are reported as unavailable, never replaced with mock."""
    from app.services.ocr.paddle_engine import PaddleOCREngine
    monkeypatch.setattr(PaddleOCREngine, "is_available", lambda self: False)

    ann_dir = tmp_path / "annotations"
    raw_dir = tmp_path / "raw"
    ann_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)

    # Valid real package doc
    doc = {
        "schema_version": "1.0.0",
        "image_metadata": {
            "image_id": "img-real-01",
            "file_name": "real_strip.jpg",
            "product_family": "paracetamol",
            "packaging_type": "blister_foil",
            "provenance": {"source": "Lab", "verified_by_human": True, "notes": "Real photo"},
        },
        "review_status": "verified_by_human",
        "transcription": "Paracetamol 500 mg",
    }
    (ann_dir / "img-real-01.json").write_text(json.dumps(doc), encoding="utf-8")

    # Create dummy image file
    img = Image.new("RGB", (100, 100), color="white")
    img.save(raw_dir / "real_strip.jpg")

    # Request tesseract and paddleocr (both unavailable in test env)
    summary = run_ocr_benchmark(
        annotations_dir=ann_dir,
        raw_images_dir=raw_dir,
        engines=["tesseract", "paddleocr"],
    )

    # Must NOT substitute mock engine
    assert summary["status"] == "ENGINES_UNAVAILABLE"
    assert summary["engine_availability"]["tesseract"]["available"] is False
    assert summary["engine_availability"]["paddleocr"]["available"] is False
    assert "mock" not in summary["per_engine_results"]


class DummyTestOCREngine(BaseOCREngine):
    """Controlled mock OCR engine used strictly for unit test verification."""

    def __init__(self, predicted_text: str):
        self._text = predicted_text

    @property
    def name(self) -> str:
        return "dummy_test_ocr"

    @property
    def version(self) -> str:
        return "1.0.0-test"

    def is_available(self) -> bool:
        return True

    def extract_text(self, image_bytes: bytes, pil_image=None, np_array=None) -> OCRResult:
        box = BoundingBox(x_min=0, y_min=0, x_max=100, y_max=100)
        tokens = [OCRToken(text=w, confidence=0.95, box=box) for w in self._text.split()]
        lines = [OCRLine(text=self._text, confidence=0.95, tokens=tokens, box=box)]
        return OCRResult(
            engine_name=self.name,
            engine_version=self.version,
            full_text=self._text,
            lines=lines,
            mean_confidence=0.95,
            execution_time_ms=12,
        )


def test_synthetic_test_fixture_execution(tmp_path: Path):
    """Verifies end-to-end benchmark calculation using a controlled dummy engine."""
    ann_dir = tmp_path / "annotations"
    raw_dir = tmp_path / "raw"
    ann_dir.mkdir(parents=True)
    raw_dir.mkdir(parents=True)

    ground_truth = "Calpol 500 Paracetamol"
    predicted = "Calpol 500 Paracetmol"  # 1 character error

    doc = {
        "schema_version": "1.0.0",
        "image_metadata": {
            "image_id": "img-calpol-01",
            "file_name": "calpol.jpg",
            "product_family": "calpol-500",
            "packaging_type": "paper_box",
            "provenance": {"source": "Lab", "verified_by_human": True, "notes": "Real photo"},
        },
        "review_status": "verified_by_human",
        "transcription": ground_truth,
    }
    (ann_dir / "img-calpol-01.json").write_text(json.dumps(doc), encoding="utf-8")

    img = Image.new("RGB", (100, 100), color="white")
    img.save(raw_dir / "calpol.jpg")

    dummy_engine = DummyTestOCREngine(predicted_text=predicted)
    custom_registry = {"dummy_test_ocr": dummy_engine}

    summary = run_ocr_benchmark(
        annotations_dir=ann_dir,
        raw_images_dir=raw_dir,
        engines=["dummy_test_ocr"],
        apply_preprocessing=False,
        custom_engine_registry=custom_registry,
    )

    assert summary["status"] == "COMPLETED"
    engine_res = summary["per_engine_results"]["dummy_test_ocr"]
    assert engine_res["status"] == "COMPLETED"
    assert engine_res["aggregate_metrics"]["images_evaluated"] == 1
    assert engine_res["aggregate_metrics"]["mean_normalized_cer"] > 0.0
    assert engine_res["aggregate_metrics"]["mean_normalized_wer"] > 0.0

    # Verify Markdown report formatting
    md = render_markdown_ocr_benchmark(summary)
    assert "# 🔬 MedLens Pretrained OCR Benchmark Report" in md
    assert "dummy_test_ocr" in md
    assert "READY" in md
    assert "Methodological Disclaimers" in md

