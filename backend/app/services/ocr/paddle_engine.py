"""PaddleOCR engine adapter for deep-learning packaging OCR."""

import io
import time
from typing import List, Optional
import numpy as np
from PIL import Image

from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox
from .base import BaseOCREngine


class PaddleOCREngine(BaseOCREngine):
    """Adapter for Baidu PaddleOCR (DBNet + SVTR/CRNN)."""

    def __init__(self, lang: str = "en", use_angle_cls: bool = True):
        self._lang = lang
        self._use_angle_cls = use_angle_cls
        self._ocr_instance = None
        self._version = self._detect_version()

    @property
    def name(self) -> str:
        return "paddleocr"

    @property
    def version(self) -> str:
        return self._version

    def _detect_version(self) -> str:
        try:
            import paddleocr
            return str(getattr(paddleocr, "__version__", "unknown"))
        except Exception:
            return "unavailable"

    def is_available(self) -> bool:
        if self._version == "unavailable":
            # Re-check in case package was installed after class loading
            self._version = self._detect_version()
            if self._version == "unavailable":
                return False
        try:
            import paddle  # PaddlePaddle runtime must be present
            import paddleocr
            return True
        except Exception:
            return False

    def _get_ocr_instance(self):
        """Lazy-loads the PaddleOCR model instance on first inference request."""
        if self._ocr_instance is None:
            try:
                from paddleocr import PaddleOCR
                self._ocr_instance = PaddleOCR(use_angle_cls=self._use_angle_cls, lang=self._lang)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize PaddleOCR engine (model weights download or runtime error): {e}"
                ) from e
        return self._ocr_instance

    def extract_text(
        self,
        image_bytes: bytes,
        pil_image: Optional[Image.Image] = None,
        np_array: Optional[np.ndarray] = None,
    ) -> OCRResult:
        if not self.is_available():
            raise RuntimeError(
                "PaddleOCR is not installed or runtime dependencies (paddlepaddle, paddleocr) are missing."
            )

        start_time = time.perf_counter()

        if np_array is None:
            if pil_image is None:
                pil_image = Image.open(io.BytesIO(image_bytes))
            np_array = np.array(pil_image)

        try:
            ocr = self._get_ocr_instance()
            raw_results = ocr.ocr(np_array, cls=self._use_angle_cls)
        except Exception as e:
            raise RuntimeError(f"PaddleOCR inference execution failed: {e}") from e

        lines_out: List[OCRLine] = []
        all_confs: List[float] = []

        if raw_results and raw_results[0]:
            for line_item in raw_results[0]:
                poly = line_item[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = line_item[1]  # (text, conf)
                text = str(text_info[0])
                conf = float(text_info[1])

                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                box = BoundingBox(
                    x_min=float(min(xs)),
                    y_min=float(min(ys)),
                    x_max=float(max(xs)),
                    y_max=float(max(ys)),
                    polygon=poly,
                )

                # Segment line into tokens
                words = text.split()
                tokens: List[OCRToken] = []
                for w in words:
                    tokens.append(OCRToken(text=w, confidence=conf, box=box))

                lines_out.append(OCRLine(text=text, confidence=conf, tokens=tokens, box=box))
                all_confs.append(conf)

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

