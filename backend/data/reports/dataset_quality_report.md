# 📊 MedLens Medicine Label Dataset Quality Report

> **Generated:** 2026-11-01T15:33:14.466631+00:00  
> **Specification:** MedLens Capstone Implementation Blueprint (Section 06)

---

## 1. Executive Summary

- **Total Medicine Images:** `21`
- **Unique Product Families:** `11` (Leakage-isolation key)
- **Total Annotated Entity Tokens:** `119`
- **Mean Entities per Image:** `5.67`
- **Human-Verified Ratio:** `100.0%`

---

## 2. Entity Token Class Distribution

| Entity Label | Instances | Percentage | Description |
| :--- | :--- | :--- | :--- |
| `BRAND` | 16 | 13.4% | Trade name / packaging commercial branding |
| `PRODUCT_NAME` | 1 | 0.8% | Descriptive generic product title |
| `INGREDIENT` | 20 | 16.8% | Active pharmaceutical ingredient chemical moiety |
| `SALT_FORM` | 28 | 23.5% | Chemical salt or pharmacopeial notation (IP, BP, USP, HCl) |
| `STRENGTH` | 20 | 16.8% | Quantitative dosage strength with unit |
| `CONCENTRATION` | 0 | 0.0% | Mass-per-volume dosage formulation *(0 instances in current sample)* |
| `STRENGTH_BASIS` | 12 | 10.1% | Dosing unit basis (per tablet, per 5 mL) |
| `DOSAGE_FORM` | 13 | 10.9% | Physical presentation (Tablet, Capsule, Syrup) |
| `ROUTE` | 1 | 0.8% | Administration route (Oral, Topical) |
| `RELEASE_TYPE` | 2 | 1.7% | Modified release modifier (SR, ER, CR) |
| `COMPOSITION_HEADER` | 6 | 5.0% | Structural composition section heading |

---

## 3. Physical Packaging Types

| Packaging Presentation | Count | Percentage |
| :--- | :--- | :--- |
| `blister_foil` | 19 | 90.5% |
| `bottle_label` | 2 | 9.5% |

---

## 4. Visual Degradation & Quality Flags

| Quality Flag | Flagged Images | Percentage | Clinical Implication |
| :--- | :--- | :--- | :--- |
| `small_text` | 12 | 57.1% | Micro-typography below 6pt requires high-DPI scaling |
| `glare` | 1 | 4.8% | Metallic blister foil specular reflection obscures fine text |

---

## 5. Partition Splits (Zero-Leakage Product Stratification)

| Split | Images | Product Families | Partition Ratio |
| :--- | :--- | :--- | :--- |
| `TRAIN` | 15 | 8 | 71.4% |
| `VAL` | 3 | 2 | 14.3% |
| `TEST` | 3 | 1 | 14.3% |

---

## 6. Provenance & Usage Licensing

| Source Organization / Origin | License | Count |
| :--- | :--- | :--- |
| Authentic Indian Retail Pharmacy Packaging (Student Collection) | CC-BY-4.0 | 21 |

---

## 7. Next Step Verification Checklist
- [x] Validated JSON schema and normalized coordinate bounds `[0, 1000]`
- [x] Zero duplicate images verified via cryptographic SHA-256
- [x] Zero product family leakage across Train / Val / Test partitions
- [x] Human verification status audited before training initiation

---

## 8. Pilot Synthetic Image Audit & Supersession Notice (ML-014)

### 8.1 Background & Audit Findings
During the initial repository bootstrap phase (October 2026), 5 synthetic test illustrations and unreviewed placeholders were added to establish baseline data schemas and mock pipelines:
1. `dolo_650_blister.jpg` (3D generic digital render lacking authentic packaging typography; flagged).
2. `augmentin_625_box.jpg` (Tight crop of blank blister pockets with zero readable text; flagged).
3. `brufen_400_strip.png` (Pillow-rendered synthetic test fixture; draft status).
4. `cetirizine_10_strip.png` (Pillow-rendered synthetic test fixture; draft status).
5. `paracetamol_500_box.jpg` (Unreviewed pilot illustration; flagged).

### 8.2 Formal Supersession & Segregation Policy
As of November 1, 2026 (`[ML-018]`, `[ML-019]`, `[ML-020]`, `[ML-021]`), 21 authentic, high-resolution physical packaging photographs across 11 core medicine families were procured and 100% human-verified with ground-truth bounding boxes and verbatim transcriptions:
- **Dolo 650:** `dolo_650_strip_back.jpg` & `front` (Micro Labs Ltd, Paracetamol 650 mg).
- **Combiflam:** `combiflam_strip_back.jpg` & `front` (Sanofi India Ltd, Ibuprofen 400 mg + Paracetamol 325 mg).
- **Pan 40:** `pan_40_strip_back.jpg` & `front` (Alkem Laboratories Ltd, Pantoprazole Sodium 40 mg).
- **Pan-D:** `pan_d_strip_back.webp` (Alkem Laboratories Ltd, Pantoprazole 40 mg + Domperidone 30 mg SR).
- **Cetirizine:** `Cetirizine_strip_back.jpg` & `front` (Cipla / Bioconic Remedies, Cetirizine Dihydrochloride 10 mg).
- **Augmentin 625 Duo:** `augmentin_625_strip.jpg` (GlaxoSmithKline Pharmaceuticals Ltd, Amoxicillin 500 mg + Clavulanic Acid 125 mg).
- **Azithral 500:** `azithral_500_strip_back.jpg` & `front` (Alembic Pharmaceuticals, Azithromycin 500 mg).
- **Benadryl Syrup:** `benedryl_bottle_back.jpg` & `front` (Johnson & Johnson / Kenvue, Diphenhydramine + Ammonium Chloride + Sodium Citrate).
- **Ecosprin 75:** `ecosprin_75_strip_back.jpg` & `front` (USV Pvt Ltd, Aspirin / Acetylsalicylic Acid 75 mg).
- **Glycomet 500:** `glycomet_500_strip_back.jpg` & `front` (USV Pvt Ltd, Metformin HCl 500 mg).
- **Montair 10:** `montair_10_strip_back.jpg` & `front` (Cipla Ltd, Montelukast Sodium 10 mg).
- **Omez 20:** `omez_20_strip.jpg` (Dr. Reddy's Laboratories, Omeprazole 20 mg).

### 8.3 Enforcement & Zero-Mock Assurance
- All synthetic fixtures and unreviewed illustrations are strictly excluded from OCR benchmarking and model training (`eligible_for_real_training: false`, `review_status: flagged_for_review`).
- All 21 authentic packaging photographs are designated as the official MedLens ground truth (`eligible_for_real_training: true`, `review_status: verified_by_human`).