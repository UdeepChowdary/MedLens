"""Create conservative, reviewable outputs from the dmedhi medicines CSV.

This tool preserves source text and does not claim that source labels or images
are correct. Parsed ingredient/strength fields are candidates for human review.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

SOURCE = "https://huggingface.co/datasets/dmedhi/indian-medicines"
COMPONENT_RE = re.compile(r"^(?P<ingredient>.+?)\s*\((?P<strength>[^()]*)\)\s*$")
STRENGTH_RE = re.compile(
    r"^\s*(?:\d+(?:\.\d+)?\s*(?:mg|mcg|ug|g|ml|iu|%\s*(?:w/v|w/w)|%)(?:\s*/\s*\d+(?:\.\d+)?\s*(?:ml|l))?|na|n/?a)\s*$",
    re.IGNORECASE,
)


def clean(value: Any) -> str:
    return html.unescape(str(value or "")).strip()


def name_key(value: str) -> str:
    # Keep decimal boundaries: "12.5 mcg" and "125 mcg" are distinct.
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def parse_composition(raw: str) -> tuple[list[dict[str, str]], str]:
    """Parse only explicit Ingredient (strength) components; never infer names."""
    if not raw:
        return [], "empty"
    chunks = [part.strip() for part in re.split(r"\s*\+\s*", raw) if part.strip()]
    parsed: list[dict[str, str]] = []
    complete = True
    for chunk in chunks:
        match = COMPONENT_RE.fullmatch(chunk)
        if not match:
            parsed.append({"raw_component": chunk, "ingredient_raw": "", "strength_raw": ""})
            complete = False
            continue
        ingredient = match.group("ingredient").strip()
        strength = match.group("strength").strip()
        parsed.append({
            "raw_component": chunk,
            "ingredient_raw": ingredient,
            "strength_raw": strength,
        })
        if not ingredient or not STRENGTH_RE.fullmatch(strength):
            complete = False
    if not complete:
        return parsed, "needs_review"
    if any(item["strength_raw"].casefold() in {"na", "n/a"} for item in parsed):
        return parsed, "ambiguous_missing_strength"
    return parsed, "candidate_parse_complete"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", required=True, type=Path, help="Source CSV")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--review-sample", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20261101)
    args = parser.parse_args()

    rows: list[dict[str, Any]] = []
    with args.file.open("r", encoding="utf-8-sig", newline="") as stream:
        for row_id, row in enumerate(csv.DictReader(stream)):
            name = clean(row.get("name"))
            composition = clean(row.get("composition"))
            ingredients, parse_status = parse_composition(composition)
            rows.append({
                "source_row_id": row_id,
                "name": name,
                "composition_raw": composition,
                "ingredients_candidate_json": json.dumps(ingredients, ensure_ascii=False),
                "parse_status": parse_status,
                "uses_source": clean(row.get("uses")),
                "side_effects_source": clean(row.get("side_effects")),
                "image_url_source_unreviewed": clean(row.get("image_url")),
                "source_dataset": SOURCE,
                "source_verification_status": "single_source_unverified",
                "image_review_status": "not_reviewed",
                "permitted_current_use": "text_parser_stress_test_only",
                "human_review_status": "pending",
            })

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[name_key(row["name"])].append(row)
    conflict_keys = {
        key for key, group in groups.items()
        if len({r["composition_raw"].casefold() for r in group}) > 1
    }
    for row in rows:
        key = name_key(row["name"])
        row["duplicate_name_group_size"] = len(groups[key])
        row["duplicate_name_composition_conflict"] = str(key in conflict_keys).lower()

    fields = list(rows[0]) if rows else []
    args.output_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = args.output_dir / "indian-medicines-candidates.csv"
    with catalog_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    # Reproducible sample, stratified by candidate parse outcome.
    rng = random.Random(args.seed)
    strata: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        strata[row["parse_status"]].append(row)
    sample: list[dict[str, Any]] = []
    remaining = max(0, args.review_sample)
    names = sorted(strata)
    while remaining and any(strata.values()):
        advanced = False
        for status in names:
            if remaining == 0:
                break
            if strata[status]:
                sample.append(strata[status].pop(rng.randrange(len(strata[status]))))
                remaining -= 1
                advanced = True
        if not advanced:
            break
    queue_fields = [
        "source_row_id", "name", "composition_raw", "ingredients_candidate_json",
        "parse_status", "image_url_source_unreviewed", "source_dataset",
        "source_verification_status", "image_review_status", "human_review_status",
        "duplicate_name_group_size", "duplicate_name_composition_conflict",
        "reviewer", "independent_source_and_reference", "image_matches_exact_product_and_strength",
        "transcription_correct", "review_notes",
    ]
    queue_path = args.output_dir / "indian-medicines-human-review.csv"
    with queue_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=queue_fields, extrasaction="ignore")
        writer.writeheader()
        for row in sample:
            writer.writerow({**row, "reviewer": "", "independent_source_and_reference": "",
                             "image_matches_exact_product_and_strength": "",
                             "transcription_correct": "", "review_notes": ""})

    summary = {
        "source_dataset": SOURCE,
        "rows": len(rows),
        "candidate_parse_status_counts": {
            status: sum(row["parse_status"] == status for row in rows)
            for status in sorted({row["parse_status"] for row in rows})
        },
        "normalized_duplicate_name_groups": sum(len(group) > 1 for group in groups.values()),
        "duplicate_name_composition_conflict_groups": len(conflict_keys),
        "review_queue_rows": len(sample),
        "sample_seed": args.seed,
        "limitations": [
            "Candidate parsing is syntactic and is not chemical or clinical validation.",
            "All labels remain single-source and unverified.",
            "Image URLs were not downloaded or inspected; usage rights are unconfirmed.",
            "Outputs are suitable for parser stress testing and human review, not image-model training.",
        ],
    }
    summary_path = args.output_dir / "indian-medicines-preparation-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"catalog": str(catalog_path), "review_queue": str(queue_path),
                      "summary": str(summary_path), **summary}, indent=2))


if __name__ == "__main__":
    main()
