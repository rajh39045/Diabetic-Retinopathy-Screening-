import cv2


def enhance_image(image):
    """
    Enhance a fundus image using:
    1. CLAHE contrast enhancement
    2. Gentle Gaussian noise reduction

    Parameters:
        image: OpenCV BGR image

    Returns:
        numpy.ndarray: Enhanced image
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    # Convert BGR to LAB color space
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    # Split LAB channels
    l_channel, a_channel, b_channel = cv2.split(lab)

    # CLAHE for local contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced_l = clahe.apply(l_channel)

    # Merge channels
    enhanced_lab = cv2.merge(
        (enhanced_l, a_channel, b_channel)
    )

    # Convert back to BGR
    enhanced = cv2.cvtColor(
        enhanced_lab,
        cv2.COLOR_LAB2BGR
    )

    # Gentle Gaussian filtering for noise reduction
    enhanced = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0
    )

    return enhanced