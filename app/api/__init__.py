from fastapi import APIRouter
from app.api.health_controller import router as health_router
from app.api.analyze_controller import router as analyze_router

router = APIRouter()
router.include_router(health_router)
router.include_router(analyze_router)