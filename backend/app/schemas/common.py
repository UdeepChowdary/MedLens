"""Common enumerated types and value objects."""

from enum import Enum


class VerificationState(str, Enum):
    """Four-state verification model per Blueprint Section 07."""
    VERIFIED = "verified"                     # All identity & evidence rules fully meet constraints
    PARTIALLY_VERIFIED = "partially_verified" # Some fields verified; others unresolved
    NEEDS_CONFIRMATION = "needs_confirmation" # Ambiguity present; user must confirm or correct
    UNABLE_TO_VERIFY = "unable_to_verify"     # Insufficient or conflicting evidence


class RoleType(str, Enum):
    """Role of an ingredient within the pharmaceutical formulation."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNKNOWN = "unknown"


class ComparisonOutcome(str, Enum):
    """Field-level outcome of deterministic comparison per Blueprint Section 09."""
    MATCH = "match"
    DIFFERENCE = "difference"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"
    NOT_APPLICABLE = "not_applicable"


class InteractionSeverity(str, Enum):
    """Documented severity level for drug-drug interactions."""
    MAJOR = "major"
    MODERATE = "moderate"
    MINOR = "minor"
    UNKNOWN = "unknown"
