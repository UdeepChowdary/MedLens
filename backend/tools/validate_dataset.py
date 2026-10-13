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


def main():
    parser = argparse.ArgumentParser(description="Validate MedLens medicine packaging dataset.")
    parser.add_argument("--annotations-dir", default="data/annotations", help="Path to annotations folder")
    parser.add_argument("--raw-dir", default="data/raw", help="Path to raw images folder")
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

    if result["is_valid"]:
        print("\nSUCCESS: All dataset annotations passed validation!")
        sys.exit(0)
    else:
        print("\nFAILED: Dataset contains validation errors that must be resolved.")
        sys.exit(1)


if __name__ == "__main__":
    main()
