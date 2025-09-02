from fastapi import APIRouter, UploadFile, File, Query, Request
from typing import Dict, Any
from app.services.analyze_service import AnalyzeService
from app.services.document_processing_orchestrator import DocumentProcessingOrchestrator
from app.services.image_extraction import ImageExtractionOrchestrator, ImageExtractionMethod
from app.validators.analyze_validator import AnalyzeValidator
from app.adapters import DocumentResponseAdapter  # ✅ RESTAURADO - mantendo adapter
from app.core.exceptions import (
    DocumentProcessingError,
    InvalidEmailException,
    MissingFileException,
    InvalidDocumentFormatException,
    MultipleValidationException,
    ValidationException
)
from app.core.utils import handle_exceptions
from app.core.logging import structured_logger

router = APIRouter()

@router.post("/analyze_document")
@handle_exceptions("document_analysis")
async def analyze_document(
    request: Request,
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(..., description="PDF file for analysis")
):
    """
    Analisa documento PDF e extrai informações estruturadas via Azure Document Intelligence
    
    Args:
        request: Objeto Request do FastAPI
        email: Email do usuário para análise
        file: Arquivo PDF para análise
    
    Returns:
        Dados extraídos do documento em formato estruturado
    
    Raises:
        ValidationException: Erro de validação de entrada
        DocumentProcessingError: Erro no processamento do documento
    """
    
    # Log contexto da operação
    structured_logger.info(
        "Starting document analysis",
        context={
            "email": email,
            "filename": file.filename,
            "content_type": file.content_type,
            "has_file": True
        }
    )
    
    # Validação de entrada
    structured_logger.debug("Executing input validation")
    AnalyzeValidator.validate_all(file, email)
    structured_logger.debug("Input validation completed successfully")

    # Processamento do documento via Azure Document Intelligence
    structured_logger.debug("Starting document processing")
    structured_logger.info(
        "Using Azure Document Intelligence for processing",
        context={
            "email": email,
            "filename": file.filename,
            "file_size": file.size if hasattr(file, 'size') else None
        }
    )
    
    # 🆕 USAR MÉTODO REFATORADO COM MODELOS PYDANTIC (INTERNO)
    internal_response = await AnalyzeService.process_document_with_models(
        file=file, 
        email=email, 
        use_refactored=True
    )
    
    # ✅ USAR ADAPTER PARA MANTER ESTRUTURA DE RESPOSTA EXATA
    api_response = DocumentResponseAdapter.to_api_response(internal_response)
    
    structured_logger.info(
        "Document analysis completed successfully with Pydantic models (internal)",
        context={
            "email": email,
            "document_id": internal_response.document_id,
            "questions_count": len(internal_response.questions),
            "context_blocks_count": len(internal_response.context_blocks),
            "api_response_structure": "preserved_via_adapter",
            "migration_status": "internal_pydantic_external_dict"
        }
    )

    return api_response  # ✅ Retorna Dict no formato esperado

@router.post("/analyze_document_mock")
@handle_exceptions("azure_mock_document_analysis")
async def analyze_document_mock(
    request: Request,
    image_extraction_method: str = Query("manual_pdf", description="Image extraction method: manual_pdf (recommended for mock)")
):
    """
    Analisa documento usando a resposta mais recente salva do Azure Document Intelligence.
    
    Este endpoint não requer arquivo PDF físico e processa automaticamente o último arquivo
    de resposta do Azure salvo no diretório tests/responses/azure.
    
    🆕 REFATORADO: Agora usa classes isoladas de extração com método manual otimizado.
    
    Args:
        request: Objeto Request do FastAPI
        image_extraction_method: Método de extração (manual_pdf recomendado para mock)
    
    Returns:
        Dados extraídos do documento em formato estruturado usando a resposta salva do Azure
        
    Raises:
        DocumentProcessingError: Erro no carregamento ou processamento da resposta salva
    """
    
    # Log início da operação
    structured_logger.info(
        "Starting Azure mock document analysis with optimized extraction",
        context={
            "email": "test@mock.com",
            "filename": "last-processed-file.pdf",
            "processing_mode": "azure_saved_response",
            "use_refactored": True,
            "image_extraction_method": image_extraction_method
        }
    )
    
    # Validar método de extração
    try:
        from app.services.image_extraction import ImageExtractionMethod
        selected_method = ImageExtractionMethod(image_extraction_method)
    except ValueError:
        from app.services.image_extraction import ImageExtractionMethod
        available_methods = [method.value for method in ImageExtractionMethod]
        raise ValidationException(
            f"Invalid extraction method '{image_extraction_method}'. Available methods: {available_methods}"
        )
    
    # Processamento usando resposta salva do Azure com extração otimizada
    structured_logger.debug("Loading saved Azure response with optimized image extraction")
    
    extracted_data = await _process_mock_with_optimized_extraction(selected_method)
    
    structured_logger.info(
        "Azure mock document analysis completed successfully",
        context={
            "email": "test@mock.com",
            "processing_mode": "azure_saved_response",
            "image_extraction_method": image_extraction_method,
            "result_keys": list(extracted_data.keys()) if extracted_data else [],
            "images_extracted": len(extracted_data.get("images", {}))
        }
    )

    return extracted_data

@router.post("/analyze_document_with_figures")
@handle_exceptions("document_analysis_with_figures")
async def analyze_document_with_figures(
    request: Request,
    email: str = Query(..., description="User email for document analysis"),
    file: UploadFile = File(..., description="PDF file for analysis"),
    extraction_method: str = Query("azure_figures", description="Image extraction method: azure_figures or manual_pdf"),
    compare_methods: bool = Query(False, description="Compare both extraction methods for validation"),
    use_refactored: bool = Query(True, description="Use refactored version with enhanced processing")
):
    """
    Analisa documento PDF e extrai informações estruturadas com foco na extração de figuras.
    
    Este endpoint utiliza estratégias especializadas para extração de imagens:
    - azure_figures: Usa a API nativa do Azure Document Intelligence para obter figuras
    - manual_pdf: Usa a abordagem de recorte manual baseado em coordenadas (método atual)
    - compare_methods=True: Executa ambos os métodos para comparação de performance
    
    Args:
        request: Objeto Request do FastAPI
        email: Email do usuário para análise
        file: Arquivo PDF para análise (obrigatório)
        extraction_method: Método de extração de imagem (azure_figures ou manual_pdf)
        compare_methods: Se deve comparar ambos os métodos
        use_refactored: Usar versão refatorada com melhorias
    
    Returns:
        Dados extraídos do documento com informações detalhadas sobre extração de figuras
    
    Raises:
        ValidationException: Erro de validação de entrada
        DocumentProcessingError: Erro no processamento do documento
    """
    
    # Log contexto da operação
    structured_logger.info(
        "Starting document analysis with figures extraction",
        context={
            "email": email,
            "filename": file.filename,
            "content_type": file.content_type,
            "extraction_method": extraction_method,
            "compare_methods": compare_methods,
            "use_refactored": use_refactored,
            "file_size": file.size if hasattr(file, 'size') else None
        }
    )
    
    # Validação de entrada
    structured_logger.debug("Executing input validation")
    AnalyzeValidator.validate_all(file, email)
    
    # Validar método de extração
    try:
        selected_method = ImageExtractionMethod(extraction_method)
    except ValueError:
        available_methods = [method.value for method in ImageExtractionMethod]
        raise ValidationException(
            f"Invalid extraction method '{extraction_method}'. Available methods: {available_methods}"
        )
    
    structured_logger.debug("Input validation completed successfully")

    # Processamento do documento com Azure Document Intelligence
    structured_logger.debug("Starting document processing with Azure DI")
    
    try:
        # Primeiro, fazer a análise padrão do documento
        extracted_data = await AnalyzeService.process_document(file, email, use_refactored=use_refactored)
        
        # Resetar ponteiro do arquivo para extração de imagens
        await file.seek(0)
        
        # Inicializar orquestrador de extração de imagens
        image_orchestrator = ImageExtractionOrchestrator()
        
        if compare_methods:
            # Comparar ambos os métodos
            structured_logger.info("Comparing image extraction methods...")
            
            image_results = await image_orchestrator.extract_images_with_comparison(
                file=file,
                document_analysis_result=extracted_data.get("metadata", {}).get("raw_response", {}),
                document_id=f"{email}_{file.filename}"
            )
            
            # Adicionar resultados de comparação aos dados extraídos
            extracted_data["image_extraction_comparison"] = image_results
            
            # Usar o melhor resultado disponível para image_data
            best_images = {}
            for method_name, images in image_results["extraction_results"].items():
                if images and len(images) > len(best_images):
                    best_images = images
            
            extracted_data["image_data"] = best_images
            
            structured_logger.info(
                "Image extraction comparison completed",
                context={
                    "methods_tested": len(image_results["extraction_results"]),
                    "best_method_images": len(best_images)
                }
            )
            
        else:
            # Usar método específico
            structured_logger.info(f"Using single extraction method: {extraction_method}")
            
            extracted_images = await image_orchestrator.extract_images_single_method(
                method=selected_method,
                file=file,
                document_analysis_result=extracted_data.get("metadata", {}).get("raw_response", {}),
                document_id=f"{email}_{file.filename}"
            )
            
            # Adicionar imagens aos dados extraídos
            extracted_data["image_data"] = extracted_images
            
            # Adicionar métricas do método usado
            extractor_metrics = image_orchestrator._extractors[selected_method].get_performance_metrics()
            extracted_data["image_extraction_metrics"] = {
                "method_used": extraction_method,
                "performance": extractor_metrics
            }
            
            structured_logger.info(
                "Single method image extraction completed",
                context={
                    "method": extraction_method,
                    "images_extracted": len(extracted_images)
                }
            )
        
        # Log final
        structured_logger.info(
            "Document analysis with figures completed successfully",
            context={
                "email": email,
                "extraction_method": extraction_method,
                "compare_methods": compare_methods,
                "use_refactored": use_refactored,
                "total_images": len(extracted_data.get("image_data", {})),
                "result_keys": list(extracted_data.keys())
            }
        )

        return extracted_data
        
    except Exception as e:
        structured_logger.error(
            "Error in document analysis with figures",
            context={
                "email": email,
                "filename": file.filename,
                "extraction_method": extraction_method,
                "error": str(e)
            }
        )
        raise

async def _process_mock_with_optimized_extraction(selected_method: 'ImageExtractionMethod') -> Dict[str, Any]:
    """
    Processa mock usando extração de imagens otimizada com classes isoladas
    
    Args:
        selected_method: Método de extração selecionado
        
    Returns:
        Dados extraídos do documento com imagens otimizadas
    """
    from app.services.azure_response_service import AzureResponseService
    from app.services.image_extraction import ImageExtractionOrchestrator
    from app.services.mock_document_service import MockDocumentService
    from app.core.constants import MockDataConstants
    
    try:
        # 1. Carregar resposta salva do Azure (para coordenadas)
        azure_response = AzureResponseService.get_latest_azure_response()
        file_info = AzureResponseService.get_latest_file_info()
        
        structured_logger.info(f"Using Azure response from file: {file_info['filename']}")
        
        # 2. Processar texto e header usando método mock tradicional (sem imagens)
        extracted_data = await MockDocumentService.process_document_mock_text_only(
            email="test@mock.com",
            filename="last-processed-file.pdf"
        )
        
        # 3. Usar extração otimizada para imagens se temos PDF físico
        pdf_path = MockDataConstants.get_primary_mock_pdf_path()
        
        if pdf_path.exists() and selected_method.value == "manual_pdf":
            structured_logger.info("🔧 Using optimized manual PDF extraction for mock")
            
            # Criar mock UploadFile do PDF físico
            mock_file = await _create_mock_uploadfile_from_path(pdf_path)
            
            # Usar orquestrador otimizado
            orchestrator = ImageExtractionOrchestrator()
            
            optimized_images = await orchestrator.extract_images_single_method(
                method=selected_method,
                file=mock_file,
                document_analysis_result=azure_response,
                document_id="mock_optimized_extraction"
            )
            
            # Substituir imagens pelos resultados otimizados
            extracted_data["images"] = optimized_images
            
            # Adicionar métricas
            extractor_metrics = orchestrator._extractors[selected_method].get_performance_metrics()
            extracted_data["image_extraction_metrics"] = {
                "method_used": selected_method.value,
                "performance": extractor_metrics,
                "extraction_source": "optimized_manual_pdf"
            }
            
            structured_logger.info(
                f"✅ Optimized mock extraction completed: {len(optimized_images)} images",
                context={
                    "method": selected_method.value,
                    "images_count": len(optimized_images)
                }
            )
            
        else:
            # Fallback para método mock tradicional
            structured_logger.info("⚠️ Using traditional mock extraction (no physical PDF or unsupported method)")
            
            # Usar método tradicional para processar imagens
            full_mock_data = await MockDocumentService.process_document_mock(
                email="test@mock.com",
                filename="last-processed-file.pdf"
            )
            
            extracted_data["images"] = full_mock_data.get("images", [])
            
            extracted_data["image_extraction_metrics"] = {
                "method_used": "traditional_mock",
                "extraction_source": "mock_fallback",
                "images_count": len(extracted_data["images"])
            }
        
        return extracted_data
        
    except Exception as e:
        structured_logger.error(f"Error in optimized mock processing: {str(e)}")
        
        # Fallback completo para método tradicional
        structured_logger.info("🔄 Falling back to traditional mock processing")
        return await DocumentProcessingOrchestrator.process_document_from_saved_azure_response()

async def _create_mock_uploadfile_from_path(pdf_path) -> UploadFile:
    """
    Cria um mock UploadFile a partir de um arquivo físico
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        
    Returns:
        Mock UploadFile para uso com extractors
    """
    import io
    from fastapi import UploadFile
    
    # Ler conteúdo do arquivo
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
    
    # Criar mock UploadFile
    mock_file = UploadFile(
        filename=pdf_path.name,
        file=io.BytesIO(file_content),
        content_type="application/pdf"
    )
    
    return mock_file