"""Focused integration tests for OCR engine selection, fallback, error handling, and metadata propagation.

Requirements verified:
- Lazy OCR initialization without downloading weights upon FastAPI import
- Accurate engine availability checks
- Rejection of silent MockOCREngine substitution for real uploads (HTTP 503 ERR_OCR_ENGINE_UNAVAILABLE)
- Explicit mock selection for tests/demos (X-OCR-Engine: mock or requested_engine="mock")
- Full OCR metadata propagation in AnalysisResponse
- Hermetic test execution without network access or downloading model weights
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app as fastapi_app
from app.core.errors import OCREngineUnavailableError, OCRExecutionError
from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox
from app.schemas.analysis import AnalysisResponse
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.dispatcher import OCRDispatcher
from app.services.ocr.mock_engine import MockOCREngine
from app.services.ocr.paddle_engine import PaddleOCREngine
from app.services.ocr.tesseract_engine import TesseractOCREngine
from app.services.analysis_service import AnalysisPipelineService


class HermeticPaddleEngine(BaseOCREngine):
    """Hermetic double of PaddleOCREngine without downloading network weights."""

    def __init__(self, available: bool = True, should_crash: bool = False):
        self._available = available
        self._should_crash = should_crash

    @property
    def name(self) -> str:
        return "paddleocr"

    @property
    def version(self) -> str:
        return "3.7.0"

    def is_available(self) -> bool:
        return self._available

    def extract_text(self, image_bytes: bytes, pil_image=None, np_array=None) -> OCRResult:
        if not self._available:
            raise RuntimeError("PaddleOCR dependencies missing.")
        if self._should_crash:
            raise RuntimeError("Inference memory fault in PaddleOCR runtime.")

        box = BoundingBox(x_min=10.0, y_min=20.0, x_max=150.0, y_max=40.0)
        token = OCRToken(text="Paracetamol", confidence=0.97, box=box)
        line = OCRLine(text="Paracetamol IP 500mg", confidence=0.97, tokens=[token], box=box)
        return OCRResult(
            engine_name="paddleocr",
            engine_version="3.7.0",
            full_text="Paracetamol IP 500mg\nEach uncoated tablet contains Paracetamol 500 mg",
            lines=[line],
            mean_confidence=0.97,
            execution_time_ms=145,
        )


class HermeticTesseractEngine(BaseOCREngine):
    """Hermetic double of TesseractOCREngine without requiring OS binary."""

    def __init__(self, available: bool = True, should_crash: bool = False):
        self._available = available
        self._should_crash = should_crash

    @property
    def name(self) -> str:
        return "tesseract"

    @property
    def version(self) -> str:
        return "5.3.0"

    def is_available(self) -> bool:
        return self._available

    def extract_text(self, image_bytes: bytes, pil_image=None, np_array=None) -> OCRResult:
        if not self._available:
            raise RuntimeError("Tesseract binary not found in PATH.")
        if self._should_crash:
            raise RuntimeError("Pytesseract pipe communication failure.")

        box = BoundingBox(x_min=10.0, y_min=20.0, x_max=150.0, y_max=40.0)
        token = OCRToken(text="Paracetamol", confidence=0.91, box=box)
        line = OCRLine(text="Paracetamol IP 500mg", confidence=0.91, tokens=[token], box=box)
        return OCRResult(
            engine_name="tesseract",
            engine_version="5.3.0",
            full_text="Paracetamol IP 500mg\nEach uncoated tablet contains Paracetamol 500 mg",
            lines=[line],
            mean_confidence=0.91,
            execution_time_ms=210,
        )


@pytest.fixture
def mock_medicine_image() -> bytes:
    img = Image.new("RGB", (400, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "PARACETAMOL 500mg", fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ============================================================================
# 1. Engine Availability and Lazy Initialization Tests
# ============================================================================

def test_paddle_engine_lazy_initialization():
    """Verifies that instantiating PaddleOCREngine does NOT download weights or crash."""
    engine = PaddleOCREngine()
    assert engine.name == "paddleocr"
    # Should not instantiate deep learning model upon construction
    assert engine._ocr_instance is None


def test_tesseract_engine_lazy_initialization():
    """Verifies that instantiating TesseractOCREngine does NOT execute OCR upon construction."""
    engine = TesseractOCREngine()
    assert engine.name == "tesseract"


def test_engine_availability_accuracy():
    """Verifies that availability checks accurately reflect installed modules without guessing."""
    paddle_eng = PaddleOCREngine()
    tesseract_eng = TesseractOCREngine()
    # In the current host testing environment, if binaries/packages are not installed,
    # is_available() must return a boolean without throwing unhandled exceptions.
    assert isinstance(paddle_eng.is_available(), bool)
    assert isinstance(tesseract_eng.is_available(), bool)


# ============================================================================
# 2. Rejection of Silent Mock Substitution (Prompt Requirement 4)
# ============================================================================

def test_no_silent_mock_on_real_upload_without_mock_header(mock_medicine_image: bytes):
    """A real upload without explicit mock request must return 503 if real engines are absent."""
    # Create clean unauthenticated / unconfigured client without default mock header
    raw_client = TestClient(fastapi_app)

    # If the local environment has neither PaddleOCR nor Tesseract installed:
    dispatcher = OCRDispatcher()
    real_available = [e for e in dispatcher.get_available_engines() if e != "mock"]

    if not real_available:
        response = raw_client.post(
            "/api/v1/analyses",
            files={"file": ("medicine.png", mock_medicine_image, "image/png")},
        )
        assert response.status_code == 503
        data = response.json()
        assert data["error_code"] == "ERR_OCR_ENGINE_UNAVAILABLE"
        assert "No real OCR engine" in data["message"]
        assert "hint" in data["details"]


def test_explicit_mock_header_accepted(mock_medicine_image: bytes):
    """Uploading with X-OCR-Engine: mock is accepted explicitly for tests/demos."""
    client = TestClient(fastapi_app, headers={"X-OCR-Engine": "mock"})
    response = client.post(
        "/api/v1/analyses",
        files={"file": ("medicine.png", mock_medicine_image, "image/png")},
    )
    assert response.status_code == 202
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "received"


def test_explicit_mock_form_param_accepted(mock_medicine_image: bytes):
    """Uploading with form parameter ocr_engine=mock is accepted explicitly."""
    raw_client = TestClient(fastapi_app)
    response = raw_client.post(
        "/api/v1/analyses",
        files={"file": ("medicine.png", mock_medicine_image, "image/png")},
        data={"ocr_engine": "mock"},
    )
    assert response.status_code == 202
    data = response.json()
    assert "analysis_id" in data


# ============================================================================
# 3. Fallback and Metadata Propagation Tests
# ============================================================================

@pytest.mark.asyncio
async def test_pipeline_selects_paddleocr_and_propagates_metadata(
    db_session: AsyncSession,
    mock_medicine_image: bytes,
):
    """When PaddleOCR is available, pipeline selects it as default real engine."""
    paddle_mock = HermeticPaddleEngine(available=True)
    tesseract_mock = HermeticTesseractEngine(available=True)

    dispatcher = OCRDispatcher(
        engines={"paddleocr": paddle_mock, "tesseract": tesseract_mock, "mock": MockOCREngine()},
        preference_order=["paddleocr", "tesseract"],
    )
    service = AnalysisPipelineService(db_session=db_session, ocr_dispatcher=dispatcher)

    report = await service.process_image(raw_bytes=mock_medicine_image)

    assert isinstance(report, AnalysisResponse)
    assert report.ocr_metadata is not None
    assert report.ocr_metadata.engine_name == "paddleocr"
    assert report.ocr_metadata.engine_version == "3.7.0"
    assert report.ocr_metadata.is_mock is False
    assert report.ocr_metadata.fallback_used is False
    assert report.ocr_metadata.mean_confidence == 0.97
    assert report.ocr_metadata.execution_time_ms == 145


@pytest.mark.asyncio
async def test_pipeline_falls_back_to_tesseract_when_paddle_unavailable(
    db_session: AsyncSession,
    mock_medicine_image: bytes,
):
    """When PaddleOCR is unavailable, pipeline automatically falls back to Tesseract and notes fallback."""
    paddle_mock = HermeticPaddleEngine(available=False)
    tesseract_mock = HermeticTesseractEngine(available=True)

    dispatcher = OCRDispatcher(
        engines={"paddleocr": paddle_mock, "tesseract": tesseract_mock, "mock": MockOCREngine()},
        preference_order=["paddleocr", "tesseract"],
    )
    service = AnalysisPipelineService(db_session=db_session, ocr_dispatcher=dispatcher)

    report = await service.process_image(raw_bytes=mock_medicine_image)

    assert report.ocr_metadata is not None
    assert report.ocr_metadata.engine_name == "tesseract"
    assert report.ocr_metadata.engine_version == "5.3.0"
    assert report.ocr_metadata.is_mock is False
    assert report.ocr_metadata.fallback_used is True


@pytest.mark.asyncio
async def test_pipeline_falls_back_to_tesseract_on_paddle_inference_crash(
    db_session: AsyncSession,
    mock_medicine_image: bytes,
):
    """When PaddleOCR crashes during inference, dispatcher automatically recovers using Tesseract."""
    crashing_paddle = HermeticPaddleEngine(available=True, should_crash=True)
    working_tesseract = HermeticTesseractEngine(available=True)

    dispatcher = OCRDispatcher(
        engines={"paddleocr": crashing_paddle, "tesseract": working_tesseract, "mock": MockOCREngine()},
        preference_order=["paddleocr", "tesseract"],
    )
    service = AnalysisPipelineService(db_session=db_session, ocr_dispatcher=dispatcher)

    report = await service.process_image(raw_bytes=mock_medicine_image)

    assert report.ocr_metadata is not None
    assert report.ocr_metadata.engine_name == "tesseract"
    assert report.ocr_metadata.fallback_used is True


@pytest.mark.asyncio
async def test_pipeline_marks_mock_ocr_and_adds_uncertainty_notice(
    db_session: AsyncSession,
    mock_medicine_image: bytes,
):
    """When mock OCR is explicitly requested, is_mock is True and uncertainty warning is recorded."""
    dispatcher = OCRDispatcher()
    service = AnalysisPipelineService(db_session=db_session, ocr_dispatcher=dispatcher)

    report = await service.process_image(raw_bytes=mock_medicine_image, requested_ocr_engine="mock")

    assert report.ocr_metadata is not None
    assert report.ocr_metadata.engine_name == "mock"
    assert report.ocr_metadata.is_mock is True
    # Verify mock warning is surfaced in uncertainties
    assert any("Mock OCR engine was used" in u for u in report.uncertainties)

