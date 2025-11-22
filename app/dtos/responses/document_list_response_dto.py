"""
DTO para resposta paginada do endpoint GET /analyze/documents

Representa uma lista paginada de documentos com metadados de paginação.
"""

from typing import List
from pydantic import BaseModel, Field

from app.dtos.responses.analyze_document_response_dto import AnalyzeDocumentResponseDTO


class PaginationMetadata(BaseModel):
    """
    Metadados de paginação para listas de recursos.
    
    Fornece informações sobre a página atual, total de itens,
    e navegação entre páginas.
    """
    
    current_page: int = Field(..., ge=1, description="Número da página atual (1-indexed)")
    page_size: int = Field(..., ge=1, le=50, description="Quantidade de itens por página")
    total_items: int = Field(..., ge=0, description="Total de itens disponíveis")
    total_pages: int = Field(..., ge=0, description="Total de páginas disponíveis")
    has_next: bool = Field(..., description="Indica se existe próxima página")
    has_previous: bool = Field(..., description="Indica se existe página anterior")

    class Config:
        """Configuração do modelo Pydantic."""
        schema_extra = {
            "example": {
                "current_page": 1,
                "page_size": 10,
                "total_items": 25,
                "total_pages": 3,
                "has_next": True,
                "has_previous": False
            }
        }

    @classmethod
    def create(
        cls,
        current_page: int,
        page_size: int,
        total_items: int
    ) -> "PaginationMetadata":
        """
        Factory method para criar metadados de paginação.
        
        Args:
            current_page: Página atual (1-indexed)
            page_size: Itens por página
            total_items: Total de itens disponíveis
            
        Returns:
            Instância de PaginationMetadata com cálculos automáticos
        """
        # Calcular total de páginas (arredondar para cima)
        total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0
        
        # Determinar navegação
        has_next = current_page < total_pages
        has_previous = current_page > 1
        
        return cls(
            current_page=current_page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )


class DocumentListResponseDTO(BaseModel):
    """
    DTO para resposta paginada de lista de documentos.
    
    Retorna uma lista de documentos analisados com metadados
    de paginação para navegação eficiente.
    """
    
    items: List[AnalyzeDocumentResponseDTO] = Field(
        ..., 
        description="Lista de documentos analisados"
    )
    pagination: PaginationMetadata = Field(
        ..., 
        description="Metadados de paginação"
    )

    class Config:
        """Configuração do modelo Pydantic."""
        schema_extra = {
            "example": {
                "items": [
                    {
                        "_id": "507f1f77bcf86cd799439011",
                        "document_name": "prova_matematica.pdf",
                        "status": "completed",
                        "analysis_results": {
                            "document_id": "doc_123",
                            "email": "professor@escola.com",
                            "filename": "prova_matematica.pdf",
                            "questions": [],
                            "context_blocks": []
                        },
                        "created_at": "2025-01-15T10:30:00Z",
                        "user_email": "professor@escola.com"
                    }
                ],
                "pagination": {
                    "current_page": 1,
                    "page_size": 10,
                    "total_items": 25,
                    "total_pages": 3,
                    "has_next": True,
                    "has_previous": False
                }
            }
        }
