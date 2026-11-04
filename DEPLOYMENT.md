# MedLens — Production & Cloud Deployment Guide

This guide provides instructions for deploying MedLens across Docker containers and popular cloud hosting providers (Vercel, Render, Railway, or Google Cloud Run).

---

## 1. Local Development Setup

### Backend (FastAPI + PaddleOCR)
Run using the included Windows batch script:
```bash
run_backend.bat
```
Or start manually with your Python environment:
```bash
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
Swagger UI Documentation: `http://127.0.0.1:8000/docs`

### Frontend (Next.js 16 + Firebase)
```bash
cd frontend
npm run dev
```
Accessible at: `http://localhost:3000`

---

## 2. Docker & Docker Compose (1-Command Full Stack)

Run the database, FastAPI backend, and Next.js frontend together:
```bash
docker compose up --build
```
* **Frontend Web App:** `http://localhost:3000`
* **FastAPI Backend:** `http://localhost:8000`
* **PostgreSQL Database:** `localhost:5432`

To shut down:
```bash
docker compose down -v
```

---

## 3. Deploying Frontend to Vercel

1. Push your repository to GitHub.
2. Go to [Vercel Dashboard](https://vercel.com) and click **"Add New Project"**.
3. Import your MedLens repository.
4. Set **Root Directory** to `frontend`.
5. Add the following **Environment Variables** in the Vercel project settings:
   * `NEXT_PUBLIC_API_URL` &rarr; `https://your-backend-domain.com/api/v1`
   * `NEXT_PUBLIC_FIREBASE_API_KEY` &rarr; `your_firebase_api_key_here`
   * `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` &rarr; `medlens-8e318.firebaseapp.com`
   * `NEXT_PUBLIC_FIREBASE_PROJECT_ID` &rarr; `medlens-8e318`
   * `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` &rarr; `medlens-8e318.firebasestorage.app`
   * `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` &rarr; `878014116991`
   * `NEXT_PUBLIC_FIREBASE_APP_ID` &rarr; `1:878014116991:web:a69ac863884e1cda73bb4a`
6. Click **Deploy**.

---

## 4. Deploying Backend to Render / Railway / Google Cloud Run

The backend includes a pre-configured multi-stage `backend/Dockerfile` with PaddleOCR, Tesseract, and OpenCV pre-installed.

### Option A: Render (Web Service via Docker)
1. In [Render Dashboard](https://dashboard.render.com), click **"New +"** &rarr; **"Web Service"**.
2. Connect your GitHub repository `MedLens`.
3. Fill in the service configuration:
   * **Name:** `medlens-backend`
   * **Region:** Select the closest region (e.g., *Oregon, US* or *Frankfurt, EU*)
   * **Branch:** `full-stack-integration` (or `main`)
   * **Root Directory:** `backend`
   * **Runtime:** `Docker`
   * **Instance Type:** `Free`
4. Add the following **Environment Variables**:
   * `ENVIRONMENT` &rarr; `production`
   * `CORS_ORIGINS` &rarr; `*` (or your frontend Vercel/Render URL)
5. Click **"Create Web Service"**.
6. Once deployed, Render will provide a public URL such as `https://medlens-backend.onrender.com`.
   * Verify API docs: `https://medlens-backend.onrender.com/docs`
   * Verify health check: `https://medlens-backend.onrender.com/api/v1/health`

### Alternative: 1-Click Render Blueprint
If you prefer 1-click infrastructure deployment, navigate to **Blueprints** in Render and select `render.yaml` from your repository root. Render will automatically configure the Docker Web Service and health probes.

### Option B: Railway
1. In [Railway](https://railway.app), create a new project from your GitHub repo.
2. Set service root directory to `backend`. Railway will detect the `Dockerfile` automatically.
3. Add a PostgreSQL database service and connect `DATABASE_URL`.
4. Add `CORS_ORIGINS` to allow your Vercel frontend URL.

---

## 5. Security & BYOK Architecture
* **Bring Your Own Key (BYOK):** Google Gemini API keys are held client-side on the user's device (`localStorage`) and never persisted in database logs.
* **Privacy:** Packaging images uploaded during analysis are processed ephemerally in RAM and purged immediately upon report generation.
