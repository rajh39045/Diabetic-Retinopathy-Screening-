from typing import Any, List, Optional

from pydantic import BaseModel


class AIScreeningResponse(BaseModel):
    grade: int
    severity: str
    confidence: float
    risk: str
    recommendation: str
    quality: Any
    gradcam_url: Optional[str] = None
    lesions: List[str] = []
    model_status: str