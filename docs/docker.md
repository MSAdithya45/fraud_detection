# Docker Guide

Containerizes the **backend** (FastAPI + ML pipeline) and **frontend** (Vite build
served by nginx). The database stays on **Supabase** (external) — connected via env vars.

```
┌─────────────┐      http://localhost:8080      ┌──────────────────┐
│   Browser   │ ──────────────────────────────▶ │ frontend (nginx) │
│             │      http://localhost:8000      └──────────────────┘
│             │ ──────────────────────────────▶ ┌──────────────────┐      ┌──────────┐
└─────────────┘            (CORS)                │ backend (uvicorn)│ ───▶ │ Supabase │
                                                 └──────────────────┘      └──────────┘
```

## 1. Prerequisites
- Docker Desktop (Compose v2).
- `fraud_detection/.env` with: `DATABASE_URL`, `DIRECT_URL`, `GEMINI_API_KEY`.
- The Supabase schema already migrated (`npx prisma migrate deploy`). The containers
  do **not** run migrations.

## 2. Run locally
```bash
cd fraud_detection
docker compose up --build
```
- Frontend → http://localhost:8080
- Backend  → http://localhost:8000  (Swagger at /docs)

Stop: `docker compose down`  ·  Rebuild after code changes: `docker compose up --build`

## 3. Push to Docker Hub
1. Add your username to `.env`: `DOCKERHUB_USER=yourusername`
2. ```bash
   docker login
   docker compose build
   docker compose push
   ```
   This pushes `yourusername/fraud-detection-backend:latest` and
   `yourusername/fraud-detection-frontend:latest`.

## 4. Run from the published images (another machine)
Copy `docker-compose.yml` + a `.env` (with the connection strings and
`DOCKERHUB_USER`) to the machine, then:
```bash
docker compose pull
docker compose up --no-build
```
Or run them directly:
```bash
docker run -d --name fraud-backend -p 8000:8000 \
  -e DATABASE_URL="..." -e DIRECT_URL="..." -e GEMINI_API_KEY="..." \
  -e CORS_ORIGINS="http://localhost:8080" \
  yourusername/fraud-detection-backend:latest

docker run -d --name fraud-frontend -p 8080:80 \
  yourusername/fraud-detection-frontend:latest
```

## 5. Deploying behind a domain / server IP
`VITE_API_BASE_URL` is **baked into the frontend at build time**. The published
frontend image assumes the backend is at `http://localhost:8000`. To serve from a
real host, rebuild the frontend with the public backend URL and update CORS:
```bash
VITE_API_BASE_URL=https://api.yourdomain.com \
CORS_ORIGINS=https://app.yourdomain.com \
docker compose build frontend
docker compose push frontend
```

## Notes
- The backend image is large (~2–3 GB) because of TensorFlow. To slim it, switch
  `tensorflow` → `tensorflow-cpu` in `requirements.txt` and drop `build-essential`
  from the Dockerfile.
- Models (`saved_models/`) and drift baselines (`baseline/`) are baked into the
  backend image and loaded at startup, so the first request after boot waits for
  model loading.
- One uvicorn worker on purpose — each worker would reload all models into memory.
