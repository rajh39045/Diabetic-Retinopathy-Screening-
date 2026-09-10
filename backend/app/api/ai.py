
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.services.screening_service import ScreeningService


router = APIRouter(prefix="/api/ai", tags=["AI Screening"])


@router.post("/screen/{case_id}")
async def screen_case(
    case_id: str,
    eye: str,
    user=Depends(get_current_user),
):
    return await ScreeningService.analyze_screening(case_id, eye)
