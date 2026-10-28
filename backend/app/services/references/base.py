"""Base interface and schema contracts for external clinical reference adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReferenceData(BaseModel):
    """Normalized structured data contract returned by all external reference adapters."""
    source_name: str = Field(description="Authoritative reference provider name.")
    source_url: str = Field(description="Canonical URL to online clinical monograph.")
    source_id: str = Field(description="Unique record identifier within source namespace.")
    jurisdiction: str = Field(description="Regulatory jurisdiction (IN, US, GLOBAL).")
    canonical_name: str = Field(description="Standardized International Nonproprietary Name.")
    chemical_identifier: Optional[str] = Field(default=None, description="Chemical identifier (e.g. PubChem CID).")
    smiles: Optional[str] = Field(default=None, description="Canonical chemical SMILES notation.")
    molecular_formula: Optional[str] = Field(default=None, description="Hill system chemical formula.")
    indications: List[str] = Field(default_factory=list, description="Approved therapeutic indications.")
    contraindications: List[str] = Field(default_factory=list, description="Documented clinical contraindications.")
    warnings: List[str] = Field(default_factory=list, description="Black box and usage safety warnings.")
    adverse_reactions: List[str] = Field(default_factory=list, description="Documented adverse reactions.")
    raw_payload: Optional[Dict[str, Any]] = Field(default=None, description="Raw provider JSON response.")
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 retrieval timestamp."
    )


class BaseReferenceAdapter(ABC):
    """Abstract base class for external monograph and chemical reference providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the reference provider."""
        pass

    @property
    @abstractmethod
    def jurisdiction(self) -> str:
        """Regulatory scope: IN, US, or GLOBAL."""
        pass

    @abstractmethod
    async def lookup(self, drug_name: str) -> Optional[ReferenceData]:
        """Queries the external source for clinical monograph or chemical data.

        Returns None if drug is not found or source is unreachable.
        Must never raise unhandled network exceptions.
        """
        pass

