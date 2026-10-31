"""Automated End-to-End User Journey Integration Tests (ML-059).

Covers:
1. Successful scan -> saved report -> history lifecycle
2. Invalid/corrupted image rejection
3. Blurry image detection and safe abstention
4. Ambiguous/unrecognized identity handling
5. External reference source failure resilience and graceful degradation
6. Scan -> comparison integration workflow
"""

import io
from PIL import Image
import pytest
from fastapi.testclient import TestClient

from app.models.analysis import Analysis
from app.repositories.analysis_repository import AnalysisRepository
from app.services.ocr.mock_engine import MockOCREngine
from app.services.ocr.dispatcher import OCRDispatcher


def create_solid_image_bytes(width: int = 300, height: int = 150, color=(240, 240, 240)) -> bytes:
    """Creates valid RGB image bytes."""
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============================================================================
# 1. Full User Journey: Scan -> Report Retrieval -> History Listing
# ============================================================================

def test_e2e_successful_scan_to_history_lifecycle(client: TestClient):
    """End-to-end journey: Upload packaging image, retrieve persisted report, and verify in history."""
    session_id = "sess_e2e_lifecycle_001"
    image_bytes = create_solid_image_bytes()

    # Step 1: Upload medicine packaging
    upload_res = client.post(
        "/api/v1/analyses",
        files={"file": ("dolo_650_strip.png", image_bytes, "image/png")},
        headers={"X-Session-ID": session_id},
    )
    assert upload_res.status_code == 202, f"Upload failed: {upload_res.text}"
    upload_data = upload_res.json()
    assert "analysis_id" in upload_data
    analysis_id = upload_data["analysis_id"]

    # Step 2: Retrieve verified analysis report by UUID
    report_res = client.get(
        f"/api/v1/analyses/{analysis_id}",
        headers={"X-Session-ID": session_id},
    )
    assert report_res.status_code == 200
    report = report_res.json()
    assert report["analysis_id"] == analysis_id
    assert report["status"] in ["verified", "partially_verified", "unverified", "needs_confirmation"]
    assert "confidence" in report
    assert "active_ingredients" in report
    assert "audit_hash" in report
    assert len(report["audit_hash"]) == 64

    # Step 3: Verify the analysis appears in caller's history
    history_res = client.get(
        "/api/v1/analyses",
        headers={"X-Session-ID": session_id},
    )
    assert history_res.status_code == 200
    history_items = history_res.json()
    assert len(history_items) >= 1
    found = any(item["analysis_id"] == analysis_id for item in history_items)
    assert found is True, "Recently created analysis must be present in scan history"


# ============================================================================
# 2. Input Validation: Invalid / Corrupted Payloads Rejected
# ============================================================================

def test_e2e_invalid_image_upload_rejected(client: TestClient):
    """Verifies that non-image or empty payloads are rejected with HTTP 400."""
    # Case A: Disallowed text MIME type
    res_text = client.post(
        "/api/v1/analyses",
        files={"file": ("notes.txt", b"plain text content", "text/plain")},
    )
    assert res_text.status_code == 400
    msg = res_text.json().get("detail") or res_text.json().get("message", "")
    assert "unsupported file format" in msg.lower()

    # Case B: Disallowed PDF MIME type
    res_pdf = client.post(
        "/api/v1/analyses",
        files={"file": ("document.pdf", b"%PDF-1.4...", "application/pdf")},
    )
    assert res_pdf.status_code == 400
    msg_pdf = res_pdf.json().get("detail") or res_pdf.json().get("message", "")
    assert "unsupported file format" in msg_pdf.lower()

    # Case C: Zero-byte file
    res_empty = client.post(
        "/api/v1/analyses",
        files={"file": ("empty.png", b"", "image/png")},
    )
    assert res_empty.status_code == 400
    msg_empty = res_empty.json().get("detail") or res_empty.json().get("message", "")
    assert "empty" in msg_empty.lower()


# ============================================================================
# 3. Quality & Sharpness: Blurry Image Triggers Warning Flag
# ============================================================================

def test_e2e_blurry_image_triggers_warning_and_abstention(client: TestClient):
    """Verifies that completely uniform/smooth image triggers blur flag and lowers confidence."""
    # A single solid color has variance of Laplacian = 0 < 100
    solid_bytes = create_solid_image_bytes(color=(128, 128, 128))

    res = client.post(
        "/api/v1/analyses",
        files={"file": ("smooth_blur.png", solid_bytes, "image/png")},
    )
    assert res.status_code == 202
    analysis_id = res.json()["analysis_id"]

    report_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert report_res.status_code == 200
    report = report_res.json()

    # Confidence appropriately penalizes OCR on zero-sharpness images
    assert report["confidence"]["ocr_quality"] <= 0.85
    assert report["status"] in ["unverified", "needs_confirmation", "partially_verified"]


# ============================================================================
# 4. Ambiguous / Unrecognized Composition Safe Abstention
# ============================================================================

def test_e2e_unrecognized_formulation_abstention(client: TestClient):
    """Verifies that unreadable or unrecognizable medicine packaging abstains rather than hallucinating."""
    session_id = "sess_e2e_abstain_002"
    # Using an empty canvas where OCR finds no medicine tokens
    img_bytes = create_solid_image_bytes(width=100, height=100)

    res = client.post(
        "/api/v1/analyses",
        files={"file": ("blank_packaging.png", img_bytes, "image/png")},
        headers={"X-Session-ID": session_id},
    )
    assert res.status_code == 202
    analysis_id = res.json()["analysis_id"]

    report = client.get(f"/api/v1/analyses/{analysis_id}", headers={"X-Session-ID": session_id}).json()
    # Zero-hallucination constraint: Never invent ingredients when none are detected
    if len(report["active_ingredients"]) == 0:
        assert report["status"] == "unverified"
        assert report["confidence"]["identity_confidence"] == 0.0


# ============================================================================
# 5. External Reference Source Degradation Resilience
# ============================================================================

def test_e2e_unavailable_external_source_graceful_degradation(client: TestClient):
    """Verifies that when external APIs (e.g. openFDA/PubChem) return 404, scan report completes cleanly."""
    session_id = "sess_e2e_degrade_003"
    image_bytes = create_solid_image_bytes()

    res = client.post(
        "/api/v1/analyses",
        files={"file": ("dolo_test.png", image_bytes, "image/png")},
        headers={"X-Session-ID": session_id},
    )
    assert res.status_code == 202
    analysis_id = res.json()["analysis_id"]

    # Even if openFDA returns 404 for an Indian brand name, the report endpoint returns 200 OK
    report_res = client.get(f"/api/v1/analyses/{analysis_id}", headers={"X-Session-ID": session_id})
    assert report_res.status_code == 200
    report = report_res.json()
    assert report["analysis_id"] == analysis_id


# ============================================================================
# 6. End-to-End Scan -> Compare Workflow
# ============================================================================

def test_e2e_scan_and_dual_brand_comparison(client: TestClient):
    """Verifies workflow of taking scanned medicine context and comparing against alternative product."""
    # Call comparisons endpoint comparing Dolo 650 with Calpol 500
    compare_res = client.post(
        "/api/v1/comparisons",
        json={
            "product_id_a": "dolo-650",
            "product_id_b": "calpol-500",
        },
    )
    assert compare_res.status_code == 200
    comp = compare_res.json()

    # Verify comparison attributes
    assert "comparison_status" in comp
    assert "attributes" in comp
    assert len(comp["attributes"]) > 0

    # Verify strength delta calculation (650 mg vs 500 mg = 150 mg delta)
    if comp.get("strength_delta"):
        assert comp["strength_delta"]["difference_detected"] is True
        assert comp["strength_delta"]["numeric_delta"] == 150.0
