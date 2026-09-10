from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# CREATE PATIENT
# ============================================================

class PatientCreate(BaseModel):

    patient_id: str = Field(
        ...,
        min_length=1,
        description="Unique patient ID"
    )

    name: str = Field(
        ...,
        min_length=2,
        description="Patient full name"
    )

    age: int = Field(
        ...,
        ge=0,
        le=120,
        description="Patient age"
    )

    gender: str = Field(
        ...,
        description="Patient gender"
    )

    phone: Optional[str] = Field(
        default=None,
        description="Patient mobile number"
    )

    diabetes_status: str = Field(
        ...,
        description="Diabetes status"
    )

    diabetes_duration: Optional[str] = Field(
        default=None,
        description="Duration of diabetes"
    )

    screening_location: str = Field(
        ...,
        min_length=2,
        description="Screening location"
    )


# ============================================================
# UPDATE PATIENT
# ============================================================

class PatientUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2
    )

    age: Optional[int] = Field(
        default=None,
        ge=0,
        le=120
    )

    gender: Optional[str] = None

    phone: Optional[str] = Field(
        default=None,
        min_length=5
    )

    diabetes_status: Optional[str] = None

    diabetes_duration: Optional[str] = None

    screening_location: Optional[str] = None


# ============================================================
# PATIENT RESPONSE
# ============================================================

class PatientResponse(BaseModel):

    patient_id: str

    name: str

    age: int

    gender: str

    phone: Optional[str] = None

    diabetes_status: str

    diabetes_duration: Optional[str] = None

    screening_location: str