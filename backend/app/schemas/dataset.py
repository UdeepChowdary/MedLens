"""Pydantic v2 schemas for medicine label dataset annotations, entities, and quality metrics."""

from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator


class DatasetEntityLabel(str, Enum):
    """Domain token classification labels defined in Blueprint Section 6.2."""
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


class PackagingType(str, Enum):
    """Physical pharmaceutical packaging presentation."""
    BLISTER_FOIL = "blister_foil"
    STRIP_PACK = "strip_pack"
    PAPER_BOX = "paper_box"
    BOTTLE_LABEL = "bottle_label"
    TUBE = "tube"
    SACHET = "sachet"
    VIAL = "vial"


class ReviewStatus(str, Enum):
    """Ground truth human verification lifecycle."""
    DRAFT = "draft"
    VERIFIED_BY_HUMAN = "verified_by_human"
    FLAGGED_FOR_REVIEW = "flagged_for_review"


class ImageDimensions(BaseModel):
    """Image pixel spatial dimensions."""
    width: int = Field(gt=0, description="Image width in pixels.")
    height: int = Field(gt=0, description="Image height in pixels.")


class ProvenanceMetadata(BaseModel):
    """Origin, licensing, and annotator provenance."""
    source: str = Field(description="Data origin, e.g. 'NIH DailyMed', 'openFDA', 'MedLens Clinical Lab'.")
    license: str = Field(description="Usage license, e.g. 'CC-BY-4.0', 'Public Domain (US Gov)', 'Proprietary Research'.")
    annotator_id: str = Field(description="Unique identifier of clinical human annotator.")
    verified_by_human: bool = Field(default=False, description="Whether record underwent manual clinical review.")
    date_annotated: str = Field(description="ISO-8601 creation timestamp.")
    notes: Optional[str] = Field(default=None, description="Clinical annotator notes or packaging edge cases.")


class QualityFlags(BaseModel):
    """Visual challenge and degradation flags observed on the packaging surface."""
    glare: bool = Field(default=False, description="Specular metallic foil reflection present.")
    blur: bool = Field(default=False, description="Motion or focus blur detected.")
    low_contrast: bool = Field(default=False, description="Subdued or metallic printing on similar background.")
    small_text: bool = Field(default=False, description="Micro-typography below 6pt font size.")
    occlusion: bool = Field(default=False, description="Obstruction by fold, tear, or sticker.")
    skew_angle: Optional[float] = Field(default=0.0, description="Estimated rotation angle in degrees.")


class EntityAnnotation(BaseModel):
    """Individual labeled token or phrase with normalized bounding box."""
    label: DatasetEntityLabel = Field(description="Token category label.")
    raw_text: str = Field(min_length=1, description="Verbatim text exactly as printed on packaging.")
    normalized_value: Optional[str] = Field(default=None, description="Canonical representation if normalized.")
    bbox: Tuple[int, int, int, int] = Field(
        description="Normalized bounding box coordinates [ymin, xmin, ymax, xmax] in range 0..1000."
    )
    char_span: Optional[Tuple[int, int]] = Field(
        default=None, description="Start and end character offsets within transcription."
    )

    @field_validator("bbox")
    @classmethod
    def validate_bbox_bounds(cls, v: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        ymin, xmin, ymax, xmax = v
        if not (0 <= ymin <= 1000 and 0 <= xmin <= 1000 and 0 <= ymax <= 1000 and 0 <= xmax <= 1000):
            raise ValueError(f"BBox coordinates must be within 0..1000 range. Got: {v}")
        if ymin >= ymax:
            raise ValueError(f"ymin ({ymin}) must be strictly less than ymax ({ymax}).")
        if xmin >= xmax:
            raise ValueError(f"xmin ({xmin}) must be strictly less than xmax ({xmax}).")
        return v


class ImageMetadata(BaseModel):
    """Core image file descriptors and hash index."""
    image_id: str = Field(description="Deterministic unique ID of image, e.g. img-dolo-650-front.")
    file_name: str = Field(description="Image file name with extension, e.g. 'dolo_650_strip.png'.")
    format: str = Field(description="Image format: png, jpeg, webp.")
    dimensions: ImageDimensions = Field(description="Width and height in pixels.")
    sha256: str = Field(min_length=64, max_length=64, description="SHA-256 cryptographic digest of image file.")
    packaging_type: PackagingType = Field(description="Physical packaging category.")
    image_side: Optional[str] = Field(
        default="back",
        description="Packaging face or aspect photographed: 'back', 'front', 'side', 'carton_flap', 'unspecified'.",
    )
    product_family: str = Field(description="Grouping key for leakage prevention, e.g. 'dolo-650', 'augmentin-625'.")
    brand_name: Optional[str] = Field(default=None, description="Commercial brand name if identified.")
    manufacturer: Optional[str] = Field(default=None, description="Manufacturing pharmaceutical company.")
    provenance: ProvenanceMetadata = Field(description="Licensing and annotator provenance.")


class PackagingAnnotationDoc(BaseModel):
    """Complete ground-truth JSON annotation schema for a single medicine image."""
    schema_version: str = Field(default="1.0.0", description="Annotation schema semantic version.")
    image_metadata: ImageMetadata = Field(description="Image descriptors and file identity.")
    quality_flags: QualityFlags = Field(default_factory=QualityFlags, description="Visual degradation attributes.")
    transcription: str = Field(description="Complete verbatim transcript of all readable text in reading order.")
    composition_text: Optional[str] = Field(
        default=None,
        description="Verbatim visible composition text exactly as printed on packaging.",
    )
    entities: List[EntityAnnotation] = Field(default_factory=list, description="Extracted entity spans.")
    has_uncertainty: bool = Field(
        default=False,
        description="Whether human annotator encountered ambiguous, degraded, or uncertain text.",
    )
    uncertainty_notes: Optional[str] = Field(
        default=None,
        description="Clinical annotator notes detailing uncertain or unreadable characters/spans.",
    )
    canonical_product_id: Optional[str] = Field(default=None, description="Linked canonical product ID in database.")
    review_status: ReviewStatus = Field(default=ReviewStatus.DRAFT, description="Human verification review status.")
