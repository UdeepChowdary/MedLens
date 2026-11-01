"""PaddleOCR engine adapter for deep-learning packaging OCR."""

import io
import os
import time
from typing import Any, Dict, List, Optional, Union
import numpy as np
from PIL import Image

from app.schemas.ocr import OCRResult, OCRLine, OCRToken, BoundingBox
from .base import BaseOCREngine


def _ensure_runtime_compatibility():
    """Configures environment flags and preloads DLLs for stable CPU inference.

    1. Windows DLL preloading: preloads PyTorch DLLs if installed to prevent
       WinError 127 shm.dll collision when PaddleX imports modelscope.
    2. CPU execution flags: PaddlePaddle 3.3.1 with oneDNN on CPU has an unimplemented
       ConvertPirAttribute2RuntimeAttribute PIR double-attribute conversion in
       onednn_instruction.cc. Disabling MKLDNN by default allows native CPU execution.
    """
    try:
        import torch  # Preload PyTorch runtime DLLs on Windows before paddle
    except Exception:
        pass

    os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
    os.environ["FLAGS_use_mkldnn"] = "0"

    try:
        import paddlex.utils.flags as pdx_flags
        pdx_flags.ENABLE_MKLDNN_BYDEFAULT = False
    except Exception:
        pass


# Ensure flags are configured before any paddle/paddleocr imports happen
_ensure_runtime_compatibility()


class PaddleOCREngine(BaseOCREngine):
    """Adapter for Baidu PaddleOCR (DBNet + SVTR/CRNN / PP-OCRv4/v6)."""

    def __init__(
        self,
        lang: str = "en",
        use_angle_cls: bool = True,
        use_textline_orientation: Optional[bool] = None,
    ):
        self._lang = lang
        self._use_angle_cls = use_angle_cls
        self._use_textline_orientation = (
            use_textline_orientation if use_textline_orientation is not None else use_angle_cls
        )
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
            _ensure_runtime_compatibility()
            try:
                from paddleocr import PaddleOCR
                try:
                    # PaddleOCR 3.x prefers use_textline_orientation
                    self._ocr_instance = PaddleOCR(
                        lang=self._lang,
                        use_doc_orientation_classify=False,
                        use_doc_unwarping=False,
                        use_textline_orientation=self._use_textline_orientation,
                    )
                except TypeError:
                    # PaddleOCR 2.x uses use_angle_cls
                    self._ocr_instance = PaddleOCR(
                        use_angle_cls=self._use_angle_cls,
                        lang=self._lang,
                    )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to initialize PaddleOCR engine (model weights download or runtime error): {e}"
                ) from e
        return self._ocr_instance

    def _parse_ocr_output(self, raw_results: Any) -> List[OCRLine]:
        """Defensively parses raw output from both PaddleOCR 2.x and PaddleOCR 3.x."""
        lines_out: List[OCRLine] = []
        if not raw_results:
            return lines_out

        first_res = raw_results[0]
        if hasattr(first_res, "json"):
            first_res = first_res.json() if callable(first_res.json) else first_res.json
        if isinstance(first_res, dict):
            first_res = first_res.get("res", first_res)

        # Format A: PaddleOCR 3.x / PaddleX pipeline dict
        if isinstance(first_res, dict) or hasattr(first_res, "get"):
            rec_texts = first_res.get("rec_texts", [])
            rec_scores = first_res.get("rec_scores", [])
            rec_polys = first_res.get("rec_polys")
            if rec_polys is None:
                rec_polys = first_res.get("dt_polys", [])
            rec_boxes = first_res.get("rec_boxes")

            for i, text_val in enumerate(rec_texts):
                text = str(text_val).strip()
                if not text:
                    continue
                conf = float(rec_scores[i]) if i < len(rec_scores) else 0.0

                poly_points: List[List[float]] = []
                if rec_polys is not None and i < len(rec_polys):
                    raw_p = rec_polys[i]
                    p_list = raw_p.tolist() if hasattr(raw_p, "tolist") else raw_p
                    if isinstance(p_list, (list, tuple)):
                        poly_points = [
                            [float(pt[0]), float(pt[1])]
                            for pt in p_list
                            if isinstance(pt, (list, tuple, np.ndarray)) and len(pt) >= 2
                        ]

                if poly_points and len(poly_points) >= 4:
                    xs = [pt[0] for pt in poly_points]
                    ys = [pt[1] for pt in poly_points]
                    box = BoundingBox(
                        x_min=float(min(xs)),
                        y_min=float(min(ys)),
                        x_max=float(max(xs)),
                        y_max=float(max(ys)),
                        polygon=poly_points,
                    )
                elif rec_boxes is not None and i < len(rec_boxes):
                    raw_b = rec_boxes[i]
                    b_list = raw_b.tolist() if hasattr(raw_b, "tolist") else raw_b
                    x_min, y_min, x_max, y_max = [float(v) for v in b_list[:4]]
                    box = BoundingBox(
                        x_min=x_min,
                        y_min=y_min,
                        x_max=x_max,
                        y_max=y_max,
                        polygon=[[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]],
                    )
                else:
                    box = BoundingBox(x_min=0.0, y_min=0.0, x_max=0.0, y_max=0.0, polygon=[])

                words = text.split()
                tokens = [OCRToken(text=w, confidence=conf, box=box) for w in words]
                lines_out.append(OCRLine(text=text, confidence=conf, tokens=tokens, box=box))

        # Format B: PaddleOCR 2.x list of [polygon, (text, conf)]
        elif isinstance(first_res, (list, tuple)):
            for line_item in first_res:
                if not line_item or len(line_item) < 2:
                    continue
                poly = line_item[0]
                text_info = line_item[1]
                if not text_info:
                    continue
                text = str(text_info[0]).strip()
                if not text:
                    continue
                conf = float(text_info[1]) if len(text_info) > 1 else 0.0

                p_list = poly.tolist() if hasattr(poly, "tolist") else poly
                poly_points = [
                    [float(pt[0]), float(pt[1])]
                    for pt in p_list
                    if isinstance(pt, (list, tuple, np.ndarray)) and len(pt) >= 2
                ]
                if poly_points:
                    xs = [pt[0] for pt in poly_points]
                    ys = [pt[1] for pt in poly_points]
                    box = BoundingBox(
                        x_min=float(min(xs)),
                        y_min=float(min(ys)),
                        x_max=float(max(xs)),
                        y_max=float(max(ys)),
                        polygon=poly_points,
                    )
                else:
                    box = BoundingBox(x_min=0.0, y_min=0.0, x_max=0.0, y_max=0.0, polygon=[])

                words = text.split()
                tokens = [OCRToken(text=w, confidence=conf, box=box) for w in words]
                lines_out.append(OCRLine(text=text, confidence=conf, tokens=tokens, box=box))

        return lines_out

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
            # In PaddleOCR 3.x, use predict() if available, otherwise ocr()
            if hasattr(ocr, "predict"):
                try:
                    raw_results = ocr.predict(np_array)
                except Exception:
                    raw_results = ocr.ocr(np_array)
            else:
                raw_results = ocr.ocr(np_array, cls=self._use_angle_cls)
        except Exception as e:
            raise RuntimeError(f"PaddleOCR inference execution failed: {e}") from e

        lines_out = self._parse_ocr_output(raw_results)
        all_confs = [l.confidence for l in lines_out]

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
