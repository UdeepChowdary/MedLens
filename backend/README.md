# 🔬 MedLens Backend

FastAPI-powered verification-first medicine composition and analysis engine.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.11+
- Virtual environment (recommended)

### 2. Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional)
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env   # Windows
# cp .env.example .env   # Linux / macOS

# Initialize and seed curated clinical database (idempotent)
python -m app.database.seed
```

### 3. Run Automated Tests
```bash
python -m pytest tests/
# Output: 31 passed in ~1s
```

### 4. Start Local Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

- API Base: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/api/v1/openapi.json`

---

## 🔍 Pretrained OCR Engine Setup & Benchmark (ML-026, ML-027)

MedLens uses a real deep-learning pretrained OCR pipeline with **Baidu PaddleOCR** (DBNet detection + SVTR/CRNN recognition) as primary engine, and **Google Tesseract-OCR** as an optional local fallback.

> [!IMPORTANT]
> **Zero Silent Mock Fallback Policy**: Real user packaging uploads and benchmark runs never silently substitute mock OCR data. If real OCR dependencies are not installed in the environment, the API returns `HTTP 503 Service Unavailable (ERR_OCR_ENGINE_UNAVAILABLE)` with actionable remediation hints. Mock OCR is strictly reserved for unit tests or explicitly marked demo fixtures (`X-OCR-Engine: mock` or `ocr_engine="mock"`).

### 1. Installation & OS Prerequisites

#### Python Packages
```bash
# Core CPU deep-learning OCR runtime
pip install "paddlepaddle>=3.0.0" "paddleocr>=3.7.0"

# Optional fallback engine wrapper
pip install "pytesseract>=0.3.13"
```

#### OS-Specific Binary Prerequisites

- **Windows**:
  - PaddlePaddle CPU requires the standard Microsoft Visual C++ 2015-2022 Redistributable (x64).
  - For Tesseract fallback, install UB-Mannheim Tesseract:
    ```powershell
    winget install UB-Mannheim.TesseractOCR
    # Add C:\Program Files\Tesseract-OCR to your PATH environment variable
    ```
- **Linux (Debian / Ubuntu)**:
  - System OpenMP runtime and Tesseract binaries:
    ```bash
    sudo apt-get update && sudo apt-get install -y libgomp1 tesseract-ocr
    ```
- **macOS**:
  - Homebrew Tesseract:
    ```bash
    brew install tesseract
    ```

### 2. First-Run Pretrained Model Weight Download & CPU Execution Flags

Model initialization is strictly **lazy**: importing FastAPI does not download model weights or contact external networks. On the **first live inference request**, PaddleOCR / PaddleX automatically downloads and verifies pretrained detection (`PP-OCRv6_medium_det` / `PP-OCRv4_det`) and recognition (`PP-OCRv6_medium_rec` / `PP-OCRv4_rec`) model weights into `~/.paddlex/` or `~/.paddleocr/` (~15–30 MB). Ensure outbound HTTPS access is available during first inference, or pre-populate the directory in air-gapped environments.

**PaddlePaddle 3.3.1 CPU Compatibility:**
When executing inference on CPU with PaddlePaddle 3.3.1, oneDNN (MKLDNN) with PIR (Program Intermediate Representation) can trigger an unimplemented static instruction error (`ConvertPirAttribute2RuntimeAttribute`). The `PaddleOCREngine` adapter automatically sets `PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT=0` and `FLAGS_use_mkldnn=0` to ensure stable CPU execution across Windows, Linux, and macOS. On Windows, if PyTorch is installed alongside PaddlePaddle, PyTorch DLLs are preloaded to prevent `shm.dll` loading collisions.

### 3. Running the OCR Benchmark Tool

MedLens provides an automated OCR benchmarking tool (`tools/benchmark_ocr.py`) to evaluate Character Error Rate (CER), Word Error Rate (WER), latency, and error distributions on human-verified packaging annotations:

```bash
# Run benchmark on test split with primary PaddleOCR engine
python tools/benchmark_ocr.py --annotations data/annotations --raw data/raw --split test --engine paddleocr

# Run benchmark evaluating both PaddleOCR and Tesseract fallback
python tools/benchmark_ocr.py --annotations data/annotations --raw data/raw --split test --engine paddleocr tesseract

# Run in mock demo mode for testing pipeline scaffolding
python tools/benchmark_ocr.py --annotations data/annotations --raw data/raw --split test --allow-mock
```

> [!NOTE]
> Pretrained OCR enables optical transcription of packaging text out-of-the-box without fine-tuning, but does not prove clinical or domain accuracy on Indian medicine packaging. Accurate evaluation requires human-verified physical packaging photographs and transcriptions.

---

## 📂 Architecture Overview

```
backend/
├── app/
│   ├── api/v1/                  # Versioned API routes
│   │   ├── endpoints/
│   │   │   ├── health.py        # GET /api/v1/health
│   │   │   ├── analyses.py      # POST /api/v1/analyses, GET /api/v1/analyses/{id}
│   │   │   ├── products.py      # GET /api/v1/products/search, GET /api/v1/products/{id}
│   │   │   └── comparisons.py   # POST /api/v1/comparisons
│   │   └── api.py               # Main v1 router aggregation
│   ├── core/                    # Application foundation
│   │   ├── config.py            # Pydantic Settings & environment variables
│   │   ├── errors.py            # Standardized exception hierarchy & ErrorResponse
│   │   └── logging.py           # Structured logging setup
│   ├── database/                # Database configuration & seeding
│   │   ├── session.py           # Async engine (PostgreSQL + SQLite fallback) & get_db
│   │   └── seed.py              # Idempotent clinical baseline seeder
│   ├── models/                  # SQLAlchemy 2.0 ORM domain entities
│   │   ├── product.py           # Product, Ingredient, ProductIngredient, IngredientAlias
│   │   ├── clinical.py          # Source, ClinicalInformation, DrugInteraction
│   │   └── analysis.py          # Analysis, ExtractedEntityModel, AnalysisSource, ModelVersion
│   ├── repositories/            # Data access & query abstraction
│   │   ├── product_repository.py      # Product search, catalog lookup & monograph retrieval
│   │   ├── ingredient_repository.py   # INN normalization & alias resolution
│   │   ├── interaction_repository.py  # Pairwise drug-drug interaction evaluation
│   │   └── analysis_repository.py     # Ephemeral audit records & token batch persistence
│   ├── schemas/                 # Pydantic v2 data contracts
│   │   ├── dataset.py           # PackagingAnnotationDoc, ImageMetadata, EntityAnnotation
│   │   ├── common.py            # VerificationState, ComparisonOutcome, RoleType
│   │   ├── entity.py            # ExtractedEntity & EntityType labels
│   │   ├── product.py           # StrengthSchema, IngredientReport, SafetyProfile
│   │   ├── analysis.py          # MultidimensionalConfidence, AnalysisResponse
│   │   ├── comparison.py        # StrengthDelta, ComparisonResponse
│   │   └── interaction.py       # InteractionRecord, InteractionCheckResponse
│   └── main.py                  # FastAPI application entry point & CORS
├── data/                        # Medicine packaging ground truth dataset
│   ├── raw/                     # Genuine uncompressed packaging photographs
│   ├── annotations/             # JSON ground-truth annotation documents (<id>.json)
│   ├── splits/                  # Leakage-free train.json, val.json, test.json
│   ├── templates/               # Standard annotation schema templates
│   └── reports/                 # Automated quality audit reports & distribution stats
├── tools/                       # Dataset engineering & curation CLI utilities
│   ├── validate_dataset.py      # Schema, bbox, duplicate-hash & unit validator
│   ├── split_dataset.py         # Zero-leakage product-family partitioner
│   ├── generate_dataset_report.py # Automated markdown & JSON quality report generator
│   └── annotate.py              # Metadata auto-calculator & entity annotation CLI
├── migrations/                  # Alembic database migration scripts
│   ├── versions/
│   │   └── 001_initial_relational_schema.py
│   └── env.py                   # Async Alembic execution environment
├── tests/                       # Pytest test suite (31 tests)
│   ├── conftest.py              # TestClient & database session fixtures
│   ├── test_health.py           # Health probe and openapi tests
│   ├── test_schemas.py          # Schema validation tests
│   ├── test_errors.py           # Domain exception tests
│   ├── test_database.py         # Schema, cascade, seeder & repository unit tests
│   ├── test_products_api.py     # Database-backed search and comparison API tests
│   └── test_dataset_pipeline.py # Dataset schema, leakage-free split & validation tests
├── alembic.ini                  # Alembic migration configuration
├── pyproject.toml               # Pytest configuration
├── requirements.txt             # Pinned dependencies
└── .env.example                 # Environment configuration template
```
