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
from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
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
        Processa documento usando Azure Document Intelligence com extração de imagens otimizada
        
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
        
        # Processar header usando modelo tipado
        legacy_header = HeaderParser.parse(extracted_data["text"])
        header_metadata = InternalDocumentMetadata.from_legacy_header(legacy_header)
        
        # Extrair questões usando parser padrão
        question_data = QuestionParser.extract(extracted_data["text"], image_data)
        
        # Processar versão refatorada com melhorias
        if use_refactored:
            logger.info("Using REFACTORED version with improvements")
            
            azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
            if azure_result and "figures" in azure_result:
                processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
                logger.info(f"{len(processed_figures)} figures processed from Azure")
                
                from app.services.refactored_context_builder import RefactoredContextBlockBuilder
                context_builder = RefactoredContextBlockBuilder()
                enhanced_context_blocks = context_builder.analyze_azure_figures_dynamically(
                    azure_result, image_data
                )
                
                logger.info(f"{len(enhanced_context_blocks)} enhanced context blocks created")
                
                if enhanced_context_blocks:
                    question_data["context_blocks"] = enhanced_context_blocks
                
                enhanced_questions = AzureFigureProcessor.associate_figures_to_questions(
                    processed_figures, question_data["questions"]
                )
                question_data["questions"] = enhanced_questions
                
                logger.info("Questions enhanced with figure associations")
        
        logger.info(f"Questions found: {len(question_data['questions'])}")
        logger.info(f"Context blocks: {len(question_data['context_blocks'])}")

        # Criar response usando modelo tipado
        response = InternalDocumentResponse(
            email=email,
            document_id=document_id,
            filename=file.filename,
            document_metadata=header_metadata,
            questions=question_data["questions"],
            context_blocks=question_data["context_blocks"],
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
        
        # Fazer parse das informações do header com imagens categorizadas
        header_data = HeaderParser.parse(extracted_data["text"], header_images)
        
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
