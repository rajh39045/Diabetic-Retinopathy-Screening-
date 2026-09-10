
from fastapi import APIRouter, Depends, status

from app.schemas.screening import ScreeningCreate, ScreeningResponse, QualityData
from app.services.screening_service import ScreeningService
from app.api.deps import get_current_user, require_roles


router = APIRouter(prefix="/api/screenings", tags=["Screenings"])


@router.post("", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
async def create_screening(
    screening: ScreeningCreate,
    user=Depends(get_current_user),
):
    return await ScreeningService.create_screening(
        case_id=screening.case_id,
        patient_id=screening.patient_id,
        screening_location=screening.screening_location,
        evaluated_eye=screening.evaluated_eye,
        quality=screening.quality.model_dump() if screening.quality else None,
        ai_prediction=screening.ai_prediction.model_dump() if screening.ai_prediction else None,
    )


@router.get("", response_model=list[ScreeningResponse])
async def get_screenings(user=Depends(get_current_user)):
    return await ScreeningService.get_all_screenings()


@router.get("/{case_id}", response_model=ScreeningResponse)
async def get_screening(case_id: str, user=Depends(get_current_user)):
    return await ScreeningService.get_screening(case_id)


@router.get("/{case_id}/comparison")
async def get_screening_comparison(
    case_id: str,
    user=Depends(require_roles("OPHTHALMOLOGIST")),
):
    return await ScreeningService.get_screening_comparison(case_id)


@router.patch("/{case_id}/quality", response_model=ScreeningResponse)
async def update_quality(
    case_id: str,
    quality: QualityData,
    user=Depends(get_current_user),
):
    return await ScreeningService.update_quality(case_id, quality.model_dump())


@router.post("/{case_id}/analyze")
async def analyze_screening(
    case_id: str,
    eye: str,
    user=Depends(get_current_user),
):
    return await ScreeningService.analyze_screening(case_id, eye)
