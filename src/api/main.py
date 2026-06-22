import os

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import router

from src.api.pipeline_loader import pipeline

load_dotenv()

app = FastAPI(
    title="Fraud Detection API"
)

# Origins that are ALWAYS allowed (local dev + local docker), plus any extra
# origins from the CORS_ORIGINS env var (comma-separated). We MERGE rather than
# replace, so setting CORS_ORIGINS for deployment never breaks local dev.
_ALWAYS_ALLOW = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
}

_extra = {
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "").split(",")
    if o.strip()
}

_origins = sorted(_ALWAYS_ALLOW | _extra)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
