"""End-to-end integration tests for Scan-to-Database analysis pipeline (ML-030 to ML-033)."""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analysis import AnalysisResponse
from app.services.analysis_service import AnalysisPipelineService
from app.repositories.analysis_repository import AnalysisRepository


def create_mock_medicine_image_bytes() -> bytes:
    """Creates a high-contrast mock medicine strip image in memory."""
    img = Image.new("RGB", (600, 300), color=(250, 250, 250))
    draw = ImageDraw.Draw(img)

    # Draw simulated packaging typography
    draw.text((20, 30), "DOLO-650 TABLETS", fill=(0, 0, 120))
    draw.text((20, 80), "Each uncoated tablet contains:", fill=(20, 20, 20))
    draw.text((20, 120), "Paracetamol IP 650 mg", fill=(20, 20, 20))
    draw.text((20, 160), "Excipients q.s.", fill=(80, 80, 80))
    draw.text((20, 210), "Mfg. Lic. No.: M/742/2016", fill=(100, 100, 100))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.asyncio
async def test_pipeline_service_full_execution(db_session: AsyncSession):
    """Verifies image ingestion, OCR, extraction, INN normalization, and database persistence."""
    image_bytes = create_mock_medicine_image_bytes()
    service = AnalysisPipelineService(db_session=db_session)

    report = await service.process_image(raw_bytes=image_bytes, requested_ocr_engine="mock")

    assert isinstance(report, AnalysisResponse)
    assert report.analysis_id is not None
    assert len(report.analysis_id) > 10
    assert report.confidence.ocr_quality > 0.0
    assert report.confidence.identity_confidence > 0.0
    assert report.ocr_metadata is not None
    assert report.ocr_metadata.engine_name == "mock"
    assert report.ocr_metadata.is_mock is True

    # Verify active ingredients detected
    assert len(report.active_ingredients) > 0
    first_ing = report.active_ingredients[0]
    assert "Paracetamol" in first_ing.canonical_name

    # Verify database persistence (ML-030, ML-032)
    repo = AnalysisRepository(db_session)
    saved = await repo.get_by_id(report.analysis_id)
    assert saved is not None
    assert saved.id == report.analysis_id
    assert saved.report_json is not None
    assert len(saved.entities) > 0


def test_api_post_image_and_get_saved_report(client: TestClient):
    """Verifies POST /api/v1/analyses persists and GET /api/v1/analyses/{id} retrieves real report."""
    image_bytes = create_mock_medicine_image_bytes()

    # 1. Ingest image
    post_res = client.post(
        "/api/v1/analyses",
        files={"file": ("dolo_label.png", image_bytes, "image/png")},
    )
    assert post_res.status_code == 202
    post_data = post_res.json()
    assert "analysis_id" in post_data
    analysis_id = post_data["analysis_id"]

    # 2. Retrieve dynamic report by analysis_id (ML-033)
    get_res = client.get(f"/api/v1/analyses/{analysis_id}")
    assert get_res.status_code == 200
    report_data = get_res.json()

    assert report_data["analysis_id"] == analysis_id
    assert "status" in report_data
    assert "confidence" in report_data
    assert report_data["confidence"]["ocr_quality"] >= 0.0
    assert "product" in report_data
    assert len(report_data["active_ingredients"]) > 0
    assert "audit_hash" in report_data


def test_demo_scan_fallback_route(client: TestClient):
    """Verifies that static demo-scan remains accessible."""
    res = client.get("/api/v1/analyses/demo-scan")
    assert res.status_code == 200
    data = res.json()
    assert data["analysis_id"] == "demo-scan"
    assert data["product"]["detected_name"] == "Dolo 650"


def test_list_analyses_endpoint(client: TestClient):
    """Verifies GET /api/v1/analyses returns history summaries (ML-047, ML-048)."""
    res = client.get("/api/v1/analyses?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    if len(data) > 0:
        first = data[0]
        assert "analysis_id" in first
        assert "status" in first
        assert "detected_name" in first
        assert "created_at" in first
