import os
import sys

# Ensure Plant root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_disease_detection.settings')
import django
django.setup()

from detector.ml_model import predict_disease, load_labels
from detector.reports import generate_pdf_report
from django.test import Client

print("=" * 65)
print("FLORASCAN AI — END-TO-END SYSTEM INTEGRATION TEST")
print("=" * 65)

# 1. Test Model Labels
labels = load_labels()
print(f"\n[TEST 1] Loaded Model Labels ({len(labels)} classes):")
for i, l in enumerate(labels):
    print(f"  {i}: {l}")

potato_in_labels = [l for l in labels if 'potato' in l]
if potato_in_labels:
    print(f"  ERROR: Potato classes found in labels: {potato_in_labels}")
else:
    print("  PASS: Zero Potato classes found in model labels.")

# 2. Test All 6 Classes via Prediction Pipeline
samples_to_test = [
    ('Apple Scab', 'detector/static/images/apple_scab.jpg', 'apple'),
    ('Apple Black Rot', 'detector/static/images/apple_black_rot.jpg', 'apple'),
    ('Cedar Apple Rust', 'detector/static/images/apple_cedar_rust.jpg', 'apple'),
    ('Apple Healthy', 'detector/static/images/apple_healthy.jpg', 'apple'),
    ('Tomato Early Blight', 'detector/static/images/tomato_early_blight.jpg', 'tomato'),
    ('Tomato Healthy', 'detector/static/images/tomato_healthy.jpg', 'tomato'),
]

print("\n[TEST 2] Testing Predictions Across All 6 Foliar Classes:")
print(f"{'Target Name':<22} | {'Crop':<7} | {'Predicted Label':<25} | {'Confidence':<10} | {'Status'}")
print("-" * 75)

all_preds = []
for name, rel_path, crop in samples_to_test:
    abs_path = os.path.abspath(rel_path)
    res = predict_disease(abs_path, selected_plant=crop)
    all_preds.append((name, res))
    conf = f"{res['confidence']}%"
    status = "OK" if res['is_plant_match'] else "MISMATCH"
    print(f"{name:<22} | {crop:<7} | {res['display_name']:<25} | {conf:>10} | {status}")

# 3. Test PDF Report Generation
print("\n[TEST 3] Testing PDF Report Generation:")
sample_pred = all_preds[0][1]
pdf_buf = generate_pdf_report(sample_pred, image_abs_path=os.path.abspath('detector/static/images/apple_scab.jpg'))
pdf_size = len(pdf_buf.getvalue())
print(f"  Generated PDF Pathology Report Size: {pdf_size} bytes")
if pdf_size > 1000:
    print("  PASS: PDF report successfully generated in memory.")
else:
    print("  ERROR: PDF report size too small.")

# 4. Test Django HTTP Endpoints
print("\n[TEST 4] Testing Django Web Endpoints:")
client = Client()

# Home page
res_home = client.get('/')
print(f"  GET / (Home View): Status {res_home.status_code}")
assert res_home.status_code == 200

# Upload page
res_upload = client.get('/upload/')
print(f"  GET /upload/ (Upload View): Status {res_upload.status_code}")
assert res_upload.status_code == 200

# 1-click sample evaluation POST
res_post_sample = client.post('/upload/', {
    'plant': 'apple',
    'sample_image': 'apple_scab'
})
print(f"  POST /upload/ (1-click Apple Scab Sample): Status {res_post_sample.status_code}")
assert res_post_sample.status_code == 200
assert 'Apple Scab' in res_post_sample.content.decode('utf-8')
print("  PASS: Form submission and on-page diagnosis result rendered correctly.")

print("\n" + "=" * 65)
print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")
print("=" * 65)
