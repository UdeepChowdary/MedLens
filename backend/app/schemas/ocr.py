"""Pydantic schemas for OCR tokens, bounding boxes, lines, and extraction results."""

from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Normalized or pixel coordinates for a detected text bounding region."""
    x_min: float = Field(ge=0.0, description="Left coordinate.")
    y_min: float = Field(ge=0.0, description="Top coordinate.")
    x_max: float = Field(ge=0.0, description="Right coordinate.")
    y_max: float = Field(ge=0.0, description="Bottom coordinate.")
    polygon: Optional[List[List[float]]] = Field(
        default=None,
        description="Optional 4-point polygon [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]."
    )


class OCRToken(BaseModel):
    """Individual word or token detected by OCR."""
    text: str = Field(description="Recognized string token.")
    confidence: float = Field(ge=0.0, le=1.0, description="OCR detection confidence score.")
    box: Optional[BoundingBox] = Field(default=None, description="Spatial bounding box.")


class OCRLine(BaseModel):
    """Structured text line comprising individual tokens."""
    text: str = Field(description="Full text line reconstructed.")
    confidence: float = Field(ge=0.0, le=1.0, description="Mean confidence for the line.")
    tokens: List[OCRToken] = Field(default_factory=list, description="Constituent tokens.")
    box: Optional[BoundingBox] = Field(default=None, description="Line-level bounding box.")


class OCRResult(BaseModel):
    """Complete structured output from an OCR engine execution."""
    engine_name: str = Field(description="Name of the executing engine (paddleocr, tesseract, mock).")
    engine_version: str = Field(description="Version string of the underlying OCR library.")
    full_text: str = Field(description="Complete raw text concatenated across all lines.")
    lines: List[OCRLine] = Field(default_factory=list, description="Individual recognized text lines.")
    mean_confidence: float = Field(ge=0.0, le=1.0, description="Aggregated overall OCR confidence.")
    execution_time_ms: int = Field(ge=0, description="Latency in milliseconds.")
    requested_engine: Optional[str] = Field(default=None, description="Engine explicitly requested by caller if specified.")
    fallback_used: bool = Field(default=False, description="Whether an automatic fallback engine was used.")


class OCRMetadata(BaseModel):
    """Metadata detailing OCR engine provenance, version, and execution fallback status."""
    engine_name: str = Field(description="Name of the OCR engine that actually processed the image.")
    engine_version: str = Field(description="Version string of the OCR engine library.")
    is_mock: bool = Field(description="True if mock engine was used (strictly for tests/demos). Never represented as real OCR.")
    requested_engine: Optional[str] = Field(default=None, description="Engine explicitly requested by caller if specified.")
    fallback_used: bool = Field(default=False, description="True if an automatic fallback occurred.")
    mean_confidence: float = Field(ge=0.0, le=1.0, description="Confidence reported by the executing engine.")
    execution_time_ms: int = Field(ge=0, description="Execution latency of the OCR step in milliseconds.")


