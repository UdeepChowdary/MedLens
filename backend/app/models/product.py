"""SQLAlchemy ORM models for products, ingredients, compositions, and aliases."""

import uuid
from typing import List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class Product(Base):
    """Commercial pharmaceutical presentation in a defined market."""
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    brand_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dosage_form: Mapped[str] = mapped_column(String(100), nullable=False)
    route: Mapped[str] = mapped_column(String(50), default="Oral")
    release_type: Mapped[str] = mapped_column(String(50), default="Immediate Release")
    country_code: Mapped[str] = mapped_column(String(10), default="IN")
    status: Mapped[str] = mapped_column(String(50), default="approved")

    # Relationships
    compositions: Mapped[List["ProductIngredient"]] = relationship(
        "ProductIngredient", back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )


class Ingredient(Base):
    """Canonical active ingredient or chemical moiety."""
    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    preferred_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    chemical_identifier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    drug_class: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    standard_mechanism: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_daily_dose_mg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    aliases: Mapped[List["IngredientAlias"]] = relationship(
        "IngredientAlias", back_populates="ingredient", cascade="all, delete-orphan", lazy="selectin"
    )
    product_associations: Mapped[List["ProductIngredient"]] = relationship(
        "ProductIngredient", back_populates="ingredient"
    )


class ProductIngredient(Base):
    """Many-to-many composition mapping between commercial product and ingredients."""
    __tablename__ = "product_ingredients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id: Mapped[str] = mapped_column(String(36), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    raw_label_text: Mapped[str] = mapped_column(String(255), nullable=False)
    strength_numeric: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    strength_unit: Mapped[str] = mapped_column(String(50), nullable=False)
    strength_basis: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", "is_active", name="uq_product_ingredient_role"),
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="compositions")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="product_associations", lazy="selectin")


class IngredientAlias(Base):
    """Verified alternative names, salt variations, and common typo variants."""
    __tablename__ = "ingredient_aliases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ingredient_id: Mapped[str] = mapped_column(String(36), ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    alias_text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_alias: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    alias_type: Mapped[str] = mapped_column(String(50), default="synonym")

    # Relationships
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="aliases")
