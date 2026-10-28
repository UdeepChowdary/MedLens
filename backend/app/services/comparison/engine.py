"""Deterministic medicine comparison engine per Blueprint Section 09."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from app.models.clinical import DrugInteraction
from app.models.product import Product, ProductIngredient
from app.schemas.common import ComparisonOutcome
from app.schemas.comparison import (
    AttributeComparison,
    ComparisonResponse,
    StrengthDelta,
)

logger = logging.getLogger(__name__)

# Unit conversion factors to milligrams (mg)
MASS_CONVERSION_FACTORS: Dict[str, float] = {
    "g": 1000.0,
    "gm": 1000.0,
    "gram": 1000.0,
    "grams": 1000.0,
    "mg": 1.0,
    "milligram": 1.0,
    "milligrams": 1.0,
    "mcg": 0.001,
    "ug": 0.001,
    "microgram": 0.001,
    "micrograms": 0.001,
}

# Recognized common excipient allergens
COMMON_EXCIPIENT_ALLERGENS: Dict[str, str] = {
    "lactose": "Lactose Monohydrate (potential risk for lactose intolerance or galactosemia)",
    "tartrazine": "Tartrazine / FD&C Yellow No. 5 (known hypersensitivity / bronchospasm trigger)",
    "aspartame": "Aspartame (contains phenylalanine; contraindicated in phenylketonuria / PKU)",
    "gluten": "Gluten-containing starch (risk for celiac disease)",
    "sulfite": "Sulfite / Metabisulfite preservative (known asthma / anaphylactoid risk)",
    "benzyl alcohol": "Benzyl alcohol preservative (contraindicated in neonates and infants)",
    "paraben": "Paraben preservative (contact allergen / sensitivity risk)",
}


class ComparisonEngine:
    """Production service for side-by-side medicine composition and safety analysis."""

    @classmethod
    def normalize_strength(
        cls,
        numeric_value: Optional[float],
        unit: Optional[str],
    ) -> Tuple[Optional[float], Optional[str]]:
        """Normalizes mass strength to milligrams (mg) for mathematical equivalence comparison."""
        if numeric_value is None or unit is None:
            return None, None

        clean_unit = unit.strip().lower()
        factor = MASS_CONVERSION_FACTORS.get(clean_unit)
        if factor is not None:
            return round(numeric_value * factor, 4), "mg"

        # Return original unit if not in mass conversion table (e.g. '% w/v', 'IU', 'ml')
        return numeric_value, clean_unit

    def compare(
        self,
        product_a: Product,
        product_b: Product,
        interactions: Optional[List[DrugInteraction]] = None,
    ) -> ComparisonResponse:
        """Executes full deterministic comparison between two commercial pharmaceutical products."""
        attributes: List[AttributeComparison] = []
        sources: Set[str] = {"Regulatory:CuratedCatalog", "National:PharmacopoeiaMonographs"}

        # ML-042: Active ingredients alignment & strength basis compatibility
        ing_comp, strength_delta = self._compare_active_ingredients_and_strengths(
            product_a, product_b, sources
        )
        attributes.extend(ing_comp)

        # ML-043: Formulation, route and release characteristics
        form_comp, route_comp, release_comp = self._compare_formulation_route_release(
            product_a, product_b
        )
        attributes.extend([form_comp, route_comp, release_comp])

        # ML-044: Excipient analysis with honest availability tracking
        excipient_diffs = self._compare_excipients(product_a, product_b)

        # ML-045: Source-backed drug interactions with honest coverage wording
        interaction_warnings, interaction_sources = self._process_interactions(
            interactions, product_a, product_b
        )
        sources.update(interaction_sources)

        # Overall comparability status
        comparison_status = self._determine_overall_status(attributes, strength_delta)

        # Mandatory clinical & legal caveats
        limitations = [
            "MedLens brand comparison provides informational packaging analysis only.",
            "This comparison does not constitute medical advice, bioequivalence certification, or substitution authority.",
            "Do not switch between branded or generic prescription medicines without explicit consultation with a qualified physician or pharmacist.",
        ]
        limitations.extend(interaction_warnings)

        return ComparisonResponse(
            comparison_status=comparison_status,
            medicine_a={
                "product_id": product_a.id,
                "name": product_a.brand_name,
                "manufacturer": product_a.manufacturer or "Unknown Manufacturer",
                "dosage_form": product_a.dosage_form,
                "route": product_a.route,
                "release_type": product_a.release_type,
            },
            medicine_b={
                "product_id": product_b.id,
                "name": product_b.brand_name,
                "manufacturer": product_b.manufacturer or "Unknown Manufacturer",
                "dosage_form": product_b.dosage_form,
                "route": product_b.route,
                "release_type": product_b.release_type,
            },
            attributes=attributes,
            strength_delta=strength_delta,
            excipient_differences=excipient_diffs,
            therapeutic_equivalence={
                "status": "not_established",
                "note": (
                    "Therapeutic equivalence / bioequivalence requires product-specific in-vivo bioequivalence studies "
                    "filed with regulatory authorities (e.g. CDSCO / US-FDA Orange Book). Equivalence cannot be "
                    "inferred from active chemical ingredient similarity alone."
                ),
            },
            limitations=limitations,
            sources=sorted(list(sources)),
        )

    def _compare_active_ingredients_and_strengths(
        self,
        product_a: Product,
        product_b: Product,
        sources: Set[str],
    ) -> Tuple[List[AttributeComparison], Optional[StrengthDelta]]:
        """ML-042: Compares active ingredients and evaluates unit/basis-compatible strength deltas."""
        active_a = [c for c in product_a.compositions if c.is_active]
        active_b = [c for c in product_b.compositions if c.is_active]

        map_a = {c.ingredient_id: c for c in active_a}
        map_b = {c.ingredient_id: c for c in active_b}

        attributes: List[AttributeComparison] = []
        strength_delta: Optional[StrengthDelta] = None

        set_a = set(map_a.keys())
        set_b = set(map_b.keys())

        # 1. Active Ingredient Identity Comparison
        if set_a == set_b and len(set_a) > 0:
            evidence = [
                f"PubChem:{c.ingredient.chemical_identifier or c.ingredient.preferred_name}"
                for c in active_a
            ]
            names = [c.ingredient.preferred_name for c in active_a]
            attributes.append(
                AttributeComparison(
                    field="active_ingredients",
                    result=ComparisonOutcome.MATCH,
                    evidence=evidence,
                    reason=f"Identical active pharmaceutical moiety profile: {', '.join(names)}.",
                )
            )
        elif len(set_a & set_b) > 0:
            shared_names = [map_a[i].ingredient.preferred_name for i in (set_a & set_b)]
            diff_a = [map_a[i].ingredient.preferred_name for i in (set_a - set_b)]
            diff_b = [map_b[i].ingredient.preferred_name for i in (set_b - set_a)]
            reason = (
                f"Partially overlapping active ingredients. Shared: {', '.join(shared_names)}. "
                f"Only in {product_a.brand_name}: {', '.join(diff_a) or 'None'}. "
                f"Only in {product_b.brand_name}: {', '.join(diff_b) or 'None'}."
            )
            attributes.append(
                AttributeComparison(
                    field="active_ingredients",
                    result=ComparisonOutcome.DIFFERENCE,
                    evidence=["CuratedFormulationCatalog"],
                    reason=reason,
                )
            )
        else:
            names_a = [c.ingredient.preferred_name for c in active_a] or ["None recorded"]
            names_b = [c.ingredient.preferred_name for c in active_b] or ["None recorded"]
            attributes.append(
                AttributeComparison(
                    field="active_ingredients",
                    result=ComparisonOutcome.CONFLICT,
                    evidence=["CuratedFormulationCatalog"],
                    reason=(
                        f"Completely different active therapeutic substances: "
                        f"{product_a.brand_name} ({', '.join(names_a)}) vs "
                        f"{product_b.brand_name} ({', '.join(names_b)})."
                    ),
                )
            )

        # 2. Strength & Basis Compatibility Evaluation
        shared_ids = list(set_a & set_b)
        if shared_ids:
            # Primary shared ingredient for quantitative delta
            primary_id = shared_ids[0]
            comp_a = map_a[primary_id]
            comp_b = map_b[primary_id]
            ing_name = comp_a.ingredient.preferred_name

            # Check dosage basis compatibility (e.g. tablet vs 5mL liquid)
            basis_a = (comp_a.strength_basis or "per dose unit").strip().lower()
            basis_b = (comp_b.strength_basis or "per dose unit").strip().lower()

            norm_val_a, norm_unit_a = self.normalize_strength(comp_a.strength_numeric, comp_a.strength_unit)
            norm_val_b, norm_unit_b = self.normalize_strength(comp_b.strength_numeric, comp_b.strength_unit)

            if basis_a != basis_b and not (
                ("tablet" in basis_a or "capsule" in basis_a) and ("tablet" in basis_b or "capsule" in basis_b)
            ):
                attributes.append(
                    AttributeComparison(
                        field="strength",
                        result=ComparisonOutcome.UNKNOWN,
                        evidence=["PackageLabeling"],
                        reason=(
                            f"Dosage administration basis differs between presentations: "
                            f"{product_a.brand_name} ({comp_a.strength_numeric} {comp_a.strength_unit} {basis_a}) vs "
                            f"{product_b.brand_name} ({comp_b.strength_numeric} {comp_b.strength_unit} {basis_b}). "
                            f"Strengths cannot be directly compared without volumetric dose conversion."
                        ),
                    )
                )
                strength_delta = StrengthDelta(
                    difference_detected=True,
                    numeric_delta=None,
                    unit=comp_a.strength_unit,
                    warning=(
                        f"Dosage basis discrepancy: {product_a.brand_name} is formulated {basis_a} while "
                        f"{product_b.brand_name} is formulated {basis_b}. Direct 1:1 substitution is not possible."
                    ),
                )

            elif norm_val_a is None or norm_val_b is None:
                attributes.append(
                    AttributeComparison(
                        field="strength",
                        result=ComparisonOutcome.UNKNOWN,
                        evidence=["PackageLabeling"],
                        reason="Quantitative strength specification missing or unverified for one or both products.",
                    )
                )
                strength_delta = StrengthDelta(
                    difference_detected=False,
                    numeric_delta=None,
                    unit=comp_a.strength_unit or comp_b.strength_unit,
                    warning="Active strength numeric values are not fully documented in packaging catalog.",
                )

            elif norm_unit_a != norm_unit_b:
                attributes.append(
                    AttributeComparison(
                        field="strength",
                        result=ComparisonOutcome.DIFFERENCE,
                        evidence=["PackageLabeling"],
                        reason=(
                            f"Incompatible dimensional units ({comp_a.strength_unit} vs {comp_b.strength_unit}). "
                            f"Quantitative arithmetic delta is not applicable."
                        ),
                    )
                )
                strength_delta = StrengthDelta(
                    difference_detected=True,
                    numeric_delta=None,
                    unit=f"{comp_a.strength_unit} vs {comp_b.strength_unit}",
                    warning="Dosing strengths use differing physical dimensions (e.g. mass vs volume).",
                )

            else:
                # Same normalized unit (e.g. mg) & compatible basis
                diff = abs(norm_val_a - norm_val_b)
                if diff < 1e-4:
                    attributes.append(
                        AttributeComparison(
                            field="strength",
                            result=ComparisonOutcome.MATCH,
                            evidence=["PackageLabeling"],
                            reason=f"Equivalent active ingredient nominal strength ({norm_val_a:g} {norm_unit_a} per unit dose).",
                        )
                    )
                    strength_delta = StrengthDelta(
                        difference_detected=False,
                        numeric_delta=0.0,
                        unit=norm_unit_a,
                        warning="Active strengths are quantitatively identical per unit dose.",
                    )
                else:
                    attributes.append(
                        AttributeComparison(
                            field="strength",
                            result=ComparisonOutcome.DIFFERENCE,
                            evidence=["PackageLabeling"],
                            reason=(
                                f"{product_a.brand_name} ({norm_val_a:g} {norm_unit_a}) vs "
                                f"{product_b.brand_name} ({norm_val_b:g} {norm_unit_b}) "
                                f"({diff:g} {norm_unit_a} discrepancy per dose)."
                            ),
                        )
                    )
                    if norm_val_a > norm_val_b:
                        warning = (
                            f"Product A ({product_a.brand_name}) contains {diff:g} {norm_unit_a} higher active "
                            f"{ing_name} per dose than Product B ({product_b.brand_name}). Caution: Higher single-dose "
                            f"strength alters dosing frequency and increases potential risk of adverse reactions."
                        )
                    else:
                        warning = (
                            f"Product A ({product_a.brand_name}) contains {diff:g} {norm_unit_a} lower active "
                            f"{ing_name} per dose than Product B ({product_b.brand_name}). Caution: Lower single-dose "
                            f"strength may lead to sub-therapeutic dosing if substituted directly without dose adjustment."
                        )
                    strength_delta = StrengthDelta(
                        difference_detected=True,
                        numeric_delta=round(diff, 4),
                        unit=norm_unit_a,
                        warning=warning,
                    )
        else:
            attributes.append(
                AttributeComparison(
                    field="strength",
                    result=ComparisonOutcome.NOT_APPLICABLE,
                    evidence=[],
                    reason="Cannot compute quantitative strength delta across distinct chemical active moieties.",
                )
            )

        return attributes, strength_delta

    def _compare_formulation_route_release(
        self,
        product_a: Product,
        product_b: Product,
    ) -> Tuple[AttributeComparison, AttributeComparison, AttributeComparison]:
        """ML-043: Compares physical dosage form, route of administration, and release kinetics."""
        # 1. Dosage form
        if (product_a.dosage_form or "").strip().lower() == (product_b.dosage_form or "").strip().lower():
            form_comp = AttributeComparison(
                field="dosage_form",
                result=ComparisonOutcome.MATCH,
                evidence=["PackagingSpecification"],
                reason=f"Both products share identical physical presentation: {product_a.dosage_form}.",
            )
        else:
            form_comp = AttributeComparison(
                field="dosage_form",
                result=ComparisonOutcome.DIFFERENCE,
                evidence=["PackagingSpecification"],
                reason=(
                    f"Different physical formulations: {product_a.brand_name} ({product_a.dosage_form}) vs "
                    f"{product_b.brand_name} ({product_b.dosage_form}). Formulation variances alter swallowing "
                    f"requirements and gastric transit."
                ),
            )

        # 2. Route of administration
        if (product_a.route or "Oral").strip().lower() == (product_b.route or "Oral").strip().lower():
            route_comp = AttributeComparison(
                field="route",
                result=ComparisonOutcome.MATCH,
                evidence=["RegulatoryMonograph"],
                reason=f"Both products share identical route of administration: {product_a.route or 'Oral'}.",
            )
        else:
            route_comp = AttributeComparison(
                field="route",
                result=ComparisonOutcome.CONFLICT,
                evidence=["RegulatoryMonograph"],
                reason=(
                    f"Incompatible administration routes: {product_a.brand_name} ({product_a.route}) vs "
                    f"{product_b.brand_name} ({product_b.route}). Never substitute across different routes."
                ),
            )

        # 3. Release kinetics
        rel_a = (product_a.release_type or "Immediate Release").strip()
        rel_b = (product_b.release_type or "Immediate Release").strip()
        if rel_a.lower() == rel_b.lower():
            release_comp = AttributeComparison(
                field="release_type",
                result=ComparisonOutcome.MATCH,
                evidence=["PharmacopeialStandard"],
                reason=f"Both products share identical release mechanism: {rel_a}.",
            )
        else:
            release_comp = AttributeComparison(
                field="release_type",
                result=ComparisonOutcome.DIFFERENCE,
                evidence=["PharmacopeialStandard"],
                reason=(
                    f"Release kinetics differ: {product_a.brand_name} ({rel_a}) vs "
                    f"{product_b.brand_name} ({rel_b}). Sustained/modified release formulations release active "
                    f"substances over an extended timeframe and CANNOT be crushed, chewed, or substituted 1:1 "
                    f"with immediate release formulations without physician supervision."
                ),
            )

        return form_comp, route_comp, release_comp

    def _compare_excipients(
        self,
        product_a: Product,
        product_b: Product,
    ) -> List[str]:
        """ML-044: Excipient analysis with strict availability verification (zero hallucination)."""
        excipients_a = [c for c in product_a.compositions if not c.is_active]
        excipients_b = [c for c in product_b.compositions if not c.is_active]

        diffs: List[str] = []

        if not excipients_a and not excipients_b:
            diffs.append(
                "Excipient (inactive binder/filler) records are unavailable in the catalog for both products; "
                "specific inactive formulation differences cannot be determined."
            )
            return diffs

        if not excipients_a:
            diffs.append(
                f"Excipient records are unavailable in catalog for {product_a.brand_name}; "
                f"inactive binder differences cannot be fully verified."
            )
            return diffs

        if not excipients_b:
            diffs.append(
                f"Excipient records are unavailable in catalog for {product_b.brand_name}; "
                f"inactive binder differences cannot be fully verified."
            )
            return diffs

        names_a = {c.ingredient.preferred_name for c in excipients_a}
        names_b = {c.ingredient.preferred_name for c in excipients_b}

        only_a = names_a - names_b
        only_b = names_b - names_a

        if not only_a and not only_b:
            diffs.append("Identical documented excipient and binder profile.")
        else:
            if only_a:
                diffs.append(f"Excipients unique to {product_a.brand_name}: {', '.join(sorted(only_a))}.")
            if only_b:
                diffs.append(f"Excipients unique to {product_b.brand_name}: {', '.join(sorted(only_b))}.")

        # Check for known common allergens
        all_excipients = list(names_a | names_b)
        for name in all_excipients:
            lower = name.lower()
            for allergen_key, allergen_advisory in COMMON_EXCIPIENT_ALLERGENS.items():
                if allergen_key in lower:
                    present_in = []
                    if name in names_a:
                        present_in.append(product_a.brand_name)
                    if name in names_b:
                        present_in.append(product_b.brand_name)
                    diffs.append(f"Allergen Alert: {allergen_advisory} detected in {', '.join(present_in)}.")

        return diffs

    def _process_interactions(
        self,
        interactions: Optional[List[DrugInteraction]],
        product_a: Product,
        product_b: Product,
    ) -> Tuple[List[str], Set[str]]:
        """ML-045: Source-backed drug interactions with mandatory honest coverage wording."""
        warnings: List[str] = []
        sources: Set[str] = set()

        if interactions:
            for item in interactions:
                ing_a = item.ingredient_a_id
                ing_b = item.ingredient_b_id
                severity = (item.severity or "unknown").upper()
                warnings.append(
                    f"Clinical Interaction Alert [{severity}]: {item.clinical_effect} "
                    f"(Source: {item.source.source_name if item.source else 'Curated Interaction Database'})."
                )
                if item.source:
                    sources.add(item.source.source_name)
        else:
            # Mandatory honest negative-proof coverage statement
            warnings.append(
                "No documented interactions found between these active ingredients in the MedLens curated knowledgebase. "
                "Note: The absence of a documented interaction in this database does not prove that no interaction exists. "
                "Always consult a healthcare professional."
            )

        return warnings, sources

    @staticmethod
    def _determine_overall_status(
        attributes: List[AttributeComparison],
        strength_delta: Optional[StrengthDelta],
    ) -> str:
        """Determines holistic comparison outcome."""
        results = {a.result for a in attributes}

        if ComparisonOutcome.CONFLICT in results:
            return "conflicting"

        active_comp = next((a for a in attributes if a.field == "active_ingredients"), None)
        if not active_comp or active_comp.result != ComparisonOutcome.MATCH:
            return "different_compositions"

        # Active ingredients match: check strength and formulation
        if strength_delta and strength_delta.difference_detected:
            return "partially_comparable"

        form_comp = next((a for a in attributes if a.field == "dosage_form"), None)
        rel_comp = next((a for a in attributes if a.field == "release_type"), None)

        if form_comp and form_comp.result != ComparisonOutcome.MATCH:
            return "partially_comparable"
        if rel_comp and rel_comp.result != ComparisonOutcome.MATCH:
            return "partially_comparable"

        return "comparable"

