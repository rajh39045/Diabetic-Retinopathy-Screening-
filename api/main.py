import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# ============================================================
# DEEP LEARNING SRC
# ============================================================

DL_SRC = os.path.join(
    PROJECT_ROOT,
    "deep-learning",
    "src"
)

if DL_SRC not in sys.path:
    sys.path.append(DL_SRC)


# ============================================================
# DIRECTORIES
# ============================================================

GRADCAM_DIR = os.path.join(
    PROJECT_ROOT,
    "deep-learning",
    "outputs",
    "gradcam"
)

LESION_DIR = os.path.join(
    PROJECT_ROOT,
    "deep-learning",
    "outputs",
    "lesion_evidence"
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

os.makedirs(
    GRADCAM_DIR,
    exist_ok=True
)

os.makedirs(
    LESION_DIR,
    exist_ok=True
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="RETINA-XAI API",
    description="Explainable AI for Diabetic Retinopathy Screening",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# STATIC AI RESULTS
# ============================================================

app.mount(
    "/results/gradcam",
    StaticFiles(
        directory=GRADCAM_DIR
    ),
    name="gradcam"
)

app.mount(
    "/results/lesion",
    StaticFiles(
        directory=LESION_DIR
    ),
    name="lesion"
)


# ============================================================
# ROUTES
# ============================================================

from api.routes.screening import router as screening_router
app.include_router(
    screening_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "RETINA-XAI API is running",
        "status": "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy",
        "service": "RETINA-XAI API"
    }