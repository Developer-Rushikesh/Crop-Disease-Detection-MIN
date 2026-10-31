import os
import io
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from .ml_model import predict_disease, load_labels, load_model_instance
from .reports import generate_pdf_report


class PlantDiseaseDetectorTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sample_apple = os.path.join(settings.BASE_DIR, 'detector', 'static', 'images', 'apple_scab.jpg')
        self.sample_tomato = os.path.join(settings.BASE_DIR, 'detector', 'static', 'images', 'tomato_early_blight.jpg')

    def test_home_page_status_and_content(self):
        response = self.client.get(reverse('detector:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FloraScan AI')
        self.assertContains(response, 'Apple')
        self.assertContains(response, 'Tomato')
        self.assertContains(response, 'AI Estimate Disclaimer')

    def test_upload_page_status_and_content(self):
        response = self.client.get(reverse('detector:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload Leaf Photograph')
        self.assertContains(response, 'Malus domestica')
        self.assertContains(response, 'Solanum lycopersicum')

    def test_labels_loaded_correctly(self):
        labels = load_labels()
        self.assertEqual(len(labels), 6)
        self.assertTrue(any('apple' in l.lower() for l in labels))
        self.assertTrue(any('tomato' in l.lower() for l in labels))
        self.assertFalse(any('potato' in l.lower() for l in labels))

    def test_model_inference_apple_scab(self):
        if os.path.exists(self.sample_apple):
            res = predict_disease(self.sample_apple, selected_plant='apple')
            self.assertEqual(res['selected_plant'], 'Apple')
            self.assertTrue(res['is_plant_match'])
            self.assertIn('apple', res['raw_class'].lower())
            self.assertGreater(res['confidence'], 50.0)
            self.assertIn('disease_info', res)
            self.assertIn('inference_time_ms', res)

    def test_model_inference_tomato_early_blight(self):
        if os.path.exists(self.sample_tomato):
            res = predict_disease(self.sample_tomato, selected_plant='tomato')
            self.assertEqual(res['selected_plant'], 'Tomato')
            self.assertTrue(res['is_plant_match'])
            self.assertIn('tomato', res['raw_class'].lower())
            self.assertIn('disease_info', res)
            self.assertIn('top_3', res)
            self.assertLessEqual(len(res['top_3']), 3)

    def test_plant_mismatch_warning(self):
        # Selecting 'apple' but feeding tomato early blight sample
        if os.path.exists(self.sample_tomato):
            res = predict_disease(self.sample_tomato, selected_plant='apple')
            self.assertFalse(res['is_plant_match'])
            self.assertIsNotNone(res['warning_message'])
            self.assertIn('Crop Mismatch Notice', res['warning_message'])

    def test_upload_sample_post_flow(self):
        response = self.client.post(reverse('detector:upload'), {
            'plant': 'apple',
            'sample_image': 'apple_scab'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detection Result for Apple')
        self.assertContains(response, 'Prediction Confidence')
        self.assertContains(response, 'Download PDF Report')

    def test_valid_uploaded_file_flow(self):
        # Generate a small valid RGB JPEG image in memory
        img = Image.new('RGB', (100, 100), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)

        uploaded = SimpleUploadedFile('test_leaf.jpg', buf.read(), content_type='image/jpeg')
        response = self.client.post(reverse('detector:upload'), {
            'plant': 'tomato',
            'image': uploaded
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Detection Result for Tomato')
        self.assertContains(response, 'Prediction Confidence')

    def test_oversized_file_rejected(self):
        # Generate genuine valid image > 5 MB
        img = Image.new('RGB', (1600, 1600), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format='PNG', compress_level=0)
        buf.seek(0)

        uploaded = SimpleUploadedFile('large_leaf.png', buf.read(), content_type='image/png')
        response = self.client.post(reverse('detector:upload'), {
            'plant': 'tomato',
            'image': uploaded
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'File exceeds maximum allowed size')

    def test_invalid_file_format_rejected(self):
        # Text file masquerading as an image
        fake_image = SimpleUploadedFile('malicious.jpg', b'Not an image payload', content_type='image/jpeg')
        response = self.client.post(reverse('detector:upload'), {
            'plant': 'tomato',
            'image': fake_image
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload a valid image file')

    def test_pdf_report_generation_unit(self):
        dummy_data = {
            'selected_plant': 'Apple',
            'display_name': 'Apple Scab',
            'confidence': 92.5,
            'is_plant_match': True,
            'inference_time_ms': 18.4,
            'disease_info': {
                'scientific_name': 'Venturia inaequalis',
                'severity': 'Moderate',
                'is_healthy': False,
                'description': 'A common fungal leaf spot disease.',
                'symptoms': ['Velvety lesions', 'Yellowing leaves'],
                'prevention': ['Prune canopy', 'Destroy leaf litter'],
                'treatment': ['Apply captan or myclobutanil']
            },
            'top_3': [
                {'display_name': 'Apple Scab', 'raw_name': 'apple apple scab', 'confidence': 92.5},
                {'display_name': 'Black Rot', 'raw_name': 'apple black rot', 'confidence': 5.2},
                {'display_name': 'Cedar Apple Rust', 'raw_name': 'apple cedar apple rust', 'confidence': 2.3}
            ]
        }
        pdf_buf = generate_pdf_report(dummy_data, image_abs_path=self.sample_apple)
        pdf_bytes = pdf_buf.getvalue()
        self.assertTrue(len(pdf_bytes) > 1000)
        self.assertTrue(pdf_bytes.startswith(b'%PDF'))

    def test_download_report_view_with_session(self):
        # First POST a prediction to store in session
        self.client.post(reverse('detector:upload'), {
            'plant': 'apple',
            'sample_image': 'apple_scab'
        })
        # Then request the PDF download
        report_response = self.client.get(reverse('detector:download_report'))
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(report_response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename=', report_response['Content-Disposition'])
        self.assertTrue(len(report_response.content) > 1000)
        self.assertTrue(report_response.content.startswith(b'%PDF'))

    def test_download_report_view_without_session_redirects(self):
        # Empty session should redirect safely back to upload page
        response = self.client.get(reverse('detector:download_report'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('detector:upload'))
