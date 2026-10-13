"""Schemas for drug-drug interaction lookups."""

from typing import List, Optional
from pydantic import BaseModel, Field
from .common import InteractionSeverity


class InteractionRecord(BaseModel):
    """Documented pairwise interaction between two canonical ingredients."""
    ingredient_a: str = Field(description="Canonical INN of first drug.")
    ingredient_b: str = Field(description="Canonical INN of second drug.")
    severity: InteractionSeverity = Field(default=InteractionSeverity.UNKNOWN, description="Severity rating.")
    clinical_effect: str = Field(description="Documented adverse pharmacological mechanism or effect.")
    evidence_source: str = Field(description="Clinical monograph citation.")
    documented_date: Optional[str] = Field(default=None, description="Source publication date.")


class InteractionCheckResponse(BaseModel):
    """Result of cross-referencing two or more medications for documented interactions."""
    has_documented_interactions: bool = Field(description="True if one or more interaction records were found.")
    coverage_status: str = Field(description="Coverage completeness, e.g. 'consulted_curated_database'.")
    interactions: List[InteractionRecord] = Field(default_factory=list, description="Found interaction records.")
    limitations: List[str] = Field(
        default_factory=lambda: [
            "Absence of an interaction record does not prove no interaction exists.",
            "Lookup is bounded by the sources currently in the MedLens reference database."
        ],
        description="Explicit notice preventing false 'all clear' assumptions."
    )
    sources: List[str] = Field(default_factory=list, description="Referenced database sources.")
