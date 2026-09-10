from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_current_user, get_optional_user
from fastapi.responses import FileResponse

from app.services.report_service import ReportService


router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)


@router.get("/{screening_id}")
async def get_report(screening_id: str, user=Depends(get_current_user)):
    try:
        return await ReportService.get_report(
            screening_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.get("/{screening_id}/pdf")
async def get_report_pdf(screening_id: str, user=Depends(get_optional_user)):
    try:
        pdf_path = await ReportService.generate_pdf(
            screening_id
        )

        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"{screening_id}_report.pdf"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )