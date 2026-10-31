# 🔬 MedLens Pretrained OCR Benchmark Report (Prompt 4)

> **Generated:** 2026-10-31T18:00:45.584552+00:00  
> **Target Split:** `test`  
> **Benchmark Status:** `ENGINES_UNAVAILABLE`  
> **Ground Truth Policy:** Only human-verified authentic physical packaging photographs evaluated.

---

## 1. Engine Availability & Execution Diagnostics

| Engine Name | Status | Installed Version | Diagnostic Reason |
| :--- | :---: | :---: | :--- |
| `paddleocr` | `UNAVAILABLE` | `unavailable` | Engine 'paddleocr' binaries or Python packages missing |
| `tesseract` | `UNAVAILABLE` | `unavailable` | Engine 'tesseract' binaries or Python packages missing |

---

## 2. Benchmark Findings & Evaluation Outcomes

> [!IMPORTANT]
> **Engines Unavailable in Environment:**
> Human-verified real packaging images exist (`1` eligible), but requested OCR engines (`tesseract`, `paddleocr`) are not installed on this host. Per MedLens integrity standards, mock results are never silently substituted into benchmark scores.

---

## 3. Methodological Disclaimers

1. **No Medical Validation Claim:** OCR Character Error Rate and Word Error Rate measure visual character recognition fidelity. They do not claim clinical accuracy or medical safety.
2. **Decoupled from Composition Parser:** OCR text transcription is evaluated strictly against verbatim text, independent of regex token extraction or INN normalization success.
3. **Zero Synthetic Ground Truth:** Test fixtures and 3D graphics are explicitly segregated from real packaging evaluations.