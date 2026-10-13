"""Schemas for raw OCR and ML extracted entities."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Domain-specific entity labels per Blueprint Section 06."""
    BRAND = "BRAND"
    PRODUCT_NAME = "PRODUCT_NAME"
    INGREDIENT = "INGREDIENT"
    SALT_FORM = "SALT_FORM"
    STRENGTH = "STRENGTH"
    CONCENTRATION = "CONCENTRATION"
    STRENGTH_BASIS = "STRENGTH_BASIS"
    DOSAGE_FORM = "DOSAGE_FORM"
    ROUTE = "ROUTE"
    RELEASE_TYPE = "RELEASE_TYPE"
    COMPOSITION_HEADER = "COMPOSITION_HEADER"


class ExtractedEntity(BaseModel):
    """Field-level token or span extracted from packaging text."""
    entity_type: EntityType = Field(description="Classified entity label.")
    raw_text: str = Field(description="Exact verbatim text parsed from the packaging image.")
    normalized_candidate: Optional[str] = Field(default=None, description="Initial normalized representation.")
    bbox: Optional[List[int]] = Field(default=None, description="Bounding box coordinates [x1, y1, x2, y2].")
    confidence: float = Field(ge=0.0, le=1.0, description="Model/extractor confidence score.")
    verification_status: str = Field(default="candidate", description="Verification state of this field.")
