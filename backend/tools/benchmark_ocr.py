"""Reproducible OCR Benchmark Tool for MedLens medicine packaging dataset (Prompt 4).

Evaluates configured OCR engines (PaddleOCR, Tesseract) against human-verified packaging ground truth.
Computes Character Error Rate (CER), Word Error Rate (WER), latency, and error distributions.
Adheres strictly to the verification-first protocol:
- Only real packaging images with verified human annotations are scored.
- Synthetic illustrations and unreviewed drafts are excluded from ground truth.
- Unavailable engines are explicitly reported; mock results are never silently substituted.
- OCR text metrics are evaluated independently of downstream composition parsing.
- Does not make medical validation claims from OCR scores.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from PIL import Image

# Support importing app modules regardless of current working directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.schemas.dataset import ReviewStatus
from app.services.image_processing.preprocessor import ImagePreprocessor
from app.services.ocr.base import BaseOCREngine
from app.services.ocr.dispatcher import OCRDispatcher
from app.services.ocr.mock_engine import MockOCREngine
from app.services.ocr.paddle_engine import PaddleOCREngine
from app.services.ocr.tesseract_engine import TesseractOCREngine

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Pure-Python Levenshtein Distance & Error Rate Metrics
# ============================================================================

def levenshtein_distance(seq1: Sequence[Any], seq2: Sequence[Any]) -> int:
    """Computes standard Wagner-Fischer edit distance between two sequences."""
    n = len(seq1)
    m = len(seq2)
    if n == 0:
        return m
    if m == 0:
        return n

    # Use two-row memory optimization
    current_row = list(range(m + 1))
    for i, c1 in enumerate(seq1):
        next_row = [i + 1] + [0] * m
        for j, c2 in enumerate(seq2):
            cost = 0 if c1 == c2 else 1
            next_row[j + 1] = min(
                current_row[j + 1] + 1,  # deletion
                next_row[j] + 1,          # insertion
                current_row[j] + cost,    # substitution
            )
        current_row = next_row

    return current_row[m]


def calculate_cer(reference: str, hypothesis: str, normalize: bool = False) -> float:
    """Calculates Character Error Rate (CER).

    CER = Levenshtein(reference_chars, hypothesis_chars) / max(1, len(reference_chars))
    """
    ref = reference
    hyp = hypothesis
    if normalize:
        ref = " ".join(ref.lower().split())
        hyp = " ".join(hyp.lower().split())

    if not ref:
        return 0.0 if not hyp else 1.0

    dist = levenshtein_distance(list(ref), list(hyp))
    return float(dist / len(ref))


def calculate_wer(reference: str, hypothesis: str, normalize: bool = False) -> float:
    """Calculates Word Error Rate (WER).

    WER = Levenshtein(reference_words, hypothesis_words) / max(1, len(reference_words))
    """
    ref = reference
    hyp = hypothesis
    if normalize:
        ref = " ".join(ref.lower().split())
        hyp = " ".join(hyp.lower().split())

    ref_words = ref.split()
    hyp_words = hyp.split()

    if not ref_words:
        return 0.0 if not hyp_words else 1.0

    dist = levenshtein_distance(ref_words, hyp_words)
    return float(dist / len(ref_words))


def compute_text_metrics(reference: str, hypothesis: str) -> Dict[str, Any]:
    """Computes comprehensive OCR transcription fidelity metrics."""
    raw_cer = calculate_cer(reference, hypothesis, normalize=False)
    raw_wer = calculate_wer(reference, hypothesis, normalize=False)
    norm_cer = calculate_cer(reference, hypothesis, normalize=True)
    norm_wer = calculate_wer(reference, hypothesis, normalize=True)

    ref_words = reference.split()
    hyp_words = hypothesis.split()

    return {
        "raw_cer": round(raw_cer, 4),
        "raw_wer": round(raw_wer, 4),
        "normalized_cer": round(norm_cer, 4),
        "normalized_wer": round(norm_wer, 4),
        "exact_match_raw": reference.strip() == hypothesis.strip(),
        "exact_match_normalized": " ".join(ref_words).lower() == " ".join(hyp_words).lower(),
        "reference_char_count": len(reference),
        "hypothesis_char_count": len(hypothesis),
        "reference_word_count": len(ref_words),
        "hypothesis_word_count": len(hyp_words),
    }


# ============================================================================
# Dataset Filtering & Ground Truth Selection
# ============================================================================

def is_eligible_real_packaging_annotation(doc: Dict[str, Any]) -> Tuple[bool, str]:
    """Checks whether annotation meets strict Prompt 4 ground-truth standards."""
    meta = doc.get("image_metadata", {})
    prov = meta.get("provenance", {})

    review_status = doc.get("review_status", "")
    verified_by_human = prov.get("verified_by_human", False)
    notes = str(prov.get("notes") or "").lower()
    source_str = str(prov.get("source") or "").lower()

    # Reject unreviewed drafts
    if review_status != ReviewStatus.VERIFIED_BY_HUMAN.value or not verified_by_human:
        return False, f"Annotation review_status is '{review_status}' (requires verified_by_human)."

    # Reject synthetic fixtures, illustrations, or mockups
    is_synthetic = (
        "3d generic illustration" in notes
        or "synthetic" in notes
        or "do not use as ground truth" in notes
        or "synthetic" in source_str
        or "fixture" in str(meta.get("product_family") or "").lower()
    )
    if is_synthetic:
        return False, "Disqualified: Image is flagged as a synthetic illustration or test fixture."

    # Must contain non-empty transcription
    transcription = doc.get("transcription", "").strip()
    if not transcription:
        return False, "Disqualified: Transcription text is empty."

    return True, "Eligible real packaging ground truth."


def load_benchmark_candidates(
    annotations_dir: Path,
    splits_dir: Optional[Path] = None,
    split_name: str = "test",
) -> List[Tuple[str, Dict[str, Any]]]:
    """Loads and filters annotations designated for held-out evaluation."""
    candidate_records: List[Tuple[str, Dict[str, Any]]] = []

    # If splits_dir provided and manifest exists, read from manifest
    if splits_dir and (splits_dir / f"{split_name}.json").exists():
        manifest_path = splits_dir / f"{split_name}.json"
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        for item in manifest.get("images", []):
            ann_file = item.get("annotation_file")
            full_path = annotations_dir / ann_file
            if full_path.exists():
                with open(full_path, "r", encoding="utf-8") as af:
                    candidate_records.append((ann_file, json.load(af)))
    else:
        # Otherwise read directly from annotations directory
        for jf in sorted(annotations_dir.glob("*.json")):
            with open(jf, "r", encoding="utf-8") as af:
                candidate_records.append((jf.name, json.load(af)))

    # Filter strictly for eligible real packaging ground truth
    eligible_records = []
    for fname, doc in candidate_records:
        eligible, reason = is_eligible_real_packaging_annotation(doc)
        if eligible:
            eligible_records.append((fname, doc))
        else:
            logger.info(f"Skipping '{fname}' from OCR benchmark: {reason}")

    return eligible_records


# ============================================================================
# OCR Execution & Benchmark Engine
# ============================================================================

class OCRBenchmarkResult:
    """Encapsulates outcome for a single (image, engine) benchmark evaluation."""

    def __init__(
        self,
        image_id: str,
        file_name: str,
        product_family: str,
        packaging_type: str,
        engine_name: str,
        engine_version: str,
        engine_status: str,  # "SUCCESS", "ENGINE_UNAVAILABLE", "EXECUTION_ERROR"
        metrics: Optional[Dict[str, Any]] = None,
        raw_ocr_text: str = "",
        ground_truth_text: str = "",
        latency_ms: int = 0,
        preprocessing_applied: bool = False,
        error_message: Optional[str] = None,
    ):
        self.image_id = image_id
        self.file_name = file_name
        self.product_family = product_family
        self.packaging_type = packaging_type
        self.engine_name = engine_name
        self.engine_version = engine_version
        self.engine_status = engine_status
        self.metrics = metrics or {}
        self.raw_ocr_text = raw_ocr_text
        self.ground_truth_text = ground_truth_text
        self.latency_ms = latency_ms
        self.preprocessing_applied = preprocessing_applied
        self.error_message = error_message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "file_name": self.file_name,
            "product_family": self.product_family,
            "packaging_type": self.packaging_type,
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "engine_status": self.engine_status,
            "metrics": self.metrics,
            "raw_ocr_text": self.raw_ocr_text,
            "ground_truth_text": self.ground_truth_text,
            "latency_ms": self.latency_ms,
            "preprocessing_applied": self.preprocessing_applied,
            "error_message": self.error_message,
        }


def run_ocr_benchmark(
    annotations_dir: Path,
    raw_images_dir: Path,
    splits_dir: Optional[Path] = None,
    split_name: str = "test",
    engines: Optional[List[str]] = None,
    apply_preprocessing: bool = True,
    custom_engine_registry: Optional[Dict[str, BaseOCREngine]] = None,
) -> Dict[str, Any]:
    """Runs reproducible OCR benchmark across configured engines and held-out real packaging images."""
    target_engines = engines or ["paddleocr", "tesseract"]
    dispatcher = OCRDispatcher(engines=custom_engine_registry)

    # 1. Load and filter eligible ground-truth images
    eligible_docs = load_benchmark_candidates(
        annotations_dir=annotations_dir,
        splits_dir=splits_dir,
        split_name=split_name,
    )

    preprocessor = ImagePreprocessor() if apply_preprocessing else None

    # Benchmark metadata header
    benchmark_summary: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target_split": split_name,
        "annotations_dir": str(annotations_dir),
        "raw_images_dir": str(raw_images_dir),
        "requested_engines": target_engines,
        "preprocessing_enabled": apply_preprocessing,
        "total_eligible_images": len(eligible_docs),
        "engine_availability": {},
        "per_engine_results": {},
        "status": "COMPLETED",
        "notes": [],
    }

    # 2. Check engine availability explicitly without mock substitution
    for eng_name in target_engines:
        eng_adapter = dispatcher._engines.get(eng_name)
        if not eng_adapter:
            benchmark_summary["engine_availability"][eng_name] = {
                "available": False,
                "version": "unknown",
                "reason": f"No adapter registered for engine '{eng_name}'",
            }
        else:
            is_avail = eng_adapter.is_available()
            ver = eng_adapter.version
            reason = "Ready" if is_avail else f"Engine '{eng_name}' binaries or Python packages missing"
            benchmark_summary["engine_availability"][eng_name] = {
                "available": is_avail,
                "version": ver,
                "reason": reason,
            }

    # 3. Handle early termination cases
    if len(eligible_docs) == 0:
        benchmark_summary["status"] = "NO_VALID_RUN_POSSIBLE"
        msg = (
            "No eligible real packaging images found in target split. "
            "All candidates were either unreviewed drafts or synthetic illustrations. "
            "Authentic packaging photographs must be collected and human-reviewed (ML-018) before OCR evaluation."
        )
        benchmark_summary["notes"].append(msg)
        return benchmark_summary

    any_engine_available = any(
        info["available"] for info in benchmark_summary["engine_availability"].values()
    )
    if not any_engine_available:
        benchmark_summary["status"] = "ENGINES_UNAVAILABLE"
        msg = (
            f"Eligible packaging images are present ({len(eligible_docs)}), but none of the requested OCR "
            f"engines ({', '.join(target_engines)}) are available in the local environment. "
            "Per MedLens policy, mock results are never silently substituted during benchmark evaluation."
        )
        benchmark_summary["notes"].append(msg)
        return benchmark_summary

    # 4. Execute OCR on eligible images
    for eng_name in target_engines:
        avail_info = benchmark_summary["engine_availability"][eng_name]
        if not avail_info["available"]:
            benchmark_summary["per_engine_results"][eng_name] = {
                "status": "ENGINE_UNAVAILABLE",
                "version": avail_info["version"],
                "reason": avail_info["reason"],
                "records": [],
                "aggregate_metrics": {},
            }
            continue

        eng_adapter = dispatcher._engines[eng_name]
        records: List[OCRBenchmarkResult] = []

        for fname, doc in eligible_docs:
            meta = doc["image_metadata"]
            image_id = meta["image_id"]
            file_name = meta["file_name"]
            product_family = meta["product_family"]
            packaging_type = meta["packaging_type"]
            ground_truth = doc.get("transcription", "").strip()

            raw_path = raw_images_dir / file_name
            if not raw_path.exists():
                logger.error(f"Image file {file_name} missing from {raw_images_dir}")
                records.append(
                    OCRBenchmarkResult(
                        image_id=image_id,
                        file_name=file_name,
                        product_family=product_family,
                        packaging_type=packaging_type,
                        engine_name=eng_name,
                        engine_version=eng_adapter.version,
                        engine_status="EXECUTION_ERROR",
                        error_message=f"Image file {file_name} missing from raw_images_dir",
                        ground_truth_text=ground_truth,
                    )
                )
                continue

            try:
                img_bytes = raw_path.read_bytes()
                t0 = time.perf_counter()

                # Optional OpenCV/Pillow Preprocessing
                if preprocessor:
                    if hasattr(preprocessor, "process"):
                        preprocessed = preprocessor.process(img_bytes)
                    else:
                        preprocessed = preprocessor.preprocess(img_bytes)
                    ocr_res = eng_adapter.extract_text(
                        image_bytes=preprocessed.processed_bytes,
                        pil_image=preprocessed.pil_image,
                        np_array=preprocessed.np_array,
                    )
                else:
                    ocr_res = eng_adapter.extract_text(image_bytes=img_bytes)

                latency_ms = int((time.perf_counter() - t0) * 1000)
                pred_text = ocr_res.full_text.strip()
                metrics = compute_text_metrics(reference=ground_truth, hypothesis=pred_text)

                records.append(
                    OCRBenchmarkResult(
                        image_id=image_id,
                        file_name=file_name,
                        product_family=product_family,
                        packaging_type=packaging_type,
                        engine_name=eng_name,
                        engine_version=eng_adapter.version,
                        engine_status="SUCCESS",
                        metrics=metrics,
                        raw_ocr_text=pred_text,
                        ground_truth_text=ground_truth,
                        latency_ms=latency_ms,
                        preprocessing_applied=apply_preprocessing,
                    )
                )
            except Exception as e:
                logger.exception(f"Engine {eng_name} failed on {image_id}: {e}")
                records.append(
                    OCRBenchmarkResult(
                        image_id=image_id,
                        file_name=file_name,
                        product_family=product_family,
                        packaging_type=packaging_type,
                        engine_name=eng_name,
                        engine_version=eng_adapter.version,
                        engine_status="EXECUTION_ERROR",
                        error_message=str(e),
                        ground_truth_text=ground_truth,
                    )
                )

        # 5. Compute aggregate statistics for this engine
        successful = [r for r in records if r.engine_status == "SUCCESS"]
        if successful:
            raw_cers = [r.metrics["raw_cer"] for r in successful]
            raw_wers = [r.metrics["raw_wer"] for r in successful]
            norm_cers = [r.metrics["normalized_cer"] for r in successful]
            norm_wers = [r.metrics["normalized_wer"] for r in successful]
            latencies = [r.latency_ms for r in successful]

            agg = {
                "images_evaluated": len(successful),
                "exact_matches_raw": sum(1 for r in successful if r.metrics["exact_match_raw"]),
                "exact_matches_normalized": sum(1 for r in successful if r.metrics["exact_match_normalized"]),
                "mean_raw_cer": round(sum(raw_cers) / len(raw_cers), 4),
                "mean_raw_wer": round(sum(raw_wers) / len(raw_wers), 4),
                "mean_normalized_cer": round(sum(norm_cers) / len(norm_cers), 4),
                "mean_normalized_wer": round(sum(norm_wers) / len(norm_wers), 4),
                "mean_latency_ms": int(sum(latencies) / len(latencies)),
            }
        else:
            agg = {"images_evaluated": 0}

        benchmark_summary["per_engine_results"][eng_name] = {
            "status": "COMPLETED",
            "version": eng_adapter.version,
            "aggregate_metrics": agg,
            "records": [r.to_dict() for r in records],
        }

    return benchmark_summary


# ============================================================================
# Markdown Report Generation
# ============================================================================

def render_markdown_ocr_benchmark(summary: Dict[str, Any]) -> str:
    """Renders clean GitHub-flavored Markdown benchmark report."""
    status = summary.get("status", "UNKNOWN")
    lines = [
        "# 🔬 MedLens Pretrained OCR Benchmark Report (Prompt 4)",
        "",
        f"> **Generated:** {summary.get('timestamp')}  ",
        f"> **Target Split:** `{summary.get('target_split')}`  ",
        f"> **Benchmark Status:** `{status}`  ",
        "> **Ground Truth Policy:** Only human-verified authentic physical packaging photographs evaluated.",
        "",
        "---",
        "",
        "## 1. Engine Availability & Execution Diagnostics",
        "",
        "| Engine Name | Status | Installed Version | Diagnostic Reason |",
        "| :--- | :---: | :---: | :--- |",
    ]

    for eng, info in summary.get("engine_availability", {}).items():
        avail = "READY" if info["available"] else "UNAVAILABLE"
        lines.append(f"| `{eng}` | `{avail}` | `{info['version']}` | {info['reason']} |")

    lines.extend([
        "",
        "---",
        "",
        "## 2. Benchmark Findings & Evaluation Outcomes",
        "",
    ])

    if status == "NO_VALID_RUN_POSSIBLE":
        lines.append(
            "> [!WARNING]\n"
            "> **No Valid Benchmark Run Was Possible:**\n"
            "> Zero human-verified real packaging images are currently present in the target split. "
            "All candidate records were either synthetic fixtures or unreviewed drafts. "
            "Per the verification protocol, mock illustrations cannot be used as ground truth.\n"
        )
    elif status == "ENGINES_UNAVAILABLE":
        lines.append(
            "> [!IMPORTANT]\n"
            "> **Engines Unavailable in Environment:**\n"
            f"> Human-verified real packaging images exist (`{summary.get('total_eligible_images')}` eligible), "
            "but requested OCR engines (`tesseract`, `paddleocr`) are not installed on this host. "
            "Per MedLens integrity standards, mock results are never silently substituted into benchmark scores.\n"
        )
    else:
        # Report results per engine
        for eng, res in summary.get("per_engine_results", {}).items():
            lines.append(f"### Engine: `{eng}` ({res.get('version')})")
            lines.append("")
            agg = res.get("aggregate_metrics", {})
            if not agg or agg.get("images_evaluated", 0) == 0:
                lines.append(f"- Status: `{res.get('status')}` ({res.get('reason', 'No images scored')})")
            else:
                lines.extend([
                    f"- **Images Evaluated:** `{agg['images_evaluated']}`",
                    f"- **Mean Normalized CER:** `{agg['mean_normalized_cer'] * 100:.2f}%`",
                    f"- **Mean Normalized WER:** `{agg['mean_normalized_wer'] * 100:.2f}%`",
                    f"- **Exact Match Count:** `{agg['exact_matches_normalized']}` / `{agg['images_evaluated']}`",
                    f"- **Mean Latency:** `{agg['mean_latency_ms']} ms`",
                    "",
                    "#### Detailed Error Samples",
                    "",
                    "| Image ID | Ground Truth Text | OCR Output | CER | WER |",
                    "| :--- | :--- | :--- | :---: | :---: |",
                ])

                for rec in res.get("records", [])[:5]:
                    if rec["engine_status"] == "SUCCESS":
                        gt_snippet = rec["ground_truth_text"].replace("\n", " ")[:40]
                        ocr_snippet = rec["raw_ocr_text"].replace("\n", " ")[:40]
                        cer = rec["metrics"]["normalized_cer"]
                        wer = rec["metrics"]["normalized_wer"]
                        lines.append(
                            f"| `{rec['image_id']}` | `{gt_snippet}` | `{ocr_snippet}` | `{cer:.2f}` | `{wer:.2f}` |"
                        )
            lines.append("")

    lines.extend([
        "---",
        "",
        "## 3. Methodological Disclaimers",
        "",
        "1. **No Medical Validation Claim:** OCR Character Error Rate and Word Error Rate measure visual character recognition fidelity. They do not claim clinical accuracy or medical safety.",
        "2. **Decoupled from Composition Parser:** OCR text transcription is evaluated strictly against verbatim text, independent of regex token extraction or INN normalization success.",
        "3. **Zero Synthetic Ground Truth:** Test fixtures and 3D graphics are explicitly segregated from real packaging evaluations.",
    ])

    return "\n".join(lines)


# ============================================================================
# CLI Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Benchmark pretrained OCR engines against MedLens ground truth.")
    parser.add_argument("--annotations-dir", default="backend/data/annotations", help="Annotations directory")
    parser.add_argument("--raw-dir", default="backend/data/raw", help="Raw images directory")
    parser.add_argument("--splits-dir", default="backend/data/splits", help="Splits directory")
    parser.add_argument("--split", default="test", help="Target split: 'test', 'val', or 'all_verified'")
    parser.add_argument("--engines", nargs="+", default=["paddleocr", "tesseract"], help="Engines to benchmark")
    parser.add_argument("--skip-preprocessing", action="store_true", help="Disable OpenCV image preprocessing")
    parser.add_argument("--output-json", default=None, help="Path to write JSON benchmark summary")
    parser.add_argument("--output-md", default=None, help="Path to write Markdown benchmark report")
    args = parser.parse_args()

    ann_dir = Path(args.annotations_dir)
    raw_dir = Path(args.raw_dir)
    splits_dir = Path(args.splits_dir) if args.splits_dir else None

    print(f"Beginning OCR Benchmark on split '{args.split}'...")
    summary = run_ocr_benchmark(
        annotations_dir=ann_dir,
        raw_images_dir=raw_dir,
        splits_dir=splits_dir,
        split_name=args.split,
        engines=args.engines,
        apply_preprocessing=not args.skip_preprocessing,
    )

    print(f"\n--- Benchmark Summary ---")
    print(f"Status: {summary['status']}")
    print(f"Eligible images found: {summary['total_eligible_images']}")
    for eng, info in summary["engine_availability"].items():
        print(f"Engine '{eng}': available={info['available']} ({info['version']})")

    if args.output_json:
        out_json = Path(args.output_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"Saved benchmark JSON to {out_json}")

    md_report = render_markdown_ocr_benchmark(summary)
    if args.output_md:
        out_md = Path(args.output_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"Saved benchmark Markdown to {out_md}")
    else:
        print("\n" + md_report)


if __name__ == "__main__":
    main()

