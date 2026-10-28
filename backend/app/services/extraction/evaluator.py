"""Standardized evaluation metrics for entity extraction and clinical tuple normalization.

Implements evaluation protocol per Blueprint Section 6.5:
1. Entity-level precision, recall, F1 across all 11 canonical entity types (strict span match).
2. Exact clinical tuple match: (canonical_ingredient, numeric_strength, strength_unit, strength_basis).
3. Abstention and human review rate (% routed to confirmation vs accepted).
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from app.schemas.common import VerificationState

# Blueprint Section 6.2 canonical 11 entity types
CANONICAL_ENTITIES = [
    "BRAND",
    "PRODUCT_NAME",
    "INGREDIENT",
    "SALT_FORM",
    "STRENGTH",
    "CONCENTRATION",
    "STRENGTH_BASIS",
    "DOSAGE_FORM",
    "ROUTE",
    "RELEASE_TYPE",
    "COMPOSITION_HEADER",
]


class ClinicalTuple(BaseModel):
    """Normalized active ingredient composition tuple."""
    ingredient: str
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    basis: Optional[str] = None

    def key(self) -> Tuple[str, Optional[float], Optional[str], Optional[str]]:
        norm_ing = self.ingredient.strip().lower()
        norm_unit = self.unit.strip().lower() if self.unit else None
        norm_basis = self.basis.strip().lower() if self.basis else None
        return (norm_ing, self.numeric_value, norm_unit, norm_basis)


class EntityMetric(BaseModel):
    """Precision, Recall, F1 for a specific entity category."""
    label: str
    true_positives: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    support: int = 0


class OverallMetrics(BaseModel):
    """Micro and macro averaged entity metrics."""
    micro_precision: float = 0.0
    micro_recall: float = 0.0
    micro_f1: float = 0.0
    macro_precision: float = 0.0
    macro_recall: float = 0.0
    macro_f1: float = 0.0


class TupleMatchMetric(BaseModel):
    """Exact clinical tuple accuracy and error breakdown."""
    total_ground_truth_tuples: int = 0
    total_predicted_tuples: int = 0
    exact_matches: int = 0
    false_positives: int = 0
    false_negatives: int = 0
    exact_tuple_accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0


class AbstentionMetric(BaseModel):
    """Safety abstention routing rates."""
    total_samples: int = 0
    abstained_samples: int = 0
    accepted_samples: int = 0
    abstention_rate: float = 0.0
    accepted_accuracy: float = 0.0


class ExtractionEvaluationReport(BaseModel):
    """Comprehensive evaluation outcome report."""
    total_samples_evaluated: int
    entity_metrics: Dict[str, EntityMetric]
    overall_entity_metrics: OverallMetrics
    clinical_tuple_metrics: TupleMatchMetric
    abstention_metrics: AbstentionMetric
    limitations_notice: str = (
        "Evaluation on small sample sizes (e.g. <= 10 packaging images) provides "
        "pipeline verification only. High variance is expected and results do NOT "
        "demonstrate generalizable clinical performance or production model accuracy."
    )


class ExtractionEvaluator:
    """Evaluates extraction predictions against ground-truth annotations."""

    @staticmethod
    def _safe_divide(numerator: float, denominator: float) -> float:
        return round(numerator / denominator, 4) if denominator > 0 else 0.0

    @classmethod
    def evaluate_entities(
        cls,
        ground_truth: List[List[Dict[str, Any]]],
        predictions: List[List[Dict[str, Any]]],
        canonical_labels: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, EntityMetric], OverallMetrics]:
        """Calculates strict span-level Precision, Recall, F1 per entity label and overall.
        
        Strict match requires identical entity label, start_char, and end_char.
        """
        labels = canonical_labels or CANONICAL_ENTITIES
        stats: Dict[str, Dict[str, int]] = {
            lbl: {"tp": 0, "fp": 0, "fn": 0, "support": 0} for lbl in labels
        }

        total_tp = 0
        total_fp = 0
        total_fn = 0

        for gt_entities, pred_entities in zip(ground_truth, predictions):
            gt_spans: Dict[str, Set[Tuple[int, int]]] = {lbl: set() for lbl in labels}
            pred_spans: Dict[str, Set[Tuple[int, int]]] = {lbl: set() for lbl in labels}

            for e in gt_entities:
                lbl = e.get("label")
                span = e.get("char_span") or (e.get("start_char"), e.get("end_char"))
                if lbl in gt_spans and span and len(span) == 2 and span[0] is not None:
                    gt_spans[lbl].add((span[0], span[1]))
                    stats[lbl]["support"] += 1

            for e in pred_entities:
                lbl = e.get("label")
                span = e.get("char_span") or (e.get("start_char"), e.get("end_char"))
                if lbl in pred_spans and span and len(span) == 2 and span[0] is not None:
                    pred_spans[lbl].add((span[0], span[1]))

            for lbl in labels:
                gts = gt_spans[lbl]
                prs = pred_spans[lbl]
                tp = len(gts & prs)
                fp = len(prs - gts)
                fn = len(gts - prs)

                stats[lbl]["tp"] += tp
                stats[lbl]["fp"] += fp
                stats[lbl]["fn"] += fn

                total_tp += tp
                total_fp += fp
                total_fn += fn

        # Compute per-label metrics
        entity_metrics: Dict[str, EntityMetric] = {}
        macro_p_sum = 0.0
        macro_r_sum = 0.0
        macro_f1_sum = 0.0
        evaluated_labels_count = 0

        for lbl in labels:
            tp = stats[lbl]["tp"]
            fp = stats[lbl]["fp"]
            fn = stats[lbl]["fn"]
            supp = stats[lbl]["support"]

            p = cls._safe_divide(tp, tp + fp)
            r = cls._safe_divide(tp, tp + fn)
            f1 = cls._safe_divide(2 * p * r, p + r) if (p + r) > 0 else 0.0

            entity_metrics[lbl] = EntityMetric(
                label=lbl,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                precision=p,
                recall=r,
                f1=f1,
                support=supp,
            )

            # Accumulate macro average for labels with occurrences or predictions
            if supp > 0 or (tp + fp) > 0:
                macro_p_sum += p
                macro_r_sum += r
                macro_f1_sum += f1
                evaluated_labels_count += 1

        denom = max(1, evaluated_labels_count)
        micro_p = cls._safe_divide(total_tp, total_tp + total_fp)
        micro_r = cls._safe_divide(total_tp, total_tp + total_fn)
        micro_f1 = cls._safe_divide(2 * micro_p * micro_r, micro_p + micro_r) if (micro_p + micro_r) > 0 else 0.0

        overall = OverallMetrics(
            micro_precision=micro_p,
            micro_recall=micro_r,
            micro_f1=micro_f1,
            macro_precision=round(macro_p_sum / denom, 4),
            macro_recall=round(macro_r_sum / denom, 4),
            macro_f1=round(macro_f1_sum / denom, 4),
        )

        return entity_metrics, overall

    @classmethod
    def evaluate_clinical_tuples(
        cls,
        ground_truth: List[List[ClinicalTuple]],
        predictions: List[List[ClinicalTuple]],
    ) -> TupleMatchMetric:
        """Calculates exact (ingredient, numeric_value, unit, basis) tuple match accuracy."""
        total_gt = 0
        total_pred = 0
        exact_matches = 0
        false_positives = 0
        false_negatives = 0

        for gt_tuples, pred_tuples in zip(ground_truth, predictions):
            gt_keys = [t.key() for t in gt_tuples]
            pred_keys = [t.key() for t in pred_tuples]

            total_gt += len(gt_keys)
            total_pred += len(pred_keys)

            matched_preds = set()
            for g in gt_keys:
                found = False
                for p_idx, p in enumerate(pred_keys):
                    if p_idx not in matched_preds and p == g:
                        exact_matches += 1
                        matched_preds.add(p_idx)
                        found = True
                        break
                if not found:
                    false_negatives += 1

            false_positives += (len(pred_keys) - len(matched_preds))

        p = cls._safe_divide(exact_matches, total_pred)
        r = cls._safe_divide(exact_matches, total_gt)
        f1 = cls._safe_divide(2 * p * r, p + r) if (p + r) > 0 else 0.0
        acc = cls._safe_divide(exact_matches, total_gt)

        return TupleMatchMetric(
            total_ground_truth_tuples=total_gt,
            total_predicted_tuples=total_pred,
            exact_matches=exact_matches,
            false_positives=false_positives,
            false_negatives=false_negatives,
            exact_tuple_accuracy=acc,
            precision=p,
            recall=r,
            f1=f1,
        )

    @classmethod
    def evaluate_abstention(
        cls,
        statuses: List[VerificationState],
        sample_correctness: List[bool],
    ) -> AbstentionMetric:
        """Calculates safety abstention rate and accuracy on accepted predictions."""
        total = len(statuses)
        if total == 0:
            return AbstentionMetric()

        abstained = sum(
            1 for s in statuses
            if s in (VerificationState.NEEDS_CONFIRMATION, VerificationState.UNABLE_TO_VERIFY)
        )
        accepted = total - abstained
        rate = cls._safe_divide(abstained, total)

        # Accuracy of accepted cases
        accepted_correct = sum(
            1 for s, corr in zip(statuses, sample_correctness)
            if s in (VerificationState.VERIFIED, VerificationState.PARTIALLY_VERIFIED) and corr
        )
        accepted_acc = cls._safe_divide(accepted_correct, accepted) if accepted > 0 else 0.0

        return AbstentionMetric(
            total_samples=total,
            abstained_samples=abstained,
            accepted_samples=accepted,
            abstention_rate=rate,
            accepted_accuracy=accepted_acc,
        )
