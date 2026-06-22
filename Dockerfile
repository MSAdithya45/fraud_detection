# ============================================================
# Backend — multi-stage build (FastAPI + ML pipeline)
# Builder compiles/installs deps into an isolated venv; the runtime
# image copies only that venv + the app, so build tools, apt caches and
# pip caches are NOT in the final image.
# ============================================================

# ---- builder ----
FROM python:3.11-slim AS builder

# Build tools live ONLY in this stage (discarded from the final image).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Isolated venv that we copy wholesale into the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ---- runtime ----
FROM python:3.11-slim

# Runtime-only shared library for XGBoost (OpenMP). No build tools here.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Bring in the prebuilt venv.
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# App code + saved_models/ + baseline/ (loaded at startup).
COPY . .

EXPOSE 8000

# One worker: models + SHAP explainer load once per process at startup.
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
