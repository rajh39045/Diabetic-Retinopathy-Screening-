from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.database.mongodb import db
from app.models.patient import create_patient_document
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientService:

    # ========================================================
    # CREATE PATIENT
    # ========================================================

    @staticmethod
    async def create_patient(data: PatientCreate):

        # Check duplicate patient ID
        existing_patient = await db.patients.find_one(
            {
                "patient_id": data.patient_id
            }
        )

        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient ID already exists"
            )

        patient = create_patient_document(
            patient_id=data.patient_id,
            name=data.name,
            age=data.age,
            gender=data.gender,
            phone=data.phone,
            diabetes_status=data.diabetes_status,
            diabetes_duration=data.diabetes_duration,
            screening_location=data.screening_location
        )

        await db.patients.insert_one(patient)

        return patient

    # ========================================================
    # GET ALL PATIENTS
    # ========================================================

    @staticmethod
    async def get_all_patients():

        cursor = db.patients.find(
            {},
            {
                "_id": 0
            }
        ).sort(
            "created_at",
            -1
        )

        patients = await cursor.to_list(
            length=1000
        )

        return patients

    # ========================================================
    # GET PATIENT BY ID
    # ========================================================

    @staticmethod
    async def get_patient(patient_id: str):

        patient = await db.patients.find_one(
            {
                "patient_id": patient_id
            },
            {
                "_id": 0
            }
        )

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        return patient

    # ========================================================
    # UPDATE PATIENT
    # ========================================================

    @staticmethod
    async def update_patient(
        patient_id: str,
        data: PatientUpdate
    ):

        # Check patient exists
        existing_patient = await db.patients.find_one(
            {
                "patient_id": patient_id
            }
        )

        if not existing_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        update_data = data.model_dump(
            exclude_unset=True,
            exclude_none=True
        )

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields provided for update"
            )

        update_data["updated_at"] = datetime.now(
            timezone.utc
        )

        await db.patients.update_one(
            {
                "patient_id": patient_id
            },
            {
                "$set": update_data
            }
        )

        updated_patient = await db.patients.find_one(
            {
                "patient_id": patient_id
            },
            {
                "_id": 0
            }
        )

        return updated_patient