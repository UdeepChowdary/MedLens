"""SQLAlchemy ORM models for ephemeral analysis jobs, token extractions, and model versions."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Analysis(Base):
    """Analysis job record with SHA-256 image fingerprint and processing telemetry."""
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[str] = mapped_column(String(50), default="received")
    image_sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    processing_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    confidence_aggregate: Mapped[float] = mapped_column(Float, default=0.0)
    model_version: Mapped[str] = mapped_column(String(50), default="v0.1.0")
    created_at: Mapped[str] = mapped_column(
        String(50), default=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Relationships
    entities: Mapped[List["ExtractedEntityModel"]] = relationship(
        "ExtractedEntityModel", back_populates="analysis", cascade="all, delete-orphan", lazy="selectin"
    )
    sources: Mapped[List["AnalysisSource"]] = relationship(
        "AnalysisSource", back_populates="analysis", cascade="all, delete-orphan", lazy="selectin"
    )


class ExtractedEntityModel(Base):
    """Field-level tokens and spans extracted from image OCR."""
    __tablename__ = "extracted_entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_text: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_candidate: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bbox_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    verification_status: Mapped[str] = mapped_column(String(50), default="candidate")

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="entities")


class AnalysisSource(Base):
    """Junction recording which evidence sources supported an analysis."""
    __tablename__ = "analysis_sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id: Mapped[str] = mapped_column(String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    query_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="sources")


class ModelVersion(Base):
    """Metadata tracking machine learning model weights, tokenizers, and dataset versions."""
    __tablename__ = "model_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    artifact_location: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
