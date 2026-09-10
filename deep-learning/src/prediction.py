import os
import cv2
import numpy as np
import torch

from config import CLASS_NAMES
from model import load_model
from model_input import prepare_image

def get_risk_level(predicted_class):

    if predicted_class == 0:
        return "Low"

    elif predicted_class == 1:
        return "Low-Mild"

    elif predicted_class == 2:
        return "Moderate"

    elif predicted_class == 3:
        return "High"

    else:
        return "Very High"


def predict(
    image_path,
    processed_image,
    review_threshold=0.60
):

    model = load_model()

    # --------------------------------------------------------
    # 1. Validate processed image
    # --------------------------------------------------------

    if processed_image is None:
        raise ValueError(
            "Processed image is required for prediction."
        )

    if processed_image.shape != (224, 224, 3):
        raise ValueError(
            f"Invalid processed image shape: "
            f"{processed_image.shape}. "
            f"Expected (224, 224, 3)."
        )

    # --------------------------------------------------------
    # 2. Processed image is currently:
    #
    # BGR
    # float32
    # [0, 1]
    #
    # Convert it to:
    #
    # RGB
    # uint8
    # [0, 255]
    #
    # because prepare_image() expects image values
    # in normal image format.
    # --------------------------------------------------------

    processed_uint8 = (
        processed_image * 255
    ).clip(
        0,
        255
    ).astype(
        np.uint8
    )

    processed_rgb = cv2.cvtColor(
        processed_uint8,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # 3. Tensor
    # --------------------------------------------------------

    input_tensor = prepare_image(
        processed_rgb
    )

    # --------------------------------------------------------
    # 4. Prediction
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 5. Risk
    # --------------------------------------------------------

    risk_level = get_risk_level(
        predicted_class
    )

    # --------------------------------------------------------
    # 6. Doctor review
    # --------------------------------------------------------

    doctor_review_required = (
        confidence < review_threshold
        or predicted_class >= 2
    )

    # --------------------------------------------------------
    # 7. Result
    # --------------------------------------------------------

    return {

        "image": os.path.basename(
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
            risk_level,

        "doctor_review_required":
            doctor_review_required
    }