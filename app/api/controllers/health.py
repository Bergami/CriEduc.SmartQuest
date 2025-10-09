from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Health check endpoint - API status, configuration and service info
    
    Returns comprehensive health status including:
    - API operational status
    - Service information  
    - Azure AI configuration status
    - Available endpoints
    """
    return {
        "status": "healthy",
        "message": "SmartQuest API is running",
        "service": {
            "name": "SmartQuest API",
            "version": "0.1.0",
            "description": "Microservice for analyzing and classifying educational assessments"
        },
        "configuration": {
            "azure_ai_configured": bool(
                settings.azure_document_intelligence_endpoint and 
                settings.azure_document_intelligence_key
            ),
            "azure_ai_enabled": settings.use_azure_ai
        },
        "endpoints": {
            "health": "/health/ - Health check and API status",
            "analyze": "/analyze/analyze_document - Document analysis endpoint"
        }
    }