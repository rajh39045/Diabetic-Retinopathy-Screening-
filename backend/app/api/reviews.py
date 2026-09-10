from fastapi import APIRouter, HTTPException, status, Depends
from app.api.deps import require_roles

from app.schemas.review import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse
)

from app.services.screening_service import ScreeningService


router = APIRouter(
    prefix="/api/reviews",
    tags=["Doctor Review"]
)


@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_review(
    review: ReviewCreate,
    user=Depends(require_roles("OPHTHALMOLOGIST")),
):
    try:
        return await ScreeningService.create_review(
            review
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "/pending"
)
async def get_pending_reviews(user=Depends(require_roles("OPHTHALMOLOGIST"))):
    return await ScreeningService.get_pending_reviews()


@router.put(
    "/{review_id}",
    response_model=ReviewResponse
)
async def update_review(
    review_id: str,
    review: ReviewUpdate,
    user=Depends(require_roles("OPHTHALMOLOGIST")),
):
    try:
        return await ScreeningService.update_review(
            review_id,
            review
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )