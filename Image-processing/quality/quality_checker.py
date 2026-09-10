import cv2
import numpy as np

from quality.blur import is_blurry
from quality.brightness import check_brightness
from quality.field_of_view import check_field_of_view


def check_retinal_visibility(image):
    """
    Check whether a visible retinal/fundus region is present.

    This is a simple OpenCV-based visibility heuristic.
    It checks whether a sufficient non-dark region is present
    in the image.

    Returns:
        tuple:
            is_visible: True if retina appears visible
            visibility_ratio: proportion of visible pixels
            status: VISIBLE / POOR VISIBILITY
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Identify pixels that are not near-black.
    visible_mask = gray > 10

    visible_pixels = np.count_nonzero(visible_mask)
    total_pixels = gray.size

    visibility_ratio = visible_pixels / total_pixels

    # Simple visibility threshold
    min_visibility_ratio = 0.20

    if visibility_ratio >= min_visibility_ratio:
        status = "VISIBLE"
        is_visible = True
    else:
        status = "POOR VISIBILITY"
        is_visible = False

    return is_visible, float(visibility_ratio), status


def assess_image_quality(image):
    """
    Perform the complete image quality assessment.

    Checks:
        1. Blur
        2. Brightness
        3. Field of View
        4. Retinal Visibility

    Returns:
        dict containing all quality measurements and
        the final ACCEPT / REJECT decision.
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    # --------------------------------------------------
    # 1. BLUR CHECK
    # --------------------------------------------------
    is_blur, blur_score = is_blurry(image)

    blur_status = "BLUR" if is_blur else "GOOD"

    # --------------------------------------------------
    # 2. BRIGHTNESS CHECK
    # --------------------------------------------------
    brightness_good, brightness_score, brightness_status = (
        check_brightness(image)
    )

    # --------------------------------------------------
    # 3. FIELD OF VIEW CHECK
    # --------------------------------------------------
    fov_good, fov_ratio, fov_status = check_field_of_view(image)

    # --------------------------------------------------
    # 4. RETINAL VISIBILITY CHECK
    # --------------------------------------------------
    visibility_good, visibility_ratio, visibility_status = (
        check_retinal_visibility(image)
    )

    # --------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------
    accepted = (
        not is_blur
        and brightness_good
        and fov_good
        and visibility_good
    )

    if accepted:
        final_status = "ACCEPT"
    else:
        final_status = "REJECT"

    return {
        "blur_score": round(blur_score, 2),
        "blur_status": blur_status,

        "brightness_score": round(brightness_score, 2),
        "brightness_status": brightness_status,

        "fov_ratio": round(fov_ratio, 3),
        "fov_status": fov_status,

        "visibility_ratio": round(visibility_ratio, 3),
        "visibility_status": visibility_status,

        "final_status": final_status
    }