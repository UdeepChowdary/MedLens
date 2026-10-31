# 📦 MedLens Medicine Packaging Dataset & Pilot Annotation Workflow

This directory contains the ground-truth packaging datasets, annotation schemas, validation tools, and split manifests for the **MedLens** medicine verification platform.

---

## 1. Directory Structure

```text
backend/data/
├── raw/               # Authentic, high-resolution physical medicine packaging photos
├── annotations/       # Ground-truth JSON annotation files (PackagingAnnotationDoc schema)
├── splits/            # Group-aware train/val/test split manifests with 0% family leakage
├── reports/           # Dataset quality reports, human review queues, and audit logs
├── templates/         # Reference JSON annotation template (annotation_template.json)
└── external/          # (Ignored) Scraped or external auxiliary datasets (e.g. Parquet)
```

---

## 2. Packaging Photo Collection Protocol

To evaluate OCR and extraction models reliably against real-world clinical conditions, **only authentic physical medicine packaging photographs** are permitted.

### Collection Rules & Ethics
1. **Physical Packaging Only:** Photograph real medicine strips, blister foils, paper boxes, or syrup bottles (e.g., from personal supplies or clinical storage). Prioritize the **back side / composition panel**, where active pharmaceutical ingredients, strengths, and excipients are printed.
2. **No Automated Web Scraping:** Do not scrape, harvest, or download e-commerce product thumbnails. Scraped CDN images are low-resolution, lack packaging typography, and cannot be used as ground-truth for OCR benchmarking.
3. **Privacy & Patient Confidentiality (No PII):** Never photograph or commit packaging that contains patient names, doctor prescriptions, pharmacy dispensation labels, batch tracking with personal identifiers, or private personal data.
4. **Ground-Truth Rejection Policy (No Synthetic Illustrations):** 
   - 3D generic renders, mockups, flat graphic illustrations, and unreadable promotional web art **cannot be counted as real packaging ground truth**.
   - Example: In this repository, [`data/annotations/img-dolo-650-blister.json`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/data/annotations/img-dolo-650-blister.json) is explicitly flagged:
     > *"Source image is a 3D generic illustration lacking readable Dolo 650 packaging typography. Pending authentic physical packaging photograph. Do NOT use as ground truth for model training."*
   - Any synthetic or promotional illustration must remain in `flagged_for_review` and is strictly excluded from evaluation splits (`val.json`, `test.json`).

---

## 3. Annotation Schema (`PackagingAnnotationDoc`)

Every image in `data/raw/` must have a corresponding `<image_id>.json` document in `data/annotations/`.

### Required Metadata Fields
- **`image_id`**: Deterministic unique identifier (e.g. `img-dolo-650-strip`).
- **`file_name`**: Image filename in `data/raw/` (e.g. `dolo_650_strip.jpg`).
- **`sha256`**: Exact 64-character SHA-256 cryptographic hash of the image file.
- **`packaging_type`**: Physical format (`blister_foil`, `strip_pack`, `paper_box`, `bottle_label`, `tube`, `sachet`, `vial`).
- **`image_side`**: Aspect photographed (`back`, `front`, `side`, `carton_flap`, `unspecified`).
- **`product_family`**: Grouping key for leakage-free splitting (e.g. `dolo-650`, `augmentin-625`).
- **`provenance`**:
  - `source`: e.g. `"MedLens Clinical Pilot Collection"`, `"DailyMed"`.
  - `license`: Usage terms (e.g. `"CC-BY-4.0"`).
  - `annotator_id`: Unique identifier of human curator (e.g. `"clinical-curator-01"`).
  - `verified_by_human`: Boolean (`true` or `false`).
  - `date_annotated`: ISO-8601 timestamp.
  - `notes`: Observations, visual challenges, or edge cases.
- **`transcription`**: Complete verbatim transcript of all readable text in reading order.
- **`composition_text`**: Verbatim visible composition statement (e.g. `"Each tablet contains: Paracetamol IP 650 mg"`).
- **`entities`**: List of labeled entity spans (`BRAND`, `INGREDIENT`, `STRENGTH`, `DOSAGE_FORM`, etc.).
  - **`char_span`**: 2-tuple `[start, end]` within `transcription`. Must satisfy `transcription[start:end] == raw_text`.
  - **`bbox`**: Normalized bounding box `[ymin, xmin, ymax, xmax]` in range `0..1000`.
- **`has_uncertainty`**: Boolean indicating whether annotator encountered ambiguous or degraded characters.
- **`uncertainty_notes`**: Explanation of ambiguous tokens if uncertainty exists.
- **`review_status`**: Human verification state (`draft`, `verified_by_human`, `flagged_for_review`).

---

## 4. Step-by-Step Workflow

### Step 1: Add a Photo
1. Place the photo in `data/raw/` (e.g., `data/raw/paracetamol_650_strip.jpg`).
2. Initialize an annotation draft using the CLI:
   ```bash
   python backend/tools/annotate.py init \
       --image data/raw/paracetamol_650_strip.jpg \
       --product-family paracetamol-650 \
       --packaging-type blister_foil \
       --brand-name "Dolo 650"
   ```

### Step 2: Annotate Verbatim Text & Entities
1. Open the generated JSON in `data/annotations/`.
2. Transcribe verbatim visible text into `transcription`.
3. Add labeled entities with bounding boxes and exact character spans `[start, end]`.
4. If characters are worn off or obscured, set `has_uncertainty: true` and detail the ambiguity in `uncertainty_notes`.

### Step 3: Human Review Queue Inspection
Before promoting an annotation to ground truth, run the review queue tool:
```bash
python backend/tools/review_queue.py --annotations-dir backend/data/annotations --output-md backend/data/reports/human_review_queue.md
```
- **Rules of Review:**
  - Automated or model-generated annotations **must never be automatically marked as verified**.
  - A human reviewer must independently inspect the physical packaging photo, check that character spans match slices, and verify clinical entity boundaries.
  - Change `review_status` to `"verified_by_human"` and set `provenance.verified_by_human: true` only after full review.

### Step 4: Validate Dataset Integrity
Run the dataset validator to check schema adherence, SHA-256 image linkage, unit validity, and character span accuracy:
```bash
python backend/tools/validate_dataset.py \
    --annotations-dir backend/data/annotations \
    --raw-dir backend/data/raw \
    --splits-dir backend/data/splits
```

### Step 5: Group-Aware Dataset Splitting (Zero Leakage)
Create or update train, validation, and test splits grouped strictly by `product_family`:
```bash
python backend/tools/split_dataset.py \
    --annotations-dir backend/data/annotations \
    --output-dir backend/data/splits \
    --train-ratio 0.70 --val-ratio 0.15 --test-ratio 0.15
```
- **Leakage Prevention:** All packages from the same product family (e.g. different photos of Dolo 650) are assigned to the same partition. No family ever appears across multiple splits.
- **Evaluation Eligibility:** The evaluation splits (`val.json` and `test.json`) strictly require `verified_by_human == true` and exclude synthetic fixtures.

---

## 5. Pilot Dataset Scope Disclaimer

> [!IMPORTANT]
> **Scope & Generalizability Disclaimer:**  
> A 15–20 image pilot collection provides a rigorously annotated benchmark for verifying OCR character error rates, parser coverage, and pipeline reproducibility.  
> It **does not** represent all commercial medicine packaging varieties, nor does it support robust deep learning model training across rare dosage formulations.  
> Claims of platform performance must distinguish between **benchmark test set validation** on this pilot and **large-scale population-level clinical accuracy**.

