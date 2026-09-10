import os
import torch


# ============================================================
# DIRECTORIES
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "models",
    "retina_xai_combined_efficientnet_b0_best.pth"
)


# ============================================================
# GRAD-CAM OUTPUT
# ============================================================

GRADCAM_DIR = os.path.join(
    PROJECT_ROOT,
    "outputs",
    "gradcam"
)

os.makedirs(GRADCAM_DIR, exist_ok=True)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMAGE_SIZE = 224


# ============================================================
# CLASS NAMES
# ============================================================

CLASS_NAMES = {
    0: "No DR",
    1: "Mild",
    2: "Moderate",
    3: "Severe",
    4: "Proliferative"
}


# ============================================================
# IMAGE NORMALIZATION
# ============================================================

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]