"""Image preprocessing and quality assessment pipeline for medicine packaging.

Implements ML-024 (Image validation & safe decoding) and ML-025 (OpenCV/NumPy preprocessing & quality flags).
Evaluates blur via Laplacian variance (σ²), normalizes EXIF orientation, standardizes contrast,
and generates SHA-256 tamper-proof audit digests.
"""

from __future__ import annotations

import hashlib
import io
from typing import List, Optional, Tuple
import numpy as np
from PIL import Image, ImageOps, ImageEnhance

from app.schemas.image import ImageQualityReport


class ImageProcessingError(Exception):
    """Base exception for image processing pipeline errors."""
    pass


class InvalidImageError(ImageProcessingError):
    """Raised when uploaded file is not a valid, supported image."""
    pass


class PreprocessedImage:
    """Container holding preprocessed image data and quality diagnostics."""

    def __init__(
        self,
        raw_bytes: bytes,
        processed_bytes: bytes,
        quality: ImageQualityReport,
        pil_image: Image.Image,
        np_array: np.ndarray,
    ):
        self.raw_bytes = raw_bytes
        self.processed_bytes = processed_bytes
        self.quality = quality
        self.pil_image = pil_image
        self.np_array = np_array

    def __repr__(self) -> str:
        return (
            f"<PreprocessedImage {self.quality.width}x{self.quality.height} "
            f"blur={self.quality.blur_score:.1f} status={self.quality.status}>"
        )


class ImagePreprocessor:
    """Deterministic, resilient image validator and preprocessor.

    Features:
    - Magic-byte validation to reject non-image payloads safely without disk writes.
    - Automatic EXIF orientation correction.
    - Laplacian variance blur detection (σ² < 100 flags blur).
    - Contrast analysis and adaptive dynamic range enhancement.
    - Image downscaling capped at max_dimension to safeguard OCR memory.
    - SHA-256 hash generation for clinical audit trails.
    """

    MAGIC_SIGNATURES = {
        "JPEG": [b"\xFF\xD8\xFF"],
        "PNG": [b"\x89PNG\r\n\x1a\n"],
        "WEBP": [b"RIFF"],  # Checked with WEBP at offset 8
        "TIFF": [b"II*\x00", b"MM\x00*"],
    }

    def __init__(
        self,
        blur_threshold: float = 100.0,
        contrast_threshold: float = 20.0,
        max_dimension: int = 2400,
    ):
        self.blur_threshold = blur_threshold
        self.contrast_threshold = contrast_threshold
        self.max_dimension = max_dimension

    def validate_magic_bytes(self, data: bytes) -> str:
        """Inspects magic header bytes to verify supported image formats."""
        if not data or len(data) < 12:
            raise InvalidImageError("Payload is empty or too short to be a valid image.")

        if data.startswith(b"\xFF\xD8\xFF"):
            return "JPEG"
        if data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "PNG"
        if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
            return "WEBP"
        if data.startswith((b"II*\x00", b"MM\x00*")):
            return "TIFF"

        raise InvalidImageError(
            "Unsupported or corrupt image format. Supported formats: JPEG, PNG, WEBP, TIFF."
        )

    def compute_sha256(self, data: bytes) -> str:
        """Calculates SHA-256 digest of original raw bytes."""
        return hashlib.sha256(data).hexdigest()

    def normalize_orientation(self, image: Image.Image) -> Tuple[Image.Image, bool]:
        """Applies EXIF orientation transpose to ensure packaging is upright."""
        try:
            transposed = ImageOps.exif_transpose(image)
            if transposed is not None:
                # Check if transpose altered dimensions or was applied
                was_corrected = (transposed.size != image.size) or (transposed != image)
                return transposed, was_corrected
        except Exception:
            pass
        return image, False

    def calculate_blur_score(self, gray_array: np.ndarray) -> float:
        """Computes Laplacian variance (σ²) as a sharpness metric.

        Attempts hardware-accelerated cv2.Laplacian first; falls back to
        vectorized 2D NumPy discrete Laplacian convolution if OpenCV is uninstalled.
        """
        if gray_array.ndim != 2:
            raise ValueError("Grayscale 2D array required for Laplacian variance calculation.")

        if gray_array.shape[0] < 3 or gray_array.shape[1] < 3:
            return 0.0

        try:
            import cv2
            laplacian = cv2.Laplacian(gray_array.astype(np.float64), cv2.CV_64F)
            return float(laplacian.var())
        except (ImportError, AttributeError):
            # Discrete 2D Laplacian convolution with standard 4-neighbor kernel
            # [ 0,  1,  0]
            # [ 1, -4,  1]
            # [ 0,  1,  0]
            lap = (
                gray_array[:-2, 1:-1]
                + gray_array[2:, 1:-1]
                + gray_array[1:-1, :-2]
                + gray_array[1:-1, 2:]
                - 4.0 * gray_array[1:-1, 1:-1]
            )
            return float(lap.var())

    def calculate_contrast_score(self, gray_array: np.ndarray) -> float:
        """Calculates RMS pixel intensity contrast (standard deviation of grayscale values)."""
        if gray_array.size == 0:
            return 0.0
        return float(np.std(gray_array))

    def enhance_contrast(self, image: Image.Image) -> Image.Image:
        """Applies adaptive auto-contrast and mild sharpening for OCR readability."""
        try:
            # Auto-contrast cuts off 1% of the darkest and lightest pixels to normalize dynamic range
            contrasted = ImageOps.autocontrast(image, cutoff=1)
            # Apply slight contrast boost (1.1x) to make foil-embossed text pop
            enhancer = ImageEnhance.Contrast(contrasted)
            return enhancer.enhance(1.15)
        except Exception:
            return image

    def resize_if_needed(self, image: Image.Image) -> Image.Image:
        """Downscales oversized images proportionally to safeguard memory during OCR."""
        w, h = image.size
        max_dim = max(w, h)
        if max_dim > self.max_dimension:
            scale = self.max_dimension / float(max_dim)
            new_size = (int(w * scale), int(h * scale))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def process(self, raw_bytes: bytes) -> PreprocessedImage:
        """Executes full preprocessing and quality diagnosis pipeline."""
        detected_format = self.validate_magic_bytes(raw_bytes)
        sha256_hash = self.compute_sha256(raw_bytes)

        # In-memory decoding
        try:
            with Image.open(io.BytesIO(raw_bytes)) as pil_img:
                # Load pixel data into memory before context manager closes
                pil_img.load()
                # Ensure RGB mode (handles RGBA, Palette, Grayscale cleanly)
                if pil_img.mode not in ("RGB", "L"):
                    img_rgb = pil_img.convert("RGB")
                else:
                    img_rgb = pil_img.copy()
        except Exception as e:
            raise InvalidImageError(f"Failed to decode image payload: {e}") from e

        # Normalize EXIF orientation
        oriented_img, orientation_corrected = self.normalize_orientation(img_rgb)

        # Resize if oversized
        oriented_img = self.resize_if_needed(oriented_img)

        # Convert to grayscale array for diagnostics
        gray_pil = oriented_img.convert("L")
        gray_arr = np.array(gray_pil, dtype=np.float64)

        # Compute quality metrics
        blur_score = self.calculate_blur_score(gray_arr)
        is_blurry = blur_score < self.blur_threshold

        contrast_score = self.calculate_contrast_score(gray_arr)
        is_low_contrast = contrast_score < self.contrast_threshold

        # Enhance contrast for OCR
        enhanced_img = self.enhance_contrast(oriented_img)
        enhanced_arr = np.array(enhanced_img)

        # Encode processed image to PNG bytes
        buffer = io.BytesIO()
        enhanced_img.save(buffer, format="PNG", optimize=True)
        processed_bytes = buffer.getvalue()

        # Build warnings list
        warnings: List[str] = []
        if is_blurry:
            warnings.append(
                f"Image sharpness score ({blur_score:.1f}) is below recommended threshold "
                f"({self.blur_threshold:.1f}). Text extraction confidence may be reduced."
            )
        if is_low_contrast:
            warnings.append(
                f"Image contrast ({contrast_score:.1f}) is low. Uneven lighting or glare detected."
            )

        # Determine overall quality status
        if is_blurry:
            status = "warning_blurry"
        elif is_low_contrast:
            status = "warning_low_contrast"
        else:
            status = "accepted"

        w, h = oriented_img.size
        channels = 3 if oriented_img.mode == "RGB" else 1

        quality = ImageQualityReport(
            sha256=sha256_hash,
            format=detected_format,
            width=w,
            height=h,
            channels=channels,
            aspect_ratio=round(float(w) / float(h), 3),
            blur_score=round(blur_score, 2),
            is_blurry=is_blurry,
            contrast_score=round(contrast_score, 2),
            is_low_contrast=is_low_contrast,
            orientation_corrected=orientation_corrected,
            status=status,
            warnings=warnings,
        )

        return PreprocessedImage(
            raw_bytes=raw_bytes,
            processed_bytes=processed_bytes,
            quality=quality,
            pil_image=enhanced_img,
            np_array=enhanced_arr,
        )

