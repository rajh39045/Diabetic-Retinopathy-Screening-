import cv2
from pathlib import Path
import sys


# ============================================================
# IMAGE PROCESSING PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_PROCESSING_DIR = str(PROJECT_ROOT / "Image-processing")

if IMAGE_PROCESSING_DIR not in sys.path:
    sys.path.insert(0, IMAGE_PROCESSING_DIR)


# ============================================================
# IMPORT IMAGE PROCESSING
# ============================================================

from utils.image_utils import process_fundus_image


# ============================================================
# IMPORT AI MODULES
# ============================================================

from prediction import predict
from gradcam import generate_gradcam
from lesion_evidence import generate_lesion_evidence


# ============================================================
# COMPLETE SCREENING PIPELINE
# ============================================================

def process_image(image_path):

    # ========================================================
    # 1. LOAD RAW IMAGE
    # ========================================================

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )


    # ========================================================
    # 2. IMAGE PROCESSING + QUALITY CHECK
    # ========================================================

    processing_result = process_fundus_image(
        image
    )

    quality_result = processing_result[
        "quality_result"
    ]

    accepted = processing_result[
        "accepted"
    ]

    processed_image = processing_result[
        "processed_image"
    ]


    # ========================================================
    # 3. STOP IF IMAGE QUALITY IS BAD
    # ========================================================

    if not accepted:

        return {

            "success": False,

            "image": image_path.split("\\")[-1],

            "quality": {

                "accepted": False,

                "result": quality_result
            },

            "message":
                "Image quality is insufficient. "
                "Please upload another retinal image."
        }


    # ========================================================
    # 4. DR PREDICTION
    # ========================================================

    prediction = predict(
        image_path,
        processed_image
    )


    # ========================================================
    # 5. GRAD-CAM
    # ========================================================

    gradcam = generate_gradcam(
        image_path,
        processed_image
    )


    # ========================================================
    # 6. LESION EVIDENCE
    # ========================================================

    lesion = generate_lesion_evidence(
        image_path
    )


    # ========================================================
    # 7. COMBINE RESULTS
    # ========================================================

    return {

        "success": True,

        "image":
            prediction["image"],


        # ----------------------------------------------------
        # IMAGE QUALITY
        # ----------------------------------------------------

        "quality": {

            "accepted":
                True,

            "result":
                quality_result
        },


        # ----------------------------------------------------
        # DR PREDICTION
        # ----------------------------------------------------

        "prediction": {

            "grade":
                prediction["predicted_grade"],

            "class":
                prediction["predicted_class"],

            "confidence":
                prediction["confidence"],

            "risk_level":
                prediction["risk_level"],

            "doctor_review_required":
                prediction[
                    "doctor_review_required"
                ]
        },


        # ----------------------------------------------------
        # GRAD-CAM
        # ----------------------------------------------------

        "gradcam": {

            "original_path":
                gradcam["original_path"],

            "heatmap_path":
                gradcam["heatmap_path"],

            "overlay_path":
                gradcam["overlay_path"]
        },


        # ----------------------------------------------------
        # LESION EVIDENCE
        # ----------------------------------------------------

        "lesion_evidence": {

            "image_path":
                lesion[
                    "lesion_evidence_path"
                ],

            "detected_classes":
                lesion[
                    "detected_classes"
                ]
        }
    }


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

__all__ = [
    "process_image"
]