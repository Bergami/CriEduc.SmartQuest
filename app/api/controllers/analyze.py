from fastapi import APIRouter, UploadFile, File, Query, Request
from typing import Optional
from datetime import datetime, date, time

# IMPORTANTE: Importar di_config PRIMEIRO para configurar dependências
from app.config import di_config  # Configura automaticamente todas as dependências

# Importações dos novos serviços e dos existentes
from app.services.extraction.document_extraction_service import DocumentExtractionService
from app.services.core.analyze_service import AnalyzeService
from app.validators.analyze_validator import AnalyzeValidator
from app.dtos.responses.document_response_dto import DocumentResponseDTO
from app.dtos.responses.analyze_document_response_dto import AnalyzeDocumentResponseDTO
from app.dtos.responses.document_list_response_dto import DocumentListResponseDTO, PaginationMetadata
from app.core.exceptions import (
    DocumentProcessingError,
    ValidationException
)
from app.core.utils import handle_exceptions
from app.core.logging import structured_logger
from fastapi import HTTPException


router = APIRouter()

@router.post("/analyze_document", response_model=DocumentResponseDTO)
@handle_exceptions("document_analysis")
async def analyze_document(
    request: Request,
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(..., description="PDF file for analysis")
) -> DocumentResponseDTO:
    """
    Analisa um documento PDF com arquitetura SOLID.
    
    Fluxo:
    1. Valida entrada
    2. Verifica duplicatas (retorna se já processado)
    3. Extrai dados do documento
    4. Orquestra análise com modelos
    5. Converte para DTO da API
    6. Persiste resultado no MongoDB
    """
    structured_logger.info(
        "Starting document analysis with SOLID architecture",
        context={"email": email, "filename": file.filename}
    )
    
    # --- VALIDAÇÃO ---
    AnalyzeValidator.validate_all(file, email)

    # --- ETAPA 1: Verificação de Duplicatas ---
    from app.core.di_container import container
    from app.services.core.duplicate_check_service import DuplicateCheckService
    from app.services.persistence import ISimplePersistenceService
    from app.core.interfaces import IAnalyzeService
    
    duplicate_service = container.resolve(DuplicateCheckService)
    duplicate_result = await duplicate_service.check_and_handle_duplicate(email, file)
    
    # Se é duplicata processada, retornar dados existentes
    if not duplicate_result.should_process:
        return duplicate_result.existing_response
    
    # --- ETAPA 2: Extração de Dados ---
    extracted_data = await DocumentExtractionService.get_extraction_data(file, email)
    if not extracted_data:
        raise DocumentProcessingError(
            "Failed to extract any data from the document. "
            "The file might be empty, corrupted, or in an unsupported format."
        )
    
    structured_logger.info(
        "Data extraction completed",
        context={"email": email, "filename": file.filename}
    )

    # --- ETAPA 3: Orquestração da Análise ---
    analyze_service = container.resolve(IAnalyzeService)
    internal_response = await analyze_service.process_document_with_models(
        extracted_data=extracted_data,
        email=email,
        filename=file.filename,
        file=file
    )
    
    # --- ETAPA 4: Conversão para DTO da API ---
    api_response = DocumentResponseDTO.from_internal_response(internal_response)
    
    # --- ETAPA 5: Persistência no MongoDB ---
    persistence_service = container.resolve(ISimplePersistenceService)
    await persistence_service.save_completed_analysis(
        email=email,
        filename=file.filename,
        file_size=duplicate_result.file_size,
        response_dict=api_response.dict()
    )
    
    structured_logger.info(
        "Document analysis completed successfully",
        context={
            "email": email,
            "document_id": internal_response.document_id,
            "questions_count": len(internal_response.questions),
            "context_blocks_count": len(internal_response.context_blocks),
            "migration_status": "100_percent_pydantic_flow"
        }
    )

    return api_response

@router.get("/analyze_document/{id}", response_model=AnalyzeDocumentResponseDTO)
@handle_exceptions("document_retrieval")
async def get_analyze_document(
    id: str,
    request: Request
) -> AnalyzeDocumentResponseDTO:
    """
    Recupera informações sobre um documento que já foi processado e armazenado.
    
    Consulta a coleção 'analyze_documents' no MongoDB usando o parâmetro 'id' fornecido.
    Se um documento com o 'id' fornecido existir, retorna seus detalhes na resposta.
    Se nenhum documento for encontrado, retorna o status 404 Not Found.
    
    Args:
        id: ID do documento no MongoDB
        request: Request context para logging
        
    Returns:
        Dados do documento analisado
        
    Raises:
        HTTPException: 404 se documento não encontrado
        HTTPException: 400 se ID inválido
        HTTPException: 500 para erros internos
    """
    structured_logger.info(
        "Starting document retrieval",
        context={"document_id": id}
    )
    
    # Validação básica do ID
    if not id or not id.strip():
        structured_logger.warning(
            "Invalid document ID provided", 
            context={"document_id": id}
        )
        raise HTTPException(
            status_code=400,
            detail="ID do documento é obrigatório e não pode estar vazio"
        )
    
    # Resolver serviço de persistência via DI Container
    from app.core.di_container import container
    from app.services.persistence import ISimplePersistenceService
    
    try:
        structured_logger.debug("Resolving persistence service via DI Container")
        persistence_service = container.resolve(ISimplePersistenceService)
        
        # Buscar documento no MongoDB
        structured_logger.debug(
            "Searching for document in MongoDB",
            context={"document_id": id}
        )
        
        document_record = await persistence_service.get_by_document_id(id)
        
        if document_record is None:
            structured_logger.info(
                "Document not found",
                context={"document_id": id}
            )
            raise HTTPException(
                status_code=404,
                detail="Documento não encontrado"
            )
        
        # Converter para DTO de resposta
        response_dto = AnalyzeDocumentResponseDTO.from_analyze_document_record(document_record)
        
        structured_logger.info(
            "Document retrieved successfully",
            context={
                "document_id": id,
                "user_email": document_record.user_email,
                "file_name": document_record.file_name,
                "status": document_record.status
            }
        )
        
        return response_dto
        
    except HTTPException:
        # Re-propagar HTTPExceptions (400, 404, etc.)
        raise
        
    except Exception as e:
        structured_logger.error(
            "Error retrieving document",
            context={"document_id": id, "error": str(e)}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar documento: {str(e)}"
        )


@router.get("/documents", response_model=DocumentListResponseDTO)
@handle_exceptions("documents_list")
async def list_documents(
    request: Request,
    email: str = Query(..., description="Email do usuário (obrigatório)"),
    start_date: Optional[date] = Query(None, description="Data início para filtro (formato YYYY-MM-DD, opcional)"),
    end_date: Optional[date] = Query(None, description="Data fim para filtro (formato YYYY-MM-DD, opcional)"),
    page: int = Query(1, ge=1, description="Número da página (mínimo 1)"),
    page_size: int = Query(10, ge=1, le=50, description="Itens por página (máximo 50)")
) -> DocumentListResponseDTO:
    """
    Lista documentos analisados com filtros e paginação.
    
    Retorna uma lista paginada de documentos previamente analisados e armazenados,
    permitindo filtros por email (obrigatório) e intervalo de datas (opcional).
    
    Args:
        request: Request context para logging
        email: Email do usuário (obrigatório)
        start_date: Data início do intervalo (opcional, requer end_date)
        end_date: Data fim do intervalo (opcional, requer start_date)
        page: Número da página (1-indexed, padrão 1)
        page_size: Quantidade de itens por página (padrão 10, máximo 50)
        
    Returns:
        Lista paginada de documentos com metadados de paginação
        
    Raises:
        HTTPException: 400 se validações falharem
        HTTPException: 422 se parâmetros inválidos
        HTTPException: 500 para erros internos
    """
    structured_logger.info(
        "Starting documents list",
        context={
            "email": email,
            "start_date": start_date,
            "end_date": end_date,
            "page": page,
            "page_size": page_size
        }
    )
    
    # Validação: email obrigatório e não vazio
    if not email or not email.strip():
        structured_logger.warning(
            "Invalid email provided",
            context={"email": email}
        )
        raise HTTPException(
            status_code=400,
            detail="Email é obrigatório e não pode estar vazio"
        )
    
    # Validação: se uma data for fornecida, ambas devem ser
    if (start_date is not None and end_date is None) or (start_date is None and end_date is not None):
        structured_logger.warning(
            "Incomplete date range",
            context={"start_date": start_date, "end_date": end_date}
        )
        raise HTTPException(
            status_code=400,
            detail="Se informar data de início, deve informar data de fim (e vice-versa)"
        )
    
    # Validação: start_date deve ser <= end_date
    if start_date is not None and end_date is not None and start_date > end_date:
        structured_logger.warning(
            "Invalid date range",
            context={"start_date": start_date, "end_date": end_date}
        )
        raise HTTPException(
            status_code=400,
            detail="Data de início deve ser anterior ou igual à data de fim"
        )
    
    # Resolver serviço de persistência via DI Container
    from app.core.di_container import container
    from app.services.persistence import ISimplePersistenceService
    
    try:
        structured_logger.debug("Resolving persistence service via DI Container")
        persistence_service = container.resolve(ISimplePersistenceService)
        
        # Converter date para datetime (início às 00:00:00 e fim às 23:59:59)
        start_datetime = datetime.combine(start_date, time.min) if start_date else None
        end_datetime = datetime.combine(end_date, time.max) if end_date else None
        
        # Buscar documentos com filtros
        structured_logger.debug(
            "Searching for documents in MongoDB",
            context={
                "email": email,
                "has_date_filter": start_date is not None,
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "page": page,
                "page_size": page_size
            }
        )
        
        documents, total_count = await persistence_service.get_by_user_email_with_filters(
            email=email,
            start_date=start_datetime,
            end_date=end_datetime,
            page=page,
            page_size=page_size
        )
        
        # Converter documentos para DTOs
        items = [
            AnalyzeDocumentResponseDTO.from_analyze_document_record(doc)
            for doc in documents
        ]
        
        # Criar metadados de paginação
        pagination = PaginationMetadata.create(
            current_page=page,
            page_size=page_size,
            total_items=total_count
        )
        
        # Montar resposta
        response = DocumentListResponseDTO(
            items=items,
            pagination=pagination
        )
        
        structured_logger.info(
            "Documents list retrieved successfully",
            context={
                "email": email,
                "documents_returned": len(items),
                "total_documents": total_count,
                "page": page,
                "total_pages": pagination.total_pages
            }
        )
        
        return response
        
    except HTTPException:
        # Re-propagar HTTPExceptions (400, 422, etc.)
        raise
        
    except Exception as e:
        structured_logger.error(
            "Error listing documents",
            context={
                "email": email,
                "page": page,
                "page_size": page_size,
                "error": str(e)
            }
        )
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao listar documentos: {str(e)}"
        )


# ==================================================================================
# 🧹 ENDPOINTS REMOVIDOS: analyze_document_mock e analyze_document_with_figures
# Removidos após confirmação de que o endpoint principal /analyze_document está funcionando
# ==================================================================================
