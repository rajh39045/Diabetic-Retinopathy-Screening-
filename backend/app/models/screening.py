from datetime import datetime, timezone


def create_screening_document(
    case_id: str,
    patient_id: str,
    screening_location: str,
    evaluated_eye: str,
    quality=None,
    ai_prediction=None
):
    now = datetime.now(timezone.utc)

    return {
        "case_id": case_id,
        "patient_id": patient_id,
        "screening_location": screening_location,
        "evaluated_eye": evaluated_eye,
        "status": "DRAFT",
        "quality": quality,
        "ai_prediction": ai_prediction,
        "created_at": now,
        "updated_at": now
    }