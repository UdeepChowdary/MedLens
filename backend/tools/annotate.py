"""CLI tool for creating, populating, and verifying medicine packaging annotations."""

import argparse
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

from app.schemas.dataset import (
    PackagingAnnotationDoc,
    ImageMetadata,
    ImageDimensions,
    ProvenanceMetadata,
    QualityFlags,
    EntityAnnotation,
    DatasetEntityLabel,
    PackagingType,
    ReviewStatus,
)


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 cryptographic digest of image file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def initialize_annotation(
    image_path: Path,
    output_dir: Path,
    product_family: str,
    packaging_type: str = "blister_foil",
    brand_name: Optional[str] = None,
    manufacturer: Optional[str] = None,
    annotator_id: str = "clinical-annotator-01",
    source: str = "MedLens Clinical Lab / Public Domain",
    license_str: str = "CC-BY-4.0",
) -> Path:
    """Creates a new validated annotation document for a raw image file."""
    if not image_path.exists():
        raise FileNotFoundError(f"Raw image file not found: {image_path}")

    # Inspect image dimensions
    with Image.open(image_path) as img:
        width, height = img.size
        img_format = img.format.lower() if img.format else image_path.suffix.lstrip(".").lower()

    file_sha256 = compute_sha256(image_path)
    clean_stem = image_path.stem.replace(" ", "_").lower()
    image_id = f"img-{clean_stem}"

    doc = PackagingAnnotationDoc(
        schema_version="1.0.0",
        image_metadata=ImageMetadata(
            image_id=image_id,
            file_name=image_path.name,
            format=img_format,
            dimensions=ImageDimensions(width=width, height=height),
            sha256=file_sha256,
            packaging_type=PackagingType(packaging_type),
            product_family=product_family,
            brand_name=brand_name,
            manufacturer=manufacturer,
            provenance=ProvenanceMetadata(
                source=source,
                license=license_str,
                annotator_id=annotator_id,
                verified_by_human=False,
                date_annotated=datetime.now(timezone.utc).isoformat(),
            ),
        ),
        quality_flags=QualityFlags(),
        transcription="",
        entities=[],
        review_status=ReviewStatus.DRAFT,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{image_id}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(doc.model_dump(), f, indent=2)

    return out_file


def add_entity_to_annotation(
    annotation_path: Path,
    label: str,
    raw_text: str,
    bbox: Tuple[int, int, int, int],
    normalized_value: Optional[str] = None,
) -> None:
    """Appends an entity token to an existing annotation file and validates bounds."""
    with open(annotation_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    doc = PackagingAnnotationDoc(**data)

    new_entity = EntityAnnotation(
        label=DatasetEntityLabel(label),
        raw_text=raw_text,
        normalized_value=normalized_value or raw_text,
        bbox=bbox,
    )
    doc.entities.append(new_entity)

    with open(annotation_path, "w", encoding="utf-8") as f:
        json.dump(doc.model_dump(), f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="MedLens Medicine Packaging Annotation CLI.")
    subparsers = parser.add_subparsers(dest="command")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize annotation template for an image")
    init_parser.add_argument("--image", required=True, help="Path to raw image file")
    init_parser.add_argument("--output-dir", default="data/annotations", help="Annotations output directory")
    init_parser.add_argument("--product-family", required=True, help="Product family key for leakage prevention")
    init_parser.add_argument("--packaging-type", default="blister_foil", help="Packaging format (blister_foil, paper_box, etc.)")
    init_parser.add_argument("--brand", default=None, help="Brand name")
    init_parser.add_argument("--manufacturer", default=None, help="Manufacturer name")
    init_parser.add_argument("--annotator", default="annotator-01", help="Annotator ID")

    # add-entity command
    add_parser = subparsers.add_parser("add-entity", help="Add labeled entity to existing annotation")
    add_parser.add_argument("--file", required=True, help="Path to annotation JSON file")
    add_parser.add_argument("--label", required=True, help="Entity label (BRAND, INGREDIENT, STRENGTH, etc.)")
    add_parser.add_argument("--text", required=True, help="Verbatim printed text")
    add_parser.add_argument("--bbox", nargs=4, type=int, required=True, metavar=("YMIN", "XMIN", "YMAX", "XMAX"), help="Normalized box in 0..1000")
    add_parser.add_argument("--norm", default=None, help="Normalized value")

    args = parser.parse_args()

    if args.command == "init":
        out = initialize_annotation(
            Path(args.image),
            Path(args.output_dir),
            product_family=args.product_family,
            packaging_type=args.packaging_type,
            brand_name=args.brand,
            manufacturer=args.manufacturer,
            annotator_id=args.annotator,
        )
        print(f"Created annotation draft: {out}")
    elif args.command == "add-entity":
        add_entity_to_annotation(
            Path(args.file),
            label=args.label,
            raw_text=args.text,
            bbox=tuple(args.bbox),
            normalized_value=args.norm,
        )
        print(f"Added {args.label} ('{args.text}') to {args.file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
