
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class QualityData(BaseModel):
    focus_sharpness: Optional[Any] = None
    brightness: Optional[Any] = None
    field_of_view: Optional[Any] = None
    vessel_visibility: Optional[Any] = None
    overall_status: Optional[str] = None


class AIPrediction(BaseModel):
    dr_grade: Optional[int] = Field(default=None, ge=0, le=4)
    grade_label: Optional[str] = None
    severity_name: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    confidence_percent: Optional[str] = None
    risk: Optional[str] = None
    recommendation: Optional[str] = None
    gradcam_url: Optional[str] = None
    lesions: List[Any] = Field(default_factory=list)
    model_status: Optional[str] = None
    eye: Optional[str] = None


class ScreeningCreate(BaseModel):
    case_id: str = Field(..., min_length=1)
    patient_id: str = Field(..., min_length=1)
    screening_location: str = Field(..., min_length=2)
    evaluated_eye: str = Field(..., min_length=2)
    quality: Optional[QualityData] = None
    ai_prediction: Optional[AIPrediction] = None


class ScreeningResponse(BaseModel):
    case_id: str
    patient_id: str
    screening_location: str
    evaluated_eye: str
    status: str
    quality: Optional[Dict[str, Any]] = None
    ai_prediction: Optional[Dict[str, Any]] = None
    images: Optional[Dict[str, Any]] = None
    doctor_review: Optional[Dict[str, Any]] = None
    created_at: Optional[Any] = None
    updated_at: Optional[Any] = None
