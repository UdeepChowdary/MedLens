"""BIO Sequence Labeling Preprocessing and Token Alignment Tool.

Converts MedLens packaging annotations into token-classification datasets
using the 23-tag BIO schema defined in Blueprint Section 6.2 and 6.4.
Validates tokenizer alignment and ensures unverified/synthetic fixtures
are explicitly flagged.
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

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

# Canonical 23 BIO tags: "O" + 2 * 11 entity types
BIO_TAGS = ["O"]
for entity in CANONICAL_ENTITIES:
    BIO_TAGS.extend([f"B-{entity}", f"I-{entity}"])

assert len(BIO_TAGS) == 23, f"Expected 23 BIO tags, got {len(BIO_TAGS)}"

LABEL2ID = {tag: i for i, tag in enumerate(BIO_TAGS)}
ID2LABEL = {i: tag for i, tag in enumerate(BIO_TAGS)}

# Entity specificity priority for resolving overlapping spans
ENTITY_PRIORITY = {
    "INGREDIENT": 100,
    "STRENGTH": 90,
    "CONCENTRATION": 85,
    "SALT_FORM": 80,
    "DOSAGE_FORM": 75,
    "STRENGTH_BASIS": 70,
    "ROUTE": 65,
    "RELEASE_TYPE": 60,
    "BRAND": 50,
    "PRODUCT_NAME": 30,
    "COMPOSITION_HEADER": 10,
}


def tokenize_with_offsets(text: str) -> List[Tuple[str, int, int]]:
    """Splits text into words/symbols while tracking exact start and end character offsets.
    
    Uses unicode regex matching words and punctuation while skipping whitespace.
    """
    token_pattern = re.compile(r"\w+|[^\w\s]")
    tokens = []
    for match in token_pattern.finditer(text):
        tokens.append((match.group(0), match.start(), match.end()))
    return tokens


def validate_alignment(
    text: str,
    tokens: List[Tuple[str, int, int]],
    entities: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Validates that character spans align cleanly with token boundaries.
    
    Detects:
    1. Mid-token clippings (span starts or ends inside a token).
    2. Transcription mismatches (text at span doesn't match raw_text).
    3. Out of bounds spans.
    """
    warnings = []
    token_starts = {tok[1]: idx for idx, tok in enumerate(tokens)}
    token_ends = {tok[2]: idx for idx, tok in enumerate(tokens)}

    for entity in entities:
        char_span = entity.get("char_span")
        if not char_span or len(char_span) != 2:
            warnings.append({
                "type": "missing_char_span",
                "label": entity.get("label"),
                "raw_text": entity.get("raw_text"),
                "message": "Entity is missing valid char_span [start, end].",
            })
            continue

        start, end = char_span
        if start < 0 or end > len(text) or start >= end:
            warnings.append({
                "type": "out_of_bounds",
                "label": entity.get("label"),
                "span": [start, end],
                "message": f"Span [{start}, {end}] is out of bounds for text of length {len(text)}.",
            })
            continue

        expected_text = entity.get("raw_text", "")
        actual_slice = text[start:end]
        if expected_text and actual_slice.strip() != expected_text.strip():
            warnings.append({
                "type": "text_mismatch",
                "label": entity.get("label"),
                "expected": expected_text,
                "found_slice": actual_slice,
                "message": f"Text slice '{actual_slice}' does not match expected '{expected_text}'.",
            })

        # Check token boundary alignment
        if start not in token_starts:
            # Find the token clipping this start
            clipping_tok = next((tok for tok in tokens if tok[1] < start < tok[2]), None)
            warnings.append({
                "type": "mid_token_clip_start",
                "label": entity.get("label"),
                "span_start": start,
                "clipping_token": clipping_tok,
                "message": f"Span starts at char {start} inside token {clipping_tok}.",
            })

        if end not in token_ends:
            clipping_tok = next((tok for tok in tokens if tok[1] < end < tok[2]), None)
            warnings.append({
                "type": "mid_token_clip_end",
                "label": entity.get("label"),
                "span_end": end,
                "clipping_token": clipping_tok,
                "message": f"Span ends at char {end} inside token {clipping_tok}.",
            })

    return warnings


def convert_doc_to_bio(
    annotation_doc: Dict[str, Any],
) -> Dict[str, Any]:
    """Converts a single PackagingAnnotationDoc into BIO token classification format."""
    text = annotation_doc.get("transcription", "")
    entities = annotation_doc.get("entities", [])
    tokens_with_offsets = tokenize_with_offsets(text)
    warnings = validate_alignment(text, tokens_with_offsets, entities)

    tokens = [tok[0] for tok in tokens_with_offsets]
    ner_labels = ["O"] * len(tokens)
    token_assigned_priority = [-1] * len(tokens)

    # Sort entities by priority descending to assign high-priority entities first
    sorted_entities = sorted(
        entities,
        key=lambda e: ENTITY_PRIORITY.get(e.get("label", ""), 0),
        reverse=True,
    )

    for entity in sorted_entities:
        label = entity.get("label")
        if label not in CANONICAL_ENTITIES:
            continue

        char_span = entity.get("char_span")
        if not char_span or len(char_span) != 2:
            continue

        e_start, e_end = char_span
        priority = ENTITY_PRIORITY.get(label, 0)

        # Identify all tokens covered by this entity span
        covered_indices = [
            i for i, tok in enumerate(tokens_with_offsets)
            if not (tok[2] <= e_start or tok[1] >= e_end)
        ]

        if not covered_indices:
            continue

        # Check if high-priority entities already claimed these tokens
        can_assign = any(token_assigned_priority[i] < priority for i in covered_indices)
        if not can_assign:
            continue

        is_first = True
        for idx in covered_indices:
            if token_assigned_priority[idx] <= priority:
                tag = f"B-{label}" if is_first else f"I-{label}"
                ner_labels[idx] = tag
                token_assigned_priority[idx] = priority
                is_first = False

    ner_tags = [LABEL2ID[tag] for tag in ner_labels]

    meta = annotation_doc.get("image_metadata", {})
    return {
        "id": meta.get("image_id", "unknown"),
        "image_id": meta.get("image_id", "unknown"),
        "product_family": meta.get("product_family"),
        "packaging_type": meta.get("packaging_type"),
        "is_synthetic_fixture": "-fixture" in str(meta.get("product_family", "")),
        "review_status": annotation_doc.get("review_status", "draft"),
        "eligible_for_real_training": (
            annotation_doc.get("review_status") == "verified_by_human"
            and "-fixture" not in str(meta.get("product_family", ""))
        ),
        "text": text,
        "tokens": tokens,
        "ner_labels": ner_labels,
        "ner_tags": ner_tags,
        "spans": [
            {
                "label": e.get("label"),
                "start_char": e.get("char_span", [0, 0])[0],
                "end_char": e.get("char_span", [0, 0])[1],
                "raw_text": e.get("raw_text"),
                "normalized_value": e.get("normalized_value"),
            }
            for e in entities
            if e.get("char_span")
        ],
        "alignment_warnings": warnings,
    }


def prepare_bio_dataset(
    annotations_dir: Path,
    splits_dir: Optional[Path],
    output_dir: Path,
) -> Dict[str, Any]:
    """Generates the processed BIO token-classification dataset and quality summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    all_docs: Dict[str, Dict[str, Any]] = {}

    for file_path in sorted(annotations_dir.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                doc = json.load(f)
            img_id = doc.get("image_metadata", {}).get("image_id") or file_path.stem
            all_docs[file_path.name] = doc
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")

    processed_samples = {}
    for filename, doc in all_docs.items():
        processed_samples[filename] = convert_doc_to_bio(doc)

    # Save full processed dataset
    full_dataset_path = output_dir / "bio_all.json"
    with open(full_dataset_path, "w", encoding="utf-8") as f:
        json.dump(list(processed_samples.values()), f, indent=2)

    split_results = {}
    if splits_dir and splits_dir.exists():
        for split_name in ["train", "val", "test"]:
            split_file = splits_dir / f"{split_name}.json"
            if split_file.exists():
                with open(split_file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                split_samples = []
                for img_entry in manifest.get("images", []):
                    ann_file = img_entry.get("annotation_file")
                    if ann_file in processed_samples:
                        split_samples.append(processed_samples[ann_file])

                out_path = output_dir / f"bio_{split_name}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(split_samples, f, indent=2)

                split_results[split_name] = {
                    "count": len(split_samples),
                    "file": str(out_path.name),
                    "eligible_for_training_count": sum(
                        1 for s in split_samples if s["eligible_for_real_training"]
                    ),
                    "synthetic_count": sum(
                        1 for s in split_samples if s["is_synthetic_fixture"]
                    ),
                }

    # Aggregate BIO tag counts across all samples
    tag_counts = {tag: 0 for tag in BIO_TAGS}
    total_tokens = 0
    total_alignment_warnings = 0

    for sample in processed_samples.values():
        for tag in sample["ner_labels"]:
            tag_counts[tag] += 1
            total_tokens += 1
        total_alignment_warnings += len(sample["alignment_warnings"])

    summary = {
        "schema_version": "1.0.0",
        "canonical_entity_count": len(CANONICAL_ENTITIES),
        "canonical_entities": CANONICAL_ENTITIES,
        "bio_tag_count": len(BIO_TAGS),
        "bio_tags": BIO_TAGS,
        "label2id": LABEL2ID,
        "id2label": ID2LABEL,
        "dataset_statistics": {
            "total_documents": len(processed_samples),
            "total_tokens": total_tokens,
            "total_alignment_warnings": total_alignment_warnings,
            "eligible_for_real_training_documents": sum(
                1 for s in processed_samples.values() if s["eligible_for_real_training"]
            ),
            "synthetic_fixture_documents": sum(
                1 for s in processed_samples.values() if s["is_synthetic_fixture"]
            ),
            "flagged_or_unverified_documents": sum(
                1 for s in processed_samples.values() if s["review_status"] != "verified_by_human"
            ),
            "tag_distribution": tag_counts,
        },
        "splits": split_results,
    }

    summary_path = output_dir / "bio_dataset_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        f"Processed {len(processed_samples)} documents ({total_tokens} tokens) "
        f"into {output_dir}. Total warnings: {total_alignment_warnings}."
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description="Prepare BIO dataset from MedLens annotations.")
    parser.add_argument(
        "--annotations-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "annotations",
        help="Path to annotations directory",
    )
    parser.add_argument(
        "--splits-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "splits",
        help="Path to splits directory",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent / "data" / "processed",
        help="Path to output processed dataset directory",
    )

    args = parser.parse_args()
    summary = prepare_bio_dataset(args.annotations_dir, args.splits_dir, args.output_dir)

    print("\n================== BIO DATASET SUMMARY ==================")
    print(f"Total Documents: {summary['dataset_statistics']['total_documents']}")
    print(f"Total Tokens: {summary['dataset_statistics']['total_tokens']}")
    print(f"Canonical Entities: {summary['canonical_entity_count']}")
    print(f"Total BIO Tags: {summary['bio_tag_count']}")
    print(f"Alignment Warnings: {summary['dataset_statistics']['total_alignment_warnings']}")
    print(f"Synthetic Fixtures: {summary['dataset_statistics']['synthetic_fixture_documents']}")
    print(f"Eligible for Real Training: {summary['dataset_statistics']['eligible_for_real_training_documents']}")
    print("\nNon-zero Tag Distribution:")
    for tag, count in summary["dataset_statistics"]["tag_distribution"].items():
        if count > 0:
            print(f"  {tag:<22}: {count}")
    print("=========================================================\n")


if __name__ == "__main__":
    main()
