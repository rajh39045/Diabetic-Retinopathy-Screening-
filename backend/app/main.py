
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database.mongodb import connect_to_mongodb, close_mongodb
from app.database.mongodb import db

from app.api.auth import router as auth_router
from app.api.patients import router as patients_router
from app.api.screenings import router as screenings_router
from app.api.images import router as images_router
from app.api.ai import router as ai_router
from app.api.reports import router as reports_router
from app.api.reviews import router as reviews_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()

    # Useful indexes for the workflow.
    await db.users.create_index("email", unique=True)
    await db.patients.create_index("patient_id", unique=True)
    await db.screening_cases.create_index("case_id", unique=True)
    await db.screening_cases.create_index("patient_id")
    await db.screening_cases.create_index("status")
    await db.screening_cases.create_index("created_at")

    yield

    await close_mongodb()


app = FastAPI(
    title="RETINA-XAI API",
    description="FastAPI + MongoDB backend for RETINA-XAI",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:5174",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(screenings_router)
app.include_router(images_router)
app.include_router(ai_router)
app.include_router(reports_router)
app.include_router(reviews_router)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
app.mount(
    "/results/gradcam",
    StaticFiles(directory=PROJECT_ROOT / "deep-learning" / "outputs" / "gradcam"),
    name="gradcam",
)
app.mount(
    "/results/lesion",
    StaticFiles(directory=PROJECT_ROOT / "deep-learning" / "outputs" / "lesion_evidence"),
    name="lesion",
)


@app.get("/")
async def root():
    return {"message": "RETINA-XAI API is running", "version": "2.0.0"}


@app.get("/health")
@app.get("/api/health")
async def health():
    await db.command("ping")
    return {"status": "healthy", "database": "connected"}
