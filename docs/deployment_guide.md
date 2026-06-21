# FraudLens — Deployment Guide

Covers local development and containerized deployment. The database is
**Supabase (PostgreSQL)** in all cases — it is not containerized.

---

## 1. Prerequisites

- Python **3.11** (3.13 has limited TensorFlow wheels — use 3.11/3.12 for local).
- Node.js 18+ (frontend) and a Docker Desktop install (containers).
- A Supabase project with the schema applied (see §3).
- `fraud_detection/.env`:
  ```
  DATABASE_URL="postgresql://postgres.<ref>:<pwd>@aws-0-<region>.pooler.supabase.com:5432/postgres?sslmode=require"
  DIRECT_URL="postgresql://postgres:<pwd>@db.<ref>.supabase.co:5432/postgres?sslmode=require"
  GEMINI_API_KEY=<key>
  # optional (docker): DOCKERHUB_USER, VITE_API_BASE_URL, CORS_ORIGINS
  ```

---

## 2. Local development

**Backend** (from `fraud_detection/`):
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```
> Run **without** `--reload` when processing batches — the reload watcher
> restarts the worker mid-request and drops the `/predict` stream. For dev with
> reload, scope it: `--reload --reload-dir src --reload-dir database`.

**Frontend** (from `fraud_detection/frontend/`):
```bash
npm install
npm run dev        # http://localhost:5173
```

CORS for `localhost:5173` and `:8080` is always allowed; extra origins via
`CORS_ORIGINS`.

---

## 3. Database setup (Supabase + Prisma)

```bash
cd fraud_detection
npm install
npx prisma migrate deploy        # creates/updates the stable tables
```
The dynamic staging/history tables are created automatically on the first
`/predict`. See [supabase_migration.md](supabase_migration.md) and
[database_design.md](database_design.md).

**Never** run `prisma migrate reset` / `prisma db push` (drops dynamic tables).

---

## 4. Containerized deployment

Two images: backend (multi-stage Python) + frontend (Vite build → nginx),
orchestrated by `docker-compose.yml`.

```bash
cd fraud_detection
docker compose up --build
# frontend → http://localhost:8080   backend → http://localhost:8000/docs
```

Push to a registry:
```bash
# set DOCKERHUB_USER in .env
docker login
docker compose build
docker compose push
```

Run from published images elsewhere:
```bash
docker compose pull
docker compose up --no-build
```

Full details, image-size notes, and the containerd-store push fix:
[docker.md](docker.md).

---

## 5. Production checklist

- [ ] `VITE_API_BASE_URL` rebuilt with the public backend URL (it is baked at
      build time).
- [ ] `CORS_ORIGINS` set to the public frontend origin.
- [ ] Supabase migrations applied (`npx prisma migrate deploy`).
- [ ] Unique-index clean-up run if older data had duplicates
      (see [database_design.md](database_design.md)).
- [ ] `saved_models/` and `baseline/` present in the backend image.
- [ ] Backend run without `--reload`; single uvicorn worker (models load once).
- [ ] Secrets provided via environment, never baked into images.

---

## 6. Common issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| CORS error from `:5173` | `CORS_ORIGINS` overrode defaults | dev origins are now always allowed; restart backend |
| `/predict` "Failed to fetch" | server restarted mid-stream (`--reload`) | run without `--reload` |
| `invalid connection option "pgbouncer"` | Prisma param in `DATABASE_URL` | handled in `connection.py` (stripped) |
| `server didn't return client encoding` | Supabase transaction pooler | use Session Pooler (port 5432) |
| push `400 Bad Request` | containerd image store bug | disable containerd image store, rebuild, push |
