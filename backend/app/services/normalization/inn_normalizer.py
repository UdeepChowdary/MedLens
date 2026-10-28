"""INN normalization pipeline: alias lookup → RapidFuzz fuzzy matching → verification states."""

import re
from typing import Optional, List, Tuple
from difflib import SequenceMatcher
from app.schemas.common import VerificationState

# Try importing rapidfuzz; fall back gracefully if not installed
try:
    from rapidfuzz import fuzz, process as rfprocess
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

# Pharmacopeial suffix patterns to normalize during lookup (not to strip blindly!)
PHARMACOPEIAL_SUFFIXES = re.compile(
    r'\b(ip|bp|usp|ep|jp|in)\b\.?$', re.IGNORECASE
)
SALT_PATTERNS = re.compile(
    r'\b(hydrochloride|hcl|sodium|potassium|maleate|tartrate|besylate|besilate'
    r'|fumarate|succinate|phosphate|sulfate|sulphate|trihydrate|dihydrate'
    r'|sesquihydrate|acetate|citrate|gluconate|malate)\b',
    re.IGNORECASE
)


class NormalizationResult:
    """Result of INN normalization for a single extracted candidate."""
    
    def __init__(
        self,
        raw_text: str,
        canonical_name: Optional[str],
        ingredient_id: Optional[str],
        verification_state: VerificationState,
        match_method: str,
        match_score: float,
        salt_form_preserved: Optional[str] = None,
        candidates: Optional[List[Tuple[str, float]]] = None,
        abstention_reason: Optional[str] = None,
    ):
        self.raw_text = raw_text
        self.canonical_name = canonical_name
        self.ingredient_id = ingredient_id
        self.verification_state = verification_state
        self.match_method = match_method
        self.match_score = match_score
        self.salt_form_preserved = salt_form_preserved
        self.candidates = candidates or []
        self.abstention_reason = abstention_reason


class INNNormalizer:
    """
    Multi-tier INN normalization pipeline.
    
    Resolution priority (per Blueprint §7.2):
    1. Exact normalized alias lookup (DB-backed)
    2. Pharmacopeial suffix stripped exact match 
    3. RapidFuzz token_sort_ratio >= 88 → candidate (never auto-verified from fuzzy alone)
    4. Fuzzy 70-87 → needs_confirmation with candidates
    5. < 70 → unable_to_verify
    """
    
    def __init__(self, alias_map: dict):
        """
        alias_map: dict mapping normalized_alias (lowercase) → (canonical_name, ingredient_id)
        Built from the database at startup.
        """
        self.alias_map = alias_map  # {normalized_alias: (preferred_name, ingredient_id)}
    
    def _normalize_text(self, text: str) -> str:
        """Safe, non-destructive text cleanup for matching."""
        text = text.strip().lower()
        # Remove pharmacopeial standard suffixes only for matching (not for display)
        text = PHARMACOPEIAL_SUFFIXES.sub('', text).strip()
        # Collapse internal whitespace
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _extract_salt_form(self, text: str) -> Optional[str]:
        """Extracts salt/form information for preservation (not stripping)."""
        match = SALT_PATTERNS.search(text)
        return match.group(0) if match else None
    
    def normalize(self, raw_text: str) -> NormalizationResult:
        """
        Normalizes a single raw ingredient span to a canonical INN.
        Returns explicit verification state; never silently invents identity.
        """
        if not raw_text or not raw_text.strip():
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=None,
                ingredient_id=None,
                verification_state=VerificationState.UNABLE_TO_VERIFY,
                match_method="none",
                match_score=0.0,
                abstention_reason="Empty or blank input text.",
            )
        
        salt_form = self._extract_salt_form(raw_text)
        normalized = self._normalize_text(raw_text)
        
        # Tier 1: Exact alias lookup (highest confidence)
        if normalized in self.alias_map:
            canonical, ing_id = self.alias_map[normalized]
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=canonical,
                ingredient_id=ing_id,
                verification_state=VerificationState.VERIFIED,
                match_method="exact_alias",
                match_score=1.0,
                salt_form_preserved=salt_form,
            )
        
        # Tier 2: Also try the full raw text (lowercase) as direct lookup
        raw_lower = raw_text.strip().lower()
        if raw_lower in self.alias_map:
            canonical, ing_id = self.alias_map[raw_lower]
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=canonical,
                ingredient_id=ing_id,
                verification_state=VerificationState.VERIFIED,
                match_method="exact_raw",
                match_score=1.0,
                salt_form_preserved=salt_form,
            )
        
        # Tier 3: Fuzzy candidate search
        alias_keys = list(self.alias_map.keys())
        
        if RAPIDFUZZ_AVAILABLE and alias_keys:
            results = rfprocess.extract(
                normalized,
                alias_keys,
                scorer=fuzz.token_sort_ratio,
                limit=5,
                score_cutoff=60,
            )
            candidates = [(k, s / 100.0) for k, s, _ in results]
        else:
            # Fallback: Python stdlib SequenceMatcher
            scored = [
                (k, SequenceMatcher(None, normalized, k).ratio())
                for k in alias_keys
            ]
            scored.sort(key=lambda x: x[1], reverse=True)
            candidates = [(k, s) for k, s in scored[:5] if s >= 0.60]
        
        if not candidates:
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=None,
                ingredient_id=None,
                verification_state=VerificationState.UNABLE_TO_VERIFY,
                match_method="fuzzy_no_match",
                match_score=0.0,
                abstention_reason=f"No candidate with sufficient similarity found for '{raw_text}'.",
            )
        
        best_key, best_score = candidates[0]
        best_canonical, best_id = self.alias_map[best_key]
        
        if best_score >= 0.88:
            # High similarity → partially_verified (candidate, needs confirmation)
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=best_canonical,
                ingredient_id=best_id,
                verification_state=VerificationState.PARTIALLY_VERIFIED,
                match_method="fuzzy_high",
                match_score=best_score,
                salt_form_preserved=salt_form,
                candidates=candidates,
            )
        elif best_score >= 0.70:
            # Medium similarity → needs_confirmation
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=best_canonical,
                ingredient_id=best_id,
                verification_state=VerificationState.NEEDS_CONFIRMATION,
                match_method="fuzzy_medium",
                match_score=best_score,
                salt_form_preserved=salt_form,
                candidates=candidates,
            )
        else:
            return NormalizationResult(
                raw_text=raw_text,
                canonical_name=None,
                ingredient_id=None,
                verification_state=VerificationState.UNABLE_TO_VERIFY,
                match_method="fuzzy_low",
                match_score=best_score,
                abstention_reason=f"Best match score {best_score:.2f} is below minimum verification threshold.",
            )
    
    def normalize_batch(self, raw_texts: List[str]) -> List[NormalizationResult]:
        """Normalizes multiple raw ingredient spans."""
        return [self.normalize(t) for t in raw_texts]


def build_alias_map_from_db_records(alias_records) -> dict:
    """
    Builds the in-memory alias lookup map from database IngredientAlias records.
    Call this at application startup or on first request.
    
    alias_records: list of IngredientAlias ORM objects with .normalized_alias, 
                   .ingredient.preferred_name, .ingredient_id
    Returns: {normalized_alias: (preferred_name, ingredient_id)}
    """
    alias_map = {}
    for record in alias_records:
        key = record.normalized_alias.lower().strip()
        alias_map[key] = (record.ingredient.preferred_name, record.ingredient_id)
    return alias_map

