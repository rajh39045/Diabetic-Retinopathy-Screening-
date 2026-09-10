import cv2


DEFAULT_BLUR_THRESHOLD = 2.5


def calculate_blur_score(image):
    """
    Calculate image sharpness using Variance of Laplacian.

    Higher score:
        Sharper image

    Lower score:
        Blurrier image

    Parameters:
        image: OpenCV BGR image

    Returns:
        float: Variance of Laplacian
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    laplacian = cv2.Laplacian(gray, cv2.CV_64F)

    blur_score = laplacian.var()

    return float(blur_score)


def is_blurry(image, threshold=DEFAULT_BLUR_THRESHOLD):
    """
    Check whether an image is blurry.

    Parameters:
        image: OpenCV BGR image
        threshold: Variance of Laplacian threshold

    Returns:
        tuple:
            is_blur: True if image is considered blurry
            score: Calculated blur score
    """

    score = calculate_blur_score(image)

    is_blur = score < threshold

    return is_blur, score