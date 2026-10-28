"""Pydantic v2 schemas for request and response contracts."""

from .common import (
    VerificationState,
    RoleType,
    ComparisonOutcome,
    InteractionSeverity,
)
from .entity import EntityType, ExtractedEntity
from .product import (
    StrengthSchema,
    EvidenceSourceSchema,
    IngredientReport,
    SafetyProfile,
    ProductReport,
)
from .analysis import (
    MultidimensionalConfidence,
    AnalysisCreateResponse,
    AnalysisResponse,
)
from .comparison import (
    AttributeComparison,
    ComparisonResponse,
    StrengthDelta,
)
from .interaction import (
    InteractionRecord,
    InteractionCheckResponse,
)
from .image import ImageQualityReport
from .ocr import BoundingBox, OCRToken, OCRLine, OCRResult

__all__ = [
    "VerificationState",
    "RoleType",
    "ComparisonOutcome",
    "InteractionSeverity",
    "EntityType",
    "ExtractedEntity",
    "StrengthSchema",
    "EvidenceSourceSchema",
    "IngredientReport",
    "SafetyProfile",
    "ProductReport",
    "MultidimensionalConfidence",
    "AnalysisCreateResponse",
    "AnalysisResponse",
    "AttributeComparison",
    "ComparisonResponse",
    "StrengthDelta",
    "InteractionRecord",
    "InteractionCheckResponse",
    "ImageQualityReport",
    "BoundingBox",
    "OCRToken",
    "OCRLine",
    "OCRResult",
]
