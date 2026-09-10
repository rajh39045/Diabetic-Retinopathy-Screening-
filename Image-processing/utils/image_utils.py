import cv2

from quality.quality_checker import assess_image_quality

from preprocessing.crop import crop_retinal_region
from preprocessing.enhance import enhance_image
from preprocessing.normalize import normalize_image
from preprocessing.resize import resize_image


def process_fundus_image(image):
    """
    Complete fundus image-processing pipeline.

    Flow:
        1. Quality assessment
        2. Crop / remove black borders
        3. Contrast enhancement + noise reduction
        4. Pixel normalization
        5. Resize to 224 x 224

    Parameters:
        image: OpenCV BGR image

    Returns:
        dict containing:
            quality_result
            accepted
            processed_image
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    # --------------------------------------------------
    # STEP 1: QUALITY CHECK
    # --------------------------------------------------

    quality_result = assess_image_quality(image)

    accepted = quality_result["final_status"] == "ACCEPT"

    # If the image fails quality assessment,
    # do not continue preprocessing.
    if not accepted:
        return {
            "quality_result": quality_result,
            "accepted": False,
            "processed_image": None
        }

    # --------------------------------------------------
    # STEP 2: CROP / REMOVE BLACK BORDERS
    # --------------------------------------------------

    cropped_image = crop_retinal_region(image)

    # --------------------------------------------------
    # STEP 3: ENHANCE
    # --------------------------------------------------

    enhanced_image = enhance_image(cropped_image)

    # --------------------------------------------------
    # STEP 4: NORMALIZE
    # --------------------------------------------------

    normalized_image = normalize_image(enhanced_image)

    # --------------------------------------------------
    # STEP 5: RESIZE
    # --------------------------------------------------

    # resize_image expects an OpenCV image.
    # Convert normalized [0,1] image back to uint8 [0,255].
    normalized_uint8 = (
        normalized_image * 255
    ).clip(0, 255).astype("uint8")

    resized_image = resize_image(normalized_uint8)

    # Convert final image back to float32 [0,1].
    processed_image = resized_image.astype("float32") / 255.0

    return {
        "quality_result": quality_result,
        "accepted": True,
        "processed_image": processed_image
    }