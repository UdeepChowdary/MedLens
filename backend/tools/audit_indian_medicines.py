"""Audit tool and composition parser benchmark for local Indian medicine datasets.

Performs text-only inspection, schema validation, and parsing yield analysis
against MedLens RuleBasedExtractor and INNNormalizer without database mutation.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Support importing app modules regardless of current working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.common import VerificationState
from app.services.extraction.rule_baseline import RuleBasedExtractor
from app.services.normalization.inn_normalizer import INNNormalizer

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ["name", "composition", "uses", "side_effects", "image_url"]


class AuditRecord:
    """Represents a validated row audit outcome preserving original data."""

    def __init__(
        self,
        row_id: int,
        raw_name: str,
        raw_composition: str,
        raw_uses: str,
        raw_side_effects: str,
        raw_image_url: str,
        category: str,  # "EXACT_MATCH", "PARTIAL_MATCH", "PARSE_FAILURE"
        parsed_ingredients: List[Dict[str, Any]],
        normalized_inns: List[Dict[str, Any]],
        failure_reasons: List[str],
        suspicious_url: bool = False,
    ):
        self.row_id = row_id
        self.raw_name = raw_name
        self.raw_composition = raw_composition
        self.raw_uses = raw_uses
        self.raw_side_effects = raw_side_effects
        self.raw_image_url = raw_image_url
        self.category = category
        self.parsed_ingredients = parsed_ingredients
        self.normalized_inns = normalized_inns
        self.failure_reasons = failure_reasons
        self.suspicious_url = suspicious_url

    def to_dict(self) -> Dict[str, Any]:
        return {
            "row_id": self.row_id,
            "raw_name": self.raw_name,
            "raw_composition": self.raw_composition,
            "raw_image_url": self.raw_image_url,
            "category": self.category,
            "parsed_ingredients": self.parsed_ingredients,
            "normalized_inns": self.normalized_inns,
            "failure_reasons": self.failure_reasons,
            "suspicious_url": self.suspicious_url,
        }


def load_dataset_rows(file_path: Path) -> List[Dict[str, Any]]:
    """Loads records from CSV or Parquet file into list of row dictionaries."""
    if not file_path.exists():
        raise FileNotFoundError(f"Source dataset file not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".csv":
        rows = []
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for idx, r in enumerate(reader):
                r["_row_id"] = idx
                rows.append(r)
        return rows
    elif suffix == ".parquet":
        try:
            import pandas as pd
            df = pd.read_parquet(file_path)
            df["_row_id"] = df.index
            return df.to_dict(orient="records")
        except ImportError:
            raise RuntimeError("Reading .parquet files requires 'pandas' and 'pyarrow'.")
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Must be .csv or .parquet.")


def validate_schema_columns(columns: List[str]) -> Tuple[bool, List[str]]:
    """Checks that all required schema columns exist."""
    normalized_cols = {c.strip().lower() for c in columns}
    missing = [req for req in REQUIRED_COLUMNS if req not in normalized_cols]
    return len(missing) == 0, missing


def is_suspicious_image_url(url: Optional[str]) -> bool:
    """Checks whether image URL is missing, non-https, or points to generic placeholder."""
    if not url or not str(url).strip():
        return True
    u = str(url).strip().lower()
    if not u.startswith("https://") and not u.startswith("http://"):
        return True
    if "placeholder" in u or "no_image" in u or "default" in u:
        return True
    return False


def audit_dataset_file(
    file_path: Path,
    extractor: Optional[RuleBasedExtractor] = None,
    normalizer: Optional[INNNormalizer] = None,
    max_rows: Optional[int] = None,
) -> Dict[str, Any]:
    """Audits local dataset file and evaluates text-only parsing yield."""
    rows = load_dataset_rows(file_path)
    if not rows:
        raise ValueError(f"Dataset file {file_path} contains zero records.")

    if max_rows and max_rows > 0:
        rows = rows[:max_rows]

    # Validate header columns
    col_valid, missing_cols = validate_schema_columns(list(rows[0].keys()))
    if not col_valid:
        raise ValueError(f"Missing required columns in {file_path}: {missing_cols}")

    rule_extractor = extractor or RuleBasedExtractor()
    inn_normalizer = normalizer or INNNormalizer()

    total_rows = len(rows)
    seen_names: Dict[str, int] = {}
    duplicate_names = 0
    missing_counts = {col: 0 for col in REQUIRED_COLUMNS}
    suspicious_url_count = 0

    exact_match_count = 0
    partial_match_count = 0
    parse_failure_count = 0

    failure_examples: List[Dict[str, Any]] = []
    audited_records: List[AuditRecord] = []

    for idx, r in enumerate(rows):
        row_id = r.get("_row_id", idx)
        raw_name = str(r.get("name") or "").strip()
        raw_comp = str(r.get("composition") or "").strip()
        raw_uses = str(r.get("uses") or "").strip()
        raw_side_effects = str(r.get("side_effects") or "").strip()
        raw_image_url = str(r.get("image_url") or "").strip()

        # Check missing values
        if not raw_name:
            missing_counts["name"] += 1
        if not raw_comp:
            missing_counts["composition"] += 1
        if not raw_uses:
            missing_counts["uses"] += 1
        if not raw_side_effects:
            missing_counts["side_effects"] += 1
        if not raw_image_url:
            missing_counts["image_url"] += 1

        # Duplicate detection (case-insensitive name)
        name_key = raw_name.lower()
        if name_key:
            if name_key in seen_names:
                duplicate_names += 1
            else:
                seen_names[name_key] = row_id

        # URL quality check
        suspicious_url = is_suspicious_image_url(raw_image_url)
        if suspicious_url:
            suspicious_url_count += 1

        # Text-only composition parsing evaluation
        reasons: List[str] = []
        parsed_ing_list: List[Dict[str, Any]] = []
        normalized_inns: List[Dict[str, Any]] = []

        if not raw_comp:
            reasons.append("COMPOSITION_EMPTY")
            category = "PARSE_FAILURE"
            parse_failure_count += 1
        else:
            # Run existing RuleBasedExtractor without modifying its internal weights
            extract_result = rule_extractor.extract(raw_comp)

            if not extract_result.ingredients:
                reasons.append("NO_INGREDIENTS_RECOGNIZED")
                category = "PARSE_FAILURE"
                parse_failure_count += 1
                if len(failure_examples) < 15:
                    failure_examples.append({
                        "row_id": row_id,
                        "name": raw_name,
                        "composition": raw_comp,
                        "reason": "No canonical ingredients resolved in baseline vocabulary.",
                    })
            else:
                all_have_strength = True
                all_have_inn = True

                for ing in extract_result.ingredients:
                    cname = ing.get("canonical_name", "")
                    strength = ing.get("strength")
                    parsed_ing_list.append(ing)

                    if not strength or strength.get("numeric_value") is None:
                        all_have_strength = False

                    # Normalize through existing INNNormalizer
                    norm_res = inn_normalizer.normalize(cname)
                    normalized_inns.append({
                        "raw": cname,
                        "canonical_name": norm_res.canonical_name,
                        "verification_state": norm_res.verification_state.value,
                        "match_score": norm_res.match_score,
                    })

                    if norm_res.verification_state not in (
                        VerificationState.VERIFIED,
                        VerificationState.PARTIALLY_VERIFIED,
                    ):
                        all_have_inn = False

                if all_have_inn and all_have_strength:
                    category = "EXACT_MATCH"
                    exact_match_count += 1
                else:
                    category = "PARTIAL_MATCH"
                    partial_match_count += 1
                    if not all_have_strength:
                        reasons.append("MISSING_OR_UNPARSED_STRENGTH")
                    if not all_have_inn:
                        reasons.append("UNVERIFIED_INN_MAPPING")

        record = AuditRecord(
            row_id=row_id,
            raw_name=raw_name,
            raw_composition=raw_comp,
            raw_uses=raw_uses,
            raw_side_effects=raw_side_effects,
            raw_image_url=raw_image_url,
            category=category,
            parsed_ingredients=parsed_ing_list,
            normalized_inns=normalized_inns,
            failure_reasons=reasons,
            suspicious_url=suspicious_url,
        )
        audited_records.append(record)

    summary = {
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "source_file": str(file_path),
        "total_records_analyzed": total_rows,
        "unique_product_names": len(seen_names),
        "duplicate_name_count": duplicate_names,
        "missing_fields": missing_counts,
        "suspicious_image_url_count": suspicious_url_count,
        "parsing_yield": {
            "exact_match_count": exact_match_count,
            "exact_match_percentage": round((exact_match_count / total_rows) * 100, 2) if total_rows else 0.0,
            "partial_match_count": partial_match_count,
            "partial_match_percentage": round((partial_match_count / total_rows) * 100, 2) if total_rows else 0.0,
            "parse_failure_count": parse_failure_count,
            "parse_failure_percentage": round((parse_failure_count / total_rows) * 100, 2) if total_rows else 0.0,
        },
        "representative_failures": failure_examples,
    }
    return summary


def render_markdown_audit_report(summary: Dict[str, Any]) -> str:
    """Renders clean GitHub-flavored Markdown audit report."""
    total = summary["total_records_analyzed"]
    pyield = summary["parsing_yield"]
    lines = [
        "# 📊 Indian Medicines Dataset Audit & Parser Benchmark Report",
        "",
        f"> **Generated:** {summary['audit_timestamp']}  ",
        f"> **Source File:** `{summary['source_file']}`  ",
        f"> **Dataset Scope:** Text-only composition parsing and schema audit (No database writes)",
        "",
        "---",
        "",
        "## 1. Schema & Data Quality Summary",
        "",
        f"- **Total Records Analyzed:** `{total}`",
        f"- **Unique Medicine Names:** `{summary['unique_product_names']}`",
        f"- **Duplicate Brand Name Instances:** `{summary['duplicate_name_count']}`",
        f"- **Suspicious or Placeholder Image URLs:** `{summary['suspicious_image_url_count']}`",
        "",
        "### Field Completeness",
        "",
        "| Field | Missing Count | Completeness Ratio |",
        "| :--- | :---: | :---: |",
    ]

    for col, count in summary["missing_fields"].items():
        ratio = round(((total - count) / total) * 100, 1) if total else 0.0
        lines.append(f"| `{col}` | {count} | {ratio}% |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Text-Only Composition Parser Yield",
        "",
        "> **Note on Terminology:** *Parser yield* measures string token extraction against the current rule dictionary. It is an algorithmic coverage metric, not a claim of clinical accuracy or medical validation.",
        "",
        "| Category | Count | Percentage | Definition |",
        "| :--- | :---: | :---: | :--- |",
        f"| **Exact Match** | `{pyield['exact_match_count']}` | `{pyield['exact_match_percentage']}%` | All extracted ingredients resolved to INN and valid strengths. |",
        f"| **Partial Match** | `{pyield['partial_match_count']}` | `{pyield['partial_match_percentage']}%` | At least 1 ingredient recognized; strength or salt partially unparsed. |",
        f"| **Parse Failure** | `{pyield['parse_failure_count']}` | `{pyield['parse_failure_percentage']}%` | Zero recognized ingredients in current dictionary or empty text. |",
        "",
        "---",
        "",
        "## 3. Representative Parse Failure Samples",
        "",
        "The following sample strings failed parsing due to missing molecules in the baseline dictionary or unsupported syntax:",
        "",
        "| Row ID | Medicine Name | Original Composition String | Observed Issue |",
        "| :---: | :--- | :--- | :--- |",
    ])

    for ex in summary["representative_failures"][:10]:
        name = ex.get("name", "N/A").replace("|", "/")
        comp = ex.get("composition", "N/A").replace("|", "/")
        reason = ex.get("reason", "").replace("|", "/")
        lines.append(f"| `{ex['row_id']}` | {name} | `{comp}` | {reason} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Key Findings & Next Steps",
        "",
        "1. **Catalog Development:** Unparsed failure cases indicate active ingredients currently absent from `KNOWN_INGREDIENTS` (e.g. multi-ingredient vitamins, herbal supplements, or newer molecules).",
        "2. **Zero Database Pollution:** This audit executed completely in-memory with zero writes to development or production databases.",
        "3. **Image Disqualification:** The presence of empty, placeholder, or CDN web thumbnail URLs confirms that `image_url` cannot be used as packaging ground truth for OCR benchmarking.",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit local Indian medicines dataset and benchmark composition parser.")
    parser.add_argument("--file", required=True, type=Path, help="Path to local CSV or Parquet dataset file")
    parser.add_argument("--output-json", type=Path, default=None, help="Path to save machine-readable audit JSON")
    parser.add_argument("--output-md", type=Path, default=None, help="Path to save Markdown audit report")
    parser.add_argument("--max-rows", type=int, default=None, help="Optional maximum row limit for quick audits")
    args = parser.parse_args()

    file_path = args.file
    print(f"Beginning audit of dataset file: {file_path}")
    summary = audit_dataset_file(file_path, max_rows=args.max_rows)

    # Save outputs if requested
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Wrote machine-readable audit output to {args.output_json}")

    md_report = render_markdown_audit_report(summary)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_md, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"Wrote Markdown audit report to {args.output_md}")
    else:
        print("\n" + md_report)


if __name__ == "__main__":
    main()
