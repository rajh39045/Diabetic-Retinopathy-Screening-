
from datetime import datetime, timezone
from pathlib import Path
import sys
import uuid

from fastapi import HTTPException, status
from starlette.concurrency import run_in_threadpool
from app.database.mongodb import db


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DL_SRC = PROJECT_ROOT / "deep-learning" / "src"
if str(DL_SRC) not in sys.path:
    sys.path.insert(0, str(DL_SRC))

GRADCAM_DIR = (PROJECT_ROOT / "deep-learning" / "outputs" / "gradcam").resolve()
LESION_DIR = (PROJECT_ROOT / "deep-learning" / "outputs" / "lesion_evidence").resolve()


def _artifact_url(path, directory, prefix):
    if not path:
        return None

    artifact_path = Path(path).resolve()
    if directory not in artifact_path.parents or not artifact_path.is_file():
        raise ValueError("AI generated an invalid result artifact")
    return f"{prefix}/{artifact_path.name}"


def _quality_data(result):
    return {
        "focus_sharpness": result.get("blur_score"),
        "blur_score": result.get("blur_score"),
        "blur_status": result.get("blur_status"),
        "brightness": result.get("brightness_score"),
        "brightness_score": result.get("brightness_score"),
        "brightness_status": result.get("brightness_status"),
        "field_of_view": result.get("fov_ratio"),
        "fov_ratio": result.get("fov_ratio"),
        "fov_status": result.get("fov_status"),
        "vessel_visibility": result.get("visibility_ratio"),
        "visibility_ratio": result.get("visibility_ratio"),
        "visibility_status": result.get("visibility_status"),
        "overall_status": result.get("final_status"),
        "final_status": result.get("final_status"),
    }


class ScreeningService:
    COLLECTION_NAME = "screening_cases"
    COMPLETED_STATUSES = ["CONFIRMED", "MODIFIED", "RECAPTURE_REQUIRED", "REFERRED"]

    ALLOWED_DECISIONS = {
        "CONFIRM_AI",
        "MODIFY_GRADE",
        "REQUEST_NEW_IMAGE",
        "REFER_PATIENT",
    }

    STATUS_MAP = {
        "CONFIRM_AI": "CONFIRMED",
        "MODIFY_GRADE": "MODIFIED",
        "REQUEST_NEW_IMAGE": "RECAPTURE_REQUIRED",
        "REFER_PATIENT": "REFERRED",
    }

    @staticmethod
    async def create_screening(case_id, patient_id, screening_location, evaluated_eye, quality=None, ai_prediction=None):
        if not await db.patients.find_one({"patient_id": patient_id}):
            raise HTTPException(404, "Patient not found")

        if await db[ScreeningService.COLLECTION_NAME].find_one({"case_id": case_id}):
            raise HTTPException(409, "Screening case already exists")

        now = datetime.now(timezone.utc)
        document = {
            "case_id": case_id,
            "patient_id": patient_id,
            "screening_location": screening_location,
            "evaluated_eye": evaluated_eye,
            "status": "DRAFT",
            "quality": quality,
            "ai_prediction": ai_prediction,
            "images": {},
            "created_at": now,
            "updated_at": now,
        }
        await db[ScreeningService.COLLECTION_NAME].insert_one(document)
        document.pop("_id", None)
        return document

    @staticmethod
    async def get_all_screenings():
        cursor = db[ScreeningService.COLLECTION_NAME].find({}, {"_id": 0}).sort("created_at", -1)
        return await cursor.to_list(length=200)

    @staticmethod
    async def get_screening(case_id):
        screening = await db[ScreeningService.COLLECTION_NAME].find_one({"case_id": case_id}, {"_id": 0})
        if not screening:
            raise HTTPException(404, "Screening case not found")
        return screening

    @staticmethod
    def _public_images(images):
        return {
            eye: {key: value for key, value in metadata.items() if key != "file_path"}
            for eye, metadata in (images or {}).items()
        }

    @staticmethod
    def _comparison_case(screening):
        ai = dict(screening.get("ai_prediction") or {})
        ai.pop("gradcam_path", None)
        ai.pop("lesion_evidence_path", None)
        images = ScreeningService._public_images(screening.get("images"))
        eyes = set(images)
        evaluated_eye = screening.get("evaluated_eye")
        if evaluated_eye:
            eyes.add(evaluated_eye.upper())
        if ai.get("eye"):
            eyes.add(ai["eye"].upper())

        eye_results = {}
        for eye in sorted(eyes):
            eye_results[eye] = {
                "image": images.get(eye),
                "ai_prediction": ai if ai.get("eye", evaluated_eye) == eye else None,
                "quality": screening.get("quality") if evaluated_eye and evaluated_eye.upper() == eye else None,
            }

        return {
            "case_id": screening.get("case_id"),
            "patient_id": screening.get("patient_id"),
            "screening_location": screening.get("screening_location"),
            "evaluated_eye": evaluated_eye,
            "created_at": screening.get("created_at"),
            "status": screening.get("status"),
            "eyes": eye_results,
        }

    @staticmethod
    async def get_screening_comparison(case_id):
        current = await db[ScreeningService.COLLECTION_NAME].find_one(
            {"case_id": case_id}, {"_id": 0}
        )
        if not current:
            raise HTTPException(404, "Screening case not found")

        previous_query = {
            "patient_id": current.get("patient_id"),
            "case_id": {"$ne": case_id},
            "status": {"$in": ScreeningService.COMPLETED_STATUSES},
            "created_at": {"$lt": current.get("created_at")},
        }
        previous = await db[ScreeningService.COLLECTION_NAME].find_one(
            previous_query,
            {"_id": 0},
            sort=[("created_at", -1)],
        )
        patient = await db.patients.find_one(
            {"patient_id": current.get("patient_id")}, {"_id": 0}
        )

        return {
            "patient": {
                "patient_id": patient.get("patient_id") if patient else current.get("patient_id"),
                "name": patient.get("name") if patient else None,
            },
            "current": ScreeningService._comparison_case(current),
            "previous": ScreeningService._comparison_case(previous) if previous else None,
        }

    @staticmethod
    async def update_quality(case_id, quality):
        now = datetime.now(timezone.utc)
        result = await db[ScreeningService.COLLECTION_NAME].update_one(
            {"case_id": case_id},
            {"$set": {"quality": quality, "updated_at": now}},
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Screening case not found")
        return await ScreeningService.get_screening(case_id)

    @staticmethod
    async def analyze_screening(case_id, eye):
        eye = eye.upper().strip()
        if eye not in {"OD", "OS"}:
            raise HTTPException(400, "Eye must be OD or OS")

        screening = await db[ScreeningService.COLLECTION_NAME].find_one({"case_id": case_id})
        if not screening:
            raise HTTPException(404, "Screening case not found")

        image = screening.get("images", {}).get(eye)
        if not image:
            raise HTTPException(400, f"No {eye} image uploaded")

        image_path = image.get("file_path")
        if not image_path or not Path(image_path).is_file():
            raise HTTPException(404, f"Stored {eye} image is missing from the server")

        try:
            from inference import process_image
            result = await run_in_threadpool(process_image, image_path)
        except ImportError as exc:
            raise HTTPException(503, "Real AI dependencies are not installed") from exc
        except Exception as exc:
            raise HTTPException(500, "AI processing failed. Please try again or upload another image.") from exc

        quality = _quality_data(result.get("quality", {}).get("result", {}))
        now = datetime.now(timezone.utc)

        if not result.get("success") or not result.get("quality", {}).get("accepted"):
            await db[ScreeningService.COLLECTION_NAME].update_one(
                {"case_id": case_id},
                {"$set": {
                    "quality": quality,
                    "ai_prediction": None,
                    "status": "QUALITY_REJECTED",
                    "updated_at": now,
                }},
            )
            return await ScreeningService.get_screening(case_id)

        model_result = result["prediction"]
        grade = model_result["grade"]
        class_name = model_result["class"]
        confidence = float(model_result["confidence"])
        gradcam = result.get("gradcam", {})
        lesion = result.get("lesion_evidence", {})
        gradcam_urls = {
            "original": _artifact_url(gradcam.get("original_path"), GRADCAM_DIR, "/results/gradcam"),
            "heatmap": _artifact_url(gradcam.get("heatmap_path"), GRADCAM_DIR, "/results/gradcam"),
            "overlay": _artifact_url(gradcam.get("overlay_path"), GRADCAM_DIR, "/results/gradcam"),
        }
        lesion_url = _artifact_url(lesion.get("image_path"), LESION_DIR, "/results/lesion")
        prediction = {
            "dr_grade": grade,
            "grade_label": class_name,
            "severity_name": f"{class_name} Diabetic Retinopathy" if class_name != "No DR" else class_name,
            "confidence": confidence,
            "confidence_percent": f"{confidence * 100:.1f}%",
            "risk": model_result["risk_level"],
            "recommendation": "Doctor/Ophthalmologist review required" if model_result["doctor_review_required"] else "Routine follow-up recommended",
            "gradcam_url": gradcam_urls["overlay"],
            "gradcam_urls": gradcam_urls,
            "gradcam_path": gradcam.get("overlay_path"),
            "lesions": lesion.get("detected_classes", []),
            "lesion_evidence_url": lesion_url,
            "lesion_evidence_path": lesion.get("image_path"),
            "model_status": "REAL_AI",
            "doctor_review_required": model_result["doctor_review_required"],
            "eye": eye,
        }

        await db[ScreeningService.COLLECTION_NAME].update_one(
            {"case_id": case_id},
            {
                "$set": {
                    "quality": quality,
                    "ai_prediction": prediction,
                    "status": "PENDING_REVIEW",
                    "updated_at": now,
                }
            },
        )

        return await ScreeningService.get_screening(case_id)

    @staticmethod
    async def create_review(review):
        screening = await db[ScreeningService.COLLECTION_NAME].find_one({"case_id": review.screening_id})
        if not screening:
            raise HTTPException(404, "Screening case not found")

        decision = review.decision.upper().strip()
        if decision not in ScreeningService.ALLOWED_DECISIONS:
            raise HTTPException(400, "Invalid review decision")

        review_id = str(uuid.uuid4())
        reviewed_at = datetime.now(timezone.utc)
        final_status = ScreeningService.STATUS_MAP[decision]

        doctor_review = {
            "review_id": review_id,
            "screening_id": review.screening_id,
            "doctor_name": review.doctor_name,
            "decision": decision,
            "final_grade": review.final_grade,
            "doctor_notes": review.doctor_notes,
            "status": final_status,
            "reviewed_at": reviewed_at,
        }

        await db[ScreeningService.COLLECTION_NAME].update_one(
            {"case_id": review.screening_id},
            {"$set": {
                "doctor_review": doctor_review,
                "status": final_status,
                "updated_at": reviewed_at,
            }},
        )

        return {
            "review_id": review_id,
            "screening_id": review.screening_id,
            "doctor_name": review.doctor_name,
            "decision": decision,
            "final_grade": review.final_grade,
            "doctor_notes": review.doctor_notes,
            "status": final_status,
            "reviewed_at": reviewed_at.isoformat(),
        }

    @staticmethod
    async def get_pending_reviews():
        cursor = db[ScreeningService.COLLECTION_NAME].find(
            {"status": "PENDING_REVIEW"}, {"_id": 0}
        ).sort("created_at", -1)
        return await cursor.to_list(length=200)

    @staticmethod
    async def update_review(review_id, review):
        screening = await db[ScreeningService.COLLECTION_NAME].find_one(
            {"doctor_review.review_id": review_id}
        )
        if not screening:
            raise HTTPException(404, "Review not found")

        update_data = review.model_dump(exclude_none=True)
        if "decision" in update_data:
            decision = update_data["decision"].upper().strip()
            if decision not in ScreeningService.ALLOWED_DECISIONS:
                raise HTTPException(400, "Invalid review decision")
            update_data["decision"] = decision

        if not update_data:
            raise HTTPException(400, "No fields to update")

        set_data = {f"doctor_review.{k}": v for k, v in update_data.items()}
        decision = update_data.get(
            "decision",
            screening.get("doctor_review", {}).get("decision")
        )
        final_status = ScreeningService.STATUS_MAP.get(
            decision,
            screening.get("doctor_review", {}).get("status", "UNDER_REVIEW")
        )
        now = datetime.now(timezone.utc)

        set_data.update({
            "doctor_review.status": final_status,
            "doctor_review.reviewed_at": now,
            "status": final_status,
            "updated_at": now,
        })

        await db[ScreeningService.COLLECTION_NAME].update_one(
            {"doctor_review.review_id": review_id},
            {"$set": set_data},
        )

        updated = await db[ScreeningService.COLLECTION_NAME].find_one(
            {"doctor_review.review_id": review_id}, {"_id": 0}
        )
        r = updated["doctor_review"]
        return {
            "review_id": r["review_id"],
            "screening_id": r["screening_id"],
            "doctor_name": r["doctor_name"],
            "decision": r["decision"],
            "final_grade": r.get("final_grade"),
            "doctor_notes": r.get("doctor_notes"),
            "status": r["status"],
            "reviewed_at": r["reviewed_at"].isoformat(),
        }
