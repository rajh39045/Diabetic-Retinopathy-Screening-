import cv2


DEFAULT_IMAGE_SIZE = (224, 224)


def resize_image(image, size=DEFAULT_IMAGE_SIZE):
    """
    Resize a fundus image to the required model-ready size.

    Parameters:
        image: OpenCV BGR image
        size: Target size as (width, height)

    Returns:
        numpy.ndarray: Resized image
    """

    if image is None:
        raise ValueError("Invalid image. Image could not be loaded.")

    resized = cv2.resize(
        image,
        size,
        interpolation=cv2.INTER_AREA
    )

    return resized