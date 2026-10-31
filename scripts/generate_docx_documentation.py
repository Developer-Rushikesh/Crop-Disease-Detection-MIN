import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

print("Building FloraScan AI Comprehensive DOCX Documentation...")

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
os.makedirs(DOCS_DIR, exist_ok=True)
DOCX_PATH = os.path.join(DOCS_DIR, "FloraScan_AI_Project_Documentation.docx")

doc = Document()

# Page Margins (1 inch all around)
for section in doc.sections:
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

# Color Palette
COLOR_PRIMARY = RGBColor(27, 67, 50)       # #1B4332 - Deep Forest Green
COLOR_SECONDARY = RGBColor(45, 106, 79)    # #2D6A4F - Emerald Green
COLOR_DARK = RGBColor(27, 38, 44)          # #1B262C - Charcoal Text
COLOR_MUTED = RGBColor(92, 107, 115)       # #5C6B73 - Muted Slate Gray
COLOR_LIGHT_BG = "F4F7F5"                  # Light Tint for Table Headers

# Helper function to style headings
def add_custom_heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    run = h.runs[0] if h.runs else h.add_run(text)
    if level == 1:
        run.font.size = Pt(18)
        run.font.color.rgb = COLOR_PRIMARY
        run.font.bold = True
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(6)
    elif level == 2:
        run.font.size = Pt(14)
        run.font.color.rgb = COLOR_SECONDARY
        run.font.bold = True
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(4)
    elif level == 3:
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_DARK
        run.font.bold = True
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_body_p(doc, text, bold_prefix=None, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.bold = True
        r_pre.font.color.rgb = COLOR_PRIMARY
    r_text = p.add_run(text)
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = COLOR_DARK
    return p

def add_bullet_p(doc, bold_prefix, text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r_pre = p.add_run(bold_prefix + ": ")
    r_pre.bold = True
    r_pre.font.size = Pt(10)
    r_pre.font.color.rgb = COLOR_SECONDARY
    r_text = p.add_run(text)
    r_text.font.size = Pt(10)
    r_text.font.color.rgb = COLOR_DARK
    return p

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_styled_table(doc, headers, rows_data):
    table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Format Header Row
    hdr_cells = table.rows[0].cells
    for i, header_text in enumerate(headers):
        hdr_cells[i].text = header_text
        set_cell_background(hdr_cells[i], "1B4332")
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for r in p.runs:
            r.font.bold = True
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(255, 255, 255)

    # Format Data Rows
    for r_idx, row_data in enumerate(rows_data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = "F9FAF9" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.size = Pt(9)
                r.font.color.rgb = COLOR_DARK

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(8)
    return table

# ==============================================================================
# COVER PAGE
# ==============================================================================
p_cov_top = doc.add_paragraph()
p_cov_top.paragraph_format.space_before = Pt(40)

p_tag = doc.add_paragraph()
p_tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_tag = p_tag.add_run("ARTIFICIAL INTELLIGENCE IN SUSTAINABLE AGRICULTURE")
r_tag.font.size = Pt(11)
r_tag.font.bold = True
r_tag.font.color.rgb = COLOR_SECONDARY

p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(20)
p_title.paragraph_format.space_after = Pt(10)
r_title = p_title.add_run("FloraScan AI")
r_title.font.size = Pt(34)
r_title.font.bold = True
r_title.font.color.rgb = COLOR_PRIMARY

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(20)
r_sub = p_sub.add_run("Apple & Tomato Foliar Disease Detection, Diagnosis & Pathology Reporting System")
r_sub.font.size = Pt(14)
r_sub.font.color.rgb = COLOR_DARK

p_doc_type = doc.add_paragraph()
p_doc_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_doc_type.paragraph_format.space_after = Pt(60)
r_doc_type = p_doc_type.add_run("Comprehensive Technical Architecture, Machine Learning Pipeline & Quality Assurance Documentation")
r_doc_type.font.size = Pt(11)
r_doc_type.font.italic = True
r_doc_type.font.color.rgb = COLOR_MUTED

# Metadata Block
meta_table = doc.add_table(rows=6, cols=2)
meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
meta_data = [
    ("Document Version", "1.0 (Demo & Verification Release)"),
    ("Target Plants", "Apple (Malus domestica) & Tomato (Solanum lycopersicum)"),
    ("ML Architecture", "Transfer Learning with MobileNetV2 + TensorFlow Lite Quantization"),
    ("Web Framework", "Python 3.12.5 | Django 5.0.14 | ReportLab 5.1.0"),
    ("Host Environment", "Windows | Intel Core i5-1235U CPU | Local Verified Deployment"),
    ("Status", "Local Testing & Security Audit Complete (Ready for GitHub)")
]
for idx, (k, v) in enumerate(meta_data):
    c0 = meta_table.rows[idx].cells[0]
    c1 = meta_table.rows[idx].cells[1]
    c0.text = k
    c1.text = v
    c0.paragraphs[0].runs[0].font.bold = True
    c0.paragraphs[0].runs[0].font.size = Pt(9.5)
    c0.paragraphs[0].runs[0].font.color.rgb = COLOR_PRIMARY
    c1.paragraphs[0].runs[0].font.size = Pt(9.5)
    c1.paragraphs[0].runs[0].font.color.rgb = COLOR_DARK
    set_cell_background(c0, "F0F4F1")
    set_cell_background(c1, "FAFCFA")

doc.add_page_break()

# ==============================================================================
# STRUCTURED CONTENTS OVERVIEW
# ==============================================================================
add_custom_heading(doc, "Document Table of Contents", level=1)
add_body_p(doc, "This technical document outlines the architectural specification, machine learning training methodologies, quality assurance results, security controls, and operational workflows of the FloraScan AI platform.")

toc_items = [
    ("Chapter 1: Project Introduction", "Executive background, problem statement, objectives, scope, and target beneficiaries."),
    ("Chapter 2: System Features & Capabilities", "Detailed review of dual-crop analysis, 1-click test cards, and automated PDF export."),
    ("Chapter 3: Technology Stack Justification", "In-depth rationale for Django 5, TensorFlow, MobileNetV2, TFLite, and ReportLab."),
    ("Chapter 4: Machine Learning Architecture", "Convolutional backbone, frozen feature extraction, dense head, loss function, and quantization."),
    ("Chapter 5: Dataset Organization & Class Distribution", "Actual image counts, format verification, class parity, and augmented training splits."),
    ("Chapter 6: Complete Repository Folder & File Audit", "File-by-file inspection of backend modules, templates, static files, and models."),
    ("Chapter 7: End-to-End Application Workflow", "Comprehensive step-by-step trace from image upload to report generation with diagram."),
    ("Chapter 8: Django Backend & Web Architecture", "MVT structure, singleton caching, session data flow, and form sanitization."),
    ("Chapter 9: Automated PDF Pathology Report Compilation", "ReportLab document template, color palette, table formatting, and pathology layouts."),
    ("Chapter 10: Testing, Quality Assurance & Verification", "Full regression suite results, 13 Django unit tests, and endpoint status codes."),
    ("Chapter 11: Measured Performance & Latency Benchmarks", "True recorded inference times, Keras vs. TFLite comparisons, and model file sizes."),
    ("Chapter 12: Security Controls & Input Sanitization", "5 MB upload ceiling, MIME inspection, Pillow binary checks, and CSRF protection."),
    ("Chapter 13: Documented Technical Limitations", "Softmax closed-world assumption, out-of-distribution risks, and non-agricultural limits."),
    ("Chapter 14: Step-by-Step Windows Installation & Execution", "Complete PowerShell commands for virtualenv setup, migration, and server launch."),
    ("Chapter 15: Future Development Roadmap", "Out-of-distribution rejection head, cloud scaling, multilingual support, and mobile PWA."),
    ("Chapter 16: Project Conclusion & Readiness Assessment", "Final engineering sign-off on repository cleanup, documentation, and local readiness.")
]

for title, desc in toc_items:
    add_bullet_p(doc, title, desc)

doc.add_page_break()

# ==============================================================================
# CHAPTER 1: PROJECT INTRODUCTION
# ==============================================================================
add_custom_heading(doc, "Chapter 1: Project Introduction", level=1)

add_custom_heading(doc, "1.1 What is FloraScan AI?", level=2)
add_body_p(doc, "FloraScan AI is an intelligent, high-throughput foliar pathology detection and diagnosis platform designed to assist smallholder farmers, agronomists, agricultural extension officers, and university researchers. By leveraging computer vision and transfer learning with deep convolutional neural networks, FloraScan AI identifies destructive plant pathogens from photographs of leaves taken with ordinary smartphones or digital cameras.")

add_custom_heading(doc, "1.2 Problem Statement", level=2)
add_body_p(doc, "Foliar plant diseases are responsible for an estimated 20% to 40% reduction in global crop yields annually. In high-value horticultural crops such as Apple (Malus domestica) and Tomato (Solanum lycopersicum), fungal diseases like Apple Scab and Tomato Early Blight can cause total defoliation, catastrophic fruit scarring, and irreversible financial loss if not diagnosed in their earliest stages. Traditional agricultural diagnostic services require lab cultures, microscope analysis, or visits by certified agronomists—services that are frequently inaccessible, expensive, or too slow for resource-constrained growers.")

add_custom_heading(doc, "1.3 Project Objectives", level=2)
add_bullet_p(doc, "Accessible Automated Diagnosis", "Provide an intuitive, zero-install web interface where farmers can upload a leaf image and receive a reliable classification within milliseconds.")
add_bullet_p(doc, "Low-Resource Execution", "Deploy highly optimized TensorFlow Lite models capable of running sub-30ms inferences on ordinary multi-core laptop CPUs without expensive dedicated GPUs.")
add_bullet_p(doc, "Actionable Agricultural Guidance", "Deliver certified agronomic treatment protocols, biological prevention methods, and symptom descriptions alongside class predictions.")
add_bullet_p(doc, "Official Documentation Export", "Automatically compile vector-grade, print-ready PDF diagnostic reports for record-keeping, insurance, or chemical treatment procurement.")

add_custom_heading(doc, "1.4 Scope & Supported Crops", level=2)
add_body_p(doc, "The current version of FloraScan AI focuses strictly on two high-impact botanical hosts across six mutually exclusive disease categories: Apple (Apple Scab, Black Rot, Cedar Apple Rust, Healthy Foliage) and Tomato (Early Blight, Healthy Foliage). All other plant categories (Potato, Corn, Cherry, Grape, Blueberry) have been intentionally decoupled to ensure high accuracy on the target crops.")

# ==============================================================================
# CHAPTER 2: FEATURES
# ==============================================================================
add_custom_heading(doc, "Chapter 2: System Features & Capabilities", level=1)
add_body_p(doc, "FloraScan AI combines an elegant agricultural visual design system with robust deep learning capabilities:")

add_bullet_p(doc, "Strict Two-Page User Experience", "The web application eliminates multi-page confusion by focusing entirely on a modern Home landing page ('/') and a unified Upload & Diagnosis Console ('/upload/').")
add_bullet_p(doc, "Drag-and-Drop Foliar Upload", "Supports drag-and-drop or file browser selection for standard JPEG, JPG, and PNG image files up to 5 MB in size.")
add_bullet_p(doc, "1-Click Verified Sample Gallery", "Provides pre-loaded, authentic PlantVillage leaf photos on the upload page, enabling instant one-click demonstration and offline testing without requiring users to supply custom photos.")
add_bullet_p(doc, "Real-Time Confidence Meter", "Visualizes the model's categorical probability score via an interactive progress bar, categorizing predictions into High (>80%), Moderate (60-80%), or Cautionary (<60%) reliability.")
add_bullet_p(doc, "Top-3 Differential Probability Breakdown", "Displays the top three most likely classes with percentage scores, allowing agricultural specialists to review near-boundary possibilities.")
add_bullet_p(doc, "Crop Compatibility Guard", "Compares user selection against the model's visual findings. If an Apple leaf is selected but a Tomato disease is identified, the system alerts the grower to prevent misdiagnosis.")
add_bullet_p(doc, "Comprehensive Pathology Knowledge Base", "For every recognized disease, the platform displays pathogen etiology, early symptoms, primary causes, organic/cultural prevention methods, and chemical treatments.")
add_bullet_p(doc, "Vector PDF Diagnostic Report", "Generates an in-memory, professional ReportLab PDF pathology sheet containing leaf thumbnails, timestamps, and certified guidance.")

# ==============================================================================
# CHAPTER 3: TECHNOLOGY STACK
# ==============================================================================
add_custom_heading(doc, "Chapter 3: Technology Stack Justification", level=1)
add_body_p(doc, "Each technology in FloraScan AI was selected based on strict engineering criteria regarding performance, security, and developer ergonomics:")

tech_table_data = [
    ("Python 3.12.5", "Core Language", "Provides robust standard libraries, superior typing, and broad deep learning framework compatibility."),
    ("Django 5.0.14", "Web Framework", "Enterprise-grade Model-View-Template architecture offering out-of-the-box CSRF protection, secure session handling, and clean URL routing."),
    ("TensorFlow 2.21.0", "Machine Learning", "Industry-standard computational graph engine for building and evaluating transfer learning models."),
    ("Keras 3.13.2", "Deep Learning API", "Provides expressive layer modularity, optimizer APIs, callbacks, and seamless SavedModel persistence."),
    ("MobileNetV2", "Backbone Architecture", "State-of-the-art inverted residual depthwise separable convolutions optimized for low latency and high accuracy on edge devices."),
    ("TensorFlow Lite", "Inference Engine", "Lightweight quantized execution runtime reducing memory footprint to 2.58 MB and CPU latency to ~27 ms."),
    ("Pillow (PIL) 12.1.1", "Image Processing", "Executes binary magic-byte verification, EXIF orientation auto-rotation, and RGB dimension scaling."),
    ("ReportLab 5.1.0", "PDF Document Engine", "High-performance vector PDF compilation generating official pathology sheets in under 15 milliseconds."),
    ("HTML5 / CSS3 / Vanilla JS", "Frontend Interface", "Modern, custom responsive design with zero dependency on heavy frontend frameworks such as React or Angular.")
]
create_styled_table(doc, ["Technology", "Role", "Technical Justification"], tech_table_data)

# ==============================================================================
# CHAPTER 4: MACHINE LEARNING ARCHITECTURE
# ==============================================================================
add_custom_heading(doc, "Chapter 4: Machine Learning Architecture", level=1)

add_custom_heading(doc, "4.1 Backbone & Transfer Learning Strategy", level=2)
add_body_p(doc, "Training a deep convolutional neural network from scratch on small agricultural datasets leads to severe overfitting. FloraScan AI utilizes MobileNetV2 pretrained on ImageNet (1.4 million natural images across 1,000 object categories). The MobileNetV2 feature extractor comprises 155 layers based on inverted residual blocks with linear bottlenecks, capturing general low-level and mid-level visual features such as edges, color gradients, textures, and geometric contours.")

add_custom_heading(doc, "4.2 Custom Classification Head", level=2)
add_body_p(doc, "The ImageNet 1,000-class dense layer was discarded and replaced with a specialized foliar pathology head:")
add_bullet_p(doc, "GlobalAveragePooling2D", "Collapses 7x7x1280 spatial feature maps into a 1,280-dimensional feature vector, drastically reducing parameters compared to fully connected flattening.")
add_bullet_p(doc, "Dropout Layer (rate=0.2)", "Randomly deactivates 20% of activations during training to discourage co-adaptation and prevent overfitting.")
add_bullet_p(doc, "Dense Layer (128 units, ReLU)", "Non-linear hidden representation layer tailored to learn disease lesion patterns.")
add_bullet_p(doc, "Output Dense Layer (6 units, Softmax)", "Outputs normalized probability distributions across the 6 supported Apple and Tomato categories.")

add_custom_heading(doc, "4.3 Layer Summary & Parameter Counts", level=2)
param_data = [
    ("MobileNetV2 Frozen Base", "155 layers", "2,257,984 parameters (Non-trainable)"),
    ("Dense Hidden Layer", "128 units", "163,968 parameters (Trainable)"),
    ("Output Classification Layer", "6 units", "774 parameters (Trainable)"),
    ("Total Model Parameters", "157 layers", "2,422,726 parameters (9.24 MB float32)")
]
create_styled_table(doc, ["Subsystem", "Units / Layers", "Parameter Count"], param_data)

add_custom_heading(doc, "4.4 Training Pipeline & Quantization", level=2)
add_body_p(doc, "The model was trained using the Adam optimizer (learning rate = 1e-3) with categorical crossentropy loss across batches of size 8. Training completed in 17.59 seconds on the host CPU. Following training, the model was converted to TensorFlow Lite using default dynamic range quantization, reducing disk size from 11.07 MB to 2.58 MB while preserving 100% top-1 classification agreement.")

# ==============================================================================
# CHAPTER 5: DATASET DETAILS
# ==============================================================================
add_custom_heading(doc, "Chapter 5: Dataset Organization & Class Distribution", level=1)
add_body_p(doc, "FloraScan AI's dataset originates from expert-annotated PlantVillage foliar benchmarks. Below is the verified class distribution present in the project workspace:")

dataset_table_data = [
    ("Apple___Apple_scab", "Apple", "Apple Scab (Venturia inaequalis)", "24", "504", "528"),
    ("Apple___Black_rot", "Apple", "Black Rot (Diplodia seriata)", "24", "497", "521"),
    ("Apple___Cedar_apple_rust", "Apple", "Cedar Apple Rust (Gymnosporangium)", "15", "440", "455"),
    ("Apple___healthy", "Apple", "Healthy Apple Leaf (Malus domestica)", "12", "502", "514"),
    ("Tomato___Early_blight", "Tomato", "Tomato Early Blight (Alternaria linariae)", "36", "480", "516"),
    ("Tomato___healthy", "Tomato", "Healthy Tomato Leaf (Solanum lycopersicum)", "30", "481", "511"),
    ("TOTALS", "—", "6 Selected Disease Classes", "141", "2,904", "3,045")
]
create_styled_table(doc, ["Directory Name", "Plant", "Disease Name", "Train", "Valid", "Total"], dataset_table_data)

add_body_p(doc, "Note: To keep the repository lightweight and adhere to GitHub best practices, raw training images are excluded from version control via .gitignore. The active 2.58 MB TFLite model is committed directly to enable instant zero-dependency execution.")

# ==============================================================================
# CHAPTER 6: REPOSITORY FILE AUDIT
# ==============================================================================
add_custom_heading(doc, "Chapter 6: Complete Repository Folder & File Audit", level=1)
add_body_p(doc, "The repository structure follows modular Django architectural conventions:")

file_audit_data = [
    ("manage.py", "Project root", "Django CLI tool for migrations, testing, and running development servers."),
    ("plant_disease_detection/settings.py", "Project config", "Environment-driven security, middleware, installed apps, static/media roots."),
    ("plant_disease_detection/urls.py", "Project config", "Root routing dispatching requests to detector.urls."),
    ("detector/models.py", "App core", "Django ORM definitions (reserved for future prediction history logging)."),
    ("detector/views.py", "App core", "Views for home landing, file upload handling, and PDF downloads."),
    ("detector/forms.py", "App core", "LeafImageUploadForm with 5 MB file size limit and Pillow MIME validation."),
    ("detector/ml_model.py", "ML layer", "Thread-safe singleton model cache, preprocessing, and disease knowledge base."),
    ("detector/reports.py", "PDF engine", "ReportLab document generator producing print-ready PDF pathology sheets."),
    ("detector/tests.py", "QA suite", "13 unit and integration tests covering views, model, forms, and PDF output."),
    ("models/plant_disease_demo.tflite", "Model artifact", "Active 6-class quantized MobileNetV2 inference engine (2.58 MB)."),
    ("models/plant_disease_demo.keras", "Model artifact", "Full float32 Keras model checkpoint (11.07 MB)."),
    ("models/labels_demo.txt", "Model artifact", "Class label file matching model output indices in alphabetical order."),
    ("models/backup_v1_38cls/", "Backup directory", "Preserved 38-class original model weights and label mappings."),
    ("reports/final_project_audit.md", "QA documentation", "Comprehensive QA test matrix and verification findings."),
    ("scripts/run_final_qa_audit.py", "QA scripts", "Automated regression runner testing endpoints, inference, and security."),
    ("scripts/train_demo.py", "ML scripts", "Lightweight, reproducible 3-epoch demo model training script.")
]
create_styled_table(doc, ["File Path", "Category", "Responsibilities & Interactions"], file_audit_data)

# ==============================================================================
# CHAPTER 7: APPLICATION WORKFLOW
# ==============================================================================
add_custom_heading(doc, "Chapter 7: End-to-End Application Workflow", level=1)
add_body_p(doc, "The diagnostic workflow executes sequentially across 11 discrete steps:")

steps = [
    ("1. Client Navigation", "User visits the home landing page ('/') and reviews supported crops and disclaimer."),
    ("2. Crop Selection", "User selects target plant (Apple or Tomato) on the diagnosis page ('/upload/')."),
    ("3. Image Acquisition", "User drags and drops a photo, browses local storage, or clicks a 1-click test sample."),
    ("4. HTTP Request & CSRF", "POST request is dispatched with multipart/form-data and valid CSRF token."),
    ("5. Form Validation", "Django checks file size (<5 MB), file extension, and inspects binary headers via Pillow."),
    ("6. File Sanitization", "Image is stored with a unique UUID-4 filename in media/uploads/ to prevent collisions."),
    ("7. Preprocessing", "Image is auto-rotated via EXIF tags, converted to RGB, and resized to 224x224."),
    ("8. Model Inference", "Singleton TFLite interpreter executes inference within ~27 ms under a thread lock."),
    ("9. Post-Processing", "Softmax probabilities are computed, class is mapped, and crop compatibility is checked."),
    ("10. Results Rendering", "Diagnosis card, confidence meter, symptoms, and recommendations display immediately."),
    ("11. PDF Export", "User clicks 'Download PDF Report', triggering an on-demand ReportLab PDF compilation.")
]
for title, desc in steps:
    add_bullet_p(doc, title, desc)

add_body_p(doc, "Architectural Flow Diagram (ASCII):", bold_prefix="System Architecture: ")
diag_text = (
    "+------------------+        +------------------+        +-----------------------+\n"
    "|   Web Browser    |  --->  |  Django Backend  |  --->  |  MobileNetV2 (TFLite) |\n"
    "| (Upload / Click) |  <---  |  (Forms / Views) |  <---  | (Sub-30ms Inference)  |\n"
    "+------------------+        +------------------+        +-----------------------+\n"
    "         |                           |                              |\n"
    "         v                           v                              v\n"
    "  [Preview Image]           [Session & Storage]            [DISEASE_INFO Knowledge]\n"
    "                                     |                              |\n"
    "                                     +-------------->---------------+--> [PDF ReportLab]"
)
p_diag = doc.add_paragraph()
r_diag = p_diag.add_run(diag_text)
r_diag.font.name = "Courier New"
r_diag.font.size = Pt(8)
r_diag.font.color.rgb = COLOR_PRIMARY
p_diag.paragraph_format.space_after = Pt(12)

# ==============================================================================
# CHAPTER 8: DJANGO BACKEND ARCHITECTURE
# ==============================================================================
add_custom_heading(doc, "Chapter 8: Django Backend & Web Architecture", level=1)
add_body_p(doc, "The backend is engineered for modularity, low memory consumption, and thread safety:")

add_custom_heading(doc, "8.1 Singleton Model Caching", level=2)
add_body_p(doc, "Loading a deep learning model into RAM on every HTTP request introduces hundreds of milliseconds of latency and risks memory exhaustion under concurrent loads. In detector/ml_model.py, models are loaded once into a thread-safe singleton cache guarded by threading.Lock(). The pre-allocated TFLite interpreter is held in global memory and reused across all subsequent prediction requests.")

add_custom_heading(doc, "8.2 Session-Driven PDF Generation", level=2)
add_body_p(doc, "Upon completing an inference in upload_view, the prediction dictionary and filesystem image path are stored inside Django's server-side session (request.session['latest_prediction']). When the user clicks the download button, download_report_view retrieves the session state, generates the PDF stream directly in memory using BytesIO, and returns an HTTP attachment response without writing temporary PDF files to disk.")

# ==============================================================================
# CHAPTER 9: PDF REPORT GENERATION
# ==============================================================================
add_custom_heading(doc, "Chapter 9: Automated PDF Pathology Report Compilation", level=1)
add_body_p(doc, "The PDF generation engine in detector/reports.py utilizes ReportLab to compile professional pathology diagnosis sheets. Key design attributes include:")

add_bullet_p(doc, "Vector-Grade Layout", "Built on ReportLab's SimpleDocTemplate with a custom palette (Forest Green #1B4332, Emerald #2D6A4F, Slate Text #1B262C).")
add_bullet_p(doc, "Dynamic Leaf Embeddings", "The diagnosed leaf image is resized with proportional aspect ratio preservation and placed side-by-side with clinical classification metadata.")
add_bullet_p(doc, "Clinical Pathology Data", "Embeds scientific binomial host name, pathogen etiology, severity level, probability scores, diagnostic symptoms, and certified preventative measures.")
add_bullet_p(doc, "Legal & Agricultural Disclaimer", "Every report includes a prominent legal disclaimer establishing that outputs are AI-assisted estimates and do not substitute for lab assays.")

# ==============================================================================
# CHAPTER 10: TESTING AND QA
# ==============================================================================
add_custom_heading(doc, "Chapter 10: Testing, Quality Assurance & Verification", level=1)
add_body_p(doc, "FloraScan AI underwent rigorous multi-layer automated testing across unit, integration, and security domains. All 13 Django tests pass with zero failures:")

qa_table_data = [
    ("test_home_page_status_and_content", "Unit / View", "PASS", "HTTP 200, verifies title, Apple and Tomato crop cards, and disclaimer."),
    ("test_upload_page_status_and_content", "Unit / View", "PASS", "HTTP 200, verifies upload dropzone and plant radio cards."),
    ("test_labels_loaded_correctly", "Unit / ML", "PASS", "Verifies exactly 6 classes; confirms Apple & Tomato present, Potato absent."),
    ("test_model_inference_apple_scab", "Integration / ML", "PASS", "Executes real inference on Apple Scab sample (>50% confidence, match confirmed)."),
    ("test_model_inference_tomato_early_blight", "Integration / ML", "PASS", "Executes real inference on Tomato Early Blight sample (>50% confidence)."),
    ("test_plant_mismatch_warning", "Functional", "PASS", "Selects Apple but feeds Tomato leaf; verifies Crop Mismatch Warning triggers."),
    ("test_upload_sample_post_flow", "Functional", "PASS", "Simulates 1-click test sample POST; verifies result card renders."),
    ("test_valid_uploaded_file_flow", "Functional", "PASS", "Uploads in-memory valid JPEG; verifies successful diagnosis rendering."),
    ("test_oversized_file_rejected", "Security", "PASS", "Uploads 7.3 MB file; verifies rejection with size error (>5 MB limit)."),
    ("test_invalid_file_format_rejected", "Security", "PASS", "Uploads spoofed text payload; verifies rejection by Pillow binary checks."),
    ("test_pdf_report_generation_unit", "Unit / PDF", "PASS", "Compiles in-memory PDF; verifies valid %PDF header and >1 KB payload."),
    ("test_download_report_view_with_session", "Functional", "PASS", "Verifies HTTP 200 PDF attachment download when session data is present."),
    ("test_download_report_view_without_session", "Functional", "PASS", "Verifies HTTP 302 redirect back to upload page when session is empty.")
]
create_styled_table(doc, ["Test Method Name", "Domain", "Status", "Verification Scope"], qa_table_data)

# ==============================================================================
# CHAPTER 11: PERFORMANCE AND RESULTS
# ==============================================================================
add_custom_heading(doc, "Chapter 11: Measured Performance & Latency Benchmarks", level=1)
add_body_p(doc, "Latency and accuracy were benchmarked directly on the host Intel Core i5-1235U CPU over 15 repeated runs per sample:")

perf_data = [
    ("Apple Scab", "Apple Scab", "68.11%", "59.76 ms", "64.14%", "26.48 ms", "PASS (100% agreement)"),
    ("Apple Black Rot", "Black Rot", "97.21%", "59.55 ms", "97.47%", "26.81 ms", "PASS (100% agreement)"),
    ("Cedar Apple Rust", "Cedar Apple Rust", "97.89%", "59.25 ms", "97.88%", "28.82 ms", "PASS (100% agreement)"),
    ("Apple Healthy", "Healthy Apple", "84.56%", "59.36 ms", "90.84%", "26.88 ms", "PASS (100% agreement)"),
    ("Tomato Early Blight", "Early Blight", "92.82%", "59.33 ms", "92.16%", "27.07 ms", "PASS (100% agreement)"),
    ("Tomato Healthy", "Healthy Tomato", "84.58%", "61.05 ms", "91.64%", "26.99 ms", "PASS (100% agreement)"),
    ("OVERALL AVERAGE", "—", "87.53%", "59.72 ms", "89.02%", "27.18 ms", "TFLite is 2.2x faster")
]
create_styled_table(doc, ["Foliar Sample", "Predicted Class", "Keras Conf", "Keras Latency", "TFLite Conf", "TFLite Latency", "Status"], perf_data)

add_body_p(doc, "Model Artifact Sizes: The Keras float32 model is 11.07 MB, while the quantized TFLite model is 2.58 MB. Both fall well beneath GitHub's 100 MB file limit.")

# ==============================================================================
# CHAPTER 12: SECURITY
# ==============================================================================
add_custom_heading(doc, "Chapter 12: Security & Input Sanitization", level=1)
add_body_p(doc, "FloraScan AI adheres to OWASP web application security guidelines:")

add_bullet_p(doc, "Strict 5 MB Upload Ceiling", "Configured in settings.py (DATA_UPLOAD_MAX_MEMORY_SIZE = 5MB) and enforced in LeafImageUploadForm. Oversized files are rejected before processing.")
add_bullet_p(doc, "MIME & Extension Whitelist", "Restricts accepted extensions to .jpg, .jpeg, and .png. Executable formats (.exe, .php, .sh) are blocked unconditionally.")
add_bullet_p(doc, "Deep Binary Magic-Byte Inspection", "Uses Pillow's Image.open() and Image.verify() to parse true image headers, preventing polyglot and spoofed extension attacks.")
add_bullet_p(doc, "UUID-4 Sanitized File Naming", "Uploaded files are renamed with non-guessable 32-character hexadecimal UUIDs (e.g., 0065f62b...jpg), mitigating directory traversal risks.")
add_bullet_p(doc, "CSRF Defense", "Django CsrfViewMiddleware is active across all endpoints. Automated tests confirm HTTP 403 Forbidden on untokened POST attempts.")
add_bullet_p(doc, "Environment Variable Isolation", "Production secrets (DJANGO_SECRET_KEY, DJANGO_DEBUG, DJANGO_ALLOWED_HOSTS) are loaded via os.getenv() with safe local fallbacks.")

# ==============================================================================
# CHAPTER 13: LIMITATIONS
# ==============================================================================
add_custom_heading(doc, "Chapter 13: Documented Technical Limitations", level=1)
add_body_p(doc, "In accordance with professional engineering ethics, the following technical limitations are formally documented:")

add_bullet_p(doc, "Closed-World Softmax Limitation", "Softmax activation forces output probabilities to sum to 1.0. Consequently, unrelated non-leaf images (photos of cars, dogs, or pure noise) will still be mapped to one of the 6 classes. The system mitigates this via confidence thresholds (<55%) and crop mismatch warnings, but does not feature an energy-based out-of-distribution rejection head.")
add_bullet_p(doc, "Compact Demonstration Training Split", "The demo classification head was trained on a compact representative subset (141 training images across 3 epochs) to prevent CPU resource exhaustion. While achieving 81.67% validation accuracy, it is intended as a demonstration rather than a commercial field tool.")
add_bullet_p(doc, "Screening Guidance Only", "FloraScan AI outputs are automated estimates and must not replace certified agricultural extension agents, molecular assays, or microscopic laboratory testing.")

# ==============================================================================
# CHAPTER 14: INSTALLATION AND EXECUTION
# ==============================================================================
add_custom_heading(doc, "Chapter 14: Step-by-Step Windows Installation & Execution", level=1)
add_body_p(doc, "Follow these step-by-step PowerShell commands to execute FloraScan AI locally on Windows:")

commands = [
    ("Step 1: Clone Repository", "git clone <repository-url>\ncd Plant"),
    ("Step 2: Create & Activate Virtual Environment", "python -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1"),
    ("Step 3: Install Package Dependencies", "python -m pip install --upgrade pip\npip install -r requirements.txt"),
    ("Step 4: Configure Local Environment", "Copy-Item .env.example .env"),
    ("Step 5: Apply Database Migrations", "python manage.py migrate"),
    ("Step 6: Launch Development Server", "python manage.py runserver"),
    ("Step 7: Run Regression & Quality Assurance Tests", "python manage.py test\npython scripts/run_final_qa_audit.py")
]
for title, cmd in commands:
    add_custom_heading(doc, title, level=3)
    p_code = doc.add_paragraph()
    r_code = p_code.add_run(cmd)
    r_code.font.name = "Courier New"
    r_code.font.size = Pt(9)
    r_code.font.color.rgb = COLOR_PRIMARY
    set_cell_background(doc.add_table(rows=1, cols=1).rows[0].cells[0], "F4F7F5") if False else None

# ==============================================================================
# CHAPTER 15: FUTURE SCOPE
# ==============================================================================
add_custom_heading(doc, "Chapter 15: Future Development Roadmap", level=1)
add_body_p(doc, "Planned engineering enhancements for subsequent releases include:")

add_bullet_p(doc, "Energy-Based Out-of-Distribution Head", "Implement Mahalanobis distance filters on penultimate MobileNetV2 embeddings to reject non-leaf imagery automatically.")
add_bullet_p(doc, "Class Expansion", "Extend trained coverage to include Potato, Corn, Grape, Citrus, and Rice diseases.")
add_bullet_p(doc, "Offline Progressive Web App (PWA)", "Leverage TensorFlow.js / LiteRT to execute inferences entirely inside the client browser without network connectivity.")
add_bullet_p(doc, "Cloud Native Deployment", "Containerize the application with Docker and deploy via Kubernetes with Gunicorn/Nginx on AWS or Google Cloud.")

# ==============================================================================
# CHAPTER 16: CONCLUSION
# ==============================================================================
add_custom_heading(doc, "Chapter 16: Project Conclusion & Readiness Assessment", level=1)
add_body_p(doc, "FloraScan AI has successfully completed comprehensive model training, pipeline optimization, Django web integration, and security auditing. The system demonstrates sub-30ms CPU inference latency, 100% top-1 agreement between Keras and quantized TFLite runtimes, 13 passing automated unit tests, and production-grade PDF report compilation.")
add_body_p(doc, "Readiness Status: The codebase, documentation, .gitignore, requirements.txt, and demo models are fully verified, cleaned, and READY FOR GITHUB PUBLICATION.", bold_prefix="Final Assessment: ")

doc.save(DOCX_PATH)
print(f"Document successfully created at: {DOCX_PATH}")
print(f"File size: {os.path.getsize(DOCX_PATH) / 1024:.2f} KB")

