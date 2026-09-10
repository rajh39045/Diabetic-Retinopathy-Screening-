from typing import Optional

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    screening_id: str = Field(
        ...,
        min_length=1,
        description="Screening case ID"
    )

    doctor_name: str = Field(
        ...,
        min_length=2,
        description="Ophthalmologist name"
    )

    decision: str = Field(
        ...,
        description="Doctor review decision"
    )

    final_grade: Optional[str] = Field(
        default=None,
        description="Final DR grade"
    )

    doctor_notes: Optional[str] = Field(
        default=None,
        description="Doctor notes"
    )


class ReviewUpdate(BaseModel):
    doctor_name: Optional[str] = Field(
        default=None,
        min_length=2
    )

    decision: Optional[str] = None

    final_grade: Optional[str] = None

    doctor_notes: Optional[str] = None


class ReviewResponse(BaseModel):
    review_id: str
    screening_id: str
    doctor_name: str
    decision: str
    final_grade: Optional[str] = None
    doctor_notes: Optional[str] = None
    status: str
    reviewed_at: str