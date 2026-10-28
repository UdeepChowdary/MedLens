"""Schemas for image quality diagnostics and preprocessing results."""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ImageQualityReport(BaseModel):
    """Quality diagnostic report generated prior to OCR ingestion (ML-024, ML-025)."""
    sha256: str = Field(description="SHA-256 cryptographic digest of raw image bytes.")
    format: str = Field(description="Detected image format (JPEG, PNG, WEBP).")
    width: int = Field(ge=1, description="Image width in pixels.")
    height: int = Field(ge=1, description="Image height in pixels.")
    channels: int = Field(ge=1, le=4, description="Number of color channels.")
    aspect_ratio: float = Field(description="Aspect ratio (width / height).")
    blur_score: float = Field(description="Laplacian variance σ² sharpness metric.")
    is_blurry: bool = Field(description="True if blur_score falls below threshold.")
    contrast_score: float = Field(description="Standard deviation of pixel intensity (RMS contrast).")
    is_low_contrast: bool = Field(description="True if contrast_score falls below threshold.")
    orientation_corrected: bool = Field(default=False, description="Whether EXIF orientation transpose was applied.")
    status: Literal["accepted", "warning_blurry", "warning_low_contrast", "rejected_corrupt"] = Field(
        description="Overall acceptance classification."
    )
    warnings: List[str] = Field(default_factory=list, description="Specific human-readable warnings.")

