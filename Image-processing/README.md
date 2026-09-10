# Image Processing

Image processing module for the Diabetic Retinopathy Screening system.

## Structure

- preprocessing/
  - resize.py
  - crop.py
  - normalize.py
  - enhance.py

- quality/
  - blur.py
  - brightness.py
  - field_of_view.py
  - quality_checker.py

- utils/
  - image_utils.py

- tests/
- notebook/
  - image_processing.ipynb

## Main Workflow

Raw Fundus Image
        ↓
Image Quality Assessment
        ↓
Accept / Reject
        ↓
Image Preprocessing
        ↓
Model-Ready Image

## Quality Assessment

The quality module checks:

1. Blur
2. Brightness
3. Field of View
4. Retinal Visibility

## Preprocessing

The preprocessing pipeline includes:

1. Resize
2. Crop
3. Remove Black Borders
4. Color Normalization
5. Contrast Enhancement
6. Noise Reduction
