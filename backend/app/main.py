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


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

# main.py location:
# backend/app/main.py
#
# parents:
# [0] -> backend/app
# [1] -> backend
# [2] -> project root
#
# Therefore:
# PROJECT_ROOT / "deep-learning"
# points to:
# project-root/deep-learning

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEEP_LEARNING_DIR = PROJECT_ROOT / "deep-learning"

GRADCAM_DIR = DEEP_LEARNING_DIR / "outputs" / "gradcam"

LESION_DIR = DEEP_LEARNING_DIR / "outputs" / "lesion_evidence"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

# Render/Linux will fail if StaticFiles points to a directory
# that does not exist. Create them automatically.

GRADCAM_DIR.mkdir(parents=True, exist_ok=True)

LESION_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# APPLICATION LIFESPAN
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Connect to MongoDB
    await connect_to_mongodb()

    # --------------------------------------------------------
    # MongoDB indexes
    # --------------------------------------------------------

    await db.users.create_index(
        "email",
        unique=True
    )

    await db.patients.create_index(
        "patient_id",
        unique=True
    )

    await db.screening_cases.create_index(
        "case_id",
        unique=True
    )

    await db.screening_cases.create_index(
        "patient_id"
    )

    await db.screening_cases.create_index(
        "status"
    )

    await db.screening_cases.create_index(
        "created_at"
    )

    # Application is running
    yield

    # Close MongoDB connection when application shuts down
    await close_mongodb()


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="RETINA-XAI API",
    description="FastAPI + MongoDB backend for RETINA-XAI",
    version="2.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        # Local Vite development
        "http://localhost:5173",
        "http://127.0.0.1:5173",

        # Other local frontend ports
        "http://localhost:3000",
        "http://localhost:5174",

        # ----------------------------------------------------
        # ADD YOUR VERCEL FRONTEND URL HERE
        # Example:
        # "https://retina-xai.vercel.app",
        # ----------------------------------------------------
    ],

    # Allow localhost with any port
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1)(:\d+)?",

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(auth_router)

app.include_router(patients_router)

app.include_router(screenings_router)

app.include_router(images_router)

app.include_router(ai_router)

app.include_router(reports_router)

app.include_router(reviews_router)


# ============================================================
# STATIC FILES
# ============================================================

# Grad-CAM result images
app.mount(
    "/results/gradcam",
    StaticFiles(directory=str(GRADCAM_DIR)),
    name="gradcam",
)


# Lesion evidence images
app.mount(
    "/results/lesion",
    StaticFiles(directory=str(LESION_DIR)),
    name="lesion",
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "RETINA-XAI API is running",
        "version": "2.0.0",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
@app.get("/api/health")
async def health():

    await db.command("ping")

    return {
        "status": "healthy",
        "database": "connected",
    }