# FloraScan AI — Complete Project Cleanup Audit

**Audit Date:** 2026-10-31  
**Project:** FloraScan AI (Apple & Tomato Foliar Disease Detection System)  
**Auditor Roles:** Senior Python Developer, Django Architect & ML Deployment Engineer  

---

## 1. Audit Classification Taxonomy

Every file and directory in the project has been inspected recursively and assigned one of seven classifications:

* **REQUIRED:** Core codebase, configuration, template, active model, or documentation essential for application operation.
* **OPTIONAL:** Helpful utility scripts, specifications, or supplemental assets that do not break the app if retained.
* **UNUSED:** Obsolete, superseded, or orphaned files eligible for safe deletion or archival.
* **DUPLICATE:** Redundant copy of an existing file (e.g. static vs media duplication).
* **GENERATED:** Output produced by test runs, training scripts, or temporary user uploads.
* **SENSITIVE:** Local credentials, secret keys, or local databases containing state.
* **NEEDS MANUAL REVIEW:** Ambiguous files requiring inspection before deletion.

---

## 2. Comprehensive File Inventory & Classification

### 2.1 Project Root Files

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `manage.py` | 701 B | **REQUIRED** | Django management CLI entrypoint. | Retain |
| `README.md` | 18 KB | **REQUIRED** | Root documentation for repository. | Update for GitHub |
| `requirements.txt` | 204 B | **REQUIRED** | Python package dependencies. | Clean & pin |
| `db.sqlite3` | 139 KB | **SENSITIVE** | Local SQLite database. | Ignore in Git |
| `data.txt` | 5.1 KB | **OPTIONAL** | Original baseline prompt specification. | Retain as reference |

---

### 2.2 Django Application — `detector/`

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `detector/__init__.py` | 0 B | **REQUIRED** | Python package marker. | Retain |
| `detector/admin.py` | 66 B | **REQUIRED** | Django admin configuration. | Retain |
| `detector/apps.py` | 154 B | **REQUIRED** | AppConfig registration. | Retain |
| `detector/forms.py` | 5.1 KB | **REQUIRED** | Form validation, MIME check, and size limit. | Retain & harden |
| `detector/ml_model.py` | 32 KB | **REQUIRED** | Model singleton, inference, and knowledge base. | Retain & harden |
| `detector/models.py` | 60 B | **REQUIRED** | Django ORM models. | Retain |
| `detector/reports.py` | 10 KB | **REQUIRED** | ReportLab PDF pathology generator. | Retain |
| `detector/tests.py` | 7.5 KB | **REQUIRED** | Automated Django test suite (13 passing tests). | Retain |
| `detector/urls.py` | 434 B | **REQUIRED** | URL routing for views and PDF download. | Retain |
| `detector/views.py` | 7.8 KB | **REQUIRED** | View logic for Home, Upload, and PDF reports. | Retain & harden |
| `detector/migrations/__init__.py` | 0 B | **REQUIRED** | Migrations package marker. | Retain |
| `detector/static/css/style.css` | 37 KB | **REQUIRED** | Complete modern responsive stylesheet. | Retain |
| `detector/static/js/script.js` | 9.2 KB | **REQUIRED** | Drag-drop, image preview, and dynamic UI logic. | Retain |
| `detector/static/images/apple_scab.jpg` | 9.6 KB | **REQUIRED** | 1-click test sample for Apple Scab. | Retain |
| `detector/static/images/apple_black_rot.jpg` | 18 KB | **REQUIRED** | 1-click test sample for Apple Black Rot. | Retain |
| `detector/static/images/apple_cedar_rust.jpg`| 10 KB | **REQUIRED** | 1-click test sample for Cedar Apple Rust. | Retain |
| `detector/static/images/apple_healthy.jpg` | 14 KB | **REQUIRED** | 1-click test sample for Healthy Apple. | Retain |
| `detector/static/images/tomato_early_blight.jpg`| 13 KB | **REQUIRED** | 1-click test sample for Tomato Early Blight. | Retain |
| `detector/static/images/tomato_healthy.jpg` | 18 KB | **REQUIRED** | 1-click test sample for Healthy Tomato. | Retain |
| `detector/static/images/potato_early_blight.jpg`| 17 KB | **UNUSED** | Legacy potato sample; unreferenced in active UI. | Safe to remove |
| `detector/static/images/potato_healthy.jpg` | 21 KB | **UNUSED** | Legacy potato sample; unreferenced in active UI. | Safe to remove |
| `detector/static/images/potato_late_blight.jpg` | 14 KB | **UNUSED** | Legacy potato sample; unreferenced in active UI. | Safe to remove |
| `detector/static/images/tomato_bacterial_spot.jpg`| 14 KB | **OPTIONAL** | Supplemental tomato asset. | Retain |
| `detector/static/images/tomato_late_blight.jpg` | 17 KB | **OPTIONAL** | Supplemental tomato asset. | Retain |
| `detector/templates/detector/base.html` | 5.8 KB | **REQUIRED** | Global base layout with nav, header, footer. | Retain |
| `detector/templates/detector/home.html` | 10 KB | **REQUIRED** | Landing page with Apple and Tomato cards. | Retain |
| `detector/templates/detector/upload.html` | 22 KB | **REQUIRED** | Upload, sample gallery, and diagnosis interface. | Retain |

---

### 2.3 Django Project Configuration — `plant_disease_detection/`

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `plant_disease_detection/__init__.py` | 0 B | **REQUIRED** | Package marker. | Retain |
| `plant_disease_detection/asgi.py` | 439 B | **REQUIRED** | ASGI application entrypoint. | Retain |
| `plant_disease_detection/wsgi.py` | 439 B | **REQUIRED** | WSGI application entrypoint. | Retain |
| `plant_disease_detection/urls.py` | 1.1 KB | **REQUIRED** | Root URL configuration. | Retain |
| `plant_disease_detection/settings.py` | 4.3 KB | **REQUIRED** | Central settings with secure environment lookups. | Retain |

---

### 2.4 Machine Learning Artifacts — `models/`

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `models/plant_disease_demo.keras` | 11.07 MB | **REQUIRED** | Active 6-class MobileNetV2 demo model. | Retain (Track in Git) |
| `models/plant_disease_demo.tflite` | 2.58 MB | **REQUIRED** | Active 6-class quantized TFLite inference model. | Retain (Track in Git) |
| `models/labels_demo.txt` | 111 B | **REQUIRED** | Active 6-class label mapping. | Retain (Track in Git) |
| `models/labels_apple_tomato.txt` | 111 B | **DUPLICATE** | Exact byte-for-byte duplicate of `labels_demo.txt`.| Safe to remove |
| `models/plant_disease_model.keras` | 12.3 MB | **OPTIONAL** | Original 38-class Keras model. | Retain in backup |
| `models/plant_disease_model.tflite`| 11.5 MB | **OPTIONAL** | Original 38-class TFLite model. | Retain in backup |
| `models/labels.txt` | 891 B | **OPTIONAL** | Original 38-class labels. | Retain in backup |
| `models/backup_v1_38cls/*` | 23.8 MB | **REQUIRED** | Dedicated protected backup of 38-class production. | Protected — NEVER DELETE |

---

### 2.5 Media Directories — `media/`

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `media/samples/apple_*.jpg` (4 files) | ~52 KB | **DUPLICATE** | Media fallback for static sample leaf images. | Retain for runtime safety |
| `media/samples/tomato_*.jpg` (4 files) | ~64 KB | **DUPLICATE** | Media fallback for static sample leaf images. | Retain for runtime safety |
| `media/samples/potato_*.jpg` (3 files) | ~52 KB | **UNUSED** | Legacy potato samples in media directory. | Safe to clean |
| `media/uploads/*.jpg` (5 files) | ~58 KB | **GENERATED** | Temporary user uploads from manual testing. | Remove before Git |

---

### 2.6 Reports & Documentation — `reports/`

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `reports/demo_evaluation_report.txt` | 344 B | **REQUIRED** | Evaluation summary for the 6-class demo model. | Retain |
| `reports/demo_training_curves.png` | 107 KB | **REQUIRED** | Loss and accuracy training curves. | Retain |
| `reports/final_project_audit.md` | 6.7 KB | **REQUIRED** | QA engineering audit matrix and test records. | Retain |
| `reports/test_noise.jpg` | 30 KB | **GENERATED** | Temporary synthetic image from OOD audit. | Safe to clean |
| `reports/test_white.jpg` | 1.4 KB | **GENERATED** | Temporary synthetic image from OOD audit. | Safe to clean |
| `reports/test_checker.jpg` | 2.1 KB | **GENERATED** | Temporary synthetic image from OOD audit. | Safe to clean |

---

### 2.7 Helper & Evaluation Scripts — `scripts/`

| File Path | Size | Classification | Purpose & Rationale | Action |
| :--- | :---: | :---: | :--- | :--- |
| `scripts/train_demo.py` | 8.8 KB | **REQUIRED** | Self-contained, lightweight 3-epoch demo training. | Retain |
| `scripts/run_final_qa_audit.py` | 26 KB | **REQUIRED** | Full regression and QA audit script. | Retain |
| `scripts/test_integration.py` | 3.4 KB | **REQUIRED** | Fast integration test suite for Apple & Tomato. | Retain |
| `scripts/verify_apple_tomato_dataset.py`| 4.1 KB | **OPTIONAL** | Dataset verification and corruption checker. | Retain |
| `scripts/inspect_dataset.py` | 3.3 KB | **OPTIONAL** | General dataset folder inspector. | Retain |
| `scripts/inspect_archive_classes.py` | 1.2 KB | **OPTIONAL** | Archive inspector utility. | Retain |
| `scripts/extract_tomato_potato.py` | 1.8 KB | **UNUSED** | Obsolete extraction script from prior potato scope. | Safe to remove |
| `scripts/train_apple_tomato.py` | 14 KB | **OPTIONAL** | Full-scale training script (kept for future GPU runs).| Retain |

---

### 2.8 Dataset Directory — `New Plant Diseases Dataset(Augmented)`

* **Classification:** **REQUIRED / DATASET** (Preserved locally, excluded from Git).
* Contains the actual training and validation leaf image classes for Apple and Tomato.
* **Strict Rule:** Must NEVER be deleted locally, but MUST be excluded in `.gitignore` to avoid repository bloat.

---

## 3. Summary of Cleanup Actions Planned for Phase 2

1. **Delete Python bytecode caches:** All `__pycache__/` directories and `*.pyc` files.
2. **Delete temporary test uploads:** Clear `media/uploads/*.jpg` (user test files).
3. **Delete synthetic audit images:** Remove `reports/test_noise.jpg`, `test_white.jpg`, and `test_checker.jpg`.
4. **Remove unreferenced legacy potato assets:** Remove `potato_*.jpg` from `detector/static/images/` and `media/samples/`.
5. **Remove duplicate labels file:** Remove `models/labels_apple_tomato.txt` (keeping the canonical `models/labels_demo.txt`).
6. **Remove obsolete script:** Remove `scripts/extract_tomato_potato.py`.
7. **Retain everything else:** Production backup, models, working Django code, templates, tests, and documentation.

