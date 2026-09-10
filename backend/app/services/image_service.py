import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.database.mongodb import db


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIR = BASE_DIR / "uploads"

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png"
}


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png"
}


ALLOWED_EYES = {
    "OD",
    "OS",
    "ADDITIONAL"
}


# ============================================================
# UPLOAD IMAGE
# ============================================================

class ImageService:

    @staticmethod
    async def upload_image(
        case_id: str,
        eye: str,
        image: UploadFile
    ):

        # ----------------------------------------------------
        # Validate eye
        # ----------------------------------------------------

        eye = eye.upper().strip()

        if eye not in ALLOWED_EYES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid eye. Use OD, OS, or ADDITIONAL."
            )

        # ----------------------------------------------------
        # Validate file name
        # ----------------------------------------------------

        if not image.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image filename is missing."
            )

        original_filename = Path(
            image.filename
        ).name

        extension = Path(
            original_filename
        ).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported image format. Use JPG, JPEG, or PNG."
            )

        # ----------------------------------------------------
        # Validate content type
        # ----------------------------------------------------

        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image content type. Use JPEG or PNG."
            )

        # ----------------------------------------------------
        # Check screening case exists
        # ----------------------------------------------------

        screening_case = await db.screening_cases.find_one(
            {
                "case_id": case_id
            }
        )

        if not screening_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Screening case not found."
            )

        # ----------------------------------------------------
        # Read image into memory
        # ----------------------------------------------------

        image_data = await image.read()

        file_size = len(image_data)

        # ----------------------------------------------------
        # Validate file size
        # ----------------------------------------------------

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty."
            )

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Image size must not exceed 10 MB."
            )

        # ----------------------------------------------------
        # Create unique image ID
        # ----------------------------------------------------

        image_id = str(uuid.uuid4())

        stored_filename = (
            f"{image_id}{extension}"
        )

        # ----------------------------------------------------
        # Create case-specific upload directory
        # ----------------------------------------------------

        case_upload_dir = (
            UPLOAD_DIR / case_id
        )

        case_upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        file_path = (
            case_upload_dir / stored_filename
        )

        # ----------------------------------------------------
        # Save file
        # ----------------------------------------------------

        try:

            with open(
                file_path,
                "wb"
            ) as file:

                file.write(
                    image_data
                )

        except OSError as exc:

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image: {str(exc)}"
            )

        # ----------------------------------------------------
        # Build image metadata
        # ----------------------------------------------------

        image_metadata = {
            "image_id": image_id,
            "eye": eye,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "content_type": image.content_type,
            "size_bytes": file_size,
            "file_path": str(file_path),
            "file_url": (
                f"/api/screenings/{case_id}/image/{image_id}"
            )
        }

        # ----------------------------------------------------
        # Save metadata in MongoDB
        # ----------------------------------------------------

        try:

            await db.screening_cases.update_one(
                {
                    "case_id": case_id
                },
                {
                    "$set": {
                        f"images.{eye}": image_metadata
                    }
                }
            )

        except Exception as exc:

            # Delete file if database update fails
            if file_path.exists():
                file_path.unlink()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save image metadata: {str(exc)}"
            )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "message": "Image uploaded successfully",
            "image_id": image_id,
            "case_id": case_id,
            "eye": eye,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "content_type": image.content_type,
            "size_bytes": file_size,
            "file_url": (
                f"/api/screenings/{case_id}/image/{image_id}"
            )
        }


    # ========================================================
    # GET IMAGE METADATA
    # ========================================================

    @staticmethod
    async def get_image_metadata(
        case_id: str,
        image_id: str
    ):

        screening_case = await db.screening_cases.find_one(
            {
                "case_id": case_id
            },
            {
                "_id": 0
            }
        )

        if not screening_case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Screening case not found."
            )

        images = screening_case.get(
            "images",
            {}
        )

        for eye, metadata in images.items():

            if metadata.get("image_id") == image_id:

                return metadata

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found."
        )


    # ========================================================
    # GET IMAGE FILE
    # ========================================================

    @staticmethod
    async def get_image_file(
        case_id: str,
        image_id: str
    ):

        metadata = await ImageService.get_image_metadata(
            case_id,
            image_id
        )

        file_path = Path(
            metadata["file_path"]
        )

        # ----------------------------------------------------
        # Security check
        # ----------------------------------------------------

        case_upload_dir = (
            UPLOAD_DIR / case_id
        ).resolve()

        resolved_file_path = file_path.resolve()

        if case_upload_dir not in resolved_file_path.parents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file path."
            )

        if not resolved_file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found on server."
            )

        return resolved_file_path, metadata["content_type"]