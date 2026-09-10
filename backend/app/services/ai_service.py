from fastapi import HTTPException, UploadFile, status

from app.database.mongodb import db


class AIService:

    ALLOWED_EYES = {"OD", "OS"}
    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png"
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    @staticmethod
    async def screen(
        patient_id: str,
        eye: str,
        image: UploadFile
    ):

        # Validate eye
        eye = eye.upper().strip()

        if eye not in AIService.ALLOWED_EYES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Eye must be OD or OS"
            )

        # Check patient
        patient = await db["patients"].find_one(
            {"patient_id": patient_id}
        )

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # Validate image type
        if image.content_type not in AIService.ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only JPEG and PNG images are supported"
            )

        # Read image
        image_bytes = await image.read()

        if not image_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty"
            )

        # Validate size
        if len(image_bytes) > AIService.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image size must not exceed 10 MB"
            )

        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Direct AI uploads are no longer supported. Upload the image to a screening case, then use its analyze endpoint.",
        )