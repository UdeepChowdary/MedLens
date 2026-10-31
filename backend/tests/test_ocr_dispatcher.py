"""Unit tests for OCR Dispatcher service and engines (ML-026, ML-027)."""

import pytest
from app.core.errors import OCREngineUnavailableError, OCRExecutionError
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

    def __init__(self, name: str = "failing_engine", available: bool = True):
        self._name = name
        self._available = available

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return "0.0.1-faulty"

    def is_available(self) -> bool:
        return self._available

    def extract_text(self, image_bytes: bytes, pil_image=None, np_array=None) -> OCRResult:
        raise RuntimeError("Simulated OCR execution crash!")


class WorkingMockRealEngine(BaseOCREngine):
    """Hermetic working real engine double for testing without downloading weights."""

    def __init__(self, name: str = "paddleocr", version: str = "3.7.0", available: bool = True):
        self._name = name
        self._version = version
        self._available = available

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def is_available(self) -> bool:
        return self._available

    def extract_text(self, image_bytes: bytes, pil_image=None, np_array=None) -> OCRResult:
        token = OCRToken(text="Paracetamol", confidence=0.98, box=BoundingBox(x_min=0, y_min=0, x_max=10, y_max=10))
        line = OCRLine(text="Paracetamol 500mg", confidence=0.98, tokens=[token], box=token.box)
        return OCRResult(
            engine_name=self._name,
            engine_version=self._version,
            full_text="Paracetamol 500mg",
            lines=[line],
            mean_confidence=0.98,
            execution_time_ms=120,
        )


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

    def test_dispatcher_rejects_mock_when_no_real_engine_available(self):
        # Dispatcher with only unavailable real engines and mock
        dispatcher = OCRDispatcher(
            engines={
                "paddleocr": WorkingMockRealEngine("paddleocr", available=False),
                "tesseract": WorkingMockRealEngine("tesseract", available=False),
                "mock": MockOCREngine(),
            },
            preference_order=["paddleocr", "tesseract"],
        )
        with pytest.raises(OCREngineUnavailableError) as exc_info:
            dispatcher.get_active_engine()
        assert "No real OCR engine is available" in str(exc_info.value.message)

    def test_dispatcher_allows_explicit_mock_request(self, sample_image_bytes: bytes):
        dispatcher = OCRDispatcher(
            engines={
                "paddleocr": WorkingMockRealEngine("paddleocr", available=False),
                "tesseract": WorkingMockRealEngine("tesseract", available=False),
                "mock": MockOCREngine(),
            },
            preference_order=["paddleocr", "tesseract"],
        )
        result = dispatcher.extract(sample_image_bytes, requested_engine="mock")
        assert result.engine_name == "mock"
        assert result.fallback_used is False
        assert result.requested_engine == "mock"

    def test_dispatcher_allows_mock_when_explicitly_permitted(self, sample_image_bytes: bytes):
        dispatcher = OCRDispatcher(
            engines={
                "paddleocr": WorkingMockRealEngine("paddleocr", available=False),
                "tesseract": WorkingMockRealEngine("tesseract", available=False),
                "mock": MockOCREngine(),
            },
            preference_order=["paddleocr", "tesseract"],
        )
        result = dispatcher.extract(sample_image_bytes, allow_mock=True)
        assert result.engine_name == "mock"
        assert result.fallback_used is True

    def test_dispatcher_selects_paddleocr_as_default_real_engine(self, sample_image_bytes: bytes):
        paddle_eng = WorkingMockRealEngine("paddleocr", version="3.7.0", available=True)
        tesseract_eng = WorkingMockRealEngine("tesseract", version="5.3.0", available=True)

        dispatcher = OCRDispatcher(
            engines={"paddleocr": paddle_eng, "tesseract": tesseract_eng, "mock": MockOCREngine()},
            preference_order=["paddleocr", "tesseract"],
        )
        result = dispatcher.extract(sample_image_bytes)
        assert result.engine_name == "paddleocr"
        assert result.engine_version == "3.7.0"
        assert result.fallback_used is False

    def test_dispatcher_falls_back_to_tesseract_when_paddle_unavailable(self, sample_image_bytes: bytes):
        paddle_eng = WorkingMockRealEngine("paddleocr", available=False)
        tesseract_eng = WorkingMockRealEngine("tesseract", version="5.3.0", available=True)

        dispatcher = OCRDispatcher(
            engines={"paddleocr": paddle_eng, "tesseract": tesseract_eng, "mock": MockOCREngine()},
            preference_order=["paddleocr", "tesseract"],
        )
        result = dispatcher.extract(sample_image_bytes)
        assert result.engine_name == "tesseract"
        assert result.fallback_used is True

    def test_dispatcher_recovers_from_primary_engine_crash(self, sample_image_bytes: bytes):
        failing_paddle = FailingTestEngine("paddleocr", available=True)
        working_tesseract = WorkingMockRealEngine("tesseract", available=True)

        dispatcher = OCRDispatcher(
            engines={"paddleocr": failing_paddle, "tesseract": working_tesseract, "mock": MockOCREngine()},
            preference_order=["paddleocr", "tesseract"],
        )
        result = dispatcher.extract(sample_image_bytes)
        assert result.engine_name == "tesseract"
        assert result.fallback_used is True

    def test_dispatcher_raises_execution_error_when_all_real_engines_crash(self, sample_image_bytes: bytes):
        failing_paddle = FailingTestEngine("paddleocr", available=True)
        failing_tesseract = FailingTestEngine("tesseract", available=True)

        dispatcher = OCRDispatcher(
            engines={"paddleocr": failing_paddle, "tesseract": failing_tesseract, "mock": MockOCREngine()},
            preference_order=["paddleocr", "tesseract"],
        )
        with pytest.raises(OCRExecutionError):
            dispatcher.extract(sample_image_bytes, allow_mock=False)
