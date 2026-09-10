import os
import cv2
import numpy as np
import torch

from PIL import Image

from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import (
    ClassifierOutputTarget
)
from pytorch_grad_cam.utils.image import (
    show_cam_on_image
)

from config import GRADCAM_DIR, CLASS_NAMES
from model import load_model, get_target_layer
from model_input import prepare_image
from prediction import get_risk_level


def generate_gradcam(
    image_path,
    processed_image
):

    model = load_model()
    target_layer = get_target_layer()

    # ========================================================
    # 1. VALIDATE PROCESSED IMAGE
    # ========================================================

    if processed_image is None:
        raise ValueError(
            "Processed image is None. "
            "Grad-CAM cannot be generated."
        )


    # ========================================================
    # 2. CONVERT PROCESSED IMAGE
    # ========================================================
    #
    # image-processing returns:
    #
    # float32
    # range: 0.0 - 1.0
    # format: BGR
    #
    # model_input.prepare_image() expects:
    #
    # RGB
    # uint8
    # range: 0 - 255
    #
    # ========================================================

    if processed_image.dtype != np.uint8:

        processed_uint8 = (
            processed_image * 255
        ).clip(
            0,
            255
        ).astype(
            np.uint8
        )

    else:

        processed_uint8 = processed_image


    # BGR → RGB

    processed_rgb = cv2.cvtColor(
        processed_uint8,
        cv2.COLOR_BGR2RGB
    )


    # ========================================================
    # 3. PREPARE TENSOR
    # ========================================================

    input_tensor = prepare_image(
        processed_rgb
    )


    # ========================================================
    # 4. PREDICTION
    # ========================================================

    with torch.no_grad():

        outputs = model(
            input_tensor
        )

        probabilities = torch.softmax(
            outputs,
            dim=1
        )


    predicted_class = torch.argmax(
        probabilities,
        dim=1
    ).item()


    confidence = probabilities[
        0,
        predicted_class
    ].item()


    # ========================================================
    # 5. GRAD-CAM
    # ========================================================

    cam = GradCAM(
        model=model,
        target_layers=[
            target_layer
        ]
    )


    targets = [
        ClassifierOutputTarget(
            predicted_class
        )
    ]


    grayscale_cam = cam(
        input_tensor=input_tensor,
        targets=targets
    )[0]


    # ========================================================
    # 6. RGB IMAGE FOR VISUALIZATION
    # ========================================================

    rgb_image = (
        processed_rgb.astype(
            np.float32
        ) / 255.0
    )


    # ========================================================
    # 7. HEATMAP
    # ========================================================

    heatmap = cv2.applyColorMap(
        np.uint8(
            255 * grayscale_cam
        ),
        cv2.COLORMAP_JET
    )


    heatmap = cv2.cvtColor(
        heatmap,
        cv2.COLOR_BGR2RGB
    )


    # ========================================================
    # 8. GRAD-CAM OVERLAY
    # ========================================================

    overlay = show_cam_on_image(
        rgb_image,
        grayscale_cam,
        use_rgb=True
    )


    # ========================================================
    # 9. FILE NAMES
    # ========================================================

    image_name = os.path.splitext(
        os.path.basename(
            image_path
        )
    )[0]


    original_path = os.path.join(
        GRADCAM_DIR,
        f"{image_name}_original.png"
    )


    heatmap_path = os.path.join(
        GRADCAM_DIR,
        f"{image_name}_heatmap.png"
    )


    overlay_path = os.path.join(
        GRADCAM_DIR,
        f"{image_name}_overlay.png"
    )


    # ========================================================
    # 10. SAVE ORIGINAL PROCESSED IMAGE
    # ========================================================

    Image.fromarray(
        processed_rgb
    ).save(
        original_path
    )


    # ========================================================
    # 11. SAVE HEATMAP
    # ========================================================

    Image.fromarray(
        heatmap
    ).save(
        heatmap_path
    )


    # ========================================================
    # 12. SAVE OVERLAY
    # ========================================================

    Image.fromarray(
        overlay
    ).save(
        overlay_path
    )


    # ========================================================
    # 13. RETURN RESULT
    # ========================================================

    return {

        "image":
            os.path.basename(
                image_path
            ),

        "predicted_grade":
            predicted_class,

        "predicted_class":
            CLASS_NAMES[
                predicted_class
            ],

        "confidence":
            confidence,

        "risk_level":
            get_risk_level(
                predicted_class
            ),

        "doctor_review_required":
            (
                confidence < 0.60
                or predicted_class >= 2
            ),

        "original_path":
            original_path,

        "heatmap_path":
            heatmap_path,

        "overlay_path":
            overlay_path
    }