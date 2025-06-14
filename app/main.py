from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(
    title="SmartQuest API",
    version="0.1.0",
    description="Microservice for analyzing and classifying educational assessments"
)

app.include_router(api_router)