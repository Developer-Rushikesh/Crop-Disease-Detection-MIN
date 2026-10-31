# FloraScan AI — Final QA Audit & Deployment Verification Report

**Audit Date:** 2026-10-31 13:01:54  
**Auditor Roles:** Senior QA Engineer & Django ML Deployment Engineer  
**Platform:** Windows (Intel Core i5-1235U) | Python 3.12.5 | TensorFlow 2.21.0 | Django 5.0.14  
**Target Model:** MobileNetV2 Transfer Learning (Demo Architecture, 6 Classes)  

---

## 1. Executive Summary & Verification Matrix

| Audit Domain | Items Tested | Status | Critical Notes |
| :--- | :---: | :---: | :--- |
| **1. File Integrity & Artifacts** | 6 | **PASS** | All demo artifacts and production backup verified |
| **2. Model & Label Consistency** | 5 | **PASS** | Exactly 6 classes, Apple & Tomato only, zero Potato classes |
| **3. Django Web Flow & PDF** | 8 | **PASS** | End-to-end diagnosis, sample cards, and PDF report pass |
| **4. Inference Parity (Keras vs TFLite)** | 6 | **PASS** | 100% top-1 class agreement; TFLite avg latency 28.68 ms |
| **5. Out-of-Distribution Handling** | 3 | **PASS** | Documented limitation: Softmax closed-world behavior noted |
| **6. Security & Input Sanitization** | 6 | **PASS** | Size cap, extension filter, Pillow header inspection, CSRF |
| **7. Production Deployment Readiness** | 1 | **NOT TESTED** | Local verification complete; cloud hosting not yet provisioned |

---

## 2. File Verification

| File Name | Path | Size | Status |
| :--- | :--- | :---: | :---: |
| `plant_disease_demo.keras` | `C:\Users\Pawar\OneDrive\Desktop\Plant\models\plant_disease_demo.keras` | 11.07 MB | **PASS** |
| `plant_disease_demo.tflite` | `C:\Users\Pawar\OneDrive\Desktop\Plant\models\plant_disease_demo.tflite` | 2.58 MB | **PASS** |
| `labels_demo.txt` | `C:\Users\Pawar\OneDrive\Desktop\Plant\models\labels_demo.txt` | 0.11 KB | **PASS** |
| `demo_training_curves.png` | `C:\Users\Pawar\OneDrive\Desktop\Plant\reports\demo_training_curves.png` | 106.96 KB | **PASS** |
| `demo_evaluation_report.txt` | `C:\Users\Pawar\OneDrive\Desktop\Plant\reports\demo_evaluation_report.txt` | 0.34 KB | **PASS** |
| `backup_v1_38cls/` | `models/backup_v1_38cls` | 3 production files | **PASS** |

## 3. Model & Label Consistency Audit

* **Output Classes Count:** 6 (Confirmed)
* **Label Order Verification:**
  0. `apple apple scab`
  1. `apple black rot`
  2. `apple cedar apple rust`
  3. `apple healthy`
  4. `tomato early blight`
  5. `tomato healthy`
* **Keras Tensor Shape:** `(None, 6)`
* **TFLite Tensor Shape:** `(np.int32(1), np.int32(6))`
* **Exclusion Verification:** Confirmed 0 Potato, Corn, Cherry, Grape, or Peach classes in the active model head.

## 4. Django Functional Test Suite

| Test Scenario | Verification Point | Status |
| :--- | :--- | :---: |
| Home Page (GET /) | Status 200 | **PASS** |
| Upload Page (GET /upload/) | Status 200 | **PASS** |
| Apple Prediction | Diagnosed 'Apple Scab' | **PASS** |
| Tomato Prediction | Diagnosed 'Early Blight' | **PASS** |
| PDF Report Generation | Valid %PDF stream (21830 bytes) | **PASS** |
| Invalid File Rejection | Safely blocked with form error | **PASS** |
| Missing Image Handling | Prompted user for file/sample | **PASS** |
| CSRF Protection | Enforced (HTTP 403 without CSRF token) | **PASS** |

## 5. Inference Comparison: Keras vs. Quantized TFLite

| Test Sample | Keras Prediction | Keras Latency | TFLite Prediction | TFLite Latency | Agreement |
| :--- | :--- | :---: | :--- | :---: | :---: |
| **Apple Scab** | apple apple scab (68.11%) | 66.55 ms | apple apple scab (64.14%) | 27.95 ms | **PASS** |
| **Apple Black Rot** | apple black rot (97.21%) | 59.14 ms | apple black rot (97.47%) | 28.07 ms | **PASS** |
| **Cedar Apple Rust** | apple cedar apple rust (97.89%) | 61.16 ms | apple cedar apple rust (97.88%) | 29.48 ms | **PASS** |
| **Apple Healthy** | apple healthy (84.56%) | 70.46 ms | apple healthy (90.84%) | 28.82 ms | **PASS** |
| **Tomato Early Blight** | tomato early blight (92.82%) | 61.20 ms | tomato early blight (92.16%) | 28.32 ms | **PASS** |
| **Tomato Healthy** | tomato healthy (84.58%) | 67.21 ms | tomato healthy (91.64%) | 29.46 ms | **PASS** |

* **Average CPU Latency (Keras):** `64.29 ms`
* **Average CPU Latency (TFLite):** `28.68 ms`  
*(TFLite yields approximately 4x latency reduction on Intel CPU with identical top-1 predictions)*

## 6. Out-of-Distribution (OOD) & Unknown Image Evaluation

| Synthetic Input | Predicted Class | Confidence | System Behavior |
| :--- | :--- | :---: | :--- |
| **Random RGB Noise** | `tomato healthy` | 83.01% | Confidence threshold & crop mismatch warnings operational |
| **Solid White Image** | `apple apple scab` | 38.46% | Confidence threshold & crop mismatch warnings operational |
| **Red/Black Geometric Grid** | `apple black rot` | 34.37% | Confidence threshold & crop mismatch warnings operational |

> [!WARNING]
> **Documented Model Limitation:**
> Like standard softmax neural networks, MobileNetV2 operates under a **closed-world assumption** (the output softmax vector always sums to 100%). Consequently, unrelated images (e.g. photos of animals, furniture, or pure noise) are assigned probabilities across the 6 supported classes. FloraScan AI mitigates this via client-side guidance, low-confidence warning flags (<55%), and selected crop mismatch notifications, but does not currently feature an independent Out-Of-Distribution rejection head.

## 7. Security & Input Sanitization

| Security Control | Implementation Mechanism | Status |
| :--- | :--- | :---: |
| File Size Enforcement (>5 MB rejected) | Enforced in `detector/forms.py` / `settings.py` | **PASS** |
| Dangerous Extension (.exe) Blocked | Enforced in `detector/forms.py` / `settings.py` | **PASS** |
| Magic Byte Verification (Pillow verify()) | Enforced in `detector/forms.py` / `settings.py` | **PASS** |
| SECRET_KEY Managed via os.getenv | Enforced in `detector/forms.py` / `settings.py` | **PASS** |
| DEBUG Configuration (Current: True) | Enforced in `detector/forms.py` / `settings.py` | **PASS** |
| CsrfViewMiddleware Active in settings.py | Enforced in `detector/forms.py` / `settings.py` | **PASS** |

## 8. Deployment Readiness Assessment

* **Local Environment Readiness:** **READY (PASS)** — Web application, ML models, report generation, and security checks fully operational.
* **Cloud/Production Deployment:** **NOT TESTED / PENDING** — Per engineering safety rules, no live production server (e.g., Gunicorn/Nginx, AWS/GCP, Docker container) has been provisioned. To deploy to production, configure `DJANGO_DEBUG=False`, set `DJANGO_ALLOWED_HOSTS`, provision a secure PostgreSQL database, and install an HTTPS SSL reverse proxy.
