"""Unit tests for image validation and preprocessing pipeline (ML-024, ML-025)."""

import io
import hashlib
import numpy as np
import pytest
from PIL import Image

from app.services.image_processing.preprocessor import (
    ImagePreprocessor,
    InvalidImageError,
    PreprocessedImage,
)
from app.schemas.image import ImageQualityReport


@pytest.fixture
def preprocessor() -> ImagePreprocessor:
    return ImagePreprocessor(blur_threshold=100.0, contrast_threshold=20.0, max_dimension=1000)


def create_test_image_bytes(
    width: int = 100,
    height: int = 100,
    format: str = "PNG",
    mode: str = "RGB",
    pattern: str = "solid",
) -> bytes:
    """Helper to synthesize test images in memory."""
    if pattern == "solid":
        img = Image.new(mode, (width, height), color=(128, 128, 128))
    elif pattern == "sharp_lines":
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        arr[::4, :, :] = 255  # High-frequency horizontal stripes
        img = Image.fromarray(arr, mode="RGB")
    elif pattern == "gradient":
        arr = np.tile(np.linspace(100, 150, width, dtype=np.uint8), (height, 1))
        img = Image.fromarray(arr, mode="L").convert("RGB")
    else:
        img = Image.new(mode, (width, height), color=(255, 255, 255))

    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


class TestImageValidation:
    """Tests for magic-byte validation and corrupt payload rejection (ML-024)."""

    def test_valid_png_recognized(self, preprocessor: ImagePreprocessor):
        png_bytes = create_test_image_bytes(format="PNG")
        assert preprocessor.validate_magic_bytes(png_bytes) == "PNG"

    def test_valid_jpeg_recognized(self, preprocessor: ImagePreprocessor):
        jpeg_bytes = create_test_image_bytes(format="JPEG")
        assert preprocessor.validate_magic_bytes(jpeg_bytes) == "JPEG"

    def test_reject_empty_bytes(self, preprocessor: ImagePreprocessor):
        with pytest.raises(InvalidImageError, match="empty or too short"):
            preprocessor.validate_magic_bytes(b"")

    def test_reject_arbitrary_text_file(self, preprocessor: ImagePreprocessor):
        text_payload = b"Hello, this is not an image file at all."
        with pytest.raises(InvalidImageError, match="Unsupported or corrupt"):
            preprocessor.validate_magic_bytes(text_payload)

    def test_reject_corrupt_truncated_bytes(self, preprocessor: ImagePreprocessor):
        # Starts with PNG magic bytes but truncated mid-header
        corrupt_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00"
        with pytest.raises(InvalidImageError):
            preprocessor.process(corrupt_png)


class TestImageQualityAndBlur:
    """Tests for blur detection (σ²), contrast, and quality report generation (ML-025)."""

    def test_sharp_image_classified_as_accepted(self, preprocessor: ImagePreprocessor):
        sharp_bytes = create_test_image_bytes(width=200, height=200, pattern="sharp_lines")
        result = preprocessor.process(sharp_bytes)

        assert isinstance(result, PreprocessedImage)
        assert isinstance(result.quality, ImageQualityReport)
        assert result.quality.blur_score > 100.0
        assert result.quality.is_blurry is False
        assert result.quality.status == "accepted"
        assert len(result.quality.warnings) == 0

    def test_smooth_image_triggers_blurry_warning(self, preprocessor: ImagePreprocessor):
        # Flat solid color has 0 Laplacian variance
        solid_bytes = create_test_image_bytes(width=100, height=100, pattern="solid")
        result = preprocessor.process(solid_bytes)

        assert result.quality.is_blurry is True
        assert result.quality.blur_score < 100.0
        assert result.quality.status == "warning_blurry"
        assert any("sharpness" in w.lower() for w in result.quality.warnings)

    def test_sha256_audit_hash_consistency(self, preprocessor: ImagePreprocessor):
        img_bytes = create_test_image_bytes(width=80, height=80, pattern="sharp_lines")
        expected_hash = hashlib.sha256(img_bytes).hexdigest()

        result = preprocessor.process(img_bytes)
        assert result.quality.sha256 == expected_hash

    def test_oversized_image_downscaling(self, preprocessor: ImagePreprocessor):
        # max_dimension on fixture is 1000
        oversized_bytes = create_test_image_bytes(width=1500, height=1200, pattern="sharp_lines")
        result = preprocessor.process(oversized_bytes)

        assert result.quality.width <= 1000
        assert result.quality.height <= 1000
        # Aspect ratio 1500/1200 = 1.25 preserved
        assert abs(result.quality.aspect_ratio - 1.25) < 0.05

    def test_rgba_converted_cleanly(self, preprocessor: ImagePreprocessor):
        rgba_bytes = create_test_image_bytes(width=100, height=100, format="PNG", mode="RGBA")
        result = preprocessor.process(rgba_bytes)

        assert result.quality.channels == 3
        assert result.quality.width == 100
        assert result.quality.height == 100

