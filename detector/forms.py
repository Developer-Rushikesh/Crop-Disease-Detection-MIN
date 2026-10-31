from django import forms
from PIL import Image

PLANT_CHOICES = [
    ('apple', 'Apple (Malus domestica)'),
    ('tomato', 'Tomato (Solanum lycopersicum)'),
]

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_PIL_FORMATS = {'JPEG', 'PNG'}
ALLOWED_SAMPLE_IDS = {
    'apple_scab',
    'apple_black_rot',
    'apple_cedar_rust',
    'apple_healthy',
    'tomato_early_blight',
    'tomato_healthy',
}

MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MIN_DIMENSION = 10
MAX_DIMENSION = 8000


class LeafImageUploadForm(forms.Form):
    plant = forms.ChoiceField(
        choices=PLANT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select-custom',
            'id': 'plantSelect'
        }),
        error_messages={
            'required': 'Please select a plant type (Apple or Tomato) before uploading.',
            'invalid_choice': 'Invalid plant selection. Please choose Apple or Tomato.'
        }
    )

    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-file-input',
            'id': 'imageInput',
            'accept': 'image/jpeg,image/png,image/jpg'
        }),
        error_messages={
            'invalid_image': 'Upload a valid image file. The uploaded file was either not an image or corrupted.'
        }
    )

    sample_image = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'selectedSampleInput'})
    )

    def clean_sample_image(self):
        sample = self.cleaned_data.get('sample_image', '').strip().lower()
        if sample:
            # Prevent path traversal or unexpected values
            if sample not in ALLOWED_SAMPLE_IDS:
                raise forms.ValidationError("Invalid test sample identifier selected.")
        return sample

    def clean_plant(self):
        plant = self.cleaned_data.get('plant', '').strip().lower()
        if plant not in ('apple', 'tomato'):
            raise forms.ValidationError("Invalid crop selected. Must be Apple or Tomato.")
        return plant

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        sample_image = cleaned_data.get('sample_image')

        # Must have either an uploaded file or a valid sample choice
        if not image and not sample_image:
            raise forms.ValidationError("Please upload a leaf photograph or select one of the test samples.")

        if image:
            # 1. Reject empty file
            if image.size == 0:
                raise forms.ValidationError("The uploaded file is empty (0 bytes). Please upload a valid image.")

            # 2. Reject file larger than 5 MB
            if image.size > MAX_FILE_SIZE_BYTES:
                size_mb = image.size / (1024 * 1024)
                raise forms.ValidationError(
                    f"File exceeds maximum allowed size ({size_mb:.2f} MB). Maximum size is {MAX_FILE_SIZE_MB} MB."
                )

            # 3. Validate filename extension safely
            filename = image.name.lower()
            ext = filename.rsplit('.', 1)[-1] if '.' in filename else ''
            if ext not in ALLOWED_EXTENSIONS:
                raise forms.ValidationError(
                    f"Unsupported file extension (.{ext}). Only JPG, JPEG, and PNG images are allowed."
                )

            # 4. Deep Inspection: Validate true binary content using Pillow
            try:
                # Open image stream to verify header
                img = Image.open(image)

                # Check format matches allowed MIME formats (not just renamed .exe or .txt)
                if img.format not in ALLOWED_PIL_FORMATS:
                    raise forms.ValidationError(
                        f"Unsupported image format: {img.format}. Only genuine JPEG and PNG images are accepted."
                    )

                # Verify image integrity
                img.verify()
                image.seek(0)

                # Re-open to inspect dimensions safely (prevents decompression bomb issues)
                img = Image.open(image)
                width, height = img.size
                if width < MIN_DIMENSION or height < MIN_DIMENSION:
                    raise forms.ValidationError(
                        f"Image dimensions are too small ({width}x{height}px). Minimum is {MIN_DIMENSION}x{MIN_DIMENSION}px."
                    )
                if width > MAX_DIMENSION or height > MAX_DIMENSION:
                    raise forms.ValidationError(
                        f"Image dimensions are too large ({width}x{height}px). Maximum dimension is {MAX_DIMENSION}px."
                    )

                # Reset file position for subsequent reading
                image.seek(0)

            except forms.ValidationError:
                raise
            except Exception:
                raise forms.ValidationError(
                    "Corrupted or invalid image data. Please ensure the file is an uncorrupted JPEG or PNG photo."
                )

        return cleaned_data
