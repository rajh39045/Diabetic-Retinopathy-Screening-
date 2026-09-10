import cv2
import numpy as np


def normalize_image(image):
    """
    Normalize the image pixel values to the range [0, 1].

    Parameters:
        image: OpenCV BGR image

    Returns:
        numpy.ndarray: Normalized image
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    # Convert from uint8 [0, 255] to float32 [0, 1]
    normalized = image.astype(np.float32) / 255.0

    return normalized