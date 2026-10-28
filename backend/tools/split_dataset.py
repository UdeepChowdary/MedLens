"""Leakage-free dataset splitting tool grouping by product family and brand."""

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def load_annotations(annotations_dir: Path) -> List[Tuple[str, Dict[str, Any]]]:
    """Loads all JSON annotation files from directory."""
    records = []
    for filepath in sorted(annotations_dir.glob("*.json")):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            records.append((filepath.name, data))
    return records


def split_dataset(
    annotations_dir: Path,
    output_dir: Path,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> Dict[str, Any]:
    """Splits dataset into train, val, and test partitions with zero product family leakage."""
    if abs((train_ratio + val_ratio + test_ratio) - 1.0) > 1e-4:
        raise ValueError(f"Split ratios must sum to 1.0. Got: {train_ratio + val_ratio + test_ratio}")

    records = load_annotations(annotations_dir)
    if not records:
        raise ValueError(f"No annotation JSON files found in {annotations_dir}")

    # 1. Group images by product_family to prevent leakage
    product_groups: Dict[str, List[Tuple[str, Dict[str, Any]]]] = defaultdict(list)
    for filename, doc in records:
        meta = doc.get("image_metadata", {})
        # Group key: product_family or brand_name fallback
        family = meta.get("product_family") or meta.get("brand_name") or f"unlabeled_{filename}"
        product_groups[family].append((filename, doc))

    all_families = sorted(list(product_groups.keys()))
    rng = random.Random(seed)
    rng.shuffle(all_families)

    # 2. Partition product families into Train, Val, Test
    num_families = len(all_families)
    if num_families < 3:
        # Edge case: If very few families during initial bootstrap, distribute across splits
        train_families = [all_families[0]]
        val_families = [all_families[1]] if num_families > 1 else []
        test_families = [all_families[2]] if num_families > 2 else []
    else:
        num_train = max(1, int(round(num_families * train_ratio)))
        num_val = max(1, int(round(num_families * val_ratio)))
        # Remaining go to test to ensure exact coverage
        train_families = all_families[:num_train]
        val_families = all_families[num_train : num_train + num_val]
        test_families = all_families[num_train + num_val :]
        if not test_families:
            if len(val_families) > 1:
                test_families = [val_families.pop()]
            elif len(train_families) > 1:
                test_families = [train_families.pop()]

    # 3. Assemble splits
    splits_data = {
        "train": {"families": train_families, "items": []},
        "val": {"families": val_families, "items": []},
        "test": {"families": test_families, "items": []},
    }

    for split_name, fam_list in [("train", train_families), ("val", val_families), ("test", test_families)]:
        for fam in fam_list:
            for fname, doc in product_groups[fam]:
                meta = doc["image_metadata"]
                prov = meta.get("provenance", {})
                review_status = doc.get("review_status", "draft")
                is_synthetic = (
                    "fixture" in fam.lower()
                    or "synthetic" in prov.get("source", "").lower()
                    or "synthetic" in prov.get("notes", "").lower()
                )
                is_eligible = (review_status == "verified_by_human") and not is_synthetic

                splits_data[split_name]["items"].append(
                    {
                        "annotation_file": fname,
                        "image_id": meta["image_id"],
                        "file_name": meta["file_name"],
                        "product_family": fam,
                        "packaging_type": meta["packaging_type"],
                        "entity_count": len(doc.get("entities", [])),
                        "review_status": review_status,
                        "is_synthetic_fixture": is_synthetic,
                        "eligible_for_real_training": is_eligible,
                    }
                )

    # 4. Strict Leakage Verification
    train_fams_set = set(train_families)
    val_fams_set = set(val_families)
    test_fams_set = set(test_families)

    leak_train_val = train_fams_set & val_fams_set
    leak_train_test = train_fams_set & test_fams_set
    leak_val_test = val_fams_set & test_fams_set

    if leak_train_val or leak_train_test or leak_val_test:
        raise RuntimeError("CRITICAL: Product family leakage detected across dataset splits!")

    # 5. Write split manifests
    output_dir.mkdir(parents=True, exist_ok=True)
    manifests = {}
    for split_name in ["train", "val", "test"]:
        manifest_path = output_dir / f"{split_name}.json"
        manifest_payload = {
            "split": split_name,
            "seed": seed,
            "total_images": len(splits_data[split_name]["items"]),
            "product_families": splits_data[split_name]["families"],
            "images": splits_data[split_name]["items"],
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_payload, f, indent=2)
        manifests[split_name] = manifest_payload

    summary = {
        "total_images": len(records),
        "total_product_families": num_families,
        "seed": seed,
        "train_count": len(splits_data["train"]["items"]),
        "train_families": len(train_families),
        "val_count": len(splits_data["val"]["items"]),
        "val_families": len(val_families),
        "test_count": len(splits_data["test"]["items"]),
        "test_families": len(test_families),
        "leakage_detected": False,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description="Create leakage-free medicine label dataset splits.")
    parser.add_argument("--annotations-dir", default="data/annotations", help="Path to annotations folder")
    parser.add_argument("--output-dir", default="data/splits", help="Path to output splits folder")
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train ratio (default 0.70)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation ratio (default 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test ratio (default 0.15)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible split")
    args = parser.parse_args()

    ann_dir = Path(args.annotations_dir)
    out_dir = Path(args.output_dir)

    print(f"Splitting dataset from {ann_dir} -> {out_dir} (seed={args.seed})...")
    res = split_dataset(
        ann_dir,
        out_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
    )

    print("\n--- Dataset Split Summary ---")
    print(f"Total Images: {res['total_images']} across {res['total_product_families']} product families")
    print(f"Train: {res['train_count']} images ({res['train_families']} families)")
    print(f"Val:   {res['val_count']} images ({res['val_families']} families)")
    print(f"Test:  {res['test_count']} images ({res['test_families']} families)")
    print(f"Data Leakage: None (Verified)")
    print(f"Manifests generated at {out_dir}/train.json, val.json, test.json")


if __name__ == "__main__":
    main()
