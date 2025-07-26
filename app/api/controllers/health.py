from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint - API status and info"""
    return {
        "message": "SmartQuest API",
        "version": "0.1.0",
        "status": "running",
        "description": "Microservice for analyzing and classifying educational assessments",
        "endpoints": {
            "health": "/health - Status da API e configurações",
            "analyze": "/analyze/analyze_document - Análise de documentos PDF"
        }
    }

@router.get("/health")
async def health_check():
    return {
        "message": "SmartQuest API está funcionando!",
        "status": "healthy",
        "azure_ai_configured": bool(settings.azure_document_intelligence_endpoint and settings.azure_document_intelligence_key),
        "azure_ai_enabled": settings.use_azure_ai,
        "version": "0.1.0"
    }