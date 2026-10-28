"""OCR service package providing unified multi-engine text extraction."""

from .base import BaseOCREngine
from .mock_engine import MockOCREngine
from .tesseract_engine import TesseractOCREngine
from .paddle_engine import PaddleOCREngine
from .dispatcher import OCRDispatcher

__all__ = [
    "BaseOCREngine",
    "MockOCREngine",
    "TesseractOCREngine",
    "PaddleOCREngine",
    "OCRDispatcher",
]

