from typing import List

from fastapi import APIRouter, status, Depends
from app.api.deps import get_current_user

from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate
)

from app.services.patient_service import PatientService


router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"]
)


# ============================================================
# CREATE PATIENT
# POST /api/patients
# ============================================================

@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_patient(
    data: PatientCreate,
    user=Depends(get_current_user),
):

    patient = await PatientService.create_patient(
        data
    )

    return patient


# ============================================================
# GET ALL PATIENTS
# GET /api/patients
# ============================================================

@router.get(
    "",
    response_model=List[PatientResponse]
)
async def get_patients(user=Depends(get_current_user)):

    patients = await PatientService.get_all_patients()

    return patients


# ============================================================
# GET PATIENT BY ID
# GET /api/patients/{id}
# ============================================================

@router.get(
    "/{patient_id}",
    response_model=PatientResponse
)
async def get_patient(
    patient_id: str,
    user=Depends(get_current_user),
):

    patient = await PatientService.get_patient(
        patient_id
    )

    return patient


# ============================================================
# UPDATE PATIENT
# PUT /api/patients/{id}
# ============================================================

@router.put(
    "/{patient_id}",
    response_model=PatientResponse
)
async def update_patient(
    patient_id: str,
    data: PatientUpdate,
    user=Depends(get_current_user),
):

    patient = await PatientService.update_patient(
        patient_id,
        data
    )

    return patient