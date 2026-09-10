
from fastapi import APIRouter, File, Form, UploadFile, status, Depends
from fastapi.responses import FileResponse

from app.schemas.image import ImageUploadResponse
from app.services.image_service import ImageService
from app.api.deps import get_current_user, get_optional_user


router = APIRouter(prefix="/api/screenings", tags=["Images"])


@router.post("/{case_id}/image", response_model=ImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_screening_image(
    case_id: str,
    eye: str = Form(...),
    image: UploadFile = File(...),
    user=Depends(get_current_user),
):
    return await ImageService.upload_image(case_id, eye, image)


@router.get("/{case_id}/image/{image_id}")
async def get_screening_image(
    case_id: str,
    image_id: str,
    user=Depends(get_optional_user),
):
    file_path, content_type = await ImageService.get_image_file(case_id, image_id)
    return FileResponse(path=file_path, media_type=content_type)
