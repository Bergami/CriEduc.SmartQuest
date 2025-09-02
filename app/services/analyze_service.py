"""
Analyze Service - Versão Limpa e Refatorada

Responsabilidades:
- Processamento de documentos reais via Azure
- Categorização de imagens
- Extração de header e questões
- Delegação para MockDocumentService para casos mock

Nota: Este serviço agora trabalha em conjunto com DocumentProcessingOrchestrator
para maior organização e flexibilidade de fluxos de processamento.
"""
import json
import os
import base64
from typing import Dict, Any
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from app.parsers.header_parser import PydanticHeaderParser
from app.parsers.question_parser import QuestionParser, PydanticQuestionParser
from app.services.document_extraction_factory import DocumentExtractionFactory
from app.services.mock_document_service import MockDocumentService
from app.services.image_categorization_service import ImageCategorizationService
from app.services.azure_figure_processor import AzureFigureProcessor
from app.models.internal import InternalDocumentResponse, InternalDocumentMetadata
from app.services.refactored_context_builder import RefactoredContextBlockBuilder
from app.core.exceptions import DocumentProcessingError
import logging

logger = logging.getLogger(__name__)


class AnalyzeService:
    """
    Serviço principal para análise de documentos.
    
    Responsabilidades:
    - Processar documentos reais via Azure Document Intelligence
    - Categorizar imagens extraídas
    - Extrair informações do header
    - Extrair questões e contexto
    - Delegar processamento mock para MockDocumentService
    """
    
    @staticmethod
    async def process_document(
        file: UploadFile, 
        email: str, 
        use_json_fallback: bool = False,
        use_refactored: bool = False
    ) -> Dict[str, Any]:
        """
        🚨 MÉTODO LEGACY: Processa documento usando Azure Document Intelligence
        
        ⚠️ DEPRECADO: Use process_document_with_models() para nova implementação Pydantic
        
        Args:
            file: Arquivo para processamento
            email: Email do usuário
            use_json_fallback: Se deve usar fallback JSON
            use_refactored: Flag para usar versão refatorada com melhorias
        """
        document_id = str(uuid4())
        logger.info(f"Processing document {file.filename} for {email}")

        if use_json_fallback:
            logger.info("Using JSON fallback mode")
            # Carrega resultado_parser.json
            with open("resultado_parser.json", "r", encoding="utf-8") as f:
                parsed_data = json.load(f)

            parsed_data["document_id"] = document_id
            parsed_data["email"] = email
            parsed_data["filename"] = file.filename
            parsed_data["extracted_text"] = "Documento carregado via fallback JSON."

            return parsed_data

        # Usar Document Extraction Factory (Azure)
        try:
            logger.info("Processing with Document Extraction Factory")
            extracted_data = await AnalyzeService._extract_text_and_metadata_with_factory(file)
            logger.info("Document extraction completed successfully")
        except Exception as e:
            logger.error(f"Document extraction failed: {str(e)}")
            error_message = f"Failed to process document: {str(e)}"
            raise DocumentProcessingError(error_message)
        
        logger.info(f"Text extracted: {len(extracted_data['text'])} characters")
        
        # 🆕 NOVA LÓGICA: Usar extratores isolados com fallback automático
        image_data = await AnalyzeService._extract_images_with_fallback(
            file=file,
            extracted_data=extracted_data,
            document_id=f"{email}_{file.filename}"
        )
        
        if image_data:
            logger.info(f"{len(image_data)} images extracted using optimized extractors")
        
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
                enhanced_context_blocks = context_builder.analyze_azure_figures_dynamically(
                    azure_result, image_data
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

        result = {
            "email": email,
            "document_id": document_id,
            "filename": file.filename,
            "header": extracted_data["header"],
            "questions": question_data["questions"],
            "context_blocks": question_data["context_blocks"]
        }
        
        # 🆕 LIMPEZA DO RESULTADO SEMPRE (independent da flag)
        context_builder = RefactoredContextBlockBuilder()
        result = context_builder.remove_associated_figures_from_result(result)
        logger.info("Associated figures and figure_ids cleaned from result")
        
        logger.info("Document processing completed successfully")
        return result

    @staticmethod
    async def process_document_with_models(
        file: UploadFile, 
        email: str, 
        use_refactored: bool = True
    ) -> InternalDocumentResponse:
        """
        🆕 VERSÃO REFATORADA: Processa documento usando modelos Pydantic tipados
        
        Args:
            file: Arquivo para processamento
            email: Email do usuário 
            use_refactored: Flag para usar versão refatorada (sempre True por padrão)
            
        Returns:
            InternalDocumentResponse: Response completo com tipagem forte
        """
        document_id = str(uuid4())
        logger.info(f"🔧 Processing document with models: {file.filename} for {email}")

        # Usar Document Extraction Factory (Azure)
        try:
            logger.info("Processing with Document Extraction Factory")
            extracted_data = await AnalyzeService._extract_text_and_metadata_with_factory(file)
            logger.info("Document extraction completed successfully")
        except Exception as e:
            logger.error(f"Document extraction failed: {str(e)}")
            error_message = f"Failed to process document: {str(e)}"
            raise DocumentProcessingError(error_message)
        
        logger.info(f"Text extracted: {len(extracted_data['text'])} characters")
        
        # Extração de imagens com fallback automático
        image_data = await AnalyzeService._extract_images_with_fallback(
            file=file,
            extracted_data=extracted_data,
            document_id=f"{email}_{file.filename}"
        )
        
        if image_data:
            logger.info(f"{len(image_data)} images extracted using optimized extractors")
        
        # Processar header usando PydanticHeaderParser
        logger.info("🆕 Using PydanticHeaderParser for metadata extraction")
        header_metadata = PydanticHeaderParser.parse(extracted_data["text"])
        
        # 🆕 MIGRAÇÃO PYDANTIC: Extrair questões e contextos usando PydanticQuestionParser
        logger.info("🆕 Using PydanticQuestionParser for questions and contexts extraction")
        context_blocks_pydantic, questions_pydantic = PydanticQuestionParser.parse(
            extracted_data["text"], image_data
        )
        
        # Processar versão refatorada com melhorias
        if use_refactored:
            logger.info("Using REFACTORED version with improvements")
            
            azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
            if azure_result and "figures" in azure_result:
                processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
                logger.info(f"{len(processed_figures)} figures processed from Azure")
                
                # 🚨 SIMPLIFICAÇÃO TEMPORÁRIA: Desabilitar RefactoredContextBuilder
                # TODO: Integrar RefactoredContextBuilder Pydantic na FASE 2
                logger.warning("RefactoredContextBuilder integration temporarily disabled - using basic Pydantic version")
        
        logger.info(f"Questions found: {len(questions_pydantic)}")
        logger.info(f"Context blocks: {len(context_blocks_pydantic)}")

        # 🆕 CRIAR RESPONSE USANDO MODELOS PYDANTIC DIRETAMENTE
        response = InternalDocumentResponse(
            email=email,
            document_id=document_id,
            filename=file.filename,
            document_metadata=header_metadata,
            questions=questions_pydantic,
            context_blocks=context_blocks_pydantic,
            extracted_text=extracted_data["text"],
            provider_metadata=extracted_data.get("metadata", {}),
            all_images=[]  # TODO: converter image_data para InternalImageData
        )
        
        logger.info("✅ Document processing completed successfully with models")
        return response

    @staticmethod
    async def _extract_images_with_fallback(
        file: UploadFile,
        extracted_data: Dict[str, Any],
        document_id: str
    ) -> Dict[str, str]:
        """
        Extrai imagens usando estratégia de fallback automático:
        1. Tenta método Manual PDF (rápido e alta qualidade)
        2. Se falhar, usa Azure Figures (mais lento mas confiável)
        
        Args:
            file: Arquivo PDF para extração
            extracted_data: Dados extraídos do documento
            document_id: ID único do documento
            
        Returns:
            Dicionário com figure_id -> base64_string das imagens extraídas
        """
        from app.services.image_extraction import ImageExtractionOrchestrator, ImageExtractionMethod
        
        logger.info("Starting image extraction with automatic fallback")
        
        # Resetar ponteiro do arquivo
        await file.seek(0)
        
        # Inicializar orquestrador
        orchestrator = ImageExtractionOrchestrator()
        
        # Obter raw_response do Azure para coordenadas
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        
        try:
            # STEP 1: Tentar método Manual PDF (rápido e alta qualidade)
            logger.info("STEP 1: Attempting Manual PDF extraction (primary method)")
            
            manual_images = await orchestrator.extract_images_single_method(
                method=ImageExtractionMethod.MANUAL_PDF,
                file=file,
                document_analysis_result=azure_result,
                document_id=document_id
            )
            
            if manual_images and len(manual_images) > 0:
                manual_metrics = orchestrator._extractors[ImageExtractionMethod.MANUAL_PDF].get_performance_metrics()
                logger.info(
                    f"✅ Manual PDF extraction successful: {len(manual_images)} images extracted in {manual_metrics.get('total_processing_time', 0):.2f}s"
                )
                return manual_images
            
            logger.warning("⚠️ Manual PDF extraction returned no images, attempting fallback")
            
        except Exception as e:
            logger.warning(f"⚠️ Manual PDF extraction failed: {str(e)}, attempting fallback")
        
        # Reset file pointer for fallback
        await file.seek(0)
        
        try:
            # STEP 2: Fallback para Azure Figures (mais lento mas confiável)
            logger.info("STEP 2: Using Azure Figures fallback (secondary method)")
            
            azure_images = await orchestrator.extract_images_single_method(
                method=ImageExtractionMethod.AZURE_FIGURES,
                file=file,
                document_analysis_result=azure_result,
                document_id=document_id
            )
            
            if azure_images and len(azure_images) > 0:
                azure_metrics = orchestrator._extractors[ImageExtractionMethod.AZURE_FIGURES].get_performance_metrics()
                logger.info(
                    f"✅ Azure Figures fallback successful: {len(azure_images)} images extracted in {azure_metrics.get('total_processing_time', 0):.2f}s"
                )
                return azure_images
                
            logger.warning("⚠️ Azure Figures fallback also returned no images")
            
        except Exception as e:
            logger.error(f"❌ Azure Figures fallback failed: {str(e)}")
        
        # STEP 3: Fallback para método legado se ambos falharem
        logger.info("STEP 3: Using legacy image extraction method (final fallback)")
        
        try:
            # Usar método legado do sistema atual
            legacy_images = extracted_data.get("images", {})
            
            if not legacy_images:
                # Tentar carregar de arquivos salvos
                legacy_images = await AnalyzeService._try_load_saved_images(extracted_data)
            
            if legacy_images:
                logger.info(f"✅ Legacy extraction successful: {len(legacy_images)} images loaded")
                return legacy_images
            
        except Exception as e:
            logger.error(f"❌ Legacy extraction failed: {str(e)}")
        
        # Se todos os métodos falharam
        logger.warning("❌ All image extraction methods failed, returning empty result")
        return {}

    @staticmethod
    async def process_document_mock(email: str, filename: str = None) -> Dict[str, Any]:
        """
        Delega o processamento mock para MockDocumentService
        """
        return await MockDocumentService.process_document_mock(email, filename)

    @staticmethod
    async def _extract_text_and_metadata_with_factory(file: UploadFile) -> Dict[str, Any]:
        """
        Extrai texto e metadados usando Document Extraction Factory.
        Suporta múltiplos provedores com fallback automático.
        """
        # Obter o provedor de extração configurado
        extractor = DocumentExtractionFactory.get_provider()
        provider_name = extractor.get_provider_name()
        
        logger.info(f"Using extraction provider: {provider_name}")
        
        # Extrair dados do documento
        extracted_data = await extractor.extract_document_data(file)
        
        # Obter dados de imagem do Azure para categorização
        raw_image_data = extracted_data.get("image_data", {})
        
        # Se não há dados de imagem diretos, tentar carregar de arquivos salvos
        if not raw_image_data:
            raw_image_data = await AnalyzeService._try_load_saved_images(extracted_data)
        
        # 🆕 USAR O NOVO SERVIÇO DE CATEGORIZAÇÃO
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        
        # Se chegou lista de metadados, carregar imagens correspondentes
        if isinstance(raw_image_data, list):
            logger.info("Converting Azure metadata list to images")
            base64_images = await AnalyzeService._load_images_from_metadata(raw_image_data, extracted_data)
            raw_image_data = base64_images
        
        # Categorizar usando o novo serviço (só se temos imagens base64)
        if isinstance(raw_image_data, dict) and raw_image_data:
            logger.info(f"Categorizing {len(raw_image_data)} extracted images")
            
            # Categorizar imagens
            header_images, content_images = ImageCategorizationService.categorize_extracted_images(
                raw_image_data, azure_result
            )
            
            logger.info(f"Categorization complete: {len(header_images)} header images, {len(content_images)} content images")
            
        else:
            logger.info("Skipping categorization - no valid image data available")
            header_images, content_images = [], {}
        
        # Fazer parse das informações do header com imagens categorizadas usando PydanticHeaderParser
        logger.info("🆕 Using PydanticHeaderParser for header extraction")
        header_metadata = PydanticHeaderParser.parse(extracted_data["text"], header_images)
        # Convert back to legacy format for compatibility with current return structure
        header_data = header_metadata.to_legacy_format()
        
        # Retornar dados estruturados compatíveis com o sistema atual
        return {
            "text": extracted_data["text"],
            "header": header_data,
            "images": content_images,  # Usar imagens de conteúdo categorizadas
            "metadata": {
                **extracted_data.get("metadata", {}),
                "extraction_provider": provider_name,
                "confidence": extracted_data.get("confidence", 0.0),
                "page_count": extracted_data.get("page_count", 1),
                "raw_response": extracted_data.get("metadata", {}).get("raw_response", {})
            }
        }
    
    @staticmethod
    async def _try_load_saved_images(extracted_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Tenta carregar imagens de arquivos salvos se não houver dados diretos
        """
        document_id = extracted_data.get("metadata", {}).get("document_id")
        if not document_id:
            return {}
            
        try:
            from app.services.storage.document_storage_service import DocumentStorageService
            
            storage = DocumentStorageService()
            base_path = storage.base_path
            provider_dir = base_path / "images" / "by_provider" / "azure" / document_id
            
            if provider_dir.exists():
                raw_image_data = {}
                for img_file in provider_dir.glob("*.jpg"):
                    figure_id = img_file.stem  # filename without extension
                    
                    # Ler arquivo de imagem e converter para base64
                    with open(img_file, 'rb') as f:
                        image_bytes = f.read()
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        raw_image_data[figure_id] = base64_image
                
                logger.info(f"Loaded {len(raw_image_data)} images from saved files")
                return raw_image_data
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error loading saved images: {str(e)}")
            return {}
    
    @staticmethod
    async def _load_images_from_metadata(metadata_list: list, extracted_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Carrega imagens base64 baseadas numa lista de metadados do Azure.
        
        Args:
            metadata_list: Lista de metadados das figuras do Azure
            extracted_data: Dados extraídos contendo informações do documento
            
        Returns:
            Dicionário com figure_id -> base64_string
        """
        logger.info(f"Processing {len(metadata_list)} metadata items for image loading")
        
        # Primeiro, tentar carregar de arquivos salvos usando os IDs dos metadados
        saved_images = await AnalyzeService._try_load_saved_images_with_metadata(metadata_list, extracted_data)
        if saved_images:
            logger.info(f"Loaded {len(saved_images)} images from saved files using metadata")
            return saved_images
        
        # Se não há arquivos salvos, tentar buscar no storage service padrão
        default_images = await AnalyzeService._try_load_saved_images(extracted_data)
        if default_images:
            logger.info(f"Loaded {len(default_images)} images from default storage")
            return default_images
        
        logger.warning("No images found for the provided metadata")
        return {}
    
    @staticmethod
    async def _try_load_saved_images_with_metadata(metadata_list: list, extracted_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Tenta carregar imagens salvas usando os IDs dos metadados
        """
        try:
            from app.services.storage.document_storage_service import DocumentStorageService
            
            storage = DocumentStorageService()
            base_path = storage.base_path
            
            # Procurar por diretórios de imagens do Azure
            azure_dirs = list((base_path / "images" / "by_provider" / "azure").glob("*"))
            
            # Procurar em todos os diretórios Azure por imagens correspondentes aos IDs
            for azure_dir in azure_dirs:
                if azure_dir.is_dir():
                    raw_image_data = {}
                    
                    for metadata in metadata_list:
                        if isinstance(metadata, dict) and 'id' in metadata:
                            figure_id = metadata['id']
                            
                            # Procurar por arquivo com esse ID
                            for img_file in azure_dir.glob(f"{figure_id}.*"):
                                # Ler arquivo de imagem e converter para base64
                                with open(img_file, 'rb') as f:
                                    image_bytes = f.read()
                                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                                    raw_image_data[figure_id] = base64_image
                                break
                    
                    if raw_image_data:
                        logger.info(f"Successfully loaded {len(raw_image_data)} images using metadata")
                        return raw_image_data
            
            return {}
                
        except Exception as e:
            logger.error(f"Error loading images with metadata: {str(e)}")
            return {}

    @staticmethod
    async def process_document_with_azure_response(
        azure_response: Dict[str, Any],
        email: str,
        filename: str,
        use_refactored: bool = True
    ) -> InternalDocumentResponse:
        """
        Processa um documento usando response já obtido do Azure Document Intelligence.
        
        Args:
            azure_response: Response completo do Azure já processado
            email: Email do usuário
            filename: Nome do arquivo para referência
            use_refactored: Se deve usar versão refatorada (Pydantic pipeline)
        
        Returns:
            InternalDocumentResponse com dados processados
        """
        logger.info(f"🔧 Processing document with saved Azure response: {filename} for {email}")
        
        try:
            # Gerar ID único para este processamento
            document_id = str(uuid4())
            
            # Extrair texto do Azure response
            extracted_text = azure_response.get("content", "")
            
            # Processar figuras do Azure response
            processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_response)
            logger.info(f"{len(processed_figures)} figures processed from Azure response")
            
            # Categorizar imagens (se houver)
            header_images, content_images = [], []
            if processed_figures:
                header_images, content_images = ImageCategorizationService.categorize_extracted_images(
                    processed_figures, azure_response
                )
                logger.info(f"Categorization complete: {len(header_images)} header images, {len(content_images)} content images")
            
            if use_refactored:
                # 🆕 PIPELINE PYDANTIC COMPLETO
                logger.info("🆕 Using PydanticHeaderParser for header extraction")
                document_metadata = PydanticHeaderParser.parse(extracted_text, header_images)
                
                # 🔧 EXTRAIR IMAGENS REAIS usando PDF mais recente + MANUAL_PDF PRIMEIRO
                logger.info("� Extracting images using last processed PDF + MANUAL_PDF strategy")
                extracted_images = {}  # Initialize with empty dict
                all_images = []
                
                if processed_figures:
                    try:
                        from app.services.image_extraction.image_extraction_orchestrator import ImageExtractionOrchestrator, ImageExtractionMethod
                        from app.services.utils.last_pdf_finder import LastPDFFinder
                        from fastapi import UploadFile
                        import io
                        
                        # Encontrar o PDF mais recente
                        last_pdf_path = LastPDFFinder.get_last_processed_pdf()
                        
                        if last_pdf_path:
                            logger.info(f"📄 Using last processed PDF: {last_pdf_path}")
                            
                            # Ler o PDF e criar UploadFile mock
                            with open(last_pdf_path, 'rb') as pdf_file:
                                pdf_content = pdf_file.read()
                            
                            # Criar UploadFile mock para compatibilidade
                            mock_file = UploadFile(
                                filename=os.path.basename(last_pdf_path),
                                file=io.BytesIO(pdf_content),
                                size=len(pdf_content)
                            )
                            
                            orchestrator = ImageExtractionOrchestrator()
                            
                            # Usar estratégia MANUAL_PDF com o último PDF
                            extracted_images = await orchestrator.extract_images_single_method(
                                method=ImageExtractionMethod.MANUAL_PDF,
                                file=mock_file,
                                document_analysis_result=azure_response,
                                document_id=document_id
                            )
                            
                            logger.info(f"✅ MANUAL_PDF extraction completed: {len(extracted_images)} images")
                        else:
                            logger.warning("❌ No processed PDF found - cannot extract images")
                            extracted_images = {}
                            
                    except Exception as e:
                        logger.error(f"❌ Failed to extract images with MANUAL_PDF: {str(e)}")
                        extracted_images = {}
                
                # Agora que temos extracted_images, usar no PydanticQuestionParser
                logger.info("�🆕 Using PydanticQuestionParser for questions and contexts extraction")
                
                # 🔧 CORREÇÃO: Usar extracted_images ao invés de processed_figures
                # extracted_images contém as imagens reais extraídas
                raw_image_data = extracted_images  # Dict[figure_id, base64_string]
                
                logger.info(f"📸 Passing {len(raw_image_data)} images to PydanticQuestionParser")
                
                # Usar PydanticQuestionParser
                context_blocks, questions = PydanticQuestionParser.parse(extracted_text, raw_image_data)
                
                logger.info("Using REFACTORED version with improvements")
                
                # Aplicar melhorias com RefactoredContextBlockBuilder (temporariamente simplificado)
                logger.warning("RefactoredContextBuilder integration temporarily disabled - using basic Pydantic version")
                
                logger.info(f"Questions found: {len(questions)}")
                logger.info(f"Context blocks: {len(context_blocks)}")
                
                # Converter extracted_images para InternalImageData
                if extracted_images:
                    try:
                        from app.models.internal.image_models import InternalImageData, ImageCategory, ImagePosition
                        
                        for figure in processed_figures:
                            figure_id = str(figure.get('id', f"fig_{len(all_images)}"))
                            
                            # Calcular posição
                            position = None
                            required_position_keys = ['x_position', 'y_position', 'width', 'height']
                            if all(key in figure for key in required_position_keys):
                                position = ImagePosition(
                                    x=figure.get('x_position', 0),
                                    y=figure.get('y_position', 0),
                                    width=figure.get('width', 0),
                                    height=figure.get('height', 0)
                                )
                            
                            # Usar imagem extraída se disponível, senão usar placeholder
                            base64_data = extracted_images.get(figure_id, "")
                            file_path = f"temp/figure_{figure_id}.png" if base64_data else ""
                            
                            image_data = InternalImageData(
                                id=figure_id,
                                file_path=file_path,
                                base64_data=base64_data,
                                page=figure.get('page_number', 1),
                                position=position,
                                azure_coordinates=figure.get('polygon'),
                                category=ImageCategory.FIGURE,
                                extracted_text=figure.get('caption', ''),
                                confidence_score=0.9 if base64_data else 0.0
                            )
                            
                            all_images.append(image_data)
                        
                        logger.info(f"✅ Created {len(all_images)} InternalImageData objects with real images")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to extract images with MANUAL_PDF: {str(e)}")
                        logger.info("🔄 Falling back to metadata-only placeholders")
                        
                        # Fallback: criar placeholders apenas com metadados
                        from app.models.internal.image_models import InternalImageData, ImageCategory, ImagePosition
                        
                        all_images = []  # Reset array for fallback
                        for figure in processed_figures:
                            figure_id = str(figure.get('id', f"fig_{len(all_images)}"))
                            
                            position = None
                            required_position_keys = ['x_position', 'y_position', 'width', 'height']
                            if all(key in figure for key in required_position_keys):
                                position = ImagePosition(
                                    x=figure.get('x_position', 0),
                                    y=figure.get('y_position', 0),
                                    width=figure.get('width', 0),
                                    height=figure.get('height', 0)
                                )
                            
                            image_data = InternalImageData(
                                id=figure_id,
                                file_path="",
                                base64_data="",
                                page=figure.get('page_number', 1),
                                position=position,
                                azure_coordinates=figure.get('polygon'),
                                category=ImageCategory.FIGURE,
                                extracted_text=figure.get('caption', ''),
                                confidence_score=0.0
                            )
                            
                            all_images.append(image_data)
                        
                        logger.warning(f"⚠️ Using {len(all_images)} placeholder images without base64 data")
                else:
                    logger.info("ℹ️ No figures found in Azure response")
                
                internal_response = InternalDocumentResponse(
                    email=email,
                    filename=filename,
                    document_id=document_id,
                    document_metadata=document_metadata,
                    questions=questions,
                    context_blocks=context_blocks,
                    all_images=all_images,  # ✅ CORRIGIDO: Usar imagens convertidas
                    extracted_text=extracted_text,
                    provider_metadata={"azure_response": azure_response}
                )
                
                logger.info("✅ Document processing completed successfully with saved Azure response")
                return internal_response
            
            else:
                # Pipeline legado (não recomendado)
                raise NotImplementedError("Legacy pipeline not supported for Azure response processing")
                
        except Exception as e:
            logger.error(f"Error processing document with Azure response: {str(e)}")
            raise DocumentProcessingError(f"Failed to process document with Azure response: {str(e)}")
