import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from api.services.screening_service import save_uploaded_image, run_screening

# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/screening",
    tags=["Screening"]
)


# ============================================================
# PREDICT
# ============================================================

@router.post("/predict")
async def screening_predict(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )


    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png"
    }

    extension = os.path.splitext(
        file.filename
    )[1].lower()


    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only JPG, JPEG and PNG "
                "images are allowed"
            )
        )


    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    filename = (
        f"{uuid.uuid4()}"
        f"{extension}"
    )


    # --------------------------------------------------------
    # Save image
    # --------------------------------------------------------

    try:

        image_path = await save_uploaded_image(
            file,
            filename
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}"
        )


    # --------------------------------------------------------
    # Run AI screening
    # --------------------------------------------------------

    try:

        result = run_screening(
            image_path
        )

        return result

    except Exception as e:

        # Remove uploaded image if AI fails
        if os.path.exists(image_path):

            os.remove(image_path)

        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {str(e)}"
        )