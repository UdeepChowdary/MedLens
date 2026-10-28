"""Unit tests for OCR Dispatcher service and engines (ML-026, ML-027)."""

import pytest
from app.services.ocr import (
    OCRDispatcher,
    MockOCREngine,
    TesseractOCREngine,
    PaddleOCREngine,
    BaseOCREngine,
)
from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox


class FailingTestEngine(BaseOCREngine):
    """Engine that simulates runtime failure to verify dispatcher fallback."""

    @property
    def name(self) -> str:
        return "failing_engine"

    @property
    def version(self) -> str:
        return "0.0.1-faulty"

    def is_available(self) -> bool:
        return True

    def extract_text(self, image_bytes: bytes, pil_image=None, np_array=None) -> OCRResult:
        raise RuntimeError("Simulated OCR execution crash!")


@pytest.fixture
def sample_image_bytes() -> bytes:
    # Minimal 1x1 PNG bytes
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05"
        b"\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )


class TestMockOCREngine:
    """Verifies deterministic mock engine behavior."""

    def test_mock_engine_basic_extraction(self, sample_image_bytes: bytes):
        engine = MockOCREngine()
        assert engine.name == "mock"
        assert engine.is_available() is True

        result = engine.extract_text(sample_image_bytes)

        assert isinstance(result, OCRResult)
        assert result.engine_name == "mock"
        assert len(result.lines) > 0
        assert "Paracetamol" in result.full_text
        assert 0.0 <= result.mean_confidence <= 1.0
        assert result.execution_time_ms >= 0

        # Check line structure
        first_line = result.lines[0]
        assert isinstance(first_line, OCRLine)
        assert len(first_line.tokens) > 0
        assert isinstance(first_line.tokens[0], OCRToken)
        assert isinstance(first_line.tokens[0].box, BoundingBox)

    def test_mock_engine_custom_lines(self, sample_image_bytes: bytes):
        custom_lines = [
            "METFORMIN HYDROCHLORIDE TABLETS IP 500mg",
            "Each uncoated tablet contains:",
            "Metformin Hydrochloride IP 500 mg",
        ]
        engine = MockOCREngine(default_lines=custom_lines, default_confidence=0.98)
        result = engine.extract_text(sample_image_bytes)

        assert len(result.lines) == 3
        assert "Metformin" in result.full_text
        assert result.mean_confidence == 0.98


class TestOCRDispatcher:
    """Verifies dispatcher engine selection, fallback, and fault tolerance."""

    def test_dispatcher_engine_listing(self):
        dispatcher = OCRDispatcher()
        available = dispatcher.get_available_engines()

        assert isinstance(available, list)
        assert "mock" in available

    def test_dispatcher_active_engine_selection(self):
        dispatcher = OCRDispatcher()
        active = dispatcher.get_active_engine()

        assert active is not None
        assert active.is_available() is True

    def test_dispatcher_explicit_engine_request(self, sample_image_bytes: bytes):
        dispatcher = OCRDispatcher()
        result = dispatcher.extract(sample_image_bytes, requested_engine="mock")

        assert result.engine_name == "mock"
        assert len(result.lines) > 0

    def test_dispatcher_fallback_on_unavailable_engine(self, sample_image_bytes: bytes):
        dispatcher = OCRDispatcher()
        # Request non-existent engine; should cleanly fall back to first available
        result = dispatcher.extract(sample_image_bytes, requested_engine="non_existent_engine_xyz")

        assert result is not None
        assert result.engine_name in dispatcher.get_available_engines()

    def test_dispatcher_recovers_from_engine_runtime_crash(self, sample_image_bytes: bytes):
        mock_eng = MockOCREngine()
        failing_eng = FailingTestEngine()

        dispatcher = OCRDispatcher(
            engines={"faulty": failing_eng, "mock": mock_eng},
            preference_order=["faulty", "mock"],
        )

        # Faulty engine is tried first and throws RuntimeError; dispatcher should catch and fall back to mock
        result = dispatcher.extract(sample_image_bytes)

        assert result is not None
        assert result.engine_name == "mock"
        assert len(result.lines) > 0

