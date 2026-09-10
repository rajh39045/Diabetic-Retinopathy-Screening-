from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, status
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from app.database.mongodb import db

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GRADCAM_DIR = PROJECT_ROOT / "deep-learning" / "outputs" / "gradcam"
LESION_DIR = PROJECT_ROOT / "deep-learning" / "outputs" / "lesion_evidence"


class ReportService:

    COLLECTION_NAME = "screening_cases"

    @staticmethod
    async def get_report_data(
        screening_id: str,
        include_internal: bool = False,
    ):
        screening = await db[
            ReportService.COLLECTION_NAME
        ].find_one(
            {"case_id": screening_id}
        )

        if not screening:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Screening not found"
            )

        patient = await db["patients"].find_one(
            {
                "patient_id": screening["patient_id"]
            }
        )

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        ai_prediction = dict(screening.get("ai_prediction") or {})
        images = screening.get("images") or {}
        if not include_internal:
            ai_prediction.pop("gradcam_path", None)
            ai_prediction.pop("lesion_evidence_path", None)
            images = {
                eye: {key: value for key, value in metadata.items() if key != "file_path"}
                for eye, metadata in images.items()
            }

        return {
            "screening_id": screening["case_id"],
            "patient": {
                "patient_id": patient["patient_id"],
                "name": patient["name"],
                "age": patient["age"],
                "gender": patient["gender"],
                "phone": patient.get("phone"),
                "diabetes_status": patient["diabetes_status"],
                "diabetes_duration": patient.get(
                    "diabetes_duration"
                ),
                "screening_location": patient[
                    "screening_location"
                ]
            },
            "screening": {
                "case_id": screening.get("case_id"),
                "evaluated_eye": screening.get(
                    "evaluated_eye"
                ),
                "created_at": screening.get("created_at"),
                "updated_at": screening.get("updated_at"),
                "quality": screening.get(
                    "quality"
                ),
                "ai_prediction": ai_prediction,
                "images": images,
                "status": screening.get(
                    "status"
                )
            },
            "doctor_review": screening.get(
                "doctor_review"
            )
        }

    @staticmethod
    async def get_report(
        screening_id: str
    ):
        return await ReportService.get_report_data(
            screening_id
        )

    @staticmethod
    async def generate_pdf(
        screening_id: str
    ):
        report = await ReportService.get_report_data(screening_id, include_internal=True)

        # Create reports directory
        base_dir = Path(__file__).resolve().parents[2]
        reports_dir = base_dir / "reports"
        reports_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        pdf_path = reports_dir / f"{screening_id}_report.pdf"

        document = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title = styles["Title"]
        heading = styles["Heading2"]
        normal = styles["BodyText"]

        story = []

        story.append(
            Paragraph(
                "RETINA-XAI Screening Report",
                title
            )
        )

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                f"Screening ID: "
                f"{report['screening_id']}",
                normal
            )
        )

        story.append(
            Spacer(1, 15)
        )

        story.append(
            Paragraph(
                "Patient Information",
                heading
            )
        )

        patient = report["patient"]

        patient_data = [
            [
                "Patient ID",
                patient["patient_id"]
            ],
            [
                "Name",
                patient["name"]
            ],
            [
                "Age",
                str(patient["age"])
            ],
            [
                "Gender",
                patient["gender"]
            ],
            [
                "Phone",
                patient.get("phone") or "-"
            ],
            [
                "Diabetes Status",
                patient["diabetes_status"]
            ],
            [
                "Diabetes Duration",
                patient.get(
                    "diabetes_duration"
                ) or "-"
            ],
            [
                "Screening Location",
                patient["screening_location"]
            ]
        ]

        patient_table = Table(
            patient_data,
            colWidths=[150, 330]
        )

        patient_table.setStyle(
            TableStyle([
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(patient_table)

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                "Screening Result",
                heading
            )
        )

        screening = report["screening"]

        ai_prediction = (
            screening.get("ai_prediction")
            or {}
        )

        screening_data = [
            [
                "Evaluated Eye",
                screening.get(
                    "evaluated_eye"
                ) or "-"
            ],
            [
                "Screening Date",
                str(screening.get("created_at") or "-"),
            ],
            [
                "DR Grade",
                str(
                    ai_prediction.get(
                        "dr_grade",
                        ai_prediction.get(
                            "grade",
                            "-"
                        )
                    )
                )
            ],
            [
                "Severity",
                ai_prediction.get(
                    "severity_name",
                    ai_prediction.get(
                        "severity",
                        "-"
                    )
                )
            ],
            [
                "Confidence",
                ai_prediction.get(
                    "confidence_percent",
                    str(
                        ai_prediction.get(
                            "confidence",
                            "-"
                        )
                    )
                )
            ],
            [
                "Risk",
                ai_prediction.get(
                    "risk",
                    "-"
                )
            ],
            [
                "Recommendation",
                ai_prediction.get(
                    "recommendation",
                    "-"
                )
            ],
            [
                "Case Status",
                screening.get(
                    "status",
                    "-"
                )
            ]
        ]

        screening_table = Table(
            screening_data,
            colWidths=[150, 330]
        )

        screening_table.setStyle(
            TableStyle([
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold"
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(screening_table)

        story.append(Spacer(1, 20))
        story.append(Paragraph("Image Quality", heading))

        quality = screening.get("quality") or {}
        quality_data = [
            ["Blur Score", str(quality.get("blur_score", quality.get("focus_sharpness", "-")))],
            ["Blur Status", str(quality.get("blur_status", "-"))],
            ["Brightness Score", str(quality.get("brightness_score", quality.get("brightness", "-")))],
            ["Brightness Status", str(quality.get("brightness_status", "-"))],
            ["FOV Ratio", str(quality.get("fov_ratio", quality.get("field_of_view", "-")))],
            ["FOV Status", str(quality.get("fov_status", "-"))],
            ["Visibility Ratio", str(quality.get("visibility_ratio", quality.get("vessel_visibility", "-")))],
            ["Visibility Status", str(quality.get("visibility_status", "-"))],
            ["Final Quality Status", str(quality.get("final_status", quality.get("overall_status", "-")))],
        ]
        quality_table = Table(quality_data, colWidths=[150, 330])
        quality_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(quality_table)

        ai_for_images = screening.get("ai_prediction") or {}
        image_entries = []
        for eye, metadata in (screening.get("images") or {}).items():
            file_path = metadata.get("file_path")
            if file_path and Path(file_path).is_file():
                image_entries.append((f"Original Fundus Image ({eye})", file_path))
                break
        gradcam_path = ai_for_images.get("gradcam_path")
        if not gradcam_path and ai_for_images.get("gradcam_url"):
            gradcam_path = GRADCAM_DIR / Path(ai_for_images["gradcam_url"]).name
        if gradcam_path and Path(gradcam_path).is_file():
            image_entries.append(("Grad-CAM Explanation", gradcam_path))
        lesion_path = ai_for_images.get("lesion_evidence_path")
        if not lesion_path and ai_for_images.get("lesion_evidence_url"):
            lesion_path = LESION_DIR / Path(ai_for_images["lesion_evidence_url"]).name
        if lesion_path and Path(lesion_path).is_file():
            image_entries.append(("Lesion Evidence", lesion_path))

        if image_entries:
            story.append(Spacer(1, 20))
            story.append(Paragraph("Visual Evidence", heading))
            for label, file_path in image_entries:
                story.append(Paragraph(label, normal))
                story.append(Image(file_path, width=250, height=180, kind="proportional"))
                story.append(Spacer(1, 8))
        if not ai_for_images:
            story.append(Paragraph("AI disease prediction was not performed for this screening.", normal))

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                "Ophthalmologist Review",
                heading
            )
        )

        review = report.get(
            "doctor_review"
        )

        if review:

            review_data = [
                [
                    "Reviewer",
                    review.get("doctor_name") or review.get("reviewer_id") or "-"
                ],
                [
                    "Decision",
                    review.get(
                        "decision",
                        "-"
                    )
                ],
                [
                    "Final Grade",
                    str(review.get("final_grade")) if review.get("final_grade") is not None else "-"
                ],
                [
                    "Comments",
                    review.get("doctor_notes") or review.get("comments") or "-"
                ],
                [
                    "Reviewed At",
                    str(
                        review.get(
                            "reviewed_at",
                            "-"
                        )
                    )
                ]
            ]

            review_table = Table(
                review_data,
                colWidths=[150, 330]
            )

            review_table.setStyle(
                TableStyle([
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (0, -1),
                        "Helvetica-Bold"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    )
                ])
            )

            story.append(review_table)

        else:

            story.append(
                Paragraph(
                    "Ophthalmologist review is not available.",
                    normal
                )
            )

        story.append(
            Spacer(1, 25)
        )

        story.append(
            Paragraph(
                "This report is generated from the "
                "RETINA-XAI screening record.",
                normal
            )
        )

        document.build(story)

        return str(pdf_path)