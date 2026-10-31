"""OCR Dispatcher coordinating OCR engine selection, execution, and fallback."""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from app.core.errors import OCREngineUnavailableError, OCRExecutionError
from app.schemas.ocr import OCRResult
from .base import BaseOCREngine
from .mock_engine import MockOCREngine
from .tesseract_engine import TesseractOCREngine
from .paddle_engine import PaddleOCREngine

logger = logging.getLogger(__name__)


class OCRDispatcher:
    """Central manager for OCR engines, automatic fallback, and execution metrics."""

    DEFAULT_PREFERENCE = ["paddleocr", "tesseract"]

    def __init__(
        self,
        engines: Optional[Dict[str, BaseOCREngine]] = None,
        preference_order: Optional[List[str]] = None,
    ):
        self._engines: Dict[str, BaseOCREngine] = engines if engines is not None else {
            "paddleocr": PaddleOCREngine(),
            "tesseract": TesseractOCREngine(),
            "mock": MockOCREngine(),
        }
        self._preference_order = preference_order or list(self.DEFAULT_PREFERENCE)

    def register_engine(self, name: str, engine: BaseOCREngine) -> None:
        """Registers a custom OCR engine adapter."""
        self._engines[name] = engine

    def get_available_engines(self) -> List[str]:
        """Returns names of all engines whose runtime dependencies are satisfied."""
        return [name for name, eng in self._engines.items() if eng.is_available()]

    def resolve_engine(
        self,
        requested_engine: Optional[str] = None,
        allow_mock: bool = False,
    ) -> Tuple[BaseOCREngine, bool]:
        """Resolves target engine and returns (engine_adapter, fallback_used).

        Strict verification-first policy:
        1. If requested_engine == 'mock': explicitly allowed, returns mock engine without fallback flag.
        2. If requested_engine is a registered engine and available: returns that engine.
        3. If requested_engine is unavailable: attempts real preference engines with fallback_used=True.
        4. If no engine is explicitly requested: selects first available engine from preference_order.
           If a secondary preference engine is picked, fallback_used=True.
        5. If NO real engine is available:
           - If allow_mock=True: returns mock engine with fallback_used=True.
           - Otherwise: raises OCREngineUnavailableError (never silently substitutes mock).
        """
        # Case 1: Explicit mock selection
        if requested_engine == "mock":
            if "mock" in self._engines:
                return self._engines["mock"], False
            return MockOCREngine(), False

        # Case 2: Specific engine requested
        if requested_engine:
            if requested_engine in self._engines and self._engines[requested_engine].is_available():
                return self._engines[requested_engine], False
            logger.warning(
                "Requested OCR engine '%s' is not available. Attempting fallback among real engines.",
                requested_engine,
            )
            for engine_name in self._preference_order:
                if engine_name != requested_engine and engine_name in self._engines and self._engines[engine_name].is_available():
                    return self._engines[engine_name], True

        # Case 3: Default selection in preference order
        for idx, engine_name in enumerate(self._preference_order):
            if engine_name in self._engines and self._engines[engine_name].is_available():
                fallback = (requested_engine is not None and requested_engine != engine_name) or (idx > 0)
                return self._engines[engine_name], fallback

        # Case 4: No real engine available
        if allow_mock:
            logger.warning("No real OCR engine available; utilizing explicit mock OCR fallback.")
            return self._engines.get("mock", MockOCREngine()), True

        available = [k for k, v in self._engines.items() if k != "mock" and v.is_available()]
        raise OCREngineUnavailableError(
            message=(
                f"No real OCR engine is available (attempted: {self._preference_order}). "
                f"Currently available real engines: {available}. "
                "Install PaddleOCR or Tesseract, or explicitly select 'mock' for tests/demos."
            ),
            details={
                "attempted_preference": self._preference_order,
                "requested_engine": requested_engine,
                "available_engines": available,
                "hint": "Install PaddleOCR ('pip install paddlepaddle paddleocr') or Tesseract-OCR, or explicitly request 'mock' for tests/demos.",
            },
        )

    def get_active_engine(
        self,
        requested_engine: Optional[str] = None,
        allow_mock: bool = False,
    ) -> BaseOCREngine:
        """Selects the active engine adapter, raising OCREngineUnavailableError if unavailable."""
        engine, _ = self.resolve_engine(requested_engine, allow_mock=allow_mock)
        return engine

    def extract(
        self,
        image_bytes: bytes,
        pil_image: Optional[Image.Image] = None,
        np_array: Optional[np.ndarray] = None,
        requested_engine: Optional[str] = None,
        allow_mock: bool = False,
    ) -> OCRResult:
        """Dispatches image to resolved OCR engine with automatic fallback on execution failure."""
        active_engine, fallback_used = self.resolve_engine(
            requested_engine=requested_engine,
            allow_mock=allow_mock,
        )

        try:
            result = active_engine.extract_text(
                image_bytes=image_bytes,
                pil_image=pil_image,
                np_array=np_array,
            )
            result.requested_engine = requested_engine
            result.fallback_used = fallback_used
            return result
        except Exception as primary_err:
            logger.error(
                "Primary OCR engine '%s' execution failed: %s. Attempting fallback.",
                active_engine.name,
                primary_err,
            )

            # Attempt fallback among remaining real engines
            attempted = {active_engine.name}
            for fallback_name in self._preference_order:
                if fallback_name in attempted:
                    continue
                attempted.add(fallback_name)
                fallback_eng = self._engines.get(fallback_name)
                if fallback_eng and fallback_eng.is_available():
                    try:
                        res = fallback_eng.extract_text(
                            image_bytes=image_bytes,
                            pil_image=pil_image,
                            np_array=np_array,
                        )
                        res.requested_engine = requested_engine
                        res.fallback_used = True
                        return res
                    except Exception as fallback_err:
                        logger.error("Fallback engine '%s' also failed: %s", fallback_name, fallback_err)

            # If all real engines failed, check if mock is permitted
            if allow_mock or requested_engine == "mock":
                mock_eng = self._engines.get("mock", MockOCREngine())
                res = mock_eng.extract_text(
                    image_bytes=image_bytes,
                    pil_image=pil_image,
                    np_array=np_array,
                )
                res.requested_engine = requested_engine
                res.fallback_used = True
                return res

            raise OCRExecutionError(
                message=f"All configured OCR engines failed during text extraction: {primary_err}",
                details={
                    "primary_engine": active_engine.name,
                    "attempted_engines": list(attempted),
                    "primary_error": str(primary_err),
                },
            ) from primary_err
