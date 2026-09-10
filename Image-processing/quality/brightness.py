import cv2


# Provisional thresholds for the APTOS dataset.
# These will be adjusted after checking sample images.
DEFAULT_MIN_BRIGHTNESS = 30.0
DEFAULT_MAX_BRIGHTNESS = 220.0


def calculate_brightness(image):
    """
    Calculate the mean brightness of an image.

    Parameters:
        image: OpenCV BGR image

    Returns:
        float: Mean grayscale intensity
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    brightness = gray.mean()

    return float(brightness)


def check_brightness(
    image,
    min_brightness=DEFAULT_MIN_BRIGHTNESS,
    max_brightness=DEFAULT_MAX_BRIGHTNESS
):
    """
    Check whether an image has acceptable brightness.

    Returns:
        tuple:
            is_good: True if brightness is acceptable
            brightness_score: Mean brightness
            status: GOOD / TOO DARK / TOO BRIGHT
    """

    brightness_score = calculate_brightness(image)

    if brightness_score < min_brightness:
        status = "TOO DARK"
        is_good = False

    elif brightness_score > max_brightness:
        status = "TOO BRIGHT"
        is_good = False

    else:
        status = "GOOD"
        is_good = True

    return is_good, brightness_score, status
