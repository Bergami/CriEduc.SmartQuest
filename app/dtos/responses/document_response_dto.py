"""
Document Response DTOs

DTOs específicos para responses da API que mantêm compatibilidade com o formato esperado
pelos clientes, mas aproveitam os benefícios do Pydantic.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from ...models.internal.document_models import InternalDocumentResponse
from ...models.internal.context_models import InternalContextBlock
from ...models.internal.question_models import InternalQuestion


class AlternativeDTO(BaseModel):
    """DTO para alternativas de questões."""
    letter: str = Field(..., description="Letra da alternativa (A, B, C, D, E)")
    text: str = Field(..., description="Texto da alternativa")


class QuestionDTO(BaseModel):
    """DTO para questões na resposta da API."""
    number: int = Field(..., description="Número da questão")
    question: str = Field(..., description="Enunciado da questão")
    alternatives: List[AlternativeDTO] = Field(..., description="Alternativas da questão")
    hasImage: bool = Field(default=False, description="Se a questão tem imagem")
    context_id: Optional[int] = Field(default=None, description="ID do context block relacionado")


class SubContextDTO(BaseModel):
    """DTO para sub-contextos."""
    sequence: str = Field(..., description="Sequência (I, II, III, IV)")
    type: str = Field(..., description="Tipo do sub-contexto")
    title: str = Field(..., description="Título do sub-contexto")
    content: str = Field(..., description="Conteúdo do sub-contexto")
    images: List[str] = Field(default_factory=list, description="URLs públicas de imagens ou base64 (fallback)")


class ContextBlockDTO(BaseModel):
    """DTO para context blocks na resposta da API."""
    id: int = Field(..., description="ID do context block")
    type: List[str] = Field(..., description="Tipos de conteúdo")
    source: str = Field(default="exam_document", description="Fonte do contexto")
    statement: Optional[str] = Field(default=None, description="Declaração/instrução")
    title: Optional[str] = Field(default=None, description="Título do context block")
    hasImage: bool = Field(default=False, description="Se tem imagem")
    images: List[str] = Field(default_factory=list, description="URLs públicas de imagens ou base64 (fallback)")
    contentType: Optional[str] = Field(default=None, description="Tipo de conteúdo")
    paragraphs: Optional[List[str]] = Field(default=None, description="Parágrafos de texto")
    sub_contexts: Optional[List[SubContextDTO]] = Field(default=None, description="Sub-contextos")

    @classmethod
    def from_internal_context_block(cls, internal_cb: InternalContextBlock) -> "ContextBlockDTO":
        """Converte InternalContextBlock para ContextBlockDTO."""
        
        # Converter sub_contexts se existirem
        sub_contexts_dto = None
        if internal_cb.sub_contexts:
            sub_contexts_dto = [
                SubContextDTO(
                    sequence=sub.sequence,
                    type=sub.type,
                    title=sub.title,
                    content=sub.content,
                    images=sub.azure_image_urls if sub.azure_image_urls else sub.images,  # Priorizar Azure URLs
                )
                for sub in internal_cb.sub_contexts
            ]
        
        # Determinar images e contentType
        images = []
        content_type = None
        
        if internal_cb.sub_contexts:
            # Context blocks com sub_contexts: imagens ficam nos sub_contexts
            images = []
        else:
            # Context blocks simples: usar imagens do próprio block
            if internal_cb.azure_image_urls:
                # Priorizar URLs do Azure
                images = internal_cb.azure_image_urls
                content_type = "image/url"
            elif internal_cb.images:
                # Fallback para base64
                images = internal_cb.images
                content_type = "image/jpeg;base64"
            else:
                images = []
        
        # Determinar paragraphs
        paragraphs = None
        if internal_cb.content and internal_cb.content.description is not None:
            paragraphs = internal_cb.content.description

        return cls(
            id=internal_cb.id,
            type=[t.value for t in internal_cb.type],
            source=internal_cb.source or "exam_document",
            statement=internal_cb.statement,
            title=internal_cb.title,
            hasImage=internal_cb.has_image,
            images=images,
            contentType=content_type,
            paragraphs=paragraphs,
            sub_contexts=sub_contexts_dto
        )


class HeaderDTO(BaseModel):
    """DTO para header do documento."""
    school: Optional[str] = Field(default=None, description="Nome da escola")
    teacher: Optional[str] = Field(default=None, description="Nome do professor")
    subject: Optional[str] = Field(default=None, description="Matéria")
    student: Optional[str] = Field(default=None, description="Nome do estudante")
    series: Optional[str] = Field(default=None, description="Série/turma")


class DocumentResponseDTO(BaseModel):
    """
    DTO principal para resposta da API de análise de documentos.
    
    Mantém compatibilidade com o formato esperado pelos clientes,
    mas aproveita os benefícios do Pydantic para validação e documentação.
    """
    email: str = Field(..., description="Email do usuário")
    document_id: str = Field(..., description="ID único do documento")
    filename: str = Field(..., description="Nome do arquivo")
    header: HeaderDTO = Field(..., description="Dados do cabeçalho")
    questions: List[QuestionDTO] = Field(default_factory=list, description="Questões extraídas")
    context_blocks: List[ContextBlockDTO] = Field(default_factory=list, description="Blocos de contexto")

    @classmethod
    def from_internal_response(cls, internal_response: InternalDocumentResponse) -> "DocumentResponseDTO":
        """Converte InternalDocumentResponse para DocumentResponseDTO."""
        
        # Converter header
        header_dto = HeaderDTO(
            school=internal_response.document_metadata.school,
            teacher=internal_response.document_metadata.teacher,
            subject=internal_response.document_metadata.subject,
            student=internal_response.document_metadata.student,
            series=None,  # series field does not exist in InternalDocumentMetadata
        )
        
        # Converter questions
        questions_dto = [
            QuestionDTO(
                number=q.number,
                question=q.content.statement,
                alternatives=[
                    AlternativeDTO(letter=opt.label, text=opt.text)
                    for opt in q.options
                ],
                hasImage=q.has_image,
                context_id=q.context_id
            )
            for q in internal_response.questions
        ]
        
        # Converter context_blocks
        context_blocks_dto = [
            ContextBlockDTO.from_internal_context_block(cb)
            for cb in internal_response.context_blocks
        ]
        
        return cls(
            email=internal_response.email,
            document_id=internal_response.document_id,
            filename=internal_response.filename,
            header=header_dto,
            questions=questions_dto,
            context_blocks=context_blocks_dto
        )

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "document_id": "doc-123",
                "filename": "prova.pdf",
                "header": {
                    "school": "UMEF Escola Exemplo",
                    "teacher": "Professor Silva",
                    "subject": "Matemática"
                },
                "questions": [
                    {
                        "number": 1,
                        "question": "Qual é o resultado de 2 + 2?",
                        "alternatives": [
                            {"letter": "A", "text": "3"},
                            {"letter": "B", "text": "4"},
                            {"letter": "C", "text": "5"}
                        ],
                        "hasImage": False,
                        "context_id": 1
                    }
                ],
                "context_blocks": [
                    {
                        "id": 1,
                        "type": ["text"],
                        "title": "Contexto Matemático",
                        "hasImage": False,
                        "images": [],
                        "paragraphs": ["Texto do contexto..."]
                    }
                ]
            }
        }
