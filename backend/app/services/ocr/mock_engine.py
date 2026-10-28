"""Mock / Synthetic OCR engine for deterministic testing and lightweight CI execution."""

import time
from typing import List, Optional
import numpy as np
from PIL import Image

from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox
from .base import BaseOCREngine


DEFAULT_SYNTHETIC_LINES = [
    "PARACETAMOL TABLETS IP 500mg",
    "Each film coated tablet contains:",
    "Paracetamol IP 500 mg",
    "Excipients q.s.",
    "Dosage: As directed by the physician.",
    "Storage: Store below 30°C. Protect from light and moisture.",
    "Mfg. Lic. No.: M/742/2016",
    "Batch No.: B24089",
    "Mfg. Date: 03/2026",
    "Exp. Date: 02/2028",
]


class MockOCREngine(BaseOCREngine):
    """Deterministic OCR engine used for automated testing and CI pipelines."""

    def __init__(
        self,
        default_lines: Optional[List[str]] = None,
        default_confidence: float = 0.95,
    ):
        self._lines = default_lines or DEFAULT_SYNTHETIC_LINES
        self._confidence = default_confidence

    @property
    def name(self) -> str:
        return "mock"

    @property
    def version(self) -> str:
        return "1.0.0-synthetic"

    def is_available(self) -> bool:
        return True

    def set_mock_lines(self, lines: List[str]) -> None:
        """Dynamically configure mock text for specific test scenarios."""
        self._lines = lines

    def extract_text(
        self,
        image_bytes: bytes,
        pil_image: Optional[Image.Image] = None,
        np_array: Optional[np.ndarray] = None,
    ) -> OCRResult:
        start_time = time.perf_counter()

        lines_out: List[OCRLine] = []
        full_text_parts: List[str] = []

        y_offset = 50.0
        line_height = 30.0

        for line_str in self._lines:
            tokens_out: List[OCRToken] = []
            words = line_str.split()
            x_offset = 20.0

            for word in words:
                token_width = float(len(word) * 12)
                token_box = BoundingBox(
                    x_min=x_offset,
                    y_min=y_offset,
                    x_max=x_offset + token_width,
                    y_max=y_offset + line_height,
                )
                tokens_out.append(
                    OCRToken(
                        text=word,
                        confidence=self._confidence,
                        box=token_box,
                    )
                )
                x_offset += token_width + 10.0

            line_box = BoundingBox(
                x_min=20.0,
                y_min=y_offset,
                x_max=x_offset,
                y_max=y_offset + line_height,
            )
            lines_out.append(
                OCRLine(
                    text=line_str,
                    confidence=self._confidence,
                    tokens=tokens_out,
                    box=line_box,
                )
            )
            full_text_parts.append(line_str)
            y_offset += line_height + 10.0

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        return OCRResult(
            engine_name=self.name,
            engine_version=self.version,
            full_text="\n".join(full_text_parts),
            lines=lines_out,
            mean_confidence=self._confidence,
            execution_time_ms=elapsed_ms,
        )

