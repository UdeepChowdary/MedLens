"""Human Review Queue generator for MedLens medicine packaging dataset.

Scans local annotations to identify items requiring human inspection, verification,
re-photographing, or clarification of ambiguous / degraded packaging typography.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Support importing app modules regardless of current working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.schemas.dataset import ReviewStatus

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ReviewQueueItem:
    """Represents an annotation item requiring human attention."""

    def __init__(
        self,
        annotation_file: str,
        image_id: str,
        file_name: str,
        product_family: str,
        packaging_type: str,
        review_status: str,
        has_uncertainty: bool,
        uncertainty_notes: Optional[str],
        quality_flags: Dict[str, Any],
        provenance_notes: Optional[str],
        reasons_for_review: List[str],
        recommended_action: str,
    ):
        self.annotation_file = annotation_file
        self.image_id = image_id
        self.file_name = file_name
        self.product_family = product_family
        self.packaging_type = packaging_type
        self.review_status = review_status
        self.has_uncertainty = has_uncertainty
        self.uncertainty_notes = uncertainty_notes
        self.quality_flags = quality_flags
        self.provenance_notes = provenance_notes
        self.reasons_for_review = reasons_for_review
        self.recommended_action = recommended_action

    def to_dict(self) -> Dict[str, Any]:
        return {
            "annotation_file": self.annotation_file,
            "image_id": self.image_id,
            "file_name": self.file_name,
            "product_family": self.product_family,
            "packaging_type": self.packaging_type,
            "review_status": self.review_status,
            "has_uncertainty": self.has_uncertainty,
            "uncertainty_notes": self.uncertainty_notes,
            "quality_flags": self.quality_flags,
            "provenance_notes": self.provenance_notes,
            "reasons_for_review": self.reasons_for_review,
            "recommended_action": self.recommended_action,
        }


def scan_review_queue(annotations_dir: Path) -> Dict[str, Any]:
    """Scans all annotations in directory and compiles items requiring review."""
    if not annotations_dir.exists():
        raise FileNotFoundError(f"Annotations directory not found: {annotations_dir}")

    json_files = sorted(list(annotations_dir.glob("*.json")))
    total_annotations = len(json_files)
    verified_count = 0
    draft_count = 0
    flagged_count = 0
    uncertain_count = 0
    synthetic_count = 0

    queue_items: List[ReviewQueueItem] = []

    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to read {jf.name}: {e}")
            continue

        meta = data.get("image_metadata", {})
        prov = meta.get("provenance", {})
        qflags = data.get("quality_flags", {})

        review_status = data.get("review_status", ReviewStatus.DRAFT.value)
        has_uncertainty = bool(data.get("has_uncertainty", False))
        uncertainty_notes = data.get("uncertainty_notes")
        prov_notes = str(prov.get("notes") or "")
        prov_source = str(prov.get("source") or "")

        reasons: List[str] = []
        action: str = "Proceed to verification."

        is_synthetic = (
            "3d generic illustration" in prov_notes.lower()
            or "synthetic" in prov_notes.lower()
            or "do not use as ground truth" in prov_notes.lower()
            or "synthetic" in prov_source.lower()
        )

        if is_synthetic:
            synthetic_count += 1
            reasons.append("SYNTHETIC_OR_MOCKUP: Package is an illustration or mockup lacking authentic packaging typography.")
            action = "Replace with real physical medicine strip/box photograph; do not use as ground truth."

        if review_status == ReviewStatus.FLAGGED_FOR_REVIEW.value:
            flagged_count += 1
            reasons.append(f"FLAGGED_STATUS: Marked '{review_status}' by curator.")
            if not is_synthetic:
                action = "Inspect packaging photo against transcription and resolve flagged issues."
        elif review_status == ReviewStatus.DRAFT.value:
            draft_count += 1
            reasons.append("DRAFT_STATUS: Initial unverified draft pending human review.")
            action = "Perform manual clinical review of character spans and bounding boxes."
        elif review_status == ReviewStatus.VERIFIED_BY_HUMAN.value:
            verified_count += 1

        if has_uncertainty or uncertainty_notes:
            uncertain_count += 1
            reasons.append(f"UNCERTAINTY_FLAG: {uncertainty_notes or 'Annotator flagged ambiguous typography'}")
            action = "Inspect high-resolution crop of disputed text and confirm transcription."

        # Degradation checks
        degradations = [k for k, v in qflags.items() if v is True]
        if degradations:
            reasons.append(f"VISUAL_DEGRADATIONS: {', '.join(degradations)}")

        if reasons:
            queue_items.append(
                ReviewQueueItem(
                    annotation_file=jf.name,
                    image_id=meta.get("image_id", jf.stem),
                    file_name=meta.get("file_name", "N/A"),
                    product_family=meta.get("product_family", "N/A"),
                    packaging_type=meta.get("packaging_type", "N/A"),
                    review_status=review_status,
                    has_uncertainty=has_uncertainty,
                    uncertainty_notes=uncertainty_notes,
                    quality_flags=qflags,
                    provenance_notes=prov_notes,
                    reasons_for_review=reasons,
                    recommended_action=action,
                )
            )

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "annotations_dir": str(annotations_dir),
        "total_annotations": total_annotations,
        "verified_count": verified_count,
        "pending_review_count": len(queue_items),
        "draft_count": draft_count,
        "flagged_count": flagged_count,
        "uncertain_count": uncertain_count,
        "synthetic_illustration_count": synthetic_count,
        "items": [it.to_dict() for it in queue_items],
    }


def render_markdown_queue_report(summary: Dict[str, Any]) -> str:
    """Renders clean GitHub-flavored Markdown review queue report."""
    total = summary["total_annotations"]
    pending = summary["pending_review_count"]
    verified = summary["verified_count"]

    lines = [
        "# 📋 MedLens Dataset Human Review Queue",
        "",
        f"> **Generated:** {summary['timestamp']}  ",
        f"> **Annotations Directory:** `{summary['annotations_dir']}`  ",
        f"> **Audit Policy:** Zero unreviewed samples permitted in evaluation splits.",
        "",
        "---",
        "",
        "## 1. Review Status Overview",
        "",
        f"- **Total Annotations:** `{total}`",
        f"- **Human-Verified Records:** `{verified}` ({round(verified / total * 100, 1) if total else 0.0}%)",
        f"- **Pending Human Review:** `{pending}` ({round(pending / total * 100, 1) if total else 0.0}%)",
        f"  - **Drafts:** `{summary['draft_count']}`",
        f"  - **Explicitly Flagged:** `{summary['flagged_count']}`",
        f"  - **Uncertain Spans:** `{summary['uncertain_count']}`",
        f"  - **Synthetic/Mockup Disqualifications:** `{summary['synthetic_illustration_count']}`",
        "",
        "---",
        "",
        "## 2. Items Requiring Review",
        "",
    ]

    if not summary["items"]:
        lines.append("✅ **All annotations are human-verified real packaging records. Queue is empty.**")
    else:
        lines.extend([
            "| Image ID | Product Family | Review Status | Issues & Notes | Recommended Human Action |",
            "| :--- | :--- | :---: | :--- | :--- |",
        ])
        for it in summary["items"]:
            img_id = it["image_id"]
            fam = it["product_family"]
            stat = it["review_status"]
            reasons = "<br>".join(f"• {r}" for r in it["reasons_for_review"])
            action = it["recommended_action"]
            lines.append(f"| `{img_id}` | `{fam}` | `{stat}` | {reasons} | {action} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. Human Review Protocol",
        "",
        "1. **Never auto-promote model predictions:** Annotations generated by automated tools or OCR must remain in `draft` until manually inspected.",
        "2. **Physical Packaging Verification:** Verify that the image is an authentic physical photograph of real medicine packaging. Reject 3D renders and promotional illustrations.",
        "3. **Character-Span Alignment:** Ensure every entity token has an exact verbatim slice match in `transcription` (`transcription[start:end] == raw_text`).",
        "4. **Promotion to Ground Truth:** Change `review_status` to `verified_by_human` only after all fields, spans, and quality notes are verified.",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate human review queue for MedLens dataset.")
    parser.add_argument("--annotations-dir", default="data/annotations", help="Path to annotations folder")
    parser.add_argument("--output-json", default=None, help="Optional path to output JSON queue report")
    parser.add_argument("--output-md", default=None, help="Optional path to output Markdown queue report")
    args = parser.parse_args()

    ann_dir = Path(args.annotations_dir)
    print(f"Scanning review queue in {ann_dir}...")
    summary = scan_review_queue(ann_dir)

    print(f"\n--- Review Queue Summary ---")
    print(f"Total annotations: {summary['total_annotations']}")
    print(f"Human verified: {summary['verified_count']}")
    print(f"Pending review: {summary['pending_review_count']}")
    print(f"  - Drafts: {summary['draft_count']}")
    print(f"  - Flagged for review: {summary['flagged_count']}")
    print(f"  - Uncertain: {summary['uncertain_count']}")
    print(f"  - Disqualified illustrations: {summary['synthetic_illustration_count']}")

    if args.output_json:
        out_json_path = Path(args.output_json)
        out_json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Wrote review queue JSON to {out_json_path}")

    md_report = render_markdown_queue_report(summary)
    if args.output_md:
        out_md_path = Path(args.output_md)
        out_md_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_md_path, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"Wrote review queue Markdown to {out_md_path}")
    else:
        print("\n" + md_report)


if __name__ == "__main__":
    main()
