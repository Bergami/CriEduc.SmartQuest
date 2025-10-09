"""
Interface abstrata para serviços de categorização de imagens.

Esta interface aplica o Dependency Inversion Principle (DIP), permitindo que o AnalyzeService
dependa de uma abstração em vez de implementações concretas.

Fase 2.3 da refatoração do AnalyzeService.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List
from app.models.internal.image_models import InternalImageData


class ImageCategorizationInterface(ABC):
    """
    Interface para serviços de categorização de imagens.
    
    Esta interface define o contrato que todos os serviços de categorização
    de imagens devem implementar, permitindo flexibilidade na escolha da
    implementação e facilitando testes unitários.
    """
    
    @abstractmethod
    def categorize_extracted_images(
        self,
        image_data: Dict[str, str],
        azure_result: Dict[str, Any],
        document_id: str = "unknown"
    ) -> Tuple[List[InternalImageData], List[InternalImageData]]:
        """
        Categoriza imagens extraídas em acadêmicas e não-acadêmicas.
        
        Args:
            image_data: Dicionário com dados das imagens extraídas.
                       Chaves são IDs das imagens, valores são dados base64.
            azure_result: Resultado do processamento Azure Document Intelligence
                         contendo metadados e informações de layout.
            document_id: Identificador único do documento para logging/debugging.
                        Default: "unknown"
        
        Returns:
            Tupla contendo:
            - List[InternalImageData]: Lista de imagens categorizadas como acadêmicas
            - List[InternalImageData]: Lista de imagens categorizadas como não-acadêmicas
        
        Raises:
            ValueError: Se image_data estiver vazio ou inválido
            TypeError: Se os tipos dos parâmetros não forem os esperados
            ProcessingError: Se houver erro durante a categorização
        
        Example:
            >>> categorizer = SomeImageCategorizationService()
            >>> academic, non_academic = categorizer.categorize_extracted_images(
            ...     image_data={"img_1": "base64_data_1", "img_2": "base64_data_2"},
            ...     azure_result={"analyze_result": {...}},
            ...     document_id="doc_123"
            ... )
            >>> print(f"Academic images: {len(academic)}, Non-academic: {len(non_academic)}")
        """
        pass