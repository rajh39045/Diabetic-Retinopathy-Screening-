
# RETINA-XAI Integrated Prototype

This package combines the provided React/Vite frontend with the provided FastAPI/MongoDB backend.

## Architecture

Browser
→ React/Vite frontend
→ FastAPI REST API
→ MongoDB

AI integration point:
React → `POST /api/screenings/{case_id}/analyze?eye=OD`
→ `ScreeningService.analyze_screening()`
→ `deep-learning/src/inference.py::process_image()`

The existing case image is processed in place. Quality rejection stops before prediction, and accepted results store real quality, EfficientNet-B0, Grad-CAM, and AI-generated lesion-evidence data in the existing screening document.

## Important cleanup

The original frontend used Firebase authentication and hard-coded dashboard/result data. This integrated version uses the backend JWT authentication and MongoDB data instead.

The original API routes and frontend routes did not match in several places. Those mismatches are fixed in this version.

## Requirements

- Windows 10/11
- Python 3.11+ recommended
- Node.js 18+
- MongoDB running locally on port `27017`, or a reachable MongoDB Atlas URI
- The model files already included in `deep-learning/models/`

## Backend setup

Open PowerShell in the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create `backend/.env` with at least:

```env
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=retina_xai
JWT_SECRET=replace-with-a-long-random-secret
```

For MongoDB Atlas, replace `MONGODB_URI` with the Atlas connection string. Make sure the current IP is allowed in Atlas and that the URI TLS connection works before starting the backend.

Start the integrated backend:

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend URLs:

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/api/health`
- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate the environment again.

## Frontend setup

Open a second PowerShell terminal in the repository root:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173` in a browser.

To create a production build:

```powershell
cd frontend
npm run build
```

The frontend uses `http://localhost:8000/api` by default. To change it, create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## API smoke test

Keep the backend running, then use a third PowerShell terminal.

### 1. Health check

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/health |
   Select-Object StatusCode, Content
```

Expected response:

```json
{"status":"healthy","database":"connected"}
```

### 2. Swagger test

Open `http://127.0.0.1:8000/docs`, register a user, log in, and authorize Swagger with the returned JWT token. Then test this workflow:

1. Create a patient with `POST /api/patients`.
2. Create a screening case with `POST /api/screenings`.
3. Upload an image with `POST /api/screenings/{case_id}/image` using form fields `eye=OD` and `image`.
4. Run real AI with `POST /api/screenings/{case_id}/analyze?eye=OD`.
5. Read the saved result with `GET /api/screenings/{case_id}`.
6. Submit doctor review with the existing review endpoint.
7. Read the final report with `GET /api/reports/{case_id}`.

The analyze request uses the already stored image. It does not upload the image a second time.

### 3. Direct health and artifact checks

```powershell
$urls = @(
   "http://127.0.0.1:8000/api/health",
   "http://127.0.0.1:8000/results/gradcam/example.png",
   "http://127.0.0.1:8000/results/lesion/example.png"
)

foreach ($url in $urls) {
   try {
      $response = Invoke-WebRequest -UseBasicParsing $url
      "$($response.StatusCode) $url"
   } catch {
      "$($_.Exception.Response.StatusCode.value__) $url"
   }
}
```

Unknown artifact names should return `404`. Real generated artifact names returned by an analyze response should return `200`.

### 4. Direct real-pipeline test

This bypasses authentication and MongoDB and tests the AI pipeline itself against a stored image:

```powershell
python -c "import json, sys; sys.path.insert(0, 'deep-learning/src'); from inference import process_image; result=process_image(r'backend/uploads/CASE_ID/image.jpg'); print(json.dumps(result, indent=2, default=str))"
```

Expected accepted output contains:

- `quality.result.final_status` equal to `ACCEPT`
- prediction grade from `0` to `4`
- Grad-CAM original, heatmap, and overlay paths
- lesion evidence image path and evidence classes

For a low-quality image, expect `success=false`, `quality.accepted=false`, and no prediction, Grad-CAM, or lesion-evidence result.

## Full application workflow

Register → Login → New patient → Upload OD/OS image → Quality screen → Run AI → Explainability → Doctor review → Final report.

## AI result URLs

Generated artifacts are served by the integrated backend at:

- `/results/gradcam/<filename>`
- `/results/lesion/<filename>`

Windows filesystem paths are never returned to the browser. Lesion output is AI-generated research/demo evidence and is not clinically confirmed.

## Legacy API folder

The root `api/` folder contains an older standalone FastAPI experiment. Do not start it for the integrated application workflow. Use `backend/app/main.py`, which preserves authentication, patients, screening cases, reviews, reports, and the real AI integration in one API.

## Troubleshooting

- `ModuleNotFoundError`: activate the backend virtual environment and rerun `python -m pip install -r requirements.txt`.
- MongoDB connection failure: start local MongoDB or check the Atlas URI, network access list, and TLS settings.
- `Real AI dependencies are not installed`: install the backend requirements in the same Python environment used to start Uvicorn.
- CPU inference is slow: the first run loads EfficientNet-B0 and the lesion model; later requests reuse the loaded models within the server process.
