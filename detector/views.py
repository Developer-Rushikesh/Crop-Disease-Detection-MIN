import os
import uuid
import logging
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import LeafImageUploadForm
from .ml_model import predict_disease
from .reports import generate_pdf_report

logger = logging.getLogger(__name__)

# Verified test samples for instant 1-click evaluation
SAMPLE_IMAGES = [
    {
        'id': 'apple_scab',
        'plant': 'apple',
        'label': 'Apple Scab',
        'filename': 'apple_scab.jpg',
        'badge': 'Fungal',
        'badge_class': 'badge-warning',
    },
    {
        'id': 'apple_black_rot',
        'plant': 'apple',
        'label': 'Apple Black Rot',
        'filename': 'apple_black_rot.jpg',
        'badge': 'Severe',
        'badge_class': 'badge-danger',
    },
    {
        'id': 'apple_cedar_rust',
        'plant': 'apple',
        'label': 'Cedar Apple Rust',
        'filename': 'apple_cedar_rust.jpg',
        'badge': 'Fungal',
        'badge_class': 'badge-warning',
    },
    {
        'id': 'apple_healthy',
        'plant': 'apple',
        'label': 'Apple Healthy',
        'filename': 'apple_healthy.jpg',
        'badge': 'Healthy',
        'badge_class': 'badge-success',
    },
    {
        'id': 'tomato_early_blight',
        'plant': 'tomato',
        'label': 'Tomato Early Blight',
        'filename': 'tomato_early_blight.jpg',
        'badge': 'Diseased',
        'badge_class': 'badge-warning',
    },
    {
        'id': 'tomato_healthy',
        'plant': 'tomato',
        'label': 'Tomato Healthy',
        'filename': 'tomato_healthy.jpg',
        'badge': 'Healthy',
        'badge_class': 'badge-success',
    },
]


def home_view(request):
    """
    Page 1: FloraScan AI Home Page
    Clean, agriculture-themed landing page with crop cards,
    3-step workflow, technology stack, and an explicit AI estimate disclaimer.
    """
    context = {
        'page_title': 'FloraScan AI | Plant Disease Detection',
        'supported_plants': [
            {
                'name': 'Apple',
                'slug': 'apple',
                'scientific_name': 'Malus domestica',
                'description': 'Apple orchards are vulnerable to Scab, Black Rot (Frogeye leaf spot), and Cedar Apple Rust. Early detection prevents foliar loss and fruit scarring.',
                'diseases': ['Apple Scab', 'Black Rot', 'Cedar Apple Rust', 'Healthy Leaf'],
                'image': 'images/apple_healthy.jpg',
            },
            {
                'name': 'Tomato',
                'slug': 'tomato',
                'scientific_name': 'Solanum lycopersicum',
                'description': 'Tomato crops are vulnerable to Early Blight and destructive fungal pathogens. Early detection saves up to 80% of crop yield.',
                'diseases': ['Early Blight', 'Healthy Leaf'],
                'image': 'images/tomato_healthy.jpg',
            }
        ]
    }
    return render(request, 'detector/home.html', context)


def upload_view(request):
    """
    Page 2: Disease Prediction and Report Generation
    Single combined interface for:
    - Crop selection (Apple or Tomato)
    - Drag-and-drop / browse image upload (JPEG/PNG up to 5 MB)
    - 1-click test sample leaves
    - Model prediction execution
    - Direct on-page diagnosis result display with PDF report download button.
    """
    initial_plant = request.GET.get('plant', 'apple').lower()
    if initial_plant not in ['apple', 'tomato']:
        initial_plant = 'apple'

    prediction_data = None

    if request.method == 'POST':
        form = LeafImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            selected_plant = form.cleaned_data['plant']
            uploaded_file = form.cleaned_data.get('image')
            sample_name = form.cleaned_data.get('sample_image')

            image_abs_path = None
            image_url = None

            try:
                # 1. Handle uploaded custom file safely
                if uploaded_file:
                    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                    if file_ext not in ('.jpg', '.jpeg', '.png'):
                        file_ext = '.jpg'

                    # Generate non-guessable, sanitized filename
                    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
                    save_relative_path = os.path.join('uploads', unique_filename)
                    saved_path = default_storage.save(
                        save_relative_path,
                        ContentFile(uploaded_file.read())
                    )
                    image_abs_path = os.path.join(settings.MEDIA_ROOT, saved_path)
                    image_url = settings.MEDIA_URL + saved_path.replace('\\', '/')

                # 2. Handle verified sample file
                elif sample_name:
                    sample_file = f"{sample_name}.jpg" if not sample_name.endswith('.jpg') else sample_name
                    image_abs_path = os.path.join(settings.MEDIA_ROOT, 'samples', sample_file)
                    if not os.path.exists(image_abs_path):
                        image_abs_path = os.path.join(
                            settings.BASE_DIR, 'detector', 'static', 'images', sample_file
                        )
                    image_url = settings.MEDIA_URL + f"samples/{sample_file}"

                # 3. Execute inference using trained model
                if image_abs_path and os.path.exists(image_abs_path):
                    prediction_data = predict_disease(image_abs_path, selected_plant=selected_plant)
                    prediction_data['image_url'] = image_url

                    # Store in session for downloadable PDF report generation
                    request.session['latest_prediction'] = prediction_data
                    request.session['latest_image_path'] = image_abs_path

                else:
                    form.add_error(None, "Could not locate the image file for prediction. Please try again.")

            except Exception as e:
                logger.error("Exception during leaf disease detection: %s", str(e), exc_info=True)
                form.add_error(
                    None,
                    "An error occurred while analyzing the leaf image. Please ensure the file is an undamaged leaf photo and try again."
                )

    else:
        form = LeafImageUploadForm(initial={'plant': initial_plant})

    context = {
        'page_title': 'Foliar Disease Prediction | FloraScan AI',
        'form': form,
        'selected_plant': form.cleaned_data.get('plant', initial_plant) if hasattr(form, 'cleaned_data') else initial_plant,
        'samples': SAMPLE_IMAGES,
        'prediction_data': prediction_data,
    }
    return render(request, 'detector/upload.html', context)


def download_report_view(request):
    """
    Direct PDF Download Endpoint:
    Generates and returns the official PDF pathology report for the latest prediction
    without routing to a separate user-facing page.
    """
    prediction_data = request.session.get('latest_prediction')
    image_path = request.session.get('latest_image_path')

    if not prediction_data:
        # Redirect back to upload if no active prediction in session
        return redirect('detector:upload')

    try:
        pdf_buffer = generate_pdf_report(prediction_data, image_abs_path=image_path)
        plant_slug = prediction_data.get('selected_plant', 'Plant').lower()
        filename = f"FloraScan_{plant_slug}_diagnosis_report.pdf"

        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error("Error generating PDF pathology report: %s", str(e), exc_info=True)
        return HttpResponse(
            "An error occurred while compiling the PDF pathology report. Please return to the upload page and retry.",
            content_type='text/plain',
            status=500
        )
