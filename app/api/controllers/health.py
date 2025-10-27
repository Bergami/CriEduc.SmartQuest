from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from app.config.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class DependencyStatus(BaseModel):
    """Status de uma dependência individual."""
    status: str  # "healthy", "unhealthy", "degraded"
    message: str
    details: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Resposta completa do health check com todas as dependências."""
    status: str  # "healthy", "unhealthy", "degraded"
    message: str
    timestamp: datetime
    service: Dict[str, str]
    environment: str
    dependencies: Dict[str, DependencyStatus]
    endpoints: Dict[str, str]




@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check completo - verifica TODAS as dependências do sistema.
    
    Testa:
    - MongoDB (persistência obrigatória)
    - Azure Blob Storage (armazenamento de imagens obrigatório)
    - Azure Document Intelligence (processamento de documentos)
    
    Returns:
        HealthResponse: Status completo do sistema e todas as dependências
        
    Status possíveis:
        - healthy: Todas as dependências funcionando
        - degraded: Sistema funcionando mas com dependências com problemas
        - unhealthy: Sistema não pode operar (dependências críticas falharam)
    """
    settings = get_settings()
    
    dependencies = {}
    overall_status = "healthy"
    critical_failures = []
    
    # =====================================================================
    # 1. MongoDB - CRÍTICO (obrigatório)
    # =====================================================================
    mongodb_status = await _check_mongodb_health()
    dependencies["mongodb"] = mongodb_status
    
    if mongodb_status.status != "healthy":
        overall_status = "unhealthy"
        critical_failures.append("MongoDB")
    
    # =====================================================================
    # 2. Azure Blob Storage - CRÍTICO (obrigatório)
    # =====================================================================
    blob_storage_status = await _check_blob_storage_health()
    dependencies["azure_blob_storage"] = blob_storage_status
    
    if blob_storage_status.status != "healthy":
        overall_status = "unhealthy"
        critical_failures.append("Azure Blob Storage")
    
    # =====================================================================
    # 3. Azure Document Intelligence - NÃO CRÍTICO (pode usar mock)
    # =====================================================================
    azure_ai_status = _check_azure_ai_health(settings)
    dependencies["azure_document_intelligence"] = azure_ai_status
    
    if azure_ai_status.status != "healthy" and overall_status == "healthy":
        overall_status = "degraded"
    
    # =====================================================================
    # Determinar mensagem final
    # =====================================================================
    if overall_status == "healthy":
        message = "All systems operational"
    elif overall_status == "degraded":
        message = "System operational with non-critical warnings"
    else:
        message = f"Critical dependencies unavailable: {', '.join(critical_failures)}"
    
    response = HealthResponse(
        status=overall_status,
        message=message,
        timestamp=datetime.utcnow(),
        service={
            "name": "SmartQuest API",
            "version": "2.0.0",
            "description": "Microservice for analyzing and classifying educational assessments"
        },
        environment=_get_environment_name(settings),
        dependencies=dependencies,
        endpoints={
            "health": "/health/ - Complete health check with all dependencies",
            "analyze": "/analyze/analyze_document - Document analysis endpoint"
        }
    )
    
    # Se houver falhas críticas, retorna 503
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response.dict())
    
    return response


async def _check_mongodb_health() -> DependencyStatus:
    """
    Verifica saúde do MongoDB usando o serviço do DI Container.
    
    Returns:
        DependencyStatus com informações sobre MongoDB
    """
    try:
        from app.core.di_container import container
        from app.services.infrastructure.mongodb_connection_service import MongoDBConnectionService
        
        if not container.is_registered(MongoDBConnectionService):
            return DependencyStatus(
                status="unhealthy",
                message="MongoDB service not registered in DI Container",
                details={"error": "Service not configured"}
            )
        
        mongo_service = container.resolve(MongoDBConnectionService)
        
        # Garante conexão
        try:
            db = await mongo_service.get_database()
        except Exception as conn_error:
            return DependencyStatus(
                status="unhealthy",
                message="Failed to connect to MongoDB",
                details={"error": str(conn_error)}
            )
        
        # Verifica health
        is_healthy = await mongo_service.health_check()
        
        if not is_healthy:
            return DependencyStatus(
                status="unhealthy",
                message="MongoDB health check failed",
                details={"error": "Health check returned False"}
            )
        
        # Obtém informações extras
        settings = get_settings()
        collections = await db.list_collection_names()
        
        return DependencyStatus(
            status="healthy",
            message="MongoDB connected and operational",
            details={
                "database": settings.mongodb_database,
                "collections_count": len(collections),
                "collections": collections
            }
        )
        
    except Exception as e:
        logger.error(f"MongoDB health check error: {e}")
        return DependencyStatus(
            status="unhealthy",
            message="MongoDB health check failed",
            details={"error": str(e)}
        )


async def _check_blob_storage_health() -> DependencyStatus:
    """
    Verifica saúde do Azure Blob Storage.
    
    Returns:
        DependencyStatus com informações sobre Blob Storage
    """
    try:
        from app.core.di_container import container
        from app.core.interfaces import IImageUploadService
        
        if not container.is_registered(IImageUploadService):
            return DependencyStatus(
                status="unhealthy",
                message="Azure Blob Storage service not registered in DI Container",
                details={"error": "Service not configured"}
            )
        
        storage_service = container.resolve(IImageUploadService)
        
        # Verifica se tem método health_check
        if hasattr(storage_service, 'health_check'):
            is_healthy = await storage_service.health_check()
            
            if is_healthy:
                # Obter informações extras se disponível
                status_info = {}
                if hasattr(storage_service, 'get_service_status'):
                    status_info = storage_service.get_service_status()
                
                return DependencyStatus(
                    status="healthy",
                    message="Azure Blob Storage connected and operational",
                    details={
                        "service": storage_service.__class__.__name__,
                        **status_info
                    }
                )
            else:
                return DependencyStatus(
                    status="unhealthy",
                    message="Azure Blob Storage health check failed",
                    details={"error": "Health check returned False"}
                )
        else:
            # Se não tem health_check, assume que está OK se foi registrado
            return DependencyStatus(
                status="healthy",
                message="Azure Blob Storage service registered",
                details={
                    "service": storage_service.__class__.__name__,
                    "note": "No health_check method available"
                }
            )
        
    except Exception as e:
        logger.error(f"Blob Storage health check error: {e}")
        return DependencyStatus(
            status="unhealthy",
            message="Azure Blob Storage health check failed",
            details={"error": str(e)}
        )


def _check_azure_ai_health(settings) -> DependencyStatus:
    """
    Verifica configuração do Azure Document Intelligence.
    
    Nota: Esta é uma verificação de configuração, não de conectividade.
    
    Returns:
        DependencyStatus com informações sobre Azure AI
    """
    try:
        has_endpoint = bool(settings.azure_document_intelligence_endpoint)
        has_key = bool(settings.azure_document_intelligence_key)
        is_enabled = settings.use_azure_ai
        
        if not is_enabled:
            return DependencyStatus(
                status="degraded",
                message="Azure Document Intelligence disabled (using mock)",
                details={
                    "enabled": False,
                    "mode": "mock"
                }
            )
        
        if has_endpoint and has_key:
            return DependencyStatus(
                status="healthy",
                message="Azure Document Intelligence configured",
                details={
                    "enabled": True,
                    "endpoint_configured": True,
                    "key_configured": True
                }
            )
        else:
            return DependencyStatus(
                status="degraded",
                message="Azure Document Intelligence not fully configured",
                details={
                    "enabled": is_enabled,
                    "endpoint_configured": has_endpoint,
                    "key_configured": has_key,
                    "note": "Missing configuration - will fallback to mock"
                }
            )
        
    except Exception as e:
        logger.error(f"Azure AI health check error: {e}")
        return DependencyStatus(
            status="degraded",
            message="Azure Document Intelligence check failed",
            details={"error": str(e)}
        )


def _get_environment_name(settings) -> str:
    """Determina nome do ambiente baseado nas configurações."""
    if hasattr(settings, 'debug') and settings.debug:
        return "development"
    elif "localhost" in settings.mongodb_url or "127.0.0.1" in settings.mongodb_url:
        return "local"
    elif "test" in settings.mongodb_database.lower():
        return "test"
    else:
        return "production"
