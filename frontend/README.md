# 🔬 MedLens Frontend

This directory contains the user interface and client-side verification engine for **MedLens**, built with [Next.js 16.3](https://nextjs.org/) (Turbopack, App Router), [React 19](https://react.dev/), [TypeScript 5](https://www.typescriptlang.org/), and [Tailwind CSS v4](https://tailwindcss.com/).

> For complete project documentation, system architecture diagrams, and medical verification pipeline specs, please refer to the [Root README](../README.md).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Local Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Production Build & Verification
```bash
npm run build
npm run start
```

---

## 📂 Architecture & File Hierarchy

```
frontend/
├── app/
│   ├── page.tsx                      # Modern clinical landing page & feature showcases
│   ├── layout.tsx                    # Root HTML layout, SEO metadata & font optimization
│   ├── globals.css                   # Tailwind v4 clinical theme tokens & custom styling
│   ├── dashboard/                    # Core verification dashboard views
│   │   ├── scan/page.tsx             # Dual-mode intake: Blister pack photo scan & typed search fallback
│   │   ├── results/[id]/page.tsx     # Dynamic verification report with confidence gauge & section citations
│   │   ├── compare/page.tsx          # Dual-medicine comparison matrix & duplicate therapy alert engine
│   │   ├── history/page.tsx          # Session-scoped historical scans with PDF export
│   │   └── profile/page.tsx          # Patient profile (known drug allergies, medical conditions)
│   ├── login/page.tsx                # Authentication modal / login interface
│   ├── terms/page.tsx                # Terms of service & clinical liability disclaimer
│   └── privacy/page.tsx              # Patient data privacy guarantee
├── components/                       # Modular clinical UI components
│   ├── Navbar.tsx                    # Header navigation with active route highlights
│   ├── Footer.tsx                    # Footer with mandatory medical disclaimer & links
│   ├── Icons.tsx                     # SVG clinical & navigation icon library
│   ├── ScrollReveal.tsx              # Viewport reveal animations
│   ├── scanner/
│   │   ├── UploadZone.tsx            # Drag-and-drop file upload & WebRTC camera stream capture
│   │   └── ProcessingPulse.tsx       # Real-time multi-stage pipeline status visualization
│   └── results/
│       ├── ConfidenceGauge.tsx       # 4-axis calibrated confidence radar/gauge
│       ├── IngredientCard.tsx        # Monospace chemical strength & salt breakdown card
│       ├── SafetyBanner.tsx          # Boxed warnings & contraindication alerts
│       └── AllergenAlert.tsx         # Cross-referenced patient allergy mismatch banner
├── lib/
│   ├── api.ts                        # Typed centralized HTTP client (analyses, search, comparison, verification)
│   └── utils.ts                      # Formatting & CSS class merging utilities
├── public/                           # Static assets, logos, and authentic blister packaging samples
│   ├── samples/                      # 18 curated baseline Indian blister packaging samples
│   └── icons/                        # Favicons and web app manifests
├── package.json                      # Pinned dependencies (Next.js 16, React 19, Lenis)
├── tsconfig.json                     # Strict TypeScript compiler options
└── next.config.ts                    # Next.js configuration
```

---

## 📱 Key Features

1. **Dual Intake Modes:**
   - **Photo Packaging Scan:** Drag-and-drop or direct camera capture with client-side resolution validation.
   - **Manual Medicine Search (Fallback):** Instant search for damaged, crumpled, or half-consumed blister strips, with 1-click popular medicine selection pills (*Zerodol-SP, Telma 40, Augmentin 625 Duo, Dolo 650, Pan 40, Glycomet 500, Allegra 120, Montair-LC, Thyronorm 25*).
2. **18-Sample Authentic Packaging Gallery:** Categorized demo samples (*Pain & Spasm, Heart & BP, Antibiotics, Diabetes & Thyroid, Cough & Allergy*) for zero-friction evaluation.
3. **Bring Your Own Key (BYOK) Gemini AI:** Option to store a personal Google Gemini API key in `localStorage` for deep personalized clinical synthesis.
4. **Dynamic Safety & Contraindication Engine:** Automatically cross-checks extracted active salts against patient profile allergies and chronic conditions.
5. **Deterministic Medicine Comparison:** Side-by-side active salt alignment, dosage deltas, and life-saving duplicate active ingredient warnings.
