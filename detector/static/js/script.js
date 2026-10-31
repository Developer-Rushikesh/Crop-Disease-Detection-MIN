/**
 * FLORASCAN AI - Client-side UI Interactions
 * Handles image preview, drag-and-drop, plant selection, sample quick-select,
 * and dynamic progress bar animations.
 */

document.addEventListener('DOMContentLoaded', function () {
    const dropzoneArea = document.getElementById('dropzoneArea');
    const imageInput = document.getElementById('imageInput');
    const dropzoneIdle = document.getElementById('dropzoneIdle');
    const dropzonePreview = document.getElementById('dropzonePreview');
    const previewImg = document.getElementById('previewImg');
    const previewFilename = document.getElementById('previewFilename');
    const previewFilesize = document.getElementById('previewFilesize');
    const removePreviewBtn = document.getElementById('removePreviewBtn');
    const selectedSampleInput = document.getElementById('selectedSampleInput');
    const uploadForm = document.getElementById('diseaseUploadForm');
    const detectSubmitBtn = document.getElementById('detectSubmitBtn');
    const plantCards = document.querySelectorAll('.plant-radio-card');
    const sampleChips = document.querySelectorAll('.sample-chip');

    // =========================================================================
    // 1. Plant Selection Sync
    // =========================================================================
    plantCards.forEach(card => {
        card.addEventListener('click', function () {
            plantCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            const radio = this.querySelector('input[type="radio"]');
            if (radio) {
                radio.checked = true;
            }
        });
    });

    // Helper: Select plant programmatically
    function selectPlant(plantName) {
        plantCards.forEach(card => {
            const radio = card.querySelector('input[type="radio"]');
            if (radio && radio.value === plantName.toLowerCase()) {
                radio.checked = true;
                card.classList.add('selected');
            } else {
                card.classList.remove('selected');
            }
        });
    }

    // =========================================================================
    // 2. Drag & Drop File Upload
    // =========================================================================
    if (dropzoneArea && imageInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzoneArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzoneArea.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzoneArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                dropzoneArea.classList.remove('drag-over');
            });
        });

        dropzoneArea.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                handleFileSelection(files[0]);
            }
        });

        imageInput.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                handleFileSelection(this.files[0]);
            }
        });
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    }

    function handleFileSelection(file) {
        // Validate type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type.toLowerCase())) {
            alert('Please select a valid JPG, JPEG, or PNG image.');
            return;
        }

        // Validate size (5 MB)
        if (file.size > 5 * 1024 * 1024) {
            alert('File exceeds maximum size of 5 MB. Please upload a smaller image.');
            return;
        }

        // Clear sample selection if any
        if (selectedSampleInput) {
            selectedSampleInput.value = '';
        }
        sampleChips.forEach(chip => chip.classList.remove('active-chip'));

        const reader = new FileReader();
        reader.onload = function (e) {
            previewImg.src = e.target.result;
            previewFilename.textContent = file.name;
            previewFilesize.textContent = formatFileSize(file.size);

            dropzoneIdle.style.display = 'none';
            dropzonePreview.style.display = 'flex';
        };
        reader.readAsDataURL(file);
    }

    // =========================================================================
    // 3. Remove Image Preview
    // =========================================================================
    if (removePreviewBtn) {
        removePreviewBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            resetUploadArea();
        });
    }

    function resetUploadArea() {
        if (imageInput) imageInput.value = '';
        if (selectedSampleInput) selectedSampleInput.value = '';
        if (previewImg) previewImg.src = '';
        if (dropzoneIdle) dropzoneIdle.style.display = 'block';
        if (dropzonePreview) dropzonePreview.style.display = 'none';
        sampleChips.forEach(chip => chip.classList.remove('active-chip'));
    }

    // =========================================================================
    // 4. Quick Test Sample Selection
    // =========================================================================
    sampleChips.forEach(chip => {
        chip.addEventListener('click', function () {
            const sampleId = this.getAttribute('data-sample-id');
            const samplePlant = this.getAttribute('data-plant');
            const sampleImgUrl = this.getAttribute('data-img-url');
            const sampleName = this.querySelector('.chip-name').textContent;

            // Mark active chip
            sampleChips.forEach(c => c.classList.remove('active-chip'));
            this.classList.add('active-chip');

            // Select matching plant automatically
            selectPlant(samplePlant);

            // Set hidden sample value
            if (selectedSampleInput) {
                selectedSampleInput.value = sampleId;
            }

            // Clear raw file input
            if (imageInput) {
                imageInput.value = '';
            }

            // Show preview
            if (previewImg) {
                previewImg.src = sampleImgUrl;
                previewFilename.textContent = sampleName + ' (Sample)';
                previewFilesize.textContent = 'PlantVillage Benchmark';
                dropzoneIdle.style.display = 'none';
                dropzonePreview.style.display = 'flex';
            }

            // Smooth scroll up to preview
            if (dropzoneArea) {
                dropzoneArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    });

    // =========================================================================
    // 5. Form Submission & Loading Spinner
    // =========================================================================
    if (uploadForm && detectSubmitBtn) {
        uploadForm.addEventListener('submit', function (e) {
            const hasFile = imageInput && imageInput.files && imageInput.files.length > 0;
            const hasSample = selectedSampleInput && selectedSampleInput.value.trim() !== '';

            if (!hasFile && !hasSample) {
                e.preventDefault();
                alert('Please upload a leaf photograph or select one of the test samples.');
                return;
            }

            // Activate loading spinner state
            const btnText = detectSubmitBtn.querySelector('.btn-text');
            const btnSpinner = detectSubmitBtn.querySelector('.btn-spinner');

            if (btnText && btnSpinner) {
                btnText.style.display = 'none';
                btnSpinner.style.display = 'inline-flex';
                detectSubmitBtn.style.opacity = '0.85';
                detectSubmitBtn.style.pointerEvents = 'none';
            }
        });
    }

    // =========================================================================
    // 6. Auto-Scroll to Result on Page Load (if present)
    // =========================================================================
    const resultSection = document.getElementById('diagnosisResultSection');
    if (resultSection) {
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    const detectAnotherScrollBtn = document.getElementById('detectAnotherScrollBtn');
    if (detectAnotherScrollBtn) {
        detectAnotherScrollBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const formSection = document.getElementById('uploadFormSection');
            if (formSection) {
                formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }

    // =========================================================================
    // 7. Dynamic Progress Bars
    // =========================================================================
    document.querySelectorAll('[data-progress-width]').forEach(function (bar) {
        const widthVal = bar.getAttribute('data-progress-width');
        if (widthVal) {
            bar.style.width = widthVal + '%';
        }
    });
});
