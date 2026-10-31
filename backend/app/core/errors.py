"""Standardized exception hierarchy and error models for MedLens."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Unified error response contract."""
    error_code: str = Field(description="Machine-readable snake_case or upper_snake error code.")
    message: str = Field(description="Human-readable explanation of the failure.")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Diagnostic contextual metadata.")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp of occurrence."
    )


class MedLensException(Exception):
    """Base domain exception for all MedLens business failures."""
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class ImageValidationError(MedLensException):
    """Raised when an uploaded packaging image fails format, size, or quality checks."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ERR_IMAGE_VALIDATION_FAILED",
            status_code=400,
            details=details,
        )


class AnalysisNotFoundError(MedLensException):
    """Raised when an analysis ID is not found in the persistence store."""
    def __init__(self, analysis_id: str):
        super().__init__(
            message=f"Analysis with ID '{analysis_id}' was not found.",
            error_code="ERR_ANALYSIS_NOT_FOUND",
            status_code=404,
            details={"analysis_id": analysis_id},
        )


class ProductNotFoundError(MedLensException):
    """Raised when a queried product is not found."""
    def __init__(self, product_id: str):
        super().__init__(
            message=f"Product with ID '{product_id}' was not found.",
            error_code="ERR_PRODUCT_NOT_FOUND",
            status_code=404,
            details={"product_id": product_id},
        )


class VerificationError(MedLensException):
    """Raised when verification constraints are violated or ambiguity cannot be resolved."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="ERR_VERIFICATION_FAILED",
            status_code=422,
            details=details,
        )


class OCREngineUnavailableError(MedLensException):
    """Raised when real OCR engine dependencies are not installed and mock OCR is not explicitly requested."""
    def __init__(
        self,
        message: str = "No real OCR engine (PaddleOCR, Tesseract) is available in this environment.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="ERR_OCR_ENGINE_UNAVAILABLE",
            status_code=503,
            details=details or {
                "hint": "Install PaddleOCR ('pip install paddlepaddle paddleocr') or Tesseract-OCR, or explicitly request 'mock' for tests/demos."
            },
        )


class OCRExecutionError(MedLensException):
    """Raised when an OCR engine encounters an unrecoverable failure during inference."""
    def __init__(
        self,
        message: str = "OCR extraction failed during inference execution.",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="ERR_OCR_EXECUTION_FAILED",
            status_code=500,
            details=details,
        )

