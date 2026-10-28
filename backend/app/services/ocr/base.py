"""Abstract base class for OCR engines."""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np
from PIL import Image

from app.schemas.ocr import OCRResult


class BaseOCREngine(ABC):
    """Abstract interface that all OCR engine adapters must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the OCR engine."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the OCR engine library."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the engine dependencies and binaries are present in the environment."""
        pass

    @abstractmethod
    def extract_text(
        self,
        image_bytes: bytes,
        pil_image: Optional[Image.Image] = None,
        np_array: Optional[np.ndarray] = None,
    ) -> OCRResult:
        """Extracts text, bounding boxes, and confidences from image data."""
        pass

