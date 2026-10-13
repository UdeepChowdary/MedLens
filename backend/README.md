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
