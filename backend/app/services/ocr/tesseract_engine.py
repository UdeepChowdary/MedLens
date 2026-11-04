"""Tesseract OCR engine adapter using pytesseract."""

import io
import time
from typing import Dict, List, Optional
import numpy as np
from PIL import Image

from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox
from .base import BaseOCREngine


class TesseractOCREngine(BaseOCREngine):
    """Adapter for Google Tesseract-OCR via pytesseract."""

    def __init__(self, psm: int = 6, oem: int = 3):
        self._psm = psm
        self._oem = oem
        self._version = self._detect_version()

    @property
    def name(self) -> str:
        return "tesseract"

    @property
    def version(self) -> str:
        return self._version

    def _detect_version(self) -> str:
        try:
            import pytesseract
            ver = str(pytesseract.get_tesseract_version())
            return ver.split()[0]
        except Exception:
            return "unavailable"

    def is_available(self) -> bool:
        if self._version == "unavailable":
            self._version = self._detect_version()
            if self._version == "unavailable":
                return False
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text(
        self,
        image_bytes: bytes,
        pil_image: Optional[Image.Image] = None,
        np_array: Optional[np.ndarray] = None,
    ) -> OCRResult:
        if not self.is_available():
            raise RuntimeError("Tesseract OCR is not installed or not in PATH.")

        import pytesseract

        start_time = time.perf_counter()

        if pil_image is None:
            pil_image = Image.open(io.BytesIO(image_bytes))

        config = f"--oem {self._oem} --psm {self._psm}"
        try:
            data = pytesseract.image_to_data(pil_image, config=config, output_type=pytesseract.Output.DICT)
        except Exception as e:
            raise RuntimeError(f"Tesseract OCR inference execution failed: {e}") from e

        lines_map: Dict[tuple, List[OCRToken]] = {}
        line_texts: Dict[tuple, List[str]] = {}

        n_boxes = len(data["text"])
        for i in range(n_boxes):
            word = data["text"][i].strip()
            conf = float(data["conf"][i])

            # Tesseract reports conf=-1 for non-word structural elements
            if not word or conf < 0:
                continue

            normalized_conf = max(0.0, min(1.0, conf / 100.0))
            box = BoundingBox(
                x_min=float(data["left"][i]),
                y_min=float(data["top"][i]),
                x_max=float(data["left"][i] + data["width"][i]),
                y_max=float(data["top"][i] + data["height"][i]),
            )
            token = OCRToken(text=word, confidence=normalized_conf, box=box)

            line_key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
            if line_key not in lines_map:
                lines_map[line_key] = []
                line_texts[line_key] = []

            lines_map[line_key].append(token)
            line_texts[line_key].append(word)

        lines_out: List[OCRLine] = []
        all_confs: List[float] = []

        for line_key, tokens in lines_map.items():
            line_str = " ".join(line_texts[line_key])
            line_conf = float(np.mean([t.confidence for t in tokens])) if tokens else 0.0
            all_confs.extend([t.confidence for t in tokens])

            line_box = BoundingBox(
                x_min=min(t.box.x_min for t in tokens if t.box),
                y_min=min(t.box.y_min for t in tokens if t.box),
                x_max=max(t.box.x_max for t in tokens if t.box),
                y_max=max(t.box.y_max for t in tokens if t.box),
            ) if any(t.box for t in tokens) else None

            lines_out.append(
                OCRLine(
                    text=line_str,
                    confidence=line_conf,
                    tokens=tokens,
                    box=line_box,
                )
            )

        mean_conf = float(np.mean(all_confs)) if all_confs else 0.0
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        full_text = "\n".join(l.text for l in lines_out)

        return OCRResult(
            engine_name=self.name,
            engine_version=self.version,
            full_text=full_text,
            lines=lines_out,
            mean_confidence=round(mean_conf, 3),
            execution_time_ms=elapsed_ms,
        )

