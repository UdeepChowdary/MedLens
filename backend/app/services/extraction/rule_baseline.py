"""Deterministic rule-based medicine ingredient extraction baseline per Blueprint Section 6.3."""

import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.schemas.common import VerificationState


class ParsedStrength(BaseModel):
    """Normalized strength magnitude and unit."""
    raw_text: str
    numeric_value: float
    unit: str
    basis: Optional[str] = None


class ExtractedCandidate(BaseModel):
    """Identified entity token from rule-based sequence labeling."""
    label: str  # INGREDIENT, STRENGTH, SALT_FORM, DOSAGE_FORM, etc.
    raw_text: str
    normalized_value: Optional[str] = None
    start_char: int
    end_char: int
    confidence: float = 1.0


class RuleExtractionResult(BaseModel):
    """Structured extraction outcome from rule-based baseline."""
    verification_status: VerificationState
    composition_header_found: bool
    composition_header_text: Optional[str] = None
    dosage_form: Optional[str] = None
    strength_basis: Optional[str] = None
    ingredients: List[Dict[str, Any]] = Field(default_factory=list)
    extracted_entities: List[ExtractedCandidate] = Field(default_factory=list)
    raw_text: str
    abstention_reason: Optional[str] = None


# Curated baseline active ingredient dictionary and verified synonym mappings
KNOWN_INGREDIENTS = {
    "paracetamol": "Paracetamol",
    "acetaminophen": "Paracetamol",
    "apap": "Paracetamol",
    "ibuprofen": "Ibuprofen",
    "amoxicillin": "Amoxicillin",
    "clavulanic acid": "Clavulanic Acid",
    "potassium clavulanate": "Clavulanic Acid",
    "clavulanate": "Clavulanic Acid",
    "cetirizine": "Cetirizine",
    "azithromycin": "Azithromycin",
    "metformin": "Metformin",
    "atorvastatin": "Atorvastatin",
    "omeprazole": "Omeprazole",
    "pantoprazole": "Pantoprazole",
}

SALT_TERMS = {
    "hydrochloride": "Hydrochloride",
    "hcl": "Hydrochloride",
    "trihydrate": "Trihydrate",
    "potassium": "Potassium Salt",
    "sodium": "Sodium Salt",
    "maleate": "Maleate",
    "phosphate": "Phosphate",
    "succinate": "Succinate",
    "ip": "Indian Pharmacopoeia",
    "bp": "British Pharmacopoeia",
    "usp": "United States Pharmacopeia",
}

DOSAGE_FORMS = {
    "film-coated tablet": "Film-coated Tablet",
    "uncoated tablet": "Uncoated Tablet",
    "tablet": "Tablet",
    "tablets": "Tablet",
    "capsule": "Capsule",
    "capsules": "Capsule",
    "syrup": "Syrup",
    "suspension": "Suspension",
    "injection": "Injection",
    "ointment": "Ointment",
    "cream": "Cream",
    "gel": "Gel",
    "drops": "Drops",
}

HEADER_PATTERNS = [
    re.compile(r"(each\s+(?:film[- ]coated\s+|uncoated\s+)?(?:tablet|capsule|5\s*ml|ml)\s+contains:?)", re.IGNORECASE),
    re.compile(r"(composition\s*:)", re.IGNORECASE),
    re.compile(r"(active\s+ingredients?\s*:)", re.IGNORECASE),
]

STRENGTH_REGEX = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mcg|ug|g|ml|% w/v|% w/w|iu)\b", re.IGNORECASE
)


class RuleBasedExtractor:
    """Deterministic, rule-based ingredient and entity extractor."""

    def __init__(self, custom_ingredients: Optional[Dict[str, str]] = None):
        self.ingredients_dict = {**KNOWN_INGREDIENTS, **(custom_ingredients or {})}

    def extract(self, text: str) -> RuleExtractionResult:
        """Extracts structured entities, compositions, and strengths from label transcription."""
        if not text or not text.strip():
            return RuleExtractionResult(
                verification_status=VerificationState.UNABLE_TO_VERIFY,
                composition_header_found=False,
                raw_text="",
                abstention_reason="Input text is empty or illegible.",
            )

        extracted_entities: List[ExtractedCandidate] = []
        clean_text = text.strip()

        # 1. Detect Composition Header
        header_text = None
        strength_basis = None
        for pattern in HEADER_PATTERNS:
            match = pattern.search(clean_text)
            if match:
                header_text = match.group(1)
                extracted_entities.append(
                    ExtractedCandidate(
                        label="COMPOSITION_HEADER",
                        raw_text=header_text,
                        start_char=match.start(),
                        end_char=match.end(),
                        confidence=0.98,
                    )
                )
                # Derive strength basis from header if present
                lower_hdr = header_text.lower()
                if "tablet" in lower_hdr:
                    strength_basis = "per tablet"
                elif "capsule" in lower_hdr:
                    strength_basis = "per capsule"
                elif "5 ml" in lower_hdr or "5ml" in lower_hdr:
                    strength_basis = "per 5 mL"
                elif "ml" in lower_hdr:
                    strength_basis = "per mL"
                break

        # 2. Detect Dosage Form
        dosage_form = None
        for form_str, form_norm in DOSAGE_FORMS.items():
            pattern = re.compile(rf"\b({re.escape(form_str)})\b", re.IGNORECASE)
            match = pattern.search(clean_text)
            if match:
                dosage_form = form_norm
                extracted_entities.append(
                    ExtractedCandidate(
                        label="DOSAGE_FORM",
                        raw_text=match.group(1),
                        normalized_value=form_norm,
                        start_char=match.start(),
                        end_char=match.end(),
                        confidence=0.95,
                    )
                )
                break

        # 3. Detect Ingredients & Strengths
        ingredient_matches: List[Tuple[str, str, int, int]] = []
        # Sort keys by length descending to match multi-word phrases first
        for key in sorted(self.ingredients_dict.keys(), key=len, reverse=True):
            pattern = re.compile(rf"\b({re.escape(key)})\b", re.IGNORECASE)
            for m in pattern.finditer(clean_text):
                canonical = self.ingredients_dict[key]
                ingredient_matches.append((m.group(1), canonical, m.start(), m.end()))

        # Deduplicate overlapping ingredient matches
        deduped_ingredients = []
        occupied_spans = set()
        for raw, canonical, start, end in sorted(ingredient_matches, key=lambda x: (x[2], -(x[3] - x[2]))):
            span_indices = set(range(start, end))
            if not (span_indices & occupied_spans):
                deduped_ingredients.append((raw, canonical, start, end))
                occupied_spans.update(span_indices)
                extracted_entities.append(
                    ExtractedCandidate(
                        label="INGREDIENT",
                        raw_text=raw,
                        normalized_value=canonical,
                        start_char=start,
                        end_char=end,
                        confidence=0.96,
                    )
                )

        # 4. Detect Strengths
        strength_matches: List[Tuple[str, float, str, int, int]] = []
        for m in STRENGTH_REGEX.finditer(clean_text):
            raw_str = m.group(0)
            val = float(m.group(1))
            unit = m.group(2).lower()
            strength_matches.append((raw_str, val, unit, m.start(), m.end()))
            extracted_entities.append(
                ExtractedCandidate(
                    label="STRENGTH",
                    raw_text=raw_str,
                    normalized_value=f"{val:g} {unit}",
                    start_char=m.start(),
                    end_char=m.end(),
                    confidence=0.98,
                )
            )

        # 5. Detect Salt Forms
        for salt_key, salt_norm in SALT_TERMS.items():
            pattern = re.compile(rf"\b({re.escape(salt_key)})\b", re.IGNORECASE)
            for m in pattern.finditer(clean_text):
                extracted_entities.append(
                    ExtractedCandidate(
                        label="SALT_FORM",
                        raw_text=m.group(1),
                        normalized_value=salt_norm,
                        start_char=m.start(),
                        end_char=m.end(),
                        confidence=0.90,
                    )
                )

        # 6. Associate Ingredients with their proximate strengths
        compositions_result = []
        for raw_ing, canonical_ing, ing_start, ing_end in deduped_ingredients:
            # Find the closest strength following the ingredient within 80 characters
            best_strength = None
            min_dist = 999999
            for raw_str, val, unit, str_start, str_end in strength_matches:
                if str_start >= ing_start:
                    dist = str_start - ing_end
                    if dist < min_dist and dist < 120:
                        min_dist = dist
                        best_strength = ParsedStrength(
                            raw_text=raw_str,
                            numeric_value=val,
                            unit=unit,
                            basis=strength_basis,
                        )

            compositions_result.append(
                {
                    "raw_ingredient": raw_ing,
                    "canonical_name": canonical_ing,
                    "strength": best_strength.model_dump() if best_strength else None,
                }
            )

        # Deduplicate compositions sharing the same canonical ingredient and strength (e.g. "eq. to" clauses)
        seen_compositions = set()
        unique_compositions = []
        for comp in compositions_result:
            s_dict = comp["strength"]
            s_tuple = (s_dict["numeric_value"], s_dict["unit"]) if s_dict else None
            key = (comp["canonical_name"], s_tuple)
            if key not in seen_compositions:
                seen_compositions.add(key)
                unique_compositions.append(comp)
        compositions_result = unique_compositions

        # 7. Abstention & Verification Determination
        if not deduped_ingredients:
            return RuleExtractionResult(
                verification_status=VerificationState.NEEDS_CONFIRMATION,
                composition_header_found=bool(header_text),
                composition_header_text=header_text,
                dosage_form=dosage_form,
                strength_basis=strength_basis,
                ingredients=[],
                extracted_entities=extracted_entities,
                raw_text=clean_text,
                abstention_reason="No recognized active pharmaceutical ingredient detected in text.",
            )

        all_have_strengths = all(c["strength"] is not None for c in compositions_result)
        if all_have_strengths and header_text:
            status = VerificationState.VERIFIED
        elif all_have_strengths:
            status = VerificationState.PARTIALLY_VERIFIED
        else:
            status = VerificationState.NEEDS_CONFIRMATION

        return RuleExtractionResult(
            verification_status=status,
            composition_header_found=bool(header_text),
            composition_header_text=header_text,
            dosage_form=dosage_form,
            strength_basis=strength_basis,
            ingredients=compositions_result,
            extracted_entities=extracted_entities,
            raw_text=clean_text,
        )
