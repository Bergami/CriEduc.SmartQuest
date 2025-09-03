"""
Document Processing Orchestrator

Classe orquestradora responsável por direcionar o processamento de documentos
entre diferentes fluxos (Azure real, Azure mock, Mock tradicional).
"""
from typing import Dict, Any
from uuid import uuid4
from fastapi import UploadFile

from app.core.logging import logger
from app.core.exceptions import DocumentProcessingError
from app.services.azure_response_service import AzureResponseService
from app.services.mock_document_service import MockDocumentService
from app.models.internal.document_models import InternalDocumentResponse, InternalDocumentMetadata
from app.models.internal.image_models import InternalImageData
from app.models.internal.context_models import InternalContextBlock
from app.models.internal.question_models import InternalQuestion


class DocumentProcessingOrchestrator:
    """
    Orquestrador principal para processamento de documentos.
    
    Decide qual fluxo usar baseado nos parâmetros e direciona o processamento
    para o serviço apropriado.
    """
    
    @staticmethod
    async def process_document_with_file(
        file: UploadFile, 
        email: str, 
        use_json_fallback: bool = False,
        use_refactored: bool = False
    ) -> Dict[str, Any]:
        """
        Processa documento real enviado pelo usuário.
        
        Args:
            file: Arquivo enviado pelo usuário
            email: Email do usuário
            use_json_fallback: Se deve usar fallback JSON
            use_refactored: Flag para usar versão refatorada
        """
        logger.info(f"Orchestrator: Processing document {file.filename} for {email}")
        
        # Importar aqui para evitar importação circular
        from app.services.analyze_service import AnalyzeService
        
        return await AnalyzeService.process_document(
            file=file,
            email=email,
            use_json_fallback=use_json_fallback,
            use_refactored=use_refactored
        )
    
    @staticmethod
    async def process_document_from_saved_azure_response() -> InternalDocumentResponse:
        """
        PHASE 2 COMPLETE: Returns InternalDocumentResponse instead of Dict.
        
        Processa documento usando a resposta mais recente salva do Azure.
        
        Este metodo simula o processamento de um documento como se tivesse sido
        enviado para o Azure, mas usando uma resposta previamente salva.
        
        Returns:
            InternalDocumentResponse: Complete Pydantic response model
            
        Raises:
            DocumentProcessingError: Se nao conseguir carregar ou processar a resposta salva
        """
        logger.info("Orchestrator: Processing document from saved Azure response")
        
        try:
            # 1. Carregar a resposta mais recente do Azure
            azure_response = AzureResponseService.get_latest_azure_response()
            file_info = AzureResponseService.get_latest_file_info()
            
            logger.info(f"Using Azure response from file: {file_info['filename']}")
            
            # 2. Converter resposta do Azure para formato esperado
            extracted_data = AzureResponseService.convert_azure_response_to_extracted_data(azure_response)
            
            # 3. Processar usando a lógica padrão do AnalyzeService
            result = await DocumentProcessingOrchestrator._process_extracted_data(
                extracted_data=extracted_data,
                email="test@mock.com",
                filename="last-processed-file.pdf",
                use_refactored=True  # Sempre usar versão refatorada para Azure mock
            )
            
            logger.info("Orchestrator: Successfully processed document from saved Azure response")
            return result
            
        except FileNotFoundError as e:
            error_msg = f"No saved Azure responses found: {str(e)}"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg)
            
        except Exception as e:
            error_msg = f"Failed to process saved Azure response: {str(e)}"
            logger.error(error_msg)
            raise DocumentProcessingError(error_msg)
    
    @staticmethod
    async def process_document_mock_traditional(email: str, filename: str = None) -> Dict[str, Any]:
        """
        Processa documento usando o sistema mock tradicional.
        
        Args:
            email: Email do usuário
            filename: Nome do arquivo (opcional)
        """
        logger.info(f"Orchestrator: Processing traditional mock document for {email}")
        
        return await MockDocumentService.process_document_mock(email, filename)
    
    @staticmethod
    async def _process_extracted_data(
        extracted_data: Dict[str, Any],
        email: str,
        filename: str,
        use_refactored: bool = True
    ) -> InternalDocumentResponse:
        """
        Processa dados já extraídos seguindo a lógica padrão do AnalyzeService.
        
        Este método replica a lógica de processamento do AnalyzeService a partir
        do ponto onde os dados já foram extraídos (linha 77 do process_document).
        
        Args:
            extracted_data: Dados extraídos (equivalente à linha 77)
            email: Email do usuário
            filename: Nome do arquivo
            use_refactored: Flag para usar versão refatorada
        """
        from app.parsers.header_parser import HeaderParser
        from app.parsers.question_parser import QuestionParser
        from app.services.azure_figure_processor import AzureFigureProcessor
        from app.services.refactored_context_builder import RefactoredContextBlockBuilder
        from app.services.image_categorization_service import ImageCategorizationService
        
        document_id = str(uuid4())
        
        logger.info(f"Processing extracted data: {len(extracted_data['text'])} characters")
        
        # Processar imagens para categorização
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        raw_image_data = extracted_data.get("image_data", {})
        
        # Se não há dados de imagem diretos, tentar carregar de arquivos salvos
        if not raw_image_data:
            logger.info("No direct image data found, attempting to load saved images")
            raw_image_data = await DocumentProcessingOrchestrator._try_load_saved_images_for_azure_response(
                azure_result, extracted_data
            )
        
        # Se chegou lista de metadados, carregar imagens correspondentes
        if isinstance(raw_image_data, list):
            logger.info("Converting Azure metadata list to images")
            raw_image_data = await DocumentProcessingOrchestrator._load_images_from_azure_figures(
                azure_result, extracted_data
            )
        
        # Categorizar imagens se disponíveis
        if isinstance(raw_image_data, dict) and raw_image_data and azure_result:
            logger.info(f"Categorizing {len(raw_image_data)} extracted images")
            header_images, content_images = ImageCategorizationService.categorize_extracted_images(
                raw_image_data, azure_result
            )
            logger.info(f"Categorized {len(header_images)} header images and {len(content_images)} content images")
        else:
            logger.info(f"No images available for categorization. raw_image_data type: {type(raw_image_data)}, length: {len(raw_image_data) if hasattr(raw_image_data, '__len__') else 'N/A'}")
            header_images, content_images = [], {}
        
        # Processar header com imagens categorizadas
        header_data = HeaderParser.parse(extracted_data["text"], header_images)
        
        # Use categorized content images from the extracted data
        image_data = content_images
        
        if image_data:
            logger.info(f"{len(image_data)} categorized content images available")
        
        # Extrair questões usando parser padrão
        question_data = QuestionParser.extract(extracted_data["text"], image_data)
        
        # 🆕 FEATURE FLAG: Usar versão refatorada se habilitada
        if use_refactored:
            logger.info("Using REFACTORED version with improvements")
            
            # 🆕 PROCESSAR FIGURAS DO AZURE PARA ASSOCIAÇÃO COM QUESTÕES E CONTEXTOS
            azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
            if azure_result and "figures" in azure_result:
                processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
                logger.info(f"{len(processed_figures)} figures processed from Azure")
                
                # 🆕 CRIAR CONTEXT BLOCKS AVANÇADOS COM TEXTOS ASSOCIADOS
                context_builder = RefactoredContextBlockBuilder()
                enhanced_context_blocks = context_builder.build_context_blocks_from_azure_figures(
                    azure_result, image_data or {}
                )
                
                logger.info(f"{len(enhanced_context_blocks)} enhanced context blocks created")
                
                # Usar context blocks avançados se disponíveis
                if enhanced_context_blocks:
                    question_data["context_blocks"] = enhanced_context_blocks
                
                # Associar figuras às questões
                enhanced_questions = AzureFigureProcessor.associate_figures_to_questions(
                    processed_figures, question_data["questions"]
                )
                question_data["questions"] = enhanced_questions
                
                logger.info("Questions enhanced with figure associations")
            else:
                logger.info("No Azure figures data, using standard refactored extraction")
        else:
            logger.info("Using STANDARD version (legacy)")
            
        logger.info(f"Questions found: {len(question_data['questions'])}")
        logger.info(f"Context blocks: {len(question_data['context_blocks'])}")

        # 🚀 PHASE 2 COMPLETE: Return InternalDocumentResponse instead of Dict
        logger.info("Creating InternalDocumentResponse with native Pydantic models")
        
        # Convert raw image data to InternalImageData if needed
        all_images = []
        if raw_image_data and isinstance(raw_image_data, dict):
            all_images = [
                InternalImageData(
                    id=img_id,
                    base64_data=img_data,
                    filename=f"image_{img_id}",
                    category="content"  # Default category
                ) for img_id, img_data in raw_image_data.items()
            ]
        
        # Create InternalDocumentMetadata
        document_metadata = InternalDocumentMetadata(
            **header_data,  # This spreads all header fields
            content_images=all_images,
            extraction_confidence=1.0,
            processing_notes="Processed with PHASE 2 complete migration"
        )
        
        # Convert questions and context_blocks if they're still in Dict format
        pydantic_questions = []
        if question_data["questions"]:
            pydantic_questions = [
                InternalQuestion.from_legacy_question(q) if isinstance(q, dict) else q
                for q in question_data["questions"]
            ]
        
        pydantic_context_blocks = []
        if question_data["context_blocks"]:
            pydantic_context_blocks = [
                InternalContextBlock.from_legacy_context_block(cb) if isinstance(cb, dict) else cb
                for cb in question_data["context_blocks"]
            ]
        
        # Create final InternalDocumentResponse
        internal_response = InternalDocumentResponse(
            email=email,
            document_id=document_id,
            filename=filename,
            document_metadata=document_metadata,
            questions=pydantic_questions,
            context_blocks=pydantic_context_blocks,
            extracted_text=extracted_data.get("text", ""),
            provider_metadata=extracted_data.get("metadata", {}),
            all_images=all_images
        )
        
        logger.info("✅ PHASE 2: InternalDocumentResponse created successfully with native Pydantic models")
        logger.info("Document processing completed successfully")
        return internal_response
    
    @staticmethod
    async def _try_load_saved_images_for_azure_response(
        azure_result: Dict[str, Any], 
        extracted_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Tenta carregar imagens salvas para uma resposta do Azure.
        """
        logger.info("Attempting to load saved images for Azure response")
        
        # Primeiro, verificar se há figuras no Azure result
        figures = azure_result.get("figures", [])
        if not figures:
            logger.info("No figures found in Azure result")
            return {}
        
        logger.info(f"Found {len(figures)} figures in Azure result")
        
        # Implementação temporária - evitar erro até implementar métodos apropriados
        try:
            # TODO: Implementar método para carregar imagens salvas do cache
            logger.info("Attempting to load saved images (placeholder implementation)")
            saved_images = {}
            
            if saved_images:
                logger.info(f"Loaded {len(saved_images)} images from saved files")
                return saved_images
            
        except Exception as e:
            logger.error(f"Error loading saved images: {str(e)}")
        
        logger.info("No saved images found")
        return {}
    
    @staticmethod
    async def _load_images_from_azure_figures(
        azure_result: Dict[str, Any], 
        extracted_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Carrega imagens baseadas nas figuras do Azure result.
        """
        logger.info("Loading images from Azure figures")
        
        figures = azure_result.get("figures", [])
        if not figures:
            return {}
        
        # Tentar carregar de arquivos salvos usando IDs das figuras
        try:
            from app.services.analyze_service import AnalyzeService
            
            figures_metadata = []
            for figure in figures:
                if figure.get("id"):
                    figures_metadata.append({"id": figure["id"]})
            
            if figures_metadata:
                saved_images = await AnalyzeService._load_images_from_metadata(
                    figures_metadata, extracted_data
                )
                logger.info(f"Loaded {len(saved_images)} images from Azure figures")
                return saved_images
                
        except Exception as e:
            logger.error(f"Error loading images from Azure figures: {str(e)}")
        
        return {}
