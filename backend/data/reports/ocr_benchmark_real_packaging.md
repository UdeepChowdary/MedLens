# 🔬 MedLens Pretrained OCR Benchmark Report (Prompt 4)

> **Generated:** 2026-11-01T13:07:01.690051+00:00  
> **Target Split:** `all_verified`  
> **Benchmark Status:** `COMPLETED`  
> **Ground Truth Policy:** Only human-verified authentic physical packaging photographs evaluated.

---

## 1. Engine Availability & Execution Diagnostics

| Engine Name | Status | Installed Version | Diagnostic Reason |
| :--- | :---: | :---: | :--- |
| `paddleocr` | `READY` | `3.7.0` | Ready |

---

## 2. Benchmark Findings & Evaluation Outcomes

### Engine: `paddleocr` (3.7.0)

- **Images Evaluated:** `9`
- **Mean Normalized CER:** `154.54%`
- **Mean Normalized WER:** `159.01%`
- **Exact Match Count:** `1` / `9`
- **Mean Latency:** `16555 ms`

#### Detailed Error Samples

| Image ID | Ground Truth Text | OCR Output | CER | WER |
| :--- | :--- | :--- | :---: | :---: |
| `img-augmentin-625-strip` | `AUGMENTIN 625 Duo. Amoxycillin and Potas` | `AUGMENTIN625 DUTO EARSOF h TRUS 625 Co-a` | `1.68` | `1.99` |
| `img-cetirizine-strip-back` | `Cetirizine Tablets IP Cetizine. Composit` | `uy Universal Life Sclence Gw74 Chandanwa` | `0.93` | `1.10` |
| `img-cetirizine-strip-front` | `Cipla` | `Cipla` | `0.00` | `0.00` |
| `img-combiflam-strip-back` | `Combiflam. Anti-inflammatory Analgesic. ` | `sununneigifieun in efßniunn tealu snnues` | `1.25` | `1.48` |
| `img-combiflam-strip-front` | `0000 6856` | `0000 6856 0000 0000 0000 0000` | `2.22` | `2.00` |

---

## 3. Methodological Disclaimers

1. **No Medical Validation Claim:** OCR Character Error Rate and Word Error Rate measure visual character recognition fidelity. They do not claim clinical accuracy or medical safety.
2. **Decoupled from Composition Parser:** OCR text transcription is evaluated strictly against verbatim text, independent of regex token extraction or INN normalization success.
3. **Zero Synthetic Ground Truth:** Test fixtures and 3D graphics are explicitly segregated from real packaging evaluations.