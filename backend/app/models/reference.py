"""SQLAlchemy ORM model for external reference caching with TTL support."""

from datetime import datetime, timezone
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.database.session import Base


class ExternalReferenceCache(Base):
    """Local persistent cache for external regulatory and pharmacopeial APIs (7-day TTL)."""
    __tablename__ = "external_reference_cache"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    drug_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    data_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True,
    )
