"""
🎯 FASE 4: Interfaces Abstratas para Dependency Injection

CONCEITO DE INTERFACES:
- Interface é um "contrato" que define métodos que uma classe deve implementar
- Em Python, usamos Protocol (typing) ou ABC (Abstract Base Class)
- Interfaces permitem programar contra abstrações, não implementações concretas

BENEFÍCIOS DAS INTERFACES:
1. DESACOPLAMENTO: Código depende de abstração, não implementação
2. TESTABILIDADE: Fácil criar mocks que implementam a interface
3. FLEXIBILIDADE: Trocar implementações sem alterar código cliente
4. EXTENSIBILIDADE: Adicionar novas implementações facilmente

PADRÃO PROTOCOL:
- Mais Pythônico que ABC
- Duck typing + type hints
- Não requer herança explícita
- Checagem estática via mypy/pylance

EXEMPLO:
```python
class IEmailService(Protocol):
    def send_email(self, to: str, subject: str) -> bool: ...

class SMTPEmailService:  # Não precisa herdar de IEmailService
    def send_email(self, to: str, subject: str) -> bool:
        # Implementação SMTP
        return True

# Type checker reconhece automaticamente que SMTPEmailService implementa IEmailService
```
"""
from typing import Protocol, Dict, Any, List
from fastapi import UploadFile
from app.models.internal import InternalDocumentResponse, InternalImageData, InternalQuestion


class IImageCategorizer(Protocol):
    """
    🏷️ INTERFACE: Categorização de Imagens
    
    RESPONSABILIDADE:
    - Analisar e categorizar imagens extraídas de documentos
    - Classificar tipo de imagem (gráfico, diagrama, foto, etc.)
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - ImageCategorizationService (atual)
    - AIImageCategorizer (futuro - com ML)
    - MockImageCategorizer (testes)
    """
    
    async def categorize_images(self, images: List[InternalImageData]) -> List[InternalImageData]:
        """
        Categoriza uma lista de imagens extraídas.
        
        Args:
            images: Lista de imagens para categorizar
            
        Returns:
            Lista de imagens com categorias atribuídas
        """
        ...


class IImageExtractor(Protocol):
    """
    📸 INTERFACE: Extração de Imagens
    
    RESPONSABILIDADE:
    - Extrair imagens de documentos PDF
    - Processar e converter formatos
    - Identificar posições e metadados
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - ImageExtractionOrchestrator (atual)
    - PyMuPDFExtractor (alternativa)
    - MockImageExtractor (testes)
    """
    
    async def extract_images_from_pdf_data(self, extracted_data: Dict[str, Any]) -> List[InternalImageData]:
        """
        Extrai imagens dos dados processados do PDF.
        
        Args:
            extracted_data: Dados extraídos do documento
            
        Returns:
            Lista de imagens extraídas
        """
        ...


class IContextBuilder(Protocol):
    """
    🧱 INTERFACE: Construção de Context Blocks
    
    RESPONSABILIDADE:
    - Construir blocos de contexto a partir de questões e texto
    - Associar contexto relevante a cada questão
    - Estruturar informações para processamento
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - ContextBlockBuilder (atual)
    - AIContextBuilder (futuro - com NLP)
    - MockContextBuilder (testes)
    """
    
    async def build_context_blocks(self, 
                                 questions: List[InternalQuestion], 
                                 extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Constrói blocos de contexto para as questões.
        
        Args:
            questions: Lista de questões extraídas
            extracted_data: Dados brutos do documento
            
        Returns:
            Lista de context blocks estruturados
        """
        ...
    
    async def build_context_blocks_from_azure_figures(self,
                                                     azure_response: Dict[str, Any],
                                                     images_base64: Dict[str, str] = None,
                                                     document_id: str = None) -> List[Dict[str, Any]]:
        """
        Constrói context blocks a partir de figuras do Azure Document Intelligence.
        
        Args:
            azure_response: Resposta completa do Azure Document Intelligence
            images_base64: Dicionário mapeando IDs de figuras para dados base64
            
        Returns:
            Lista de context blocks estruturados
        """
        ...


class IFigureProcessor(Protocol):
    """
    🖼️ INTERFACE: Processamento de Figuras
    
    RESPONSABILIDADE:
    - Processar figuras através de serviços Azure
    - Extrair texto e metadados de imagens
    - Associar figuras a questões relevantes
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - AzureFigureProcessor (atual)
    - LocalFigureProcessor (alternativa)
    - MockFigureProcessor (testes)
    """
    
    async def process_figures(self, 
                            images: List[InternalImageData], 
                            context_blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa figuras e associa a context blocks.
        
        Args:
            images: Lista de imagens categorizadas
            context_blocks: Blocos de contexto das questões
            
        Returns:
            Dicionário com figuras processadas e associações
        """
        ...


class IDocumentAnalysisOrchestrator(Protocol):
    """
    🎭 INTERFACE: Orquestrador de Análise de Documentos
    
    RESPONSABILIDADE:
    - Coordenar o pipeline completo de análise
    - Orquestrar todas as fases do processamento
    - Agregar resultados finais
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - DocumentAnalysisOrchestrator (atual)
    - FastDocumentOrchestrator (otimizada)
    - MockDocumentOrchestrator (testes)
    """
    
    async def orchestrate_analysis(self,
                                    extracted_data: Dict[str, Any],
                                    email: str,
                                    filename: str,
                                    file: UploadFile) -> InternalDocumentResponse:
        """
        Orquestra a análise completa do documento.
        
        Args:
            extracted_data: Dados brutos extraídos
            email: Email do usuário
            filename: Nome do arquivo
            file: UploadFile para fallback
            
        Returns:
            Resposta estruturada completa
        """
        ...


class IAnalyzeService(Protocol):
    """
    🎯 INTERFACE: Serviço Principal de Análise
    
    RESPONSABILIDADE:
    - Validar dados de entrada
    - Delegar análise para orquestrador
    - Retornar resposta formatada
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - AnalyzeService (atual)
    - QuickAnalyzeService (versão simplificada)
    - MockAnalyzeService (testes)
    """
    
    async def process_document_with_models(self,
                                         extracted_data: Dict[str, Any],
                                         email: str,
                                         filename: str,
                                         file: UploadFile) -> InternalDocumentResponse:
        """
        Processa documento com modelos internos.
        
        Args:
            extracted_data: Dados brutos extraídos
            email: Email do usuário
            filename: Nome do arquivo
            file: UploadFile para fallback
            
        Returns:
            Resposta estruturada completa
        """
        ...


class IImageUploadService(Protocol):
    """
    🌐 INTERFACE: Serviço de Upload de Imagens
    
    RESPONSABILIDADE:
    - Fazer upload de imagens para storage externo (Azure Blob Storage)
    - Converter base64 em URLs públicas
    - Gerenciar nomenclatura e organização de arquivos
    
    IMPLEMENTAÇÕES POSSÍVEIS:
    - AzureImageUploadService (atual - Azure Blob Storage)
    - S3ImageUploadService (futuro - AWS S3)
    - LocalImageUploadService (desenvolvimento local)
    - MockImageUploadService (testes)
    """
    
    async def upload_images_and_get_urls(self,
                                       images_base64: Dict[str, str],
                                       document_id: str,
                                       document_guid: str = None) -> Dict[str, str]:
        """
        Faz upload de múltiplas imagens e retorna URLs públicas.
        
        Args:
            images_base64: Dicionário {image_id: base64_string}
            document_id: ID único do documento para organização
            document_guid: GUID único do documento (gerado se não fornecido)
            
        Returns:
            Dicionário {image_id: public_url}
            
        Raises:
            ValueError: Se configurações não estão disponíveis
            Exception: Se falha no upload
        """
        ...


# ==================================================================================
# 📝 DOCUMENTAÇÃO DE USO DAS INTERFACES
# ==================================================================================
"""
COMO USAR AS INTERFACES COM DI CONTAINER:

1. REGISTRO NO CONTAINER:
```python
from app.core.di_container import container

# Mapear interfaces para implementações concretas
container.register(IImageCategorizer, ImageCategorizationService)
container.register(IImageExtractor, ImageExtractionOrchestrator)
container.register(IContextBuilder, ContextBlockBuilder)
container.register(IFigureProcessor, AzureFigureProcessor)
container.register(IDocumentAnalysisOrchestrator, DocumentAnalysisOrchestrator)
```

2. CONSTRUTOR COM INTERFACES:
```python
class DocumentAnalysisOrchestrator:
    def __init__(self,
                 image_categorizer: IImageCategorizer,  # ← Interface, não implementação
                 image_extractor: IImageExtractor,      # ← Interface, não implementação
                 context_builder: IContextBuilder,      # ← Interface, não implementação
                 figure_processor: IFigureProcessor):   # ← Interface, não implementação
        self._image_categorizer = image_categorizer
        self._image_extractor = image_extractor
        self._context_builder = context_builder
        self._figure_processor = figure_processor
```

3. RESOLUÇÃO AUTOMÁTICA:
```python
# O container automaticamente resolve todas as interfaces
orchestrator = container.resolve(IDocumentAnalysisOrchestrator)
# Nenhuma dependência manual necessária!
```

4. FACILITA TESTES:
```python
# Mock implementations para testes
class MockImageCategorizer:
    async def categorize_images(self, images): return images

class MockImageExtractor:
    async def extract_images_from_pdf_data(self, data): return []

# Registrar mocks para testes
test_container.register(IImageCategorizer, MockImageCategorizer)
test_container.register(IImageExtractor, MockImageExtractor)
```

BENEFÍCIOS ALCANÇADOS:
✅ Zero acoplamento entre classes
✅ Fácil substituição de implementações
✅ Testes simplificados com mocks
✅ Configuração centralizada no container
✅ Auto-wiring baseado em type hints
✅ Detecção de dependências circulares
✅ Gestão automática de ciclo de vida
"""