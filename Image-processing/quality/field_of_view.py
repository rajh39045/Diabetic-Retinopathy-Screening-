import cv2
import numpy as np


DEFAULT_MIN_FOV_RATIO = 0.20


def calculate_fov_ratio(image):
    """
    Estimate the proportion of the image occupied by the
    visible retinal field of view.

    Parameters:
        image: OpenCV BGR image

    Returns:
        float: Estimated retinal area ratio
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Threshold to separate the dark background from the
    # brighter retinal region.
    _, mask = cv2.threshold(gray, 10, 255, cv2.THRESH_BINARY)

    # Count non-black pixels
    retinal_pixels = cv2.countNonZero(mask)

    total_pixels = mask.shape[0] * mask.shape[1]

    fov_ratio = retinal_pixels / total_pixels

    return float(fov_ratio)


def check_field_of_view(
    image,
    min_fov_ratio=DEFAULT_MIN_FOV_RATIO
):
    """
    Check whether sufficient retinal area is visible.

    Returns:
        tuple:
            is_good: True if sufficient retinal area is present
            fov_ratio: Estimated retinal area ratio
            status: GOOD / INSUFFICIENT FOV
    """

    fov_ratio = calculate_fov_ratio(image)

    if fov_ratio < min_fov_ratio:
        status = "INSUFFICIENT FOV"
        is_good = False
    else:
        status = "GOOD"
        is_good = True

    return is_good, fov_ratio, status