"""
Configuração do Dependency Injection Container.

Define mapeamentos entre interfaces e implementações com ciclo de vida singleton.
"""
import logging
from app.core.di_container import container, ServiceLifetime
from app.core.interfaces import (
    IImageExtractor, 
    IContextBuilder,
    IFigureProcessor,
    IDocumentAnalysisOrchestrator,
    IAnalyzeService,
    IImageUploadService
)
from app.services.image.interfaces.image_categorization_interface import ImageCategorizationInterface
from app.services.image.image_categorization_service import ImageCategorizationService
from app.services.image.extraction.image_extraction_orchestrator import ImageExtractionOrchestrator
from app.services.context.context_block_builder import ContextBlockBuilder
# Note: Using the original (corrected) context_block_builder instead of refactored_context_builder
# because it has the proper text context block extraction in parse_to_pydantic
from app.services.azure.azure_figure_processor import AzureFigureProcessor
from app.services.core.document_analysis_orchestrator import DocumentAnalysisOrchestrator
from app.services.core.analyze_service import AnalyzeService
from app.services.storage.azure_image_upload_service import AzureImageUploadService
from app.services.persistence import ISimplePersistenceService, MongoDBPersistenceService
from app.services.infrastructure import MongoDBConnectionService
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def configure_dependencies() -> None:
    """Configure all system dependencies with appropriate lifecycles."""
    logger.info("Starting dependency configuration...")
    
    container.register(
        interface_type=ImageCategorizationInterface,
        implementation_type=ImageCategorizationService,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("ImageCategorizationInterface -> ImageCategorizationService (Singleton)")
    
    container.register(
        interface_type=IImageExtractor,
        implementation_type=ImageExtractionOrchestrator,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("IImageExtractor -> ImageExtractionOrchestrator (Singleton)")
    
    container.register(
        interface_type=IContextBuilder,
        implementation_type=ContextBlockBuilder,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("IContextBuilder -> ContextBlockBuilder (Singleton)")
    
    container.register(
        interface_type=IFigureProcessor,
        implementation_type=AzureFigureProcessor,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("IFigureProcessor -> AzureFigureProcessor (Singleton)")
    
    container.register(
        interface_type=IDocumentAnalysisOrchestrator,
        implementation_type=DocumentAnalysisOrchestrator,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("IDocumentAnalysisOrchestrator -> DocumentAnalysisOrchestrator (Singleton)")
    
    container.register(
        interface_type=IAnalyzeService,
        implementation_type=AnalyzeService,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("IAnalyzeService -> AnalyzeService (Singleton)")
    
    container.register(
        interface_type=IImageUploadService,
        implementation_type=AzureImageUploadService,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("IImageUploadService -> AzureImageUploadService (Singleton)")
    
    container.register(
        interface_type=MongoDBConnectionService,
        implementation_type=MongoDBConnectionService,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("MongoDBConnectionService -> MongoDBConnectionService (Singleton)")
    
    container.register(
        interface_type=ISimplePersistenceService,
        implementation_type=MongoDBPersistenceService,
        lifetime=ServiceLifetime.SINGLETON
    )
    logger.debug("ISimplePersistenceService -> MongoDBPersistenceService (Singleton)")
    
    settings = get_settings()
    logger.info(f"MongoDB configured: {settings.mongodb_database} @ {settings.mongodb_url}")
    logger.info(f"Dependency configuration completed successfully! Total services: {len(container.get_registrations())}")


def configure_test_dependencies() -> None:
    """Configure dependencies for test environment."""
    logger.info("Configuring TEST dependencies...")
    configure_dependencies()
    logger.info("TEST dependency configuration completed!")


def get_registered_services() -> dict:
    """Get information about registered services for debugging."""
    registrations = container.get_registrations()
    
    services_info = {}
    for interface_type, registration in registrations.items():
        services_info[interface_type.__name__] = {
            'interface': interface_type.__name__,
            'implementation': registration.implementation_type.__name__,
            'lifetime': registration.lifetime.value,
            'has_cached_instance': registration.cached_instance is not None
        }
    
    return services_info


def validate_configuration() -> bool:
    """Validate that all essential interfaces are registered and resolvable."""
    logger.info("Validating dependency configuration...")
    
    essential_interfaces = [
        ImageCategorizationInterface,
        IImageExtractor,
        IContextBuilder,
        IFigureProcessor,
        IDocumentAnalysisOrchestrator,
        IAnalyzeService,
        ISimplePersistenceService
    ]
    
    try:
        for interface in essential_interfaces:
            if not container.is_registered(interface):
                logger.error(f"Interface not registered: {interface.__name__}")
                return False
            logger.debug(f"Interface registered: {interface.__name__}")
        
        logger.info("Testing full dependency resolution...")
        analyze_service = container.resolve(IAnalyzeService)
        
        if analyze_service is None:
            logger.error("Failed to resolve IAnalyzeService")
            return False
        
        logger.info("Dependency configuration validation PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"Dependency configuration validation FAILED: {str(e)}")
        return False


logger.info("Auto-configuring dependencies...")
configure_dependencies()

if validate_configuration():
    logger.info("SmartQuest DI Container ready!")
else:
    logger.error("DI Container configuration failed!")