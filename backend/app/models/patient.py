from datetime import datetime, timezone


def create_patient_document(
    patient_id: str,
    name: str,
    age: int,
    gender: str,
    phone: str,
    diabetes_status: str,
    diabetes_duration: str | None,
    screening_location: str
):
    return {
        "patient_id": patient_id,
        "name": name,
        "age": age,
        "gender": gender,
        "phone": phone,
        "diabetes_status": diabetes_status,
        "diabetes_duration": diabetes_duration,
        "screening_location": screening_location,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }