"""
Configuração do Dependency Injection Container

Configuração centralizada de todas as dependências do sistema.
Define mapeamentos entre interfaces e implementações com ciclo de vida singleton.
"""
import logging
from app.core.di_container import container, ServiceLifetime
from app.core.interfaces import (
    IImageCategorizer,
    IImageExtractor, 
    IContextBuilder,
    IFigureProcessor,
    IDocumentAnalysisOrchestrator,
    IAnalyzeService,
    IImageUploadService
)

# Importar implementações concretas
from app.services.image.image_categorization_service import ImageCategorizationService
from app.services.image.extraction.image_extraction_orchestrator import ImageExtractionOrchestrator
from app.services.context.context_block_builder import ContextBlockBuilder
from app.services.azure.azure_figure_processor import AzureFigureProcessor
from app.services.core.document_analysis_orchestrator import DocumentAnalysisOrchestrator
from app.services.core.analyze_service import AnalyzeService
from app.services.storage.azure_image_upload_service import AzureImageUploadService

# ========== NOVAS IMPORTAÇÕES - FASE 2 MONGODB ==========
from app.services.persistence import ISimplePersistenceService, MongoDBPersistenceService
from app.services.infrastructure import MongoDBConnectionService
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


def configure_dependencies() -> None:
    """
    🔧 CONFIGURA todas as dependências do sistema
    
    ARQUITETURA DE DEPENDÊNCIAS:
    
    AnalyzeService
    └── DocumentAnalysisOrchestrator
        ├── ImageCategorizationService
        ├── ImageExtractionOrchestrator
        ├── ContextBlockBuilder
        └── AzureFigureProcessor
    
    PROCESSO:
    1. Registra cada interface com sua implementação
    2. Define ciclo de vida apropriado
    3. O container resolve automaticamente toda a árvore
    
    SINGLETONS vs TRANSIENTS:
    - Singletons: Serviços stateless, caros de criar
    - Transients: Serviços com estado, leves
    """
    
    logger.info("🔧 Starting dependency configuration...")
    
    # ==================================================================================
    # 🏷️ IMAGE CATEGORIZATION SERVICE
    # ==================================================================================
    container.register(
        interface_type=IImageCategorizer,
        implementation_type=ImageCategorizationService,
        lifetime=ServiceLifetime.SINGLETON  # Stateless, pode ser reutilizado
    )
    logger.debug("✅ IImageCategorizer -> ImageCategorizationService (Singleton)")
    
    # ==================================================================================
    # 📸 IMAGE EXTRACTION ORCHESTRATOR  
    # ==================================================================================
    container.register(
        interface_type=IImageExtractor,
        implementation_type=ImageExtractionOrchestrator,
        lifetime=ServiceLifetime.SINGLETON  # Orquestrador stateless
    )
    logger.debug("✅ IImageExtractor -> ImageExtractionOrchestrator (Singleton)")
    
    # ==================================================================================
    # 🧱 CONTEXT BUILDER
    # ==================================================================================
    container.register(
        interface_type=IContextBuilder,
        implementation_type=ContextBlockBuilder,
        lifetime=ServiceLifetime.SINGLETON  # Builder stateless
    )
    logger.debug("✅ IContextBuilder -> ContextBlockBuilder (Singleton)")
    
    # ==================================================================================
    # 🖼️ FIGURE PROCESSOR (Azure)
    # ==================================================================================
    container.register(
        interface_type=IFigureProcessor,
        implementation_type=AzureFigureProcessor,
        lifetime=ServiceLifetime.SINGLETON  # Comunicação externa, reutilizar conexões
    )
    logger.debug("✅ IFigureProcessor -> AzureFigureProcessor (Singleton)")
    
    # ==================================================================================
    # 🎭 DOCUMENT ANALYSIS ORCHESTRATOR
    # ==================================================================================
    container.register(
        interface_type=IDocumentAnalysisOrchestrator,
        implementation_type=DocumentAnalysisOrchestrator,
        lifetime=ServiceLifetime.SINGLETON  # Orquestrador principal, stateless
    )
    logger.debug("✅ IDocumentAnalysisOrchestrator -> DocumentAnalysisOrchestrator (Singleton)")
    
    # ==================================================================================
    # 🎯 ANALYZE SERVICE (Ponto de entrada)
    # ==================================================================================
    container.register(
        interface_type=IAnalyzeService,
        implementation_type=AnalyzeService,
        lifetime=ServiceLifetime.SINGLETON  # Service layer, stateless
    )
    logger.debug("✅ IAnalyzeService -> AnalyzeService (Singleton)")
    
    # ==================================================================================
    # 🌐 IMAGE UPLOAD SERVICE (Azure Blob Storage)
    # ==================================================================================
    container.register(
        interface_type=IImageUploadService,
        implementation_type=AzureImageUploadService,
        lifetime=ServiceLifetime.SINGLETON  # Stateless, reutilizar conexões HTTP
    )
    logger.debug("✅ IImageUploadService -> AzureImageUploadService (Singleton)")
    
    # ==================================================================================
    # 💾 MONGODB CONNECTION SERVICE
    # ==================================================================================
    container.register(
        interface_type=MongoDBConnectionService,
        implementation_type=MongoDBConnectionService,
        lifetime=ServiceLifetime.SINGLETON  # Singleton para reutilizar conexões
    )
    logger.debug("✅ MongoDBConnectionService -> MongoDBConnectionService (Singleton)")
    
    # ==================================================================================
    # 💾 PERSISTENCE SERVICE (MongoDB)
    # ==================================================================================
    container.register(
        interface_type=ISimplePersistenceService,
        implementation_type=MongoDBPersistenceService,
        lifetime=ServiceLifetime.SINGLETON  # Singleton para reutilizar conexões
    )
    
    logger.debug("✅ ISimplePersistenceService -> MongoDBPersistenceService (Singleton)")
    
    settings = get_settings()
    logger.info(f"🔗 MongoDB configured: {settings.mongodb_database} @ {settings.mongodb_url}")
    
    logger.info("✅ Dependency configuration completed successfully!")
    logger.info(f"📊 Total services registered: {len(container.get_registrations())}")


def configure_test_dependencies() -> None:
    """
    🧪 CONFIGURA dependências para ambiente de teste
    
    DIFERENÇAS DO AMBIENTE PRODUÇÃO:
    - Mocks para serviços externos (Azure)
    - Implementações em memória
    - Sem side effects
    - Execução mais rápida
    
    USO:
    ```python
    # Em testes
    container.clear()  # Limpa configuração padrão
    configure_test_dependencies()  # Carrega mocks
    ```
    """
    
    logger.info("🧪 Configuring TEST dependencies...")
    
    # TODO: Implementar mocks quando necessário
    # Por enquanto, usa as mesmas implementações
    configure_dependencies()
    
    logger.info("✅ TEST dependency configuration completed!")


def get_registered_services() -> dict:
    """
    📋 OBTÉM informações sobre serviços registrados
    
    Útil para debugging e documentação
    
    Returns:
        Dict com informações dos serviços registrados
    """
    
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
    """
    ✅ VALIDA se a configuração está correta
    
    VERIFICAÇÕES:
    1. Todas as interfaces essenciais estão registradas
    2. Implementações podem ser resolvidas
    3. Não há dependências circulares
    
    Returns:
        True se configuração válida, False caso contrário
    """
    
    logger.info("🔍 Validating dependency configuration...")
    
    # Interfaces essenciais que devem estar registradas
    essential_interfaces = [
        IImageCategorizer,
        IImageExtractor,
        IContextBuilder,
        IFigureProcessor,
        IDocumentAnalysisOrchestrator,
        IAnalyzeService,
        ISimplePersistenceService  # MongoDB sempre deve estar registrado
    ]
    
    try:
        # Verifica se todas as interfaces estão registradas
        for interface in essential_interfaces:
            if not container.is_registered(interface):
                logger.error(f"❌ Interface not registered: {interface.__name__}")
                return False
            
            logger.debug(f"✅ Interface registered: {interface.__name__}")
        
        # Tenta resolver o serviço principal para validar toda a árvore
        logger.info("🔧 Testing full dependency resolution...")
        analyze_service = container.resolve(IAnalyzeService)
        
        if analyze_service is None:
            logger.error("❌ Failed to resolve IAnalyzeService")
            return False
        
        logger.info("✅ Dependency configuration validation PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Dependency configuration validation FAILED: {str(e)}")
        return False


# ==================================================================================
# 🚀 AUTO-CONFIGURATION
# ==================================================================================
# Configura automaticamente quando o módulo é importado
# Isso garante que as dependências estejam sempre disponíveis

logger.info("🚀 Auto-configuring dependencies...")
configure_dependencies()

# Valida configuração durante importação
if validate_configuration():
    logger.info("🎉 SmartQuest DI Container ready!")
else:
    logger.error("💥 DI Container configuration failed!")


# ==================================================================================
# 📝 EXEMPLO DE USO
# ==================================================================================
"""
COMO USAR A CONFIGURAÇÃO:

1. IMPORTAÇÃO AUTOMÁTICA:
```python
# Apenas importar já configura tudo
from app.config.di_config import container

# Resolver qualquer serviço
service = container.resolve(IAnalyzeService)
```

2. RECONFIGURAÇÃO PARA TESTES:
```python
from app.config.di_config import configure_test_dependencies
from app.core.di_container import container

# Limpar e reconfigurar
container.clear()
configure_test_dependencies()
```

3. DEBUGGING:
```python
from app.config.di_config import get_registered_services

# Ver todos os serviços
services = get_registered_services()
print(services)
```

4. VALIDAÇÃO:
```python
from app.config.di_config import validate_configuration

if validate_configuration():
    print("✅ Configuration OK")
else:
    print("❌ Configuration FAILED")
```

BENEFÍCIOS ALCANÇADOS:
✅ Configuração centralizada e visível
✅ Auto-configuração na importação
✅ Validação automática de dependências
✅ Suporte a diferentes ambientes
✅ Debugging facilitado
✅ Zero configuração manual necessária
"""