# 📦 MedLens Medicine Packaging Dataset Creation & Annotation Guidelines

> **Master Specification Reference:** MedLens Capstone Implementation Blueprint (Section 06 & Section 07)  
> **Target Lifecycle:** Phase 3 Dataset Engineering & Preparation for Phase 4 Sequence Labeling

---

## 1. Objective & Non-Negotiable Rules

The goal of the MedLens dataset pipeline is to construct a **high-fidelity, verifiable ground-truth corpus** of medicine packaging typography, chemical compositions, and dosage strengths.

### ⚠️ Binding Principles
1. **Never Invent Annotations:** Every labeled token must match verbatim text physically printed on the package. Never impute missing strengths or guess abbreviations.
2. **Never Treat Unverified ML Predictions as Ground Truth:** Models cannot train on hallucinated or auto-accepted synthetic labels. All ground truth must be verified by a human curator.
3. **Appropriate Usage Permissions Only:** Collect imagery exclusively from open clinical reference repositories (e.g., NIH DailyMed, openFDA) or physical packages photographed with research/academic consent.
4. **Zero-Leakage Product Partitioning:** Multiple photographs of the same medicine brand (*e.g., Dolo 650 blister foil front vs back, or different lighting conditions*) must remain strictly inside the **same split**. They must **never** leak between Training, Validation, and Test partitions.
5. **Preserve Salt Forms:** Chemical salts (*e.g., Hydrochloride, Potassium, Trihydrate, IP*) must be labeled distinctly from base active moieties (*e.g., Cetirizine, Amoxicillin*).

---

## 2. Directory Architecture

All dataset assets reside under `backend/data/`:

```
backend/data/
├── raw/                      # Genuine, high-resolution medicine packaging images (lossless PNG/JPG)
├── annotations/              # Ground truth JSON annotations (<image_id>.json)
├── processed/                # Preprocessed images (standardized DPI, EXIF stripped)
├── splits/                   # Product-partitioned dataset manifests
│   ├── train.json            # Training manifest (~70%)
│   ├── val.json              # Validation manifest (~15%)
│   └── test.json             # Held-out benchmark test manifest (~15%, frozen)
├── templates/                # Standard schema template
│   └── annotation_template.json
└── reports/                  # Automated quality and distribution audits
    ├── dataset_quality_report.md
    └── dataset_stats.json
```

---

## 3. Annotation Schema & Token Labels

Each medicine image corresponds to an individual `<image_id>.json` conforming to `PackagingAnnotationDoc` schema in [`app.schemas.dataset`](file:///C:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/app/schemas/dataset.py).

### Entity Label Definitions

| Label | Definition | Ground Truth Examples | Critical Decision Boundary |
| :--- | :--- | :--- | :--- |
| `BRAND` | Commercial trade name | `Dolo 650`, `Augmentin 625 Duo`, `Calpol 500` | Only mark commercial trademarked branding. |
| `PRODUCT_NAME` | Generic title if no trade brand exists | `Cetirizine 10 mg`, `Paracetamol Tablets` | Use when generic presentation lacks a distinct trade brand. |
| `INGREDIENT` | Active pharmaceutical moiety | `Paracetamol`, `Amoxicillin`, `Ibuprofen` | Do **not** include salt words here. |
| `SALT_FORM` | Chemical salt or pharmacopeial notation | `Hydrochloride`, `Trihydrate`, `IP`, `BP`, `USP` | Preserve exact printed salt notation. |
| `STRENGTH` | Numeric magnitude + unit | `650 mg`, `500 mg`, `10 mg`, `125 mg` | Must include valid unit (`mg`, `mcg`, `g`, `ml`, `% w/v`). |
| `CONCENTRATION` | Mass-per-volume dosage strength | `125 mg / 5 mL`, `0.5% w/v` | Multi-token formulation expression. |
| `STRENGTH_BASIS` | Physical administration basis | `per tablet`, `per capsule`, `per 5 mL` | Extract administration unit. |
| `DOSAGE_FORM` | Physical pharmaceutical presentation | `tablet`, `capsule`, `syrup`, `injection` | Must reflect dosage formulation. |
| `ROUTE` | Stated administration route | `For Oral Use`, `Topical` | Only label when explicitly printed. |
| `RELEASE_TYPE` | Modified-release modifier | `Immediate Release`, `SR`, `CR`, `ER` | Only label when text explicitly states release kinetics. |
| `COMPOSITION_HEADER` | Section start context | `Each tablet contains:`, `Composition:` | Bounding line anchoring active ingredients. |

### Coordinate Convention
All bounding boxes (`bbox`) must use integer coordinates normalized to $[0, 1000]$:
$$\text{bbox} = [y_{\min}, x_{\min}, y_{\max}, x_{\max}]$$
where $0 \le y_{\min} < y_{\max} \le 1000$ and $0 \le x_{\min} < x_{\max} \le 1000$.

---

## 4. Step-by-Step Annotation Workflow

### Step 1: Image Collection & Intake
1. Photograph packaging under diffuse lighting (avoid extreme glare or oblique angles).
2. Save raw uncompressed image into `backend/data/raw/<product_name>.<ext>`.
3. Ensure no personal health information (PHI), pharmacy customer stickers, or private patient details are visible.

### Step 2: Initialize Annotation Document
Run the CLI annotation tool:
```bash
python -m tools.annotate init \
  --image data/raw/dolo_650_blister.jpg \
  --product-family dolo-650 \
  --brand "Dolo 650" \
  --packaging-type blister_foil \
  --annotator "curator-01"
```
This automatically computes the file's SHA-256 digest, reads pixel dimensions, and generates `data/annotations/img-dolo_650_blister.json`.

### Step 3: Transcribe and Annotate Entities
Open `data/annotations/<image_id>.json` in your editor or use `tools/annotate.py add-entity`:
```bash
python -m tools.annotate add-entity \
  --file data/annotations/img-dolo_650_blister.json \
  --label INGREDIENT \
  --text "Paracetamol" \
  --bbox 370 50 460 420
```

### Step 4: Validate Dataset Integrity
Run the automated validation suite:
```bash
python -m tools.validate_dataset --annotations-dir data/annotations --raw-dir data/raw
```
The validator automatically verifies:
- JSON schema syntax.
- Bounding box limits ($0 \le \text{coord} \le 1000$).
- SHA-256 digest matches raw physical file.
- No duplicate image hashes exist.
- Units conform to recognized medical standards (`mg`, `mcg`, `g`, etc.).

### Step 5: Generate Leakage-Free Splits
Run the partition generator:
```bash
python -m tools.split_dataset \
  --annotations-dir data/annotations \
  --output-dir data/splits \
  --train-ratio 0.70 \
  --val-ratio 0.15 \
  --test-ratio 0.15 \
  --seed 42
```

### Step 6: Audit Quality and Generate Statistics
Generate the Markdown and JSON reports:
```bash
python -m tools.generate_dataset_report \
  --annotations-dir data/annotations \
  --splits-dir data/splits \
  --reports-dir data/reports
```

---

## 5. Human Annotation vs. Automated Pipeline Division

| Stage | Responsibility | Automation Level |
| :--- | :--- | :--- |
| **Image Ingestion** | Collecting permissible blister packs | Human collection |
| **Metadata & Hash Calculation** | File dimensions, SHA-256 fingerprinting | **100% Automated** (`annotate.py init`) |
| **Full Transcription** | Verbatim packaging text reading | Human medical annotator |
| **Entity Token Spanning** | Label tagging & bounding box delineation | Human annotator + Canvas tool |
| **Schema & Unit Validation** | Typo catching, unit check, range verification | **100% Automated** (`validate_dataset.py`) |
| **Duplicate Prevention** | Cryptographic hash collision check | **100% Automated** (`validate_dataset.py`) |
| **Product Stratification** | Zero-leakage grouping by medicine family | **100% Automated** (`split_dataset.py`) |
| **Quality Reporting** | Class balance & visual degradation statistics | **100% Automated** (`generate_dataset_report.py`) |
| **Final Clinical Sign-Off** | Verifying clinical accuracy before Phase 4 | Human clinical lead sign-off |
