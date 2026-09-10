# RETINA-XAI Frontend

A complete React + Vite frontend for an explainable retinal screening workflow.

## Included

- Login, registration, password recovery and OTP login
- Protected application routes
- Clinical dashboard
- Patient registration
- Fundus image upload/capture UI
- Image-quality review
- AI screening result page
- Explainability / attention-map view
- Doctor review and decision capture
- Final report with print support
- Responsive layout for desktop/tablet/mobile
- Axios API service layer ready for a backend
- Local demo authentication using `localStorage`

## Run

```bash
npm install
npm run dev
```

Then open the Vite URL shown in the terminal.

## Backend integration

Set:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

The API layer is in `src/services/api.js`.

Expected endpoint groups:

- `/auth/*`
- `/patients`
- `/screenings/:patientId/image`
- `/screenings/:patientId/result`
- `/screenings/:patientId/explainability`
- `/screenings/:patientId/review`
- `/screenings/:patientId/report`

The current UI intentionally works without a backend so the entire frontend can be previewed immediately.
