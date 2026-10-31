# 🌿 FloraScan AI — Apple & Tomato Foliar Disease Detection System

[![Python](https://img.shields.io/badge/Python-3.12.5-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0.14-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.21.0-FF6F00?logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An intelligent, accessible, and production-ready foliar pathology detection system designed to identify and diagnose common diseases in **Apple** and **Tomato** crops from leaf photographs. Powered by **Transfer Learning with MobileNetV2** and **TensorFlow Lite**, paired with a hardened **Django 5** web architecture and vector-grade **ReportLab** PDF pathology report generator.

---

## 📌 1. Project Overview & Problem Statement

Foliar pathogens such as Apple Scab (*Venturia inaequalis*), Black Rot (*Diplodia seriata*), Cedar Apple Rust (*Gymnosporangium*), and Tomato Early Blight (*Alternaria linariae*) cause catastrophic crop yield losses and economic damage for smallholder farmers and agricultural communities worldwide. Early diagnosis is the single most critical intervention to mitigate field-wide defoliation and fruit loss.

**FloraScan AI** delivers a fast, secure, and user-friendly web interface that allows farmers, agronomists, and researchers to:
1. Upload a photograph of an affected leaf or select from verified 1-click test samples.
2. Obtain instantaneous machine learning diagnosis with class confidence metrics and top-3 probability distributions.
3. Review detailed agronomic symptoms, causes, preventive actions, and treatment recommendations.
4. Export a comprehensive, print-ready PDF Pathology Diagnostic Report directly from the browser.

---

## ✨ 2. Key Features

* **Strict 2-Page MVT Architecture:** Zero clutter, focused user journey:
  * **Home Page (`/`)**: Overview, supported crop information cards, technology summary, and an AI estimate disclaimer.
  * **Prediction & Report Console (`/upload/`)**: Drag-and-drop file upload, verified 1-click sample gallery, live visual preview, real-time ML diagnosis, and direct PDF download.
* **Dual Inference Runtimes (Keras + TFLite):**
  * **Quantized TFLite Model (`plant_disease_demo.tflite`):** Only **$2.58\text{ MB}$** on disk, executing CPU inference in **$\approx 27\text{ ms}$** on standard multi-core processors.
  * **Keras Model (`plant_disease_demo.keras`):** Full-precision float32 model ($11.07\text{ MB}$) for validation and transfer fine-tuning.
* **Thread-Safe Singleton Model Cache:** Reuses the model interpreter in memory across concurrent web requests using Python `threading.Lock` to eliminate cold-start overhead.
* **Crop Compatibility Guard & Reliability Alerts:**
  * Checks user-selected crop against the predicted class (e.g. alerts if an Apple leaf is uploaded under Tomato selection).
  * Automatically flags low-confidence predictions ($<55\%$) advising laboratory or agronomist inspection.
* **Comprehensive Vector PDF Pathology Report (`/download-report/`):** Built with ReportLab, compiling leaf images, botanical names, severity rankings, symptoms, and prevention protocols into an official downloadable document.
* **Hardened Web Security:**
  * Strict upload limit enforced at **$5\text{ MB}$**.
  * Deep binary header validation using Pillow `Image.verify()` to reject malformed, corrupted, or non-image payloads.
  * Extension whitelist limited to `.jpg`, `.jpeg`, and `.png`.
  * Sanitized UUID-4 randomized file storage in `media/uploads/`.
  * Enforced CSRF protection, `X-Frame-Options: DENY`, and `X-Content-Type-Options: nosniff`.

---

## 📸 3. Screenshots

| Home Page (`/`) | Diagnosis Console (`/upload/`) |
|:---:|:---:|
| *(Screenshot placeholder: Home page hero and supported crops)* | *(Screenshot placeholder: Drag-drop upload with 1-click samples)* |

| On-Page Diagnosis Result | Generated PDF Pathology Report |
|:---:|:---:|
| *(Screenshot placeholder: Pathology cards, meter & treatment)* | *(Screenshot placeholder: Vector ReportLab PDF download)* |

---

## 🔬 4. Supported Disease Classes

The model classifies leaf images into **6 mutually exclusive categories**:

| # | Scientific Name | Botanical Host | Pathogen / Condition | Typical Visual Symptoms |
|---|---|:---:|---|---|
| 1 | *Venturia inaequalis* | Apple | **Apple Scab** (Fungal) | Olive-green velvety lesions on leaves, leaf distortion, fruit scabbing. |
| 2 | *Diplodia seriata* | Apple | **Black Rot** (Fungal) | Frogeye leaf spots with purple borders, limb cankers, black fruit rot. |
| 3 | *Gymnosporangium* | Apple | **Cedar Apple Rust** (Fungal) | Bright yellow-orange leaf spots with black specks and tubular aecia. |
| 4 | *Malus domestica* | Apple | **Healthy Apple Foliage** | Uniform vibrant green color, intact serrated margins, no lesions. |
| 5 | *Alternaria linariae* | Tomato | **Tomato Early Blight** (Fungal) | Dark brown spots with concentric target-board rings on lower foliage. |
| 6 | *Solanum lycopersicum* | Tomato | **Healthy Tomato Leaf** | Crisp foliage, green venation, natural trichomes, zero necrosis. |

---

## 🛠️ 5. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|:---:|---|
| **Backend Framework** | Django | 5.0.14 | Robust Model-View-Template web engine |
| **Language** | Python | 3.12.5 | Core execution runtime |
| **Deep Learning** | TensorFlow | 2.21.0 | Model construction and evaluation engine |
| **High-Level ML API** | Keras | 3.13.2 | Transfer learning head and fine-tuning |
| **Lightweight Inference** | TensorFlow Lite | Built-in | Sub-30ms CPU quantized inference |
| **Computer Vision** | Pillow (PIL) | 12.1.1 | Image loading, resizing, EXIF auto-rotation, binary checks |
| **PDF Engine** | ReportLab | 5.1.0 | Vector-grade pathology report compilation |
| **Database** | SQLite 3 | Built-in | Lightweight session management |
| **Frontend** | HTML5 / CSS3 / Vanilla JS | Modern | Responsive agricultural UI with zero heavy JS dependencies |

---

## 📁 6. Repository Structure

```text
Plant/
├── manage.py                          # Django management CLI entrypoint
├── requirements.txt                   # Pinned Python package dependencies
├── .env.example                       # Template for environment configuration
├── .gitignore                         # Comprehensive Git exclusion rules
├── README.md                          # Repository documentation
│
├── plant_disease_detection/           # Django project root configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # Environment-driven security settings
│   ├── urls.py                        # Root URL router
│   └── wsgi.py
│
├── detector/                          # Core Foliar Disease Detection app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                       # Leaf image validation & size checks
│   ├── ml_model.py                    # Singleton model cache & inference logic
│   ├── models.py
│   ├── reports.py                     # ReportLab PDF report generation
│   ├── tests.py                       # 13 automated unit & integration tests
│   ├── urls.py                        # App route definitions
│   ├── views.py                       # Web views for Home, Upload, and Download
│   ├── static/                        # Static stylesheets, JS, and sample assets
│   │   ├── css/style.css
│   │   ├── js/script.js
│   │   └── images/                    # Verified test samples (Apple & Tomato)
│   └── templates/detector/            # HTML5 MVT templates
│       ├── base.html
│       ├── home.html
│       └── upload.html
│
├── models/                            # Machine learning models & labels
│   ├── labels_demo.txt                # 6-class alphabetical label mapping
│   ├── plant_disease_demo.keras       # Full Keras MobileNetV2 demo model (11 MB)
│   ├── plant_disease_demo.tflite      # Quantized TFLite inference model (2.58 MB)
│   └── backup_v1_38cls/               # Protected backup of 38-class weights
│
├── media/                             # Runtime user uploads (git-ignored)
│   ├── samples/                       # Sample images for instant testing
│   └── uploads/                       # User upload directory (.gitkeep)
│
├── reports/                           # QA audit reports and evaluation metrics
│   ├── demo_evaluation_report.txt     # Demo training summary
│   ├── demo_training_curves.png       # Loss and accuracy curves
│   ├── final_project_audit.md         # Final comprehensive QA audit report
│   └── project_cleanup_audit.md       # File inventory and cleanup report
│
├── docs/                              # Formal Microsoft Word documentation
│   └── FloraScan_AI_Project_Documentation.docx
│
└── scripts/                           # Reproducible training & QA test scripts
    ├── run_final_qa_audit.py          # Regression & security test suite
    ├── test_integration.py            # End-to-end integration test runner
    ├── train_demo.py                  # Lightweight 3-epoch demo training script
    └── verify_apple_tomato_dataset.py # Dataset integrity checker
```

---

## 🚀 7. Installation & Local Setup (Windows)

Follow these step-by-step instructions to set up and run FloraScan AI on Windows:

### Step 1: Clone the Repository
```powershell
git clone <your-repository-url>
cd Plant
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
*(Optionally modify `.env` to set your custom `DJANGO_SECRET_KEY`)*.

### Step 5: Run Database Migrations
```powershell
python manage.py migrate
```

### Step 6: Start the Development Server
```powershell
python manage.py runserver
```

Open your browser and navigate to:
**`http://127.0.0.1:8000/`**

---

## 🧪 8. Testing & Quality Assurance

Run the automated Django unit test suite (13 passing tests):
```powershell
python manage.py test
```

Run the complete QA audit and latency benchmark:
```powershell
python scripts/run_final_qa_audit.py
```

Expected test coverage:
* Home page rendering & content validation.
* Upload interface, form handling, and crop selection.
* Single-leaf inference on all 6 Apple and Tomato classes.
* Crop mismatch detection (e.g. uploading Tomato leaf under Apple).
* 5 MB file size limit and file type whitelist validation.
* Pillow binary magic-byte integrity inspection.
* ReportLab PDF report generation and stream download.
* CSRF protection enforcement (HTTP 403 on untokened requests).

---

## 📊 9. Performance & Model Benchmarks

| Metric | Measured Value | Notes |
|---|:---:|---|
| **Demo Validation Accuracy** | **81.67%** | Evaluated on held-out validation images |
| **Demo Validation Loss** | **0.6130** | Categorical crossentropy |
| **TFLite Model Size** | **$2.58\text{ MB}$** | Tracked in Git repository |
| **Keras Model Size** | **$11.07\text{ MB}$** | Full float32 checkpoint |
| **TFLite CPU Latency** | **$27.18\text{ ms}$** | Measured on Intel Core i5-1235U CPU |
| **Keras CPU Latency** | **$59.72\text{ ms}$** | Standard TensorFlow model runtime |

---

## ⚠️ 10. Documented Technical Limitations

1. **Closed-World Softmax Assumption:** Standard CNN classifiers assign probabilities summing to $1.0$. Non-leaf inputs (e.g. random noise or unrelated images) will still be mapped to one of the 6 classes. The system mitigates this with confidence thresholds ($<55\%$) and crop mismatch warnings, but does not feature an energy-based out-of-distribution head.
2. **Demo Dataset Scale:** The demo model classification head was trained on a compact representative subset ($141$ training images across $3$ epochs) to prevent CPU resource exhaustion. While achieving $81.67\%$ validation accuracy, it is intended as a demonstration rather than a commercial field tool.
3. **Advisory Screening Only:** FloraScan AI outputs are automated estimates and must not replace certified agricultural extension agents or laboratory assays.

---

## 🔮 11. Future Roadmap

- [ ] Incorporate an energy-based Out-Of-Distribution (OOD) filter to strictly reject non-leaf imagery.
- [ ] Expand class coverage to include Corn, Potato, Grape, and Citrus diseases.
- [ ] Add multilingual interface support (Spanish, Hindi, Swahili) for smallholder farmers.
- [ ] Containerize application with Docker and deploy to cloud Kubernetes / AWS ECS.
- [ ] Build offline progressive web app (PWA) / Flutter mobile companion app.

---

## 📄 12. License & Authorship

* **Author:** FloraScan AI Project Team
* **License:** [MIT License](LICENSE)
* **Citation:** Built with reference to the open-access PlantVillage leaf pathology benchmark.
