from fastapi import FastAPI

from src.api.routes import router

from src.api.pipeline_loader import pipeline

app = FastAPI(
    title="Fraud Detection API"
)

app.include_router(router)