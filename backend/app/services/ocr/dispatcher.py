"""OCR Dispatcher coordinating OCR engine selection, execution, and fallback."""

import logging
from typing import Dict, List, Optional
import numpy as np
from PIL import Image

from app.schemas.ocr import OCRResult
from .base import BaseOCREngine
from .mock_engine import MockOCREngine
from .tesseract_engine import TesseractOCREngine
from .paddle_engine import PaddleOCREngine

logger = logging.getLogger(__name__)


class OCRDispatcher:
    """Central manager for OCR engines, automatic fallback, and execution metrics."""

    DEFAULT_PREFERENCE = ["paddleocr", "tesseract", "mock"]

    def __init__(
        self,
        engines: Optional[Dict[str, BaseOCREngine]] = None,
        preference_order: Optional[List[str]] = None,
    ):
        self._engines: Dict[str, BaseOCREngine] = engines or {
            "paddleocr": PaddleOCREngine(),
            "tesseract": TesseractOCREngine(),
            "mock": MockOCREngine(),
        }
        self._preference_order = preference_order or self.DEFAULT_PREFERENCE

    def register_engine(self, name: str, engine: BaseOCREngine) -> None:
        """Registers a custom OCR engine adapter."""
        self._engines[name] = engine

    def get_available_engines(self) -> List[str]:
        """Returns names of all engines whose runtime dependencies are satisfied."""
        return [name for name, eng in self._engines.items() if eng.is_available()]

    def get_active_engine(self, requested_engine: Optional[str] = None) -> BaseOCREngine:
        """Selects the requested engine if available, or the first available in preference order."""
        if requested_engine:
            if requested_engine in self._engines and self._engines[requested_engine].is_available():
                return self._engines[requested_engine]
            logger.warning(
                "Requested OCR engine '%s' is not available. Falling back to default order.",
                requested_engine,
            )

        for engine_name in self._preference_order:
            if engine_name in self._engines and self._engines[engine_name].is_available():
                return self._engines[engine_name]

        # Fail-safe: always return mock if everything else is missing
        return self._engines.get("mock", MockOCREngine())

    def extract(
        self,
        image_bytes: bytes,
        pil_image: Optional[Image.Image] = None,
        np_array: Optional[np.ndarray] = None,
        requested_engine: Optional[str] = None,
    ) -> OCRResult:
        """Dispatches image to optimal OCR engine with automatic fallback on execution failure."""
        active_engine = self.get_active_engine(requested_engine)

        try:
            return active_engine.extract_text(
                image_bytes=image_bytes,
                pil_image=pil_image,
                np_array=np_array,
            )
        except Exception as e:
            logger.error("Primary OCR engine '%s' failed: %s. Attempting fallback.", active_engine.name, e)

            # Try fallback engines
            for fallback_name in self._preference_order:
                if fallback_name == active_engine.name:
                    continue
                fallback_eng = self._engines.get(fallback_name)
                if fallback_eng and fallback_eng.is_available():
                    try:
                        return fallback_eng.extract_text(
                            image_bytes=image_bytes,
                            pil_image=pil_image,
                            np_array=np_array,
                        )
                    except Exception as fallback_err:
                        logger.error("Fallback engine '%s' also failed: %s", fallback_name, fallback_err)

            raise RuntimeError(f"All available OCR engines failed to extract text from payload: {e}") from e

