from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging
import asyncio
import re
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


class HealthChecker:
    """
    Centralized health checking with dependency injection support.
    
    This class encapsulates all health check logic for system dependencies,
    providing a testable and reusable interface for health verification.
    
    Responsibilities:
        - Check individual service health (MongoDB, Azure Blob Storage, Azure AI)
        - Aggregate health check results
        - Calculate overall system health status
        - Provide detailed diagnostics for each dependency
    
    Design Patterns:
        - Strategy Pattern: Each check method implements a health verification strategy
        - Dependency Injection: Container and logger injected via constructor
        - Single Responsibility: Each method checks one specific dependency
    
    Usage:
        ```python
        from app.core.di_container import container
        
        checker = HealthChecker(container)
        dependencies = await checker.check_all(settings)
        overall_status, message, failures = checker.calculate_overall_status(dependencies)
        ```
    
    Attributes:
        container: DI Container instance for service resolution
        logger: Logger instance for diagnostic messages
        CRITICAL_SERVICES: Set of service names that are mandatory for system operation
    """
    
    CRITICAL_SERVICES = {"mongodb", "azure_blob_storage"}
    
    # Whitelist of safe fields to expose in health check responses (security measure)
    SAFE_STATUS_FIELDS = {
        "service",
        "enabled",
        "configured",
        "mode",
        "has_endpoint",
        "has_credentials",
        "collections_count",
        "has_collections",
        "endpoint_configured",
        "key_configured",
        "note"
    }
    
    def __init__(self, container, logger: Optional[logging.Logger] = None):
        """
        Initialize health checker with dependencies.
        
        Args:
            container: DI Container instance for resolving services
            logger: Optional logger instance (uses module logger if None)
        """
        self.container = container
        self.logger = logger or logging.getLogger(__name__)
    
    def _resolve_service(self, service_class, service_name: str) -> Tuple[Optional[Any], Optional[DependencyStatus]]:
        """
        Resolve service from DI container with standardized error handling.
        
        Args:
            service_class: Service class to resolve
            service_name: Human-readable service name for error messages
        
        Returns:
            Tuple of (service_instance, error_status):
                - If successful: (service, None)
                - If failed: (None, DependencyStatus with error)
        """
        if not self.container.is_registered(service_class):
            return None, DependencyStatus(
                status="unhealthy",
                message=f"{service_name} not registered in DI Container",
                details={"error": "Service not configured"}
            )
        
        try:
            service = self.container.resolve(service_class)
            return service, None
        except Exception as e:
            self.logger.error(f"Failed to resolve {service_name}: {e}")
            return None, DependencyStatus(
                status="unhealthy",
                message=f"Failed to resolve {service_name}",
                details=self._sanitize_error(e)
            )
    
    def _sanitize_error(self, error: Exception) -> Dict[str, str]:
        """
        Sanitize error messages to prevent sensitive data leakage.
        
        Removes: file paths, connection strings, API keys, credentials.
        Internal logs still contain full error details for debugging.
        
        Args:
            error: Exception to sanitize
        
        Returns:
            Dictionary with safe error information for public response
        """
        error_str = str(error)
        error_type = type(error).__name__
        
        safe_message = error_str
        
        # Remove file paths
        safe_message = re.sub(r'[A-Za-z]:\\[^\s]+', '[PATH]', safe_message)
        safe_message = re.sub(r'/[^\s]+/', '[PATH]/', safe_message)
        
        # Remove connection strings and URLs with credentials
        safe_message = re.sub(r'mongodb://[^\s]+', 'mongodb://[REDACTED]', safe_message)
        safe_message = re.sub(r'https?://[^@\s]*@[^\s]+', 'https://[REDACTED]', safe_message)
        
        # Remove keys, tokens, passwords
        safe_message = re.sub(r'(key|token|password|secret)[=:][^\s&]+', r'\1=[REDACTED]', safe_message, flags=re.IGNORECASE)
        
        return {
            "error_type": error_type,
            "message": safe_message[:200],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _safe_mongodb_details(self, collections: List[str]) -> Dict[str, Any]:
        """
        Build safe MongoDB details without exposing internal schema.
        
        Args:
            collections: List of collection names
        
        Returns:
            Dictionary with non-sensitive MongoDB information
        """
        return {
            "collections_count": len(collections),
            "has_collections": len(collections) > 0
        }
    
    def _filter_safe_fields(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter details dictionary to only include whitelisted safe fields.
        
        Args:
            details: Full details dictionary
        
        Returns:
            Filtered dictionary with only safe fields
        """
        return {
            key: value 
            for key, value in details.items() 
            if key in self.SAFE_STATUS_FIELDS
        }
    
    async def check_mongodb(self) -> DependencyStatus:
        """
        Check MongoDB connection and health.
        
        Verifies:
            - Service is registered in DI Container
            - Database connection can be established
            - Health check passes (ping successful)
            - Collections can be listed
        
        Returns:
            DependencyStatus with MongoDB health information including:
                - Database name
                - Number of collections
                - List of collection names
        """
        try:
            from app.services.infrastructure.mongodb_connection_service import MongoDBConnectionService
            
            mongo_service, error = self._resolve_service(
                MongoDBConnectionService, 
                "MongoDB service"
            )
            if error:
                return error
            
            try:
                db = await mongo_service.get_database()
            except Exception as conn_error:
                self.logger.error(f"MongoDB connection failed: {conn_error}")
                return DependencyStatus(
                    status="unhealthy",
                    message="Failed to connect to MongoDB",
                    details=self._sanitize_error(conn_error)
                )
            
            is_healthy = await mongo_service.health_check()
            
            if not is_healthy:
                return DependencyStatus(
                    status="unhealthy",
                    message="MongoDB health check failed",
                    details={"error": "Health check returned False"}
                )
            
            collections = await db.list_collection_names()
            
            return DependencyStatus(
                status="healthy",
                message="MongoDB connected and operational",
                details=self._safe_mongodb_details(collections)
            )
            
        except Exception as e:
            self.logger.error(f"MongoDB health check error: {e}")
            return DependencyStatus(
                status="unhealthy",
                message="MongoDB health check failed",
                details=self._sanitize_error(e)
            )
    
    async def check_blob_storage(self) -> DependencyStatus:
        """
        Check Azure Blob Storage connectivity.
        
        Verifies:
            - Service is registered in DI Container
            - Service has health_check method implemented
            - Health check passes (can access storage)
            - Service configuration status
        
        Returns:
            DependencyStatus with Blob Storage health information including:
                - Service class name
                - Configuration details (enabled, URLs, tokens)
                - Service readiness status
        """
        try:
            from app.core.interfaces import IImageUploadService
            
            storage_service, error = self._resolve_service(
                IImageUploadService,
                "Azure Blob Storage service"
            )
            if error:
                return error
            
            if hasattr(storage_service, 'health_check'):
                is_healthy = await storage_service.health_check()
                
                if is_healthy:
                    status_info = {}
                    if hasattr(storage_service, 'get_service_status'):
                        status_info = storage_service.get_service_status()
                        status_info = self._filter_safe_fields(status_info)
                    
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
                return DependencyStatus(
                    status="healthy",
                    message="Azure Blob Storage service registered",
                    details={
                        "service": storage_service.__class__.__name__,
                        "note": "No health_check method available"
                    }
                )
            
        except Exception as e:
            self.logger.error(f"Blob Storage health check error: {e}")
            return DependencyStatus(
                status="unhealthy",
                message="Azure Blob Storage health check failed",
                details=self._sanitize_error(e)
            )
    
    def check_azure_ai(self, settings) -> DependencyStatus:
        """
        Check Azure Document Intelligence configuration.
        
        ⚠️ IMPORTANT: Azure Document Intelligence is REQUIRED for production.
        Mock mode (USE_AZURE_AI=false) should ONLY be used for local development/testing.
        
        This is a configuration check, not a connectivity test.
        
        Verifies:
            - Service is enabled in settings
            - Endpoint URL is configured
            - API key is configured
        
        Args:
            settings: Application settings instance
            
        Returns:
            DependencyStatus with Azure AI configuration status including:
                - Enabled status
                - Configuration completeness
                - Development mode warning if mock is active
        """
        try:
            has_endpoint = bool(settings.azure_document_intelligence_endpoint)
            has_key = bool(settings.azure_document_intelligence_key)
            is_enabled = settings.use_azure_ai
            
            if not is_enabled:
                return DependencyStatus(
                    status="degraded",
                    message="Azure Document Intelligence disabled - DEVELOPMENT MODE ONLY",
                    details={
                        "enabled": False,
                        "mode": "development",
                        "warning": "⚠️ Mock mode active. NOT suitable for production use."
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
                    status="unhealthy",
                    message="Azure Document Intelligence not fully configured - PRODUCTION BLOCKER",
                    details={
                        "enabled": is_enabled,
                        "endpoint_configured": has_endpoint,
                        "key_configured": has_key,
                        "error": "⚠️ Missing Azure credentials. Document processing will FAIL."
                    }
                )
            
        except Exception as e:
            self.logger.error(f"Azure AI health check error: {e}")
            return DependencyStatus(
                status="unhealthy",
                message="Azure Document Intelligence check failed",
                details=self._sanitize_error(e)
            )
    
    async def check_all(self, settings) -> Dict[str, DependencyStatus]:
        """
        Execute all health checks concurrently and return aggregated results.
        
        Uses asyncio.gather to run async checks in parallel for better performance.
        Synchronous checks are executed after async checks complete.
        
        Args:
            settings: Application settings instance
            
        Returns:
            Dictionary mapping service names to their health status:
                - "mongodb": MongoDB health status
                - "azure_blob_storage": Blob Storage health status
                - "azure_document_intelligence": Azure AI health status
        """
        mongodb_task = self.check_mongodb()
        blob_task = self.check_blob_storage()
        
        mongodb_result, blob_result = await asyncio.gather(
            mongodb_task,
            blob_task,
            return_exceptions=True
        )
        
        if isinstance(mongodb_result, Exception):
            self.logger.error(f"MongoDB check raised exception: {mongodb_result}")
            mongodb_result = DependencyStatus(
                status="unhealthy",
                message="MongoDB check failed with exception",
                details=self._sanitize_error(mongodb_result)
            )
        
        if isinstance(blob_result, Exception):
            self.logger.error(f"Blob Storage check raised exception: {blob_result}")
            blob_result = DependencyStatus(
                status="unhealthy",
                message="Blob Storage check failed with exception",
                details=self._sanitize_error(blob_result)
            )
        
        azure_ai_result = self.check_azure_ai(settings)
        
        return {
            "mongodb": mongodb_result,
            "azure_blob_storage": blob_result,
            "azure_document_intelligence": azure_ai_result
        }
    
    def calculate_overall_status(
        self,
        dependencies: Dict[str, DependencyStatus]
    ) -> Tuple[str, str, List[str]]:
        """
        Calculate overall system health from individual dependency statuses.
        
        Rules:
            - If ANY critical service is unhealthy → System is UNHEALTHY
            - If ALL critical services are healthy but non-critical are degraded → System is DEGRADED
            - If ALL services are healthy → System is HEALTHY
        
        Critical services are defined in CRITICAL_SERVICES class attribute.
        
        Args:
            dependencies: Dictionary of service name to health status
            
        Returns:
            Tuple containing:
                - overall_status (str): "healthy", "degraded", or "unhealthy"
                - message (str): Human-readable status message
                - critical_failures (List[str]): Names of failed critical services
        """
        overall_status = "healthy"
        critical_failures = []
        
        # Check each dependency
        for service_name, status in dependencies.items():
            if service_name in self.CRITICAL_SERVICES:
                # Critical service must be healthy
                if status.status != "healthy":
                    overall_status = "unhealthy"
                    critical_failures.append(
                        service_name.replace("_", " ").title()
                    )
            elif status.status != "healthy" and overall_status == "healthy":
                # Non-critical service degraded
                overall_status = "degraded"
        
        # Build human-readable message
        if overall_status == "healthy":
            message = "All systems operational"
        elif overall_status == "degraded":
            message = "System operational with non-critical warnings"
        else:
            message = f"Critical dependencies unavailable: {', '.join(critical_failures)}"
        
        return overall_status, message, critical_failures


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check completo - verifica TODAS as dependências do sistema.
    
    Este endpoint executa verificações de saúde em todas as dependências críticas
    e não-críticas do sistema, retornando um status consolidado.
    
    Dependências Verificadas:
        - MongoDB (CRÍTICO): Persistência de dados obrigatória
        - Azure Blob Storage (CRÍTICO): Armazenamento de imagens obrigatório
        - Azure Document Intelligence (NÃO CRÍTICO): Pode usar mock se indisponível
    
    Status Possíveis:
        - healthy (200): Todas as dependências funcionando corretamente
        - degraded (200): Sistema operacional mas com avisos não-críticos
        - unhealthy (503): Dependências críticas indisponíveis - sistema não pode operar
    
    Returns:
        HealthResponse: Status completo do sistema com detalhes de cada dependência
        
    Raises:
        HTTPException 503: Se dependências críticas estiverem indisponíveis
    
    Example Response (healthy):
        ```json
        {
            "status": "healthy",
            "message": "All systems operational",
            "timestamp": "2025-10-27T22:00:00",
            "dependencies": {
                "mongodb": {"status": "healthy", ...},
                "azure_blob_storage": {"status": "healthy", ...},
                "azure_document_intelligence": {"status": "healthy", ...}
            }
        }
        ```
    """
    from app.core.di_container import container
    settings = get_settings()
    
    # Initialize health checker with DI Container
    checker = HealthChecker(container)
    
    # Execute all health checks concurrently
    dependencies = await checker.check_all(settings)
    
    # Calculate overall system status
    overall_status, message, _ = checker.calculate_overall_status(dependencies)
    
    # Build response
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
    
    # Return 503 Service Unavailable if critical dependencies failed
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response.dict())
    
    return response


def _get_environment_name(settings) -> str:
    """
    Determina nome do ambiente baseado nas configurações.
    
    Args:
        settings: Application settings instance
        
    Returns:
        Environment name: "development", "local", "test", or "production"
    """
    if hasattr(settings, 'debug') and settings.debug:
        return "development"
    elif "localhost" in settings.mongodb_url or "127.0.0.1" in settings.mongodb_url:
        return "local"
    elif "test" in settings.mongodb_database.lower():
        return "test"
    else:
        return "production"
