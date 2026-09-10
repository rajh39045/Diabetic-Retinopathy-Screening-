import numpy as np
import torch
from PIL import Image

from config import (
    DEVICE,
    IMAGE_SIZE,
    IMAGENET_MEAN,
    IMAGENET_STD
)


# ============================================================
# PREPARE PROCESSED IMAGE FOR MODEL
# ============================================================

def prepare_image(image):
    """
    Convert an already processed image into
    an EfficientNet-compatible tensor.

    Input:
        RGB image
        uint8
        0-255
        Expected size: 224 x 224 x 3

    Output:
        Tensor
        Shape: (1, 3, 224, 224)
        ImageNet normalized
    """

    if image is None:
        raise ValueError(
            "Processed image is None."
        )

    # --------------------------------------------------------
    # Convert to PIL
    # --------------------------------------------------------

    image = Image.fromarray(image)

    # --------------------------------------------------------
    # Ensure model input size
    # --------------------------------------------------------

    image = image.resize(
        (IMAGE_SIZE, IMAGE_SIZE)
    )

    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    image = np.array(
        image
    ).astype(
        np.float32
    )

    # --------------------------------------------------------
    # Convert 0-255 → 0-1
    # --------------------------------------------------------

    image = image / 255.0

    # --------------------------------------------------------
    # ImageNet normalization
    # --------------------------------------------------------

    mean = np.array(
        IMAGENET_MEAN,
        dtype=np.float32
    )

    std = np.array(
        IMAGENET_STD,
        dtype=np.float32
    )

    image = (
        image - mean
    ) / std

    # --------------------------------------------------------
    # HWC → CHW
    # --------------------------------------------------------

    tensor = torch.from_numpy(
        image
    ).permute(
        2,
        0,
        1
    )

    # --------------------------------------------------------
    # Add batch dimension
    # --------------------------------------------------------

    tensor = tensor.unsqueeze(0)

    # --------------------------------------------------------
    # Move to CPU / GPU
    # --------------------------------------------------------

    tensor = tensor.to(
        DEVICE
    )

    return tensor