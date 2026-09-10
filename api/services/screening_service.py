import os
import shutil


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = os.path.join(
    PROJECT_ROOT,
    "api",
    "uploads"
)

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ============================================================
# IMPORT AI PIPELINE
# ============================================================

import sys

DL_SRC = os.path.join(
    PROJECT_ROOT,
    "deep-learning",
    "src"
)

if DL_SRC not in sys.path:
    sys.path.append(DL_SRC)


from inference import process_image


# ============================================================
# SAVE UPLOADED IMAGE
# ============================================================

async def save_uploaded_image(
    file,
    filename
):

    image_path = os.path.join(
        UPLOAD_DIR,
        filename
    )

    with open(
        image_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return image_path


# ============================================================
# RUN SCREENING
# ============================================================

def run_screening(
    image_path
):

    # Run complete AI pipeline
    result = process_image(
        image_path
    )


    # ========================================================
    # QUALITY REJECTED
    # ========================================================

    if not result["success"]:

        return {

            "success": False,

            "image":
                result["image"],

            "quality":
                result["quality"],

            "message":
                result["message"]
        }


    # ========================================================
    # GRAD-CAM FILENAMES
    # ========================================================

    gradcam_original = os.path.basename(
        result["gradcam"]["original_path"]
    )

    gradcam_heatmap = os.path.basename(
        result["gradcam"]["heatmap_path"]
    )

    gradcam_overlay = os.path.basename(
        result["gradcam"]["overlay_path"]
    )


    # ========================================================
    # LESION EVIDENCE FILENAME
    # ========================================================

    lesion_image = os.path.basename(
        result["lesion_evidence"]["image_path"]
    )


    # ========================================================
    # API RESPONSE
    # ========================================================

    return {

        "success": True,

        "image":
            result["image"],


        # ====================================================
        # IMAGE QUALITY
        # ====================================================

        "quality": {

            "accepted":
                result["quality"]["accepted"],

            "result":
                result["quality"]["result"]
        },


        # ====================================================
        # PREDICTION
        # ====================================================

        "prediction": {

            "grade":
                result["prediction"]["grade"],

            "class":
                result["prediction"]["class"],

            "confidence":
                result["prediction"]["confidence"],

            "risk_level":
                result["prediction"]["risk_level"],

            "doctor_review_required":
                result["prediction"][
                    "doctor_review_required"
                ]
        },


        # ====================================================
        # GRAD-CAM
        # ====================================================

        "gradcam": {

            "original_url":
                f"/results/gradcam/"
                f"{gradcam_original}",

            "heatmap_url":
                f"/results/gradcam/"
                f"{gradcam_heatmap}",

            "overlay_url":
                f"/results/gradcam/"
                f"{gradcam_overlay}"
        },


        # ====================================================
        # LESION EVIDENCE
        # ====================================================

        "lesion_evidence": {

            "image_url":
                f"/results/lesion/"
                f"{lesion_image}",

            "detected_classes":
                result[
                    "lesion_evidence"
                ][
                    "detected_classes"
                ]
        }
    }