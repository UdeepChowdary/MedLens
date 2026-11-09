# Product Requirements Document (PRD)

## Project: MedLens
**Tagline:** Scan. Understand. Verify.  
**System Classification:** AI-Powered Pharmaceutical Composition Verification & Clinical Intelligence Platform  
**Document Status:** Approved & Production-Ready  
**Version:** 2.0.0  
**Target Environments:** Web & Mobile Responsive (Next.js 16 + React 19 / Python FastAPI)  
**Author:** MedLens Engineering Team  

---

## 1. Executive Summary & Vision

### 1.1 Product Vision
**MedLens** is an intelligent, image-first pharmaceutical verification and patient education platform. It allows patients, chronic disease caregivers, healthcare students, and consumers to photograph or upload medicine packaging (tablet blister packs, capsule strips, bottle labels, or suspension cartons) and immediately obtain a deterministic, scientifically verified, and understandable analysis of its active pharmaceutical ingredients (APIs), excipients, indications, contraindications, and therapeutic equivalents.

### 1.2 Core Philosophy
> **"Do not treat the generative language model as the source of truth. Treat it as a clinical synthesis and reasoning layer operating strictly on top of deterministic image extraction, active salt normalization, and grounded pharmacopeial retrieval."**

MedLens operates strictly as an **educational, informational, and verification platform**, never as an automated prescribing authority or diagnostic engine. Every active chemical salt, therapeutic dose, and contraindication is grounded against canonical pharmacopeial datasets (such as the *Indian Pharmacopoeia (IP)*, *British Pharmacopoeia (BP)*, *United States Pharmacopeia (USP)*, *openFDA*, and *PubChem*).

```
   ┌────────────────────────────────────────────────────────────────────────┐
   │                        MEDLENS PROCESSING PARADIGM                     │
   └────────────────────────────────────────────────────────────────────────┘
     [Camera / Image Intake]
                │
                ▼
     [1. Image Diagnostics]   ──▶ Rejects blurry, tilted, or occluded photos
                │
                ▼
     [2. Deterministic OCR]   ──▶ Extracts raw text tokens & spatial layout
                │
                ▼
     [3. Salt Normalization]  ──▶ Maps trade aliases to canonical INN entities
                │
                ▼
     [4. Monograph Grounding] ──▶ Queries openFDA, PubChem & Pharmacopoeia
                │
                ▼
     [5. Constrained AI]      ──▶ Synthesizes structured clinical breakdown (Temp 0.0)
                │
                ▼
     [6. Personalization]     ──▶ Cross-checks patient profile for contraindications
                │
                ▼
     [7. Structured UI Cards] ──▶ Delivers verifiable, transparent report with audit trail
```

---

## 2. Problem Statement & Market Opportunity

### 2.1 The Clinical & Consumer Problem
1. **Information Density & Cryptic Packaging:** Medicine packaging is filled with dense abbreviations (*I.P.*, *B.P.*, *U.S.P.*, *q.s.*, *w/v*), complex chemical nomenclature (*Paracetamol* vs *Acetaminophen*), and inactive excipients (*Microcrystalline Cellulose*, *Titanium Dioxide IP*).
2. **Active vs. Inactive Confusion:** Over 70% of non-expert patients cannot identify which ingredient delivers the therapeutic effect and which ingredients are binders, preservatives, or colorants.
3. **Dangerous Accidental Overdoses (Brand Duplication):** In India and global generic drug markets, the same active molecule is sold under hundreds of proprietary brand names (e.g., *Dolo 650*, *Calpol 650*, *Crocin 650*, *Pacimol 650* all contain Paracetamol 650 mg). Patients frequently take two different brands concurrently, leading to toxic liver injury (hepatotoxicity).
4. **Counterfeit & Mislabeled Medicines:** Substandard, spurious, or incorrectly packaged medicines cause severe clinical complications due to a lack of immediate composition verification tools.
5. **General AI Hallucination:** Mainstream generic LLMs (ChatGPT, Gemini, Claude) generate conversational, unvalidated prose when asked about medicines, frequently hallucinating strengths, dosages, or contraindications without a deterministic evidence trail.

### 2.2 Competitive Advantage Matrix

| Feature Dimension | Generic LLMs (ChatGPT / Claude) | Health Portals (WebMD, 1mg, Practo) | MedLens Verification Engine |
| :--- | :--- | :--- | :--- |
| **Primary Input** | Unstructured text prompts or generic image upload | Manual keyword search by brand name | **Image-First:** Real-time camera or blister pack photo upload |
| **Extraction Engine** | End-to-end black-box generative text | Static relational database queries | **Deterministic Multi-Stage:** OpenCV $\rightarrow$ PaddleOCR/Tesseract $\rightarrow$ INN Normalizer |
| **Salt Identification** | Probabilistic (prone to hallucinating dosages) | Requires exact brand spelling | **Fuzzy INN Matching & Alias Resolution** (e.g., *APAP* $\rightarrow$ *Paracetamol*) |
| **Verification Depth** | Unreferenced text summary | Product listing / Commercial catalog | **Monograph-Grounded:** Cross-referenced with openFDA, PubChem & IP |
| **Brand Comparison** | Subjective, conversational advice | Commercial cross-selling | **Pharmacological Equivalence Matching** (Active Salts, Strengths, Forms) |
| **Personalized Safety** | Requires manual medical history re-prompting | Static warnings | **Patient-Specific Contraindication & Drug-Drug Interaction Alerts** |
| **Explainability** | Black box | Static articles | **Transparent Evidence Trail** with multidimensional confidence scores |

---

## 3. User Personas & Target Audiences

### 3.1 Persona Profiles

```
┌────────────────────────────────────────────────────────────────────────┐
│ Persona A: Chronic Disease Caregiver (Meera, 44)                       │
├────────────────────────────────────────────────────────────────────────┤
│ Context: Manages daily medication for elderly hypertensive parents.    │
│ Pain Point: Local chemist provides generic substitutes with unfamiliar │
│             brand names; terrified of giving the wrong medicine.       │
│ Goal: Snap the strip and immediately verify active salt equivalency.   │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ Persona B: Informed Patient with Allergies (Rahul, 29)                 │
├────────────────────────────────────────────────────────────────────────┤
│ Context: Prescribed combination cold medicine; has severe NSAID ulcer. │
│ Pain Point: Does not know if the combination tablet contains aspirin   │
│             or ibuprofen under a complex brand name.                   │
│ Goal: Instant allergy and contraindication alert against user profile. │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ Persona C: Medical / Pharmacy Student (Ananya, 22)                     │
├────────────────────────────────────────────────────────────────────────┤
│ Context: Studying pharmaceutical formulations and clinical monographs. │
│ Pain Point: Needs fast reference on active salt ratios, pharmacopeial  │
│             monographs, and excipient functional categories.           │
│ Goal: Structured breakdowns of OTC and prescription formulations.      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Product Goals & Key Performance Indicators (KPIs)

### 4.1 Product Objectives
* Provide an instantaneous, zero-confusion verification tool for real-world medicine packaging.
* Eliminate accidental multi-brand duplicate dosing through accurate active salt identification.
* Enable patient safety checks by flagging personalized contraindications and drug interactions.

### 4.2 Measurable Technical KPIs
1. **End-to-End Processing Latency:** $\le 3.5\text{ seconds}$ from image upload to structured report generation on standard 4G/broadband connections.
2. **OCR Text Accuracy:** Character Error Rate (CER) $\le 4.5\%$ on clear packaging photographs.
3. **Active Salt Extraction Precision:** $\ge 96.0\%$ precision on canonical top-100 Indian pharmaceutical formulations.
4. **Image Rejection Precision:** $100\%$ detection of unusable, out-of-focus images ($\sigma_{\text{Laplacian}}^2 < 100.0$) preventing false extractions.
5. **Zero Generative Hallucinations:** $0\%$ hallucination of non-existent active salts by constraining generative models strictly to extracted tokens and verified database monographs.

---

## 5. Functional Requirements (FR)

### FR-1: Image Capture & Quality Diagnostics
* **FR-1.1:** The system shall allow users to capture an image directly using the device camera (WebRTC / HTML5 MediaDevices API) or upload existing image files (`.jpg`, `.jpeg`, `.png`, `.webp`, maximum size $15\text{ MB}$).
* **FR-1.2:** The system shall perform client-side and server-side image quality diagnostics:
  * Check image resolution (minimum $300 \times 300\text{ px}$).
  * Compute blur variance using the Laplacian operator ($\sigma_L^2$). If $\sigma_L^2 < 100.0$, the system shall reject the image with a descriptive error: `ERR_IMAGE_BLURRY` ("Packaging image is too blurry. Please steady your camera and ensure good lighting").
  * Calculate image SHA-256 digest to prevent duplicate processing of identical uploads.
* **FR-1.3:** Multimodal Manual Medicine Search Fallback:
  * The system shall provide an intuitive manual text lookup fallback (`POST /api/v1/analyses/text`) on the scan page for instances where medicine blister strips have been cut by a pharmacy, torn, half-consumed, or missing printed text panels.
  * The text intake shall resolve brand trade names (e.g., *Zerodol-SP*, *Telma 40*, *Augmentin 625 Duo*, *Dolo 650*) and generic chemical salts into their multi-ingredient active compositions via `ProductIngredient` relations.
  * The generated report shall conform identically to the optical analysis schema (`AnalysisResponse`), eliminating OCR errors with an assigned optical confidence of $1.0$ while performing canonical INN normalization, boxed warning extraction, and personalized safety cross-checks.

### FR-2: Optical Character Recognition (OCR) Engine
* **FR-2.1:** The system shall dispatch preprocessed images through a dual OCR pipeline (PaddleOCR as primary high-precision text detector, with Tesseract OCR fallback).
* **FR-2.2:** The OCR engine shall extract raw text lines along with their 2D bounding box spatial coordinates (`[x_min, y_min, x_max, y_max]`) and token confidence scores ($0.0 - 1.0$).
* **FR-2.3:** The OCR post-processor shall reconstruct multi-line composition panels (e.g., `"Each film coated tablet contains: Paracetamol IP 650 mg"`).

### FR-3: Active Salt & Dosage Extraction
* **FR-3.1:** The system shall extract active pharmaceutical ingredients (APIs), strengths, units of measurement (`mg`, `mcg`, `g`, `ml`, `IU`, `w/v`, `w/w`), and pharmacopeial standards (`IP`, `BP`, `USP`).
* **FR-3.2:** The system shall separate therapeutic active salts from inactive excipients, binders, disintegrants, and colorants (e.g., *Titanium Dioxide*, *Starch*, *Sunset Yellow*).
* **FR-3.3:** The system shall support multi-ingredient combination formulations (e.g., *Amoxicillin 500 mg + Potassium Clavulanate 125 mg*).

### FR-4: INN Normalization & Pharmacopeial Grounding
* **FR-4.1:** The system shall normalize trade aliases, common abbreviations, and phonetic misspellings into standardized International Nonproprietary Names (INN) using normalized Levenshtein distance:
  $$\text{Similarity}(s_1, s_2) = 1.0 - \frac{\text{Levenshtein}(s_1, s_2)}{\max(|s_1|, |s_2|)}$$
  (e.g., mapping `"Acetaminophen"`, `"APAP"`, `"Paracetamolum"` to canonical `"Paracetamol"`).
* **FR-4.2:** The system shall cross-reference normalized active salts against trusted clinical reference databases:
  * **openFDA API:** Approved indications, warnings, boxed warnings, mechanism of action.
  * **PubChem:** Compound Identification (CID), IUPAC chemical structure, molecular weight.
  * **Indian Pharmacopoeia (IP) Monographs:** Regional standards, recommended OTC dosages, and storage conditions.

### FR-5: Clinical Verification Report Generation
* **FR-5.1:** The system shall compile a structured verification report containing:
  * Detected Medicine Name and Manufacturer.
  * Active Ingredients Table (Salt Name, Strength, Unit, Therapeutic Role).
  * Excipients & Additives breakdown.
  * Primary Medical Indications ("What this medicine treats").
  * Safe Usage Guidelines & Standard Administration Times (e.g., "Take after meals").
  * Common & Serious Side Effects.
  * Multidimensional Confidence Score ($0 - 100\%$) indicating extraction and verification certainty.
* **FR-5.2:** Every report shall display a permanent, unambiguous educational medical disclaimer.

### FR-6: Therapeutic Brand Comparison & Substitution
* **FR-6.1:** The system shall provide a "Compare by Disease / Indication" module.
* **FR-6.2:** Users shall be able to select a clinical condition (e.g., *Fever & Pain*, *Acid Reflux*, *Bacterial Infection*, *Hypertension*) or input two commercial brands to compare:
  * Active Salt Equivalence (identical vs. differing therapeutic molecules).
  * Strength / Dosage Match.
  * Price vs. Generic Savings Estimation.
  * Manufacturer Quality Standards.

### FR-7: Patient Profile & Personalized Contraindication Engine
* **FR-7.1:** The system shall allow authenticated users to maintain a persistent health profile containing:
  * Age, gender, pregnancy/lactation status.
  * Pre-existing medical conditions (e.g., *Chronic Kidney Disease*, *Hypertension*, *Type 2 Diabetes*, *Gastric Ulcers*).
  * Known drug allergies (e.g., *Penicillin*, *Sulfa drugs*, *NSAIDs*).
  * Current daily medications.
* **FR-7.2:** During each packaging analysis, the system shall execute real-time personalized safety checks:
  * **Drug-Condition Alerts:** Warning if the scanned active salt is contraindicated for the patient's recorded conditions (e.g., *Ibuprofen* contraindicated in active peptic ulcer disease).
  * **Drug-Drug Interaction Warnings:** Flagging adverse interactions with currently active medications (e.g., *Sildenafil* + *Nitrates*, or *Warfarin* + *Aspirin*).
  * **Severity Tiering:** Categorized into `CRITICAL (Red)`, `MODERATE (Yellow)`, and `INFO (Blue)`.

### FR-8: User Authentication, History & Audit Logs
* **FR-8.1:** The system shall support secure user authentication via Google OAuth 2.0 and Email/Password using Firebase Authentication.
* **FR-8.2:** The system shall maintain an audit history of all completed scans with timestamp, extracted composition, and verification status for patient reference.
* **FR-8.3:** Users shall have full autonomy to delete historical scan logs and export reports to PDF.

---

## 6. User Stories & Acceptance Criteria (Gherkin Format)

### User Story 1: Blurry Packaging Detection
```gherkin
Scenario: User uploads an out-of-focus medicine package photograph
  Given the user is on the MedLens scan dashboard
  When the user uploads an image with Laplacian variance less than 100.0
  Then the system immediately rejects the upload without calling the OCR engine
  And displays an alert: "Packaging image is too blurry (Variance: 42.1 < 100). Please hold steady and recapture."
```

### User Story 2: Active Salt & Strength Extraction
```gherkin
Scenario: User scans a blister strip of Dolo 650
  Given a clear image of a "Dolo 650" tablet packaging is uploaded
  When the verification pipeline processes the image
  Then the system identifies "Paracetamol" as the active pharmaceutical salt
  And extracts the strength as "650 mg" with pharmacopeial standard "IP"
  And separates "Starch" and "PVP K30" into inactive excipients
  And calculates an overall verification confidence score >= 90%.
```

### User Story 3: Personalized Contraindication Alert
```gherkin
Scenario: Patient with chronic kidney disease scans an NSAID medication
  Given the logged-in user has "Chronic Kidney Disease (CKD Stage 3)" in their profile
  When the user scans a blister pack of "Combiflam" (Ibuprofen 400 mg + Paracetamol 325 mg)
  Then the system displays a prominent CRITICAL WARNING banner
  And explains: "Ibuprofen is contraindicated in renal impairment as NSAIDs decrease renal blood flow"
  And advises: "Consult your prescribing nephrologist before administering this formulation."
```

### User Story 4: Damaged / Cut Blister Strip Fallback
```gherkin
Scenario: Patient has a half-consumed blister strip with cut-off text labels
  Given the patient has an unreadable, cut-off tablet strip but knows the trade name "Zerodol-SP"
  When the patient switches to the "Search / Type Medicine" tab on the scan page and submits "Zerodol-SP"
  Then the system resolves all 3 active chemical salts (Aceclofenac 100 mg, Paracetamol 325 mg, Serratiopeptidase 15 mg)
  And evaluates contraindications against the user's recorded health profile
  And generates the complete clinical report with 100% extraction fidelity.
```

---

## 7. Non-Functional Requirements (NFR)

| ID | Category | Requirement Specification | Measurement Metric |
| :--- | :--- | :--- | :--- |
| **NFR-1** | **Performance** | API response time for complete scan pipeline shall not exceed $3.5\text{ s}$ under normal load ($p95 \le 4.2\text{ s}$). | Server processing duration timer |
| **NFR-2** | **Availability** | The system web interface and REST API shall achieve $99.5\%$ uptime during academic and production hosting. | Uptime monitoring probe |
| **NFR-3** | **Security & Privacy** | Images uploaded for analysis shall be processed in-memory or stored ephemerally; no PHI (Protected Health Information) is shared with public third-party models. | TLS 1.3 encryption in transit, SHA-256 hashed filenames |
| **NFR-4** | **Usability** | Mobile-first responsive design supporting screen widths from $320\text{ px}$ (smartphones) to $2560\text{ px}$ (desktop displays). | Lighthouse Accessibility score $\ge 92/100$ |
| **NFR-5** | **Scalability** | Stateless API architecture supporting containerized horizontal scaling with SQLite (local development) and PostgreSQL / Neon (production). | Simultaneous connection testing |
| **NFR-6** | **Extensibility** | Pluggable OCR interface allowing seamless swapping between Tesseract, PaddleOCR, and Cloud Vision without breaking service contracts. | Unified `BaseOCREngine` abstract base class |

---

## 8. Medical Safety & Legal Compliance Guardrails

1. **Mandatory Educational Disclaimer:**
   Every page, report, and export must prominently display:
   > *"MedLens is an AI-assisted pharmaceutical verification tool designed for educational and informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or prescription from a licensed healthcare provider."*
2. **Scheduled Drug Handling:**
   For formulations containing Schedule H, H1, or X controlled substances (e.g., *Alprazolam*, *Codeine*, *Tramadol*), the system shall flag a bold warning: *"Warning: This medication is a controlled scheduled drug. Dispense and consume strictly under registered medical prescription."*
3. **No Automated Prescribing:**
   The platform strictly rejects queries asking for prescription changes, dosage alterations, or therapeutic substitutions without doctor consultation.

---

## 9. Out of Scope & Future Roadmap

### 9.1 Out of Scope for Version 2.0
* Physical pill shape/color computer vision identification (tablet debossing/imprint recognition).
* Barcode / 2D DataMatrix scanning for supply-chain batch traceability.
* Direct e-pharmacy checkout or commercial affiliate purchasing links.

### 9.2 Future Roadmap (Version 3.0+)
* **Multilingual Vernacular Audio:** Voice readout of dosage and side effects in regional languages (Hindi, Telugu, Tamil, Bengali, Spanish).
* **Doctor Prescription OCR Matching:** Upload both doctor's prescription slip and medicine strip to verify accurate dispensing by pharmacists.
* **Pediatric & Geriatric Dose Adjusters:** Automatic renal/weight-adjusted dose verification calculator.
