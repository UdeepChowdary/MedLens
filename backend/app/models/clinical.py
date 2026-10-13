"""SQLAlchemy ORM models for sources, clinical monographs, and drug interactions."""

import uuid
from typing import Optional
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Source(Base):
    """Evidence provenance and clinical reference metadata."""
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_name: Mapped[str] = mapped_column(String(150), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), default="monograph")
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(50), default="GLOBAL")
    retrieval_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class ClinicalInformation(Base):
    """Source-backed clinical claims (purpose, precautions, contraindications, adverse effects)."""
    __tablename__ = "clinical_information"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'product' or 'ingredient'
    subject_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)      # 'purpose', 'precaution', 'contraindication', 'adverse_effect'
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    source: Mapped["Source"] = relationship("Source", lazy="selectin")


class DrugInteraction(Base):
    """Documented pairwise interaction between two canonical ingredients."""
    __tablename__ = "drug_interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ingredient_a_id: Mapped[str] = mapped_column(String(36), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_b_id: Mapped[str] = mapped_column(String(36), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), default="unknown")
    clinical_effect: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    source: Mapped["Source"] = relationship("Source", lazy="selectin")
