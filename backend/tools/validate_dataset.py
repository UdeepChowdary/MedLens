"""Dataset validation script detecting missing fields, invalid coordinates, duplicate images, and inconsistent units."""

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Valid pharmaceutical units per Capstone Blueprint Section 07
VALID_UNITS = {
    "mg",
    "g",
    "mcg",
    "ug",
    "ml",
    "l",
    "iu",
    "u",
    "% w/v",
    "% w/w",
    "% v/v",
    "%",
    "mg/ml",
    "mg/5ml",
    "mcg/dose",
    "q.s.",
}

STRENGTH_REGEX = re.compile(
    r"^(\d+(?:\.\d+)?)\s*([a-zA-Z%]+(?:\s*[a-zA-Z%/.0-9]+)*)$", re.IGNORECASE
)


class ValidationErrorItem:
    """Individual dataset validation issue."""

    def __init__(self, annotation_file: str, error_type: str, message: str, severity: str = "ERROR"):
        self.annotation_file = annotation_file
        self.error_type = error_type
        self.message = message
        self.severity = severity  # "ERROR" or "WARNING"

    def to_dict(self) -> Dict[str, str]:
        return {
            "annotation_file": self.annotation_file,
            "error_type": self.error_type,
            "message": self.message,
            "severity": self.severity,
        }

    def __str__(self) -> str:
        return f"[{self.severity}] {self.annotation_file} -> {self.error_type}: {self.message}"


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 digest of image file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_strength_text(raw_text: str) -> Tuple[bool, str]:
    """Validates that a STRENGTH entity contains a recognized numeric magnitude and unit."""
    cleaned = raw_text.strip().lower()
    if cleaned == "q.s." or cleaned.startswith("q.s"):
        return True, "q.s."

    match = STRENGTH_REGEX.match(cleaned)
    if not match:
        return False, f"Cannot parse numeric value and unit from strength token '{raw_text}'"

    _, unit = match.groups()
    unit = unit.strip()
    if unit not in VALID_UNITS:
        return False, f"Unrecognized clinical pharmaceutical unit '{unit}' in token '{raw_text}'"

    return True, unit


def validate_annotation_file(
    filepath: Path,
    raw_images_dir: Path,
    seen_hashes: Dict[str, str],
    check_image_exists: bool = True,
) -> List[ValidationErrorItem]:
    """Validates single annotation document against MedLens dataset rules."""
    errors: List[ValidationErrorItem] = []
    rel_path = filepath.name

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        errors.append(ValidationErrorItem(rel_path, "JSON_SYNTAX_ERROR", str(e)))
        return errors

    # 1. Schema Version Check
    if "schema_version" not in data:
        errors.append(ValidationErrorItem(rel_path, "MISSING_FIELD", "Missing 'schema_version'."))

    # 2. Image Metadata Checks
    meta = data.get("image_metadata")
    if not isinstance(meta, dict):
        errors.append(ValidationErrorItem(rel_path, "MISSING_FIELD", "Missing 'image_metadata' object."))
        return errors

    required_meta = ["image_id", "file_name", "sha256", "packaging_type", "product_family", "dimensions"]
    for f in required_meta:
        if f not in meta or not meta[f]:
            errors.append(ValidationErrorItem(rel_path, "MISSING_FIELD", f"Missing 'image_metadata.{f}'."))

    image_sha256 = meta.get("sha256", "").strip().lower()
    if image_sha256:
        if len(image_sha256) != 64:
            errors.append(ValidationErrorItem(rel_path, "INVALID_SHA256", f"SHA256 hash must be 64 characters, got {len(image_sha256)}."))
        else:
            # Duplicate Image Hash Detection
            if image_sha256 in seen_hashes:
                prev_file = seen_hashes[image_sha256]
                errors.append(
                    ValidationErrorItem(
                        rel_path,
                        "DUPLICATE_IMAGE_HASH",
                        f"Image hash {image_sha256[:12]}... matches existing annotation '{prev_file}'. Duplicate detected!",
                    )
                )
            else:
                seen_hashes[image_sha256] = rel_path

    # Check physical image file existence & hash verification if raw directory supplied
    file_name = meta.get("file_name")
    if file_name and check_image_exists and raw_images_dir.exists():
        raw_image_path = raw_images_dir / file_name
        if not raw_image_path.exists():
            errors.append(
                ValidationErrorItem(
                    rel_path, "MISSING_IMAGE_FILE", f"Raw image '{file_name}' not found in {raw_images_dir}."
                )
            )
        else:
            actual_hash = compute_sha256(raw_image_path)
            if image_sha256 and actual_hash != image_sha256:
                errors.append(
                    ValidationErrorItem(
                        rel_path,
                        "HASH_MISMATCH",
                        f"Declared SHA256 '{image_sha256[:12]}...' does not match physical file hash '{actual_hash[:12]}...'.",
                    )
                )

    # 3. Transcription Check
    transcription = data.get("transcription", "")
    if not isinstance(transcription, str) or not transcription.strip():
        errors.append(ValidationErrorItem(rel_path, "EMPTY_TRANSCRIPTION", "Transcription text is empty."))

    # 4. Entities and Bounding Box Validation
    entities = data.get("entities")
    if not isinstance(entities, list):
        errors.append(ValidationErrorItem(rel_path, "INVALID_ENTITIES", "'entities' must be a list."))
        return errors

    has_brand = False
    has_ingredient = False

    for idx, ent in enumerate(entities):
        label = ent.get("label")
        raw_text = ent.get("raw_text", "")
        bbox = ent.get("bbox")

        if not label:
            errors.append(ValidationErrorItem(rel_path, "INVALID_ENTITY", f"Entity at index {idx} missing 'label'."))
            continue

        if label in ["BRAND", "PRODUCT_NAME"]:
            has_brand = True
        if label in ["INGREDIENT", "SALT_FORM"]:
            has_ingredient = True

        if not raw_text or not raw_text.strip():
            errors.append(ValidationErrorItem(rel_path, "EMPTY_RAW_TEXT", f"Entity {label} at index {idx} has empty raw_text."))

        # Bbox validation: [ymin, xmin, ymax, xmax] in range 0..1000
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            errors.append(ValidationErrorItem(rel_path, "INVALID_BBOX_FORMAT", f"Entity {label} at index {idx} bbox must be 4 elements."))
        else:
            ymin, xmin, ymax, xmax = bbox
            for coord, name in zip([ymin, xmin, ymax, xmax], ["ymin", "xmin", "ymax", "xmax"]):
                if not isinstance(coord, (int, float)) or coord < 0 or coord > 1000:
                    errors.append(ValidationErrorItem(rel_path, "BBOX_OUT_OF_BOUNDS", f"Entity {label} {name}={coord} outside [0, 1000]."))
            if ymin >= ymax:
                errors.append(ValidationErrorItem(rel_path, "INVALID_BBOX_SPAN", f"Entity {label} ymin ({ymin}) >= ymax ({ymax})."))
            if xmin >= xmax:
                errors.append(ValidationErrorItem(rel_path, "INVALID_BBOX_SPAN", f"Entity {label} xmin ({xmin}) >= xmax ({xmax})."))

        # Strength / Unit validation
        if label in ["STRENGTH", "CONCENTRATION"]:
            valid, reason = validate_strength_text(raw_text)
            if not valid:
                errors.append(ValidationErrorItem(rel_path, "INCONSISTENT_UNIT", reason, severity="ERROR"))

        # Character span validation (if char_span present)
        char_span = ent.get("char_span")
        if char_span is not None:
            if not isinstance(char_span, (list, tuple)) or len(char_span) != 2:
                errors.append(
                    ValidationErrorItem(
                        rel_path,
                        "INVALID_CHAR_SPAN_FORMAT",
                        f"Entity {label} at index {idx} char_span must be a 2-element [start, end] list.",
                    )
                )
            else:
                c_start, c_end = char_span
                if not isinstance(c_start, int) or not isinstance(c_end, int):
                    errors.append(
                        ValidationErrorItem(
                            rel_path,
                            "INVALID_CHAR_SPAN_FORMAT",
                            f"Entity {label} at index {idx} char_span indices must be integers.",
                        )
                    )
                elif c_start < 0 or c_end > len(transcription) or c_start >= c_end:
                    errors.append(
                        ValidationErrorItem(
                            rel_path,
                            "CHAR_SPAN_OUT_OF_BOUNDS",
                            f"Entity {label} char_span [{c_start}, {c_end}] out of bounds for transcription length {len(transcription)}.",
                        )
                    )
                else:
                    sliced = transcription[c_start:c_end]
                    if sliced != raw_text:
                        errors.append(
                            ValidationErrorItem(
                                rel_path,
                                "CHAR_SPAN_TEXT_MISMATCH",
                                f"Entity {label} slice '{sliced}' does not match declared raw_text '{raw_text}'.",
                            )
                        )

    # 5. Provenance & Real Packaging Ground Truth Policy Check
    prov = meta.get("provenance", {})
    if not isinstance(prov, dict):
        errors.append(ValidationErrorItem(rel_path, "MISSING_FIELD", "Missing 'image_metadata.provenance'."))
    else:
        if not prov.get("source"):
            errors.append(ValidationErrorItem(rel_path, "MISSING_FIELD", "Missing 'provenance.source'."))
        if not prov.get("annotator_id"):
            errors.append(ValidationErrorItem(rel_path, "MISSING_FIELD", "Missing 'provenance.annotator_id'."))

        review_status = data.get("review_status")
        notes = str(prov.get("notes") or "").lower()
        source_str = str(prov.get("source") or "").lower()

        is_synthetic = (
            "synthetic" in notes
            or "synthetic" in source_str
            or "3d generic illustration" in notes
            or "do not use as ground truth" in notes
        )
        if is_synthetic and review_status == "verified_by_human":
            errors.append(
                ValidationErrorItem(
                    rel_path,
                    "SYNTHETIC_CANNOT_BE_VERIFIED",
                    "Synthetic illustrations and unreadable promotional images cannot be marked as 'verified_by_human' real packaging ground truth.",
                )
            )

    # Clinical completeness warning
    if not has_brand and not has_ingredient:
        errors.append(
            ValidationErrorItem(
                rel_path,
                "MISSING_CORE_CLINICAL_FIELDS",
                "Annotation contains neither BRAND nor INGREDIENT/SALT_FORM labels.",
                severity="WARNING",
            )
        )

    return errors


def validate_dataset(
    annotations_dir: Path,
    raw_images_dir: Path,
    check_image_exists: bool = True,
) -> Dict[str, Any]:
    """Validates all annotation JSON files in directory."""
    if not annotations_dir.exists():
        raise FileNotFoundError(f"Annotations directory not found: {annotations_dir}")

    json_files = list(annotations_dir.glob("*.json"))
    seen_hashes: Dict[str, str] = {}
    all_issues: List[ValidationErrorItem] = []

    for jf in json_files:
        issues = validate_annotation_file(
            jf, raw_images_dir, seen_hashes, check_image_exists=check_image_exists
        )
        all_issues.extend(issues)

    error_count = sum(1 for i in all_issues if i.severity == "ERROR")
    warning_count = sum(1 for i in all_issues if i.severity == "WARNING")

    return {
        "total_files": len(json_files),
        "valid_files": len(json_files) - len({i.annotation_file for i in all_issues if i.severity == "ERROR"}),
        "error_count": error_count,
        "warning_count": warning_count,
        "is_valid": error_count == 0,
        "issues": [i.to_dict() for i in all_issues],
    }


def validate_split_manifests(
    splits_dir: Path,
    annotations_dir: Path,
    require_human_verified: bool = True,
) -> Dict[str, Any]:
    """Validates split manifests (train, val, test) ensuring zero leakage and evaluation split eligibility."""
    if not splits_dir.exists():
        raise FileNotFoundError(f"Splits directory not found: {splits_dir}")

    issues: List[ValidationErrorItem] = []
    split_families: Dict[str, Set[str]] = {}

    for split_name in ["train", "val", "test"]:
        manifest_file = splits_dir / f"{split_name}.json"
        if not manifest_file.exists():
            issues.append(
                ValidationErrorItem(
                    manifest_file.name,
                    "MISSING_SPLIT_MANIFEST",
                    f"Required split manifest '{split_name}.json' missing in {splits_dir}.",
                )
            )
            continue

        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                split_data = json.load(f)
        except Exception as e:
            issues.append(ValidationErrorItem(manifest_file.name, "JSON_SYNTAX_ERROR", str(e)))
            continue

        families = set(split_data.get("product_families", []))
        split_families[split_name] = families
        items = split_data.get("images", [])

        for it in items:
            ann_filename = it.get("annotation_file")
            image_id = it.get("image_id", "unknown")
            review_status = it.get("review_status", "draft")
            is_synthetic = it.get("is_synthetic_fixture", False)

            # Check that referenced annotation file actually exists
            ann_path = annotations_dir / ann_filename
            if not ann_path.exists():
                issues.append(
                    ValidationErrorItem(
                        manifest_file.name,
                        "MISSING_ANNOTATION_FILE",
                        f"Split {split_name} references non-existent annotation '{ann_filename}'.",
                    )
                )
                continue

            # In evaluation splits (val, test), records MUST be verified by human and not synthetic
            if split_name in ("val", "test"):
                sev = "ERROR" if require_human_verified else "WARNING"
                if review_status != "verified_by_human":
                    issues.append(
                        ValidationErrorItem(
                            manifest_file.name,
                            "UNREVIEWED_RECORD_IN_EVAL_SPLIT",
                            f"Evaluation split '{split_name}' contains unverified item '{image_id}' with status '{review_status}'.",
                            severity=sev,
                        )
                    )
                if is_synthetic:
                    issues.append(
                        ValidationErrorItem(
                            manifest_file.name,
                            "SYNTHETIC_RECORD_IN_EVAL_SPLIT",
                            f"Evaluation split '{split_name}' contains synthetic fixture '{image_id}'.",
                            severity=sev,
                        )
                    )

    # Verify zero product family leakage
    train_f = split_families.get("train", set())
    val_f = split_families.get("val", set())
    test_f = split_families.get("test", set())

    leak_train_val = train_f & val_f
    leak_train_test = train_f & test_f
    leak_val_test = val_f & test_f

    if leak_train_val:
        issues.append(
            ValidationErrorItem(
                "splits",
                "PRODUCT_FAMILY_LEAKAGE",
                f"Train and Val share product families: {sorted(list(leak_train_val))}",
            )
        )
    if leak_train_test:
        issues.append(
            ValidationErrorItem(
                "splits",
                "PRODUCT_FAMILY_LEAKAGE",
                f"Train and Test share product families: {sorted(list(leak_train_test))}",
            )
        )
    if leak_val_test:
        issues.append(
            ValidationErrorItem(
                "splits",
                "PRODUCT_FAMILY_LEAKAGE",
                f"Val and Test share product families: {sorted(list(leak_val_test))}",
            )
        )

    error_count = sum(1 for i in issues if i.severity == "ERROR")
    return {
        "is_valid": error_count == 0,
        "error_count": error_count,
        "issues": [i.to_dict() for i in issues],
    }


def main():
    parser = argparse.ArgumentParser(description="Validate MedLens medicine packaging dataset.")
    parser.add_argument("--annotations-dir", default="data/annotations", help="Path to annotations folder")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw images folder")
    parser.add_argument("--splits-dir", default=None, help="Optional path to splits folder to validate manifests")
    parser.add_argument("--skip-image-check", action="store_true", help="Skip physical image file checks")
    args = parser.parse_args()

    ann_dir = Path(args.annotations_dir)
    raw_dir = Path(args.raw_dir)

    print(f"Validating dataset in {ann_dir}...")
    result = validate_dataset(ann_dir, raw_dir, check_image_exists=not args.skip_image_check)

    print(f"\n--- Validation Summary ---")
    print(f"Total annotations analyzed: {result['total_files']}")
    print(f"Valid annotations: {result['valid_files']}")
    print(f"Errors detected: {result['error_count']}")
    print(f"Warnings detected: {result['warning_count']}")

    if result["issues"]:
        print("\n--- Detailed Issues ---")
        for iss in result["issues"]:
            print(f"[{iss['severity']}] {iss['annotation_file']}: {iss['error_type']} - {iss['message']}")

    if args.splits_dir:
        splits_path = Path(args.splits_dir)
        print(f"\nValidating splits in {splits_path}...")
        split_result = validate_split_manifests(splits_path, ann_dir)
        print(f"Splits valid: {split_result['is_valid']}, Errors: {split_result['error_count']}")
        for iss in split_result["issues"]:
            print(f"[{iss['severity']}] {iss['annotation_file']}: {iss['error_type']} - {iss['message']}")
        if not split_result["is_valid"]:
            result["is_valid"] = False

    if result["is_valid"]:
        print("\nSUCCESS: All dataset annotations passed validation!")
        sys.exit(0)
    else:
        print("\nFAILED: Dataset contains validation errors that must be resolved.")
        sys.exit(1)


if __name__ == "__main__":
    main()
