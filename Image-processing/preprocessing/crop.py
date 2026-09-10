import cv2
import numpy as np


def crop_retinal_region(image):
    """
    Crop the image to the main retinal/fundus region
    and remove unnecessary black borders.

    Parameters:
        image: OpenCV BGR image

    Returns:
        numpy.ndarray: Cropped retinal image
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Create mask for non-black pixels
    mask = gray > 10

    # Find coordinates of visible pixels
    coordinates = np.column_stack(np.where(mask))

    if coordinates.size == 0:
        raise ValueError("No visible retinal region found.")

    # Get bounding box
    y_min, x_min = coordinates.min(axis=0)
    y_max, x_max = coordinates.max(axis=0)

    # Crop to the bounding box
    cropped = image[y_min:y_max + 1, x_min:x_max + 1]

    return cropped


def remove_black_borders(image):
    """
    Remove black borders from a fundus image.

    Parameters:
        image: OpenCV BGR image

    Returns:
        numpy.ndarray: Image with black borders removed
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect non-black pixels
    mask = gray > 10

    coordinates = np.column_stack(np.where(mask))

    if coordinates.size == 0:
        return image

    y_min, x_min = coordinates.min(axis=0)
    y_max, x_max = coordinates.max(axis=0)

    cropped = image[y_min:y_max + 1, x_min:x_max + 1]

    return cropped