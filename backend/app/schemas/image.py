from typing import Optional

from pydantic import BaseModel


class ImageUploadResponse(BaseModel):
    message: str
    image_id: str
    case_id: str
    eye: str
    original_filename: str
    stored_filename: str
    content_type: str
    size_bytes: int
    file_url: str