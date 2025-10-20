from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import asyncio
from app.config.settings import get_settings

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Basic health check response model."""
    status: str
    message: str
    timestamp: datetime
    service: Dict[str, str]
    configuration: Dict[str, Any]
    endpoints: Dict[str, str]


class DatabaseHealthResponse(BaseModel):
    """Database health check response model."""
    status: str
    timestamp: datetime
    mongodb: Dict[str, Any]
    environment: str
    api_version: str = "2.0"


@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint - API status, configuration and service info
    
    Returns comprehensive health status including:
    - API operational status
    - Service information  
    - Azure AI configuration status
    - Available endpoints
    """
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        message="SmartQuest API is running",
        timestamp=datetime.utcnow(),
        service={
            "name": "SmartQuest API",
            "version": "2.0.0",
            "description": "Microservice for analyzing and classifying educational assessments"
        },
        configuration={
            "azure_ai_configured": bool(
                settings.azure_document_intelligence_endpoint and 
                settings.azure_document_intelligence_key
            ),
            "azure_ai_enabled": settings.use_azure_ai,
            "mongodb_enabled": settings.enable_mongodb_persistence,
            "environment": _get_environment_name(settings)
        },
        endpoints={
            "health": "/health/ - Health check and API status",
            "health_database": "/health/database - Database connectivity check",
            "analyze": "/analyze/analyze_document - Document analysis endpoint"
        }
    )


@router.get("/database", response_model=DatabaseHealthResponse)
async def database_health_check():
    """
    Database connectivity health check.
    
    Verifies MongoDB connection and returns environment information.
    Uses the DI Container's IPersistenceService for unified health checking.
    
    Returns:
        DatabaseHealthResponse: Database health and environment details
        
    Raises:
        HTTPException: 503 if database is unreachable
    """
    settings = get_settings()
    
    mongodb_info = {
        "url": _mask_connection_string(settings.mongodb_url),
        "database": settings.mongodb_database,
        "timeout": settings.mongodb_connection_timeout,
        "persistence_enabled": settings.enable_mongodb_persistence,
        "connection_status": "unknown",
        "collections": [],
        "indexes": {},
        "sample_document_exists": False,
        "service_health": {}
    }
    
    if not settings.enable_mongodb_persistence:
        mongodb_info["connection_status"] = "disabled"
        return DatabaseHealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            mongodb=mongodb_info,
            environment=_get_environment_name(settings),
            api_version="2.0"
        )
    
    try:
        # Use DI Container to get persistence service
        from app.core.di_container import container
        from app.services.persistence import IPersistenceService
        
        if container.is_registered(IPersistenceService):
            # Use the configured persistence service for health check
            persistence_service = container.resolve(IPersistenceService)
            service_health = await persistence_service.health_check()
            
            mongodb_info["service_health"] = service_health
            
            if service_health.get("status") == "healthy":
                mongodb_info["connection_status"] = "connected"
                mongodb_info["collections"] = service_health.get("collections_count", 0)
            else:
                mongodb_info["connection_status"] = "service_unhealthy"
                mongodb_info["error"] = service_health.get("error", "Service health check failed")
                
        else:
            # Fallback to direct connection test
            logger.warning("IPersistenceService not registered, using direct MongoDB connection")
            # Import here to avoid issues if motor is not installed
            from motor.motor_asyncio import AsyncIOMotorClient
            
            # Test MongoDB connection
            client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=settings.mongodb_connection_timeout
            )
            
            database = client[settings.mongodb_database]
            
            # Test connection with server info
            await asyncio.wait_for(
                client.admin.command('ping'),
                timeout=settings.mongodb_connection_timeout / 1000
            )
            
            mongodb_info["connection_status"] = "connected"
            await client.close()
        
        # Import here to avoid issues if motor is not installed
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Additional detailed checks if direct connection is needed
        if mongodb_info["connection_status"] == "connected":
            client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=settings.mongodb_connection_timeout
            )
            
            database = client[settings.mongodb_database]
            
            # Get collection information
            collection_names = await database.list_collection_names()
            mongodb_info["collections"] = collection_names
            
            # Get indexes information for analyzeDocuments collection
            if "analyzeDocuments" in collection_names:
                collection = database["analyzeDocuments"]
                
                # Get indexes
                indexes = []
                async for index in collection.list_indexes():
                    indexes.append({
                        "name": index.get("name", "unknown"),
                        "key": index.get("key", {}),
                        "unique": index.get("unique", False)
                    })
                mongodb_info["indexes"]["analyzeDocuments"] = indexes
                
                # Check if sample document exists
                sample_count = await collection.count_documents({"userEmail": "admin@smartquest.com.br"})
                mongodb_info["sample_document_exists"] = sample_count > 0
                
                # Get collection stats
                try:
                    stats = await database.command("collStats", "analyzeDocuments")
                    mongodb_info["stats"] = {
                        "documents": stats.get("count", 0),
                        "size_bytes": stats.get("size", 0),
                        "storage_size_bytes": stats.get("storageSize", 0)
                    }
                except Exception as e:
                    logger.warning(f"Could not get collection stats: {e}")
                    mongodb_info["stats"] = {"error": "Could not retrieve stats"}
            
            await client.close()
        
        return DatabaseHealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            mongodb=mongodb_info,
            environment=_get_environment_name(settings),
            api_version="2.0"
        )
        
    except ImportError:
        logger.error("Motor package not available")
        mongodb_info["connection_status"] = "motor_not_installed"
        mongodb_info["error"] = "Motor package not available"
        
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "mongodb": mongodb_info,
                "environment": _get_environment_name(settings),
                "error": "Motor MongoDB driver not installed"
            }
        )
        
    except asyncio.TimeoutError:
        logger.error("MongoDB connection timeout")
        mongodb_info["connection_status"] = "timeout"
        mongodb_info["error"] = "Connection timeout"
        
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "mongodb": mongodb_info,
                "environment": _get_environment_name(settings),
                "error": "Database connection timeout"
            }
        )
        
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        mongodb_info["connection_status"] = "error"
        mongodb_info["error"] = str(e)
        
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "mongodb": mongodb_info,
                "environment": _get_environment_name(settings),
                "error": f"Database connection error: {str(e)}"
            }
        )


def _get_environment_name(settings) -> str:
    """Determine environment name based on settings."""
    if hasattr(settings, 'debug') and settings.debug:
        return "development"
    elif "localhost" in settings.mongodb_url or "127.0.0.1" in settings.mongodb_url:
        return "local"
    elif "test" in settings.mongodb_database.lower():
        return "test"
    else:
        return "production"


def _mask_connection_string(url: str) -> str:
    """Mask sensitive information in connection string."""
    if "@" in url:
        # mongodb://user:password@host:port/db -> mongodb://***:***@host:port/db
        parts = url.split("@")
        if "//" in parts[0]:
            protocol_user = parts[0].split("//")
            if ":" in protocol_user[1]:
                protocol_user[1] = "***:***"
            else:
                protocol_user[1] = "***"
            parts[0] = "//".join(protocol_user)
        return "@".join(parts)
    return url