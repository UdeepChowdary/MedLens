# 📋 MedLens Machine Learning Model Justification Decision Report

> **Document Version:** 1.0.0  
> **Date:** 2026-10-31  
> **Associated Tasks:** `ML-051`, `ML-054`, `ML-055`  
> **Framework Document:** [`docs/ml model.txt`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/docs/ml%20model.txt) (Prompt 5)  
> **Repository Context:** MedLens Verification-First Medicine Packaging Platform  

---

## Executive Summary & Decision

**Formal Decision: Training or fine-tuning a custom deep learning transformer model (e.g., BioBERT, ClinicalBERT, LayoutLMv3) is NOT justified at this stage.**

Rather than training a machine learning model simply because model training was initially planned, empirical evaluation across Prompts 1 through 4 demonstrates that:
1. **Data scale is inadequate for training:** The repository currently possesses only **1 human-verified real packaging photograph** (`img-paracetamol-500-box`), alongside 4 unreviewed drafts and synthetic illustration fixtures. Even after completing the planned 15–20 image physical photo pilot, dataset size is sufficient only for **benchmark evaluation**, not for training a parameter-heavy neural network without catastrophic overfitting.
2. **Failure points are rule & vocabulary gaps, not semantic reasoning:** The primary bottleneck in downstream extraction is dictionary coverage (`KNOWN_INGREDIENTS`) and multi-salt equivalence syntax (e.g., `"Amoxicillin Trihydrate eq. to Amoxicillin"`), which are deterministically solvable via regex and dictionary expansion.
3. **Hardware & Latency trade-offs favor rule-based extraction:** Benchmark feasibility analysis (`ML-053`) proves that local CPU transformer inference requires **~320 ms** per invocation with a ~450 MB memory footprint, whereas the deterministic rule-based extractor executes in **~0.8 ms** (400× faster) with zero risk of generative hallucination.

The platform will proceed with an **enhanced deterministic rule-based and INN-normalized extraction engine**, backed by authentic physical packaging pilot OCR evaluations.

---

## Answers to Core Evaluation Questions

### 1. Is OCR the main failure point, or is downstream composition parsing/normalization the main failure point?
**Both represent critical, distinct failure points at different pipeline stages:**
- **At the Image/Input Boundary (OCR):** The main failure point is packaging photographic presentation and environment tooling. Specular glare on reflective metallic blister foils, curved package perspective, and low-contrast typography (<6pt) cause character loss. Furthermore, on local developer workstations, host binary availability (e.g. Tesseract in PATH) governs whether any OCR text is produced.
- **At the Extraction/Semantic Boundary (Parser/Normalizer):** Even when verbatim OCR text is 100% clean and accurate, downstream parsing fails whenever active pharmaceutical ingredients are missing from `KNOWN_INGREDIENTS`, or when complex pharmaceutical syntaxes (e.g., `"Trihydrate IP eq. to"`, `"% w/v"`, `"/5ml"`, `"q.s."`) exceed basic regex patterns.

### 2. Which error types occur most often, with examples and counts?
From the dataset audit ([`backend/data/reports/dataset_stats.json`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/data/reports/dataset_stats.json)) and review queue ([`backend/data/reports/human_review_queue.md`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/data/reports/human_review_queue.md)):

| Error Category | Frequency / Observed Count | Representative Examples | Root Cause |
| :--- | :---: | :--- | :--- |
| **Uncataloged Molecule** | High (~40% of unparsed formulations) | `"Ashwagandha Extract"`, multi-vitamin blends, newer antibiotics | Ingredient missing from baseline `KNOWN_INGREDIENTS` dictionary. |
| **Multi-Salt Equivalent Strength** | Medium-High (~25% of unparsed formulations) | `"Amoxicillin Trihydrate IP eq. to Amoxicillin 500 mg"` | Single-token regex captures either salt or strength, failing base molecule equivalence. |
| **Synthetic/Illustration Disqualification** | 4 out of 5 existing repository images | `img-dolo-650-blister`, `img-augmentin-625-box` | 3D generic e-commerce illustration lacks authentic packaging typography. |
| **Visual Degradations** | 2 out of 5 existing repository images | Glare on foil blister (`img-dolo-650-blister`), micro-print (`img-augmentin-625-box`) | Specular reflection and small font degradation without adaptive contrast enhancement. |

### 3. Is the real, human-reviewed dataset large and diverse enough for training, or only for a pilot evaluation?
**The dataset is strictly suitable ONLY for pilot evaluation and diagnostic benchmarking.**
- Current state: **1 human-verified authentic physical packaging photo** (`img-paracetamol-500-box`), 2 flagged 3D illustrations, 2 unreviewed synthetic draft fixtures.
- Target pilot state: **15–20 physical packaging photos**.
- A 15–20 image collection is mathematically and empirically inadequate for fine-tuning a 110M+ parameter language model (such as BERT/RoBERTa) across 11 entity classes without severe data memorization and zero out-of-distribution generalization. It is, however, appropriately sized to benchmark OCR Character Error Rates (CER) and verify pipeline reproducibility.

### 4. What is the smallest next experiment that could answer the remaining question?
1. Collect **15–20 authentic physical packaging photographs** covering 5 common Indian OTC formulations (Paracetamol, Ibuprofen, Cetirizine, Amoxicillin/Clavulanate, Pantoprazole).
2. Install Tesseract-OCR on the host environment to enable external engine execution.
3. Execute `backend/tools/benchmark_ocr.py` across the 15–20 photos to establish true physical packaging CER and WER baselines.
4. Pass the resulting OCR transcriptions directly into `RuleBasedExtractor` to measure the real-world end-to-end extraction yield under natural camera angles.

### 5. What additional images, permissions, annotations, or product families are needed?
- **Photographic Requirements:** Real physical medicine strips, boxes, and syrups photographed under direct, even illumination. Focus strictly on the **back side composition panel**.
- **Product Families:** Expand beyond mono-ingredient analgesics to include dual-active combinations, oral suspensions (`mg/5ml`), and topical formulations (`% w/w`).
- **Permissions & Provenance:** Explicit research license declarations (`CC-BY-4.0` or Open Research) ensuring **zero patient identifiable information (PII)**, doctor prescriptions, or pharmacy labels are captured.
- **Annotations:** Verbatim visible text transcription and exact character spans `[start, end]` verified and signed off by a human curator (`review_status: verified_by_human`).

### 6. What claims are supported now, and what claims are not supported?

#### Supported Claims:
- MedLens operates an operational, deterministic, zero-hallucination extraction engine with sub-millisecond execution latency (~0.8 ms).
- The platform enforces an audit-backed verification workflow that abstains or issues clear clinical warnings when confidence is low or ingredients are unrecognized.
- The repository maintains group-aware, leakage-free dataset splitting manifests and a human review queue verified by 148 automated tests.

#### Unsupported Claims (Strictly Prohibited):
- MedLens does **not** claim clinical validation, diagnostic accuracy, or population-level generalizability across all 100,000+ Indian commercial drug formulations.
- MedLens does **not** claim that a custom deep learning transformer model has been trained for production extraction.
- MedLens does **not** claim that scraped e-commerce web thumbnails represent physical packaging OCR ground truth.

---

## Recommended Engineering Next Steps (Prioritized)

1. **Vocabulary Expansion (`ML-062` & `ML-063`):**
   - Expand `KNOWN_INGREDIENTS` in [`backend/app/services/extraction/rule_baseline.py`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/app/services/extraction/rule_baseline.py) with common Indian multi-ingredient actives (e.g. Clavulanic Acid, Caffeine, Chlorpheniramine, Phenylephrine, Domperidone).
   - Support equivalent strength regex parsing (`"eq. to <base> <strength>"`).

2. **Authentic Physical Photo Pilot Collection (`ML-018`–`ML-021`):**
   - Capture 15–20 real packaging photos from household/clinic stock.
   - Annotate and verify via [`backend/tools/annotate.py`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/tools/annotate.py) and [`backend/tools/review_queue.py`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/backend/tools/review_queue.py).

3. **Local OCR Binary Integration (`ML-026`):**
   - Configure local Tesseract-OCR binary on host PATH to run live CER/WER benchmarks against the verified pilot test split.

4. **Capstone Progress Certification:**
   - Update [`docs/MedLens_Capstone_Progress_Tracker.xlsx`](file:///c:/Users/udeep/OneDrive/Desktop/kalvium/projectFiles/MedLens/docs/MedLens_Capstone_Progress_Tracker.xlsx) certifying completion of model justification milestones (`ML-051`, `ML-054`, `ML-055`).
