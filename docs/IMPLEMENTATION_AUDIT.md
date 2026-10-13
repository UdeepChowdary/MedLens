# MedLens Implementation Audit & Reality Report

**Document Date:** October 13, 2026  
**Audited Against:** `MedLens_Capstone_Implementation_Blueprint.md` (Version 1.0)  
**Status:** Task 0 Complete — Pre-Implementation Baseline  

---

## 1. Executive Summary

This audit assesses the current state of the MedLens repository against the target requirements defined in the **MedLens Capstone Implementation Blueprint**. 

### Key Findings
- **Frontend Layer:** Implemented with Next.js 16.3.6 (App Router), React 19, TypeScript, and Tailwind CSS v4. Complete UI views exist for landing, camera/upload scanner, analysis report, brand comparison, scan history, and user profile. However, all results, processing steps, and comparisons are currently driven by static mock data (`demo-scan`, Dolo 650, Calpol 500) and simulated timers.
- **Backend Layer:** Not yet implemented. No FastAPI service, Dockerfile, or backend directory exists in the workspace.
- **Database Layer:** Not yet implemented. No PostgreSQL database, Alembic migrations, or relational tables exist.
- **Machine Learning & OCR:** Not yet implemented. No local OCR engine (PaddleOCR/Tesseract) or token classification extraction models exist.
- **Data Adapters:** Not yet implemented. No integration with RxNorm, openFDA, DailyMed, or PubChem exists.

---

## 2. Directory Structure & Key Dependencies

### 2.1 Current Workspace Layout
```
MedLens/
├── frontend/                                   # Active Next.js 16 Application
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── compare/page.tsx                # Brand comparison view (Mock data)
│   │   │   ├── history/page.tsx                # Scan history view (Mock data)
│   │   │   ├── profile/page.tsx                # User profile & allergy tags
│   │   │   ├── results/[id]/page.tsx           # Analysis report view (Mock Dolo 650)
│   │   │   ├── scan/page.tsx                   # Image intake (Dropzone + LiveCamera)
│   │   │   ├── layout.tsx                      # Dashboard sidebar layout
│   │   │   └── page.tsx                        # Dashboard overview & analytics chart
│   │   ├── login/page.tsx                      # Mock authentication form
│   │   ├── privacy/page.tsx                    # Privacy policy
│   │   ├── terms/page.tsx                      # Terms of service
│   │   ├── globals.css                         # Clinical theme variables & scrollbars
│   │   ├── layout.tsx                          # Root layout & font loading
│   │   └── page.tsx                            # Landing page
│   ├── components/
│   │   ├── report/                             # ProductOverview, IngredientCard, SafetyModule, ExcipientCollapse
│   │   ├── scanner/                            # LiveCamera (WebRTC), UploadZone, ProcessingPulse
│   │   ├── ui/                                 # Badge, MonospaceValue
│   │   └── [Landing Components]                # Hero, Problem, HowItWorks, Comparison, FAQ, Footer
│   ├── public/                                 # Static demonstration assets
│   ├── package.json                            # Next.js 16.3.6, React 19.2.8, Lenis 1.3.26
│   └── tsconfig.json
├── MedLens_Capstone_Implementation_Blueprint.md# Target Blueprint Specification
├── medlens_system_architecture_and_software_design_document.md
├── medlens_complete_product_requirements_document.md
└── README.md
```

### 2.2 Key Frontend Dependencies (`frontend/package.json`)
- `next`: `16.3.6`
- `react`: `19.2.8`
- `react-dom`: `19.2.8`
- `lenis`: `^1.3.26`
- `tailwindcss`: `^4` (PostCSS v4)
- `typescript`: `^5`
- `eslint`: `^9`

---

## 3. Working User Flows vs. Planned Backend

| Flow | Current Implementation | Planned Target Behavior |
|---|---|---|
| **Image Intake** | `UploadZone.tsx` accepts files or streams camera via `LiveCamera.tsx`. Image is stored in `sessionStorage` (`scanned_image`). | Files streamed to `POST /api/v1/analyses`; validated for MIME type, dimensions, and Laplacian blur score. |
| **Pipeline Status** | `ProcessingPulse.tsx` simulates 4 progress steps using `setTimeout` (extract, normalize, verify, report). | Server-Sent Events (SSE) or polling `GET /api/v1/analyses/{id}` reflecting real worker state machine. |
| **Analysis Report** | `/dashboard/results/[id]` loads hardcoded `mockReport` (Dolo 650) with static PubChem/OpenFDA links. | Dynamic report populated from verified database monographs, explicit uncertainty flags, and real OCR bounding boxes. |
| **Brand Comparison** | `/dashboard/compare` contains hardcoded comparison between Dolo 650 and Calpol 500. | `POST /api/v1/comparisons` computing deterministic active salt match, strength delta, excipient diff, and evidence citations. |
| **Authentication** | `/login` simulates login via 800ms timer and redirects to `/dashboard`. | Optional Firebase Auth / JWT verifying session on the FastAPI backend. |

---

## 4. Build, Lint & Test Health

### 4.1 Lint Execution (`npm run lint`)
Executed against `frontend`:
- **Errors found (5):**
  - Unescaped entity characters in `app/dashboard/page.tsx` (L14), `app/login/page.tsx` (L100), and `components/report/IngredientCard.tsx` (L34).
  - Synchronous `setState` in `useEffect` in `app/dashboard/results/[id]/page.tsx` (L71) flagged by React 19 rules.
- **Warnings found (10):**
  - Unused imports (`IcoArrow`, `useState`, etc.) and `<img>` vs Next.js `<Image />` tags.
- **Tests:** Zero unit or integration test suites currently exist.

---

## 5. Architectural Alignment & Blueprint Compliance

The **Capstone Implementation Blueprint** establishes strict non-negotiable boundaries that must guide development:

1. **No External Generative AI API Dependency:**
   - The core extraction, normalization, and report pipeline must run via local ML (PaddleOCR + PyTorch token classifier) and deterministic database monographs.
2. **PostgreSQL as Canonical Source of Truth:**
   - Products, ingredients, aliases, clinical monographs, and drug-drug interactions must be stored in PostgreSQL with strict relational schemas and foreign keys, managed via Alembic migrations.
3. **No Blind Salt Stripping:**
   - Chemical salts must not be blindly truncated via string regex alone; source-backed relationships must be preserved.
4. **Multidimensional Confidence (No Fake Percentages):**
   - The UI must report discrete confidence dimensions: OCR quality, extraction quality, identity confidence, and evidence coverage.
5. **Explicit 4-State Verification Model:**
   - Every candidate output must resolve to `verified`, `partially_verified`, `needs_confirmation`, or `unable_to_verify`.

---

## 6. Environment Variables Blueprint (Names Only)

The target backend will require the following environment variables (defined in `.env.example`):
- `DATABASE_URL` (PostgreSQL connection string)
- `API_V1_PREFIX` (e.g. `/api/v1`)
- `ENVIRONMENT` (`development` / `production`)
- `CORS_ORIGINS` (Allowed origins, e.g. `http://localhost:3000`)
- `OCR_ENGINE` (`paddleocr` / `tesseract`)
- `MODEL_CHECKPOINT_DIR` (Path to local fine-tuned Hugging Face weights)
- `MAX_UPLOAD_SIZE_MB` (e.g. `15`)
- `OPENFDA_API_KEY` (Optional for rate limit headroom, not a mandatory inference dependency)

---

## 7. Recommended Implementation Sequence

Mapped directly to Blueprint Section 13.2:

```
[Phase 0: Audit] (Completed in this document)
       │
       ▼
[Phase 1: Backend Skeleton & Schemas]
  ├── Create backend/ with FastAPI, Pydantic v2 schemas, and health checks
  ├── Fix existing frontend lint errors to ensure clean Next.js builds
  └── Add pytest unit test scaffold for backend schemas
       │
       ▼
[Phase 2: PostgreSQL Relational Database]
  ├── Define SQLAlchemy models and Alembic migrations
  └── Ingest initial seed fixture (top 50 common Indian/global OTC medications)
       │
       ▼
[Phase 3: Image Intake & OCR Pipeline]
  ├── OpenCV preprocessing service (blur, glare, deskew)
  └── PaddleOCR v4 / Tesseract spatial extraction service
       │
       ▼
[Phase 4 & 5: Extraction Model & Normalization]
  ├── Rule-based baseline + Hugging Face token classifier
  └── Alias lookup, RapidFuzz candidate search, and verification states
       │
       ▼
[Phase 6 & 7: Evidence Reports & Comparison Engine]
  ├── Deterministic per-field comparison matrix
  └── Interaction checking against curated drug-drug database
       │
       ▼
[Phase 8: Full-Stack Frontend Integration]
  └── Connect Next.js UploadZone and results view to real FastAPI endpoints
```
