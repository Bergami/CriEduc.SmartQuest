"""
Analyze Service - Versão Refatorada (SOLID)

Responsabilidades:
- Orquestrar o fluxo de análise de um documento a partir de dados já extraídos.
- Categorizar imagens.
- Extrair header e questões.
- Delegar para MockDocumentService para casos mock.

Esta classe não tem mais conhecimento sobre cache ou a origem dos dados (Azure, etc.),
seguindo o Princípio da Responsabilidade Única.
"""
import logging
from typing import Dict, Any
from uuid import uuid4
from fastapi import UploadFile

from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.services.image_categorization_service_pure_pydantic import ImageCategorizationService
from app.services.azure_figure_processor import AzureFigureProcessor
from app.models.internal import (
    InternalDocumentResponse,
    InternalDocumentMetadata,
    InternalQuestion,
    InternalContextBlock,
    InternalImageData
)
from app.services.refactored_context_builder import RefactoredContextBlockBuilder
from app.core.exceptions import DocumentProcessingError
from app.services.mock_document_service import MockDocumentService

logger = logging.getLogger(__name__)


class AnalyzeService:
    """
    Serviço de orquestração da análise de documentos.
    Recebe dados brutos e os transforma em um InternalDocumentResponse estruturado.
    """

    @staticmethod
    async def process_document_with_models(
        extracted_data: Dict[str, Any],
        email: str,
        filename: str,
        file: UploadFile, # Necessário para o fallback de extração de imagem
        use_refactored: bool = True
    ) -> InternalDocumentResponse:
        """
        ✅ REFATORADO: Orquestra a análise a partir de dados já extraídos.
        Não possui mais conhecimento sobre cache ou provedores de extração.

        Args:
            extracted_data: Dicionário com os dados brutos extraídos pelo DocumentExtractionService.
            email: Email do usuário.
            filename: Nome do arquivo original.
            file: O objeto UploadFile, necessário para o fallback de extração de imagem.
            use_refactored: Flag para usar lógica de processamento avançada.

        Returns:
            InternalDocumentResponse: O objeto de resposta Pydantic completo.
        """
        document_id = str(uuid4())
        logger.info(f"🔧 Orchestrating analysis for {filename} for {email}")

        # 1. Extrair informações primárias dos dados recebidos
        extracted_text = extracted_data.get("text", "")
        raw_image_data = extracted_data.get("image_data", {})
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        
        logger.info(f"Text received: {len(extracted_text)} characters")

        # 2. Extração de imagens com fallback (ainda necessário aqui, pois depende do azure_result)
        # Esta lógica poderia ser movida para um ImageExtractionService no futuro.
        image_data = await AnalyzeService._extract_images_with_fallback(
            file=file,
            extracted_data=extracted_data,
            document_id=f"{email}_{filename}"
        )
        if image_data:
            logger.info(f"{len(image_data)} images extracted using optimized extractors")

        # 3. Categorizar imagens usando o serviço Pydantic
        header_images_pydantic, content_images_pydantic = [], []
        if isinstance(image_data, dict) and image_data:
            logger.info(f"🔧 Categorizing {len(image_data)} extracted images using PURE PYDANTIC service")
            header_images_pydantic, content_images_pydantic = ImageCategorizationService.categorize_extracted_images(
                image_data, azure_result, document_id=f"analyze_{len(image_data)}_images"
            )
            logger.info(f"🔧 PURE PYDANTIC Categorization complete: {len(header_images_pydantic)} header images, {len(content_images_pydantic)} content images")
        else:
            logger.info("🔧 Skipping image categorization - no valid image data available")

        # Combine all categorized images into a single list
        all_categorized_images = header_images_pydantic + content_images_pydantic

        # 4. Parse do Header usando o método Pydantic e as imagens já categorizadas
        logger.info(f"Using Pydantic HeaderParser with {len(header_images_pydantic)} categorized header images")
        header_metadata = HeaderParser.parse_to_pydantic(
            header=extracted_text,
            header_images=header_images_pydantic,
            content_images=content_images_pydantic
        )

        # 5. Extrair questões
        question_data = QuestionParser.extract(extracted_text, image_data)
        logger.info(f"Questions found: {len(question_data['questions'])}")
        logger.info(f"Context blocks found: {len(question_data['context_blocks'])}")

        # 6. Processar melhorias da versão refatorada (se aplicável)
        if use_refactored:
            logger.info("🚀 Using REFACTORED version with PHASE 2 Pydantic improvements")
            azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
            if azure_result:
                # PHASE 2: Use native Pydantic interface
                context_builder = RefactoredContextBlockBuilder()
                
                # Log para debugging
                logger.info(f"Building context blocks with Azure result and {len(image_data) if image_data else 0} images")
                
                # Try new Pydantic method first, fallback to legacy if needed
                try:
                    logger.info("🔥 PHASE 2: Using parse_to_pydantic() - Native Pydantic Interface")
                    pydantic_context_blocks = context_builder.parse_to_pydantic(azure_result, image_data)
                    question_data["context_blocks"] = pydantic_context_blocks
                    logger.info(f"✅ PHASE 2 SUCCESS: Created {len(pydantic_context_blocks)} context blocks using native Pydantic")
                    
                    # Log context blocks with images for debugging
                    blocks_with_images = sum(1 for cb in pydantic_context_blocks if cb.has_images)
                    logger.info(f"Context blocks with images: {blocks_with_images}/{len(pydantic_context_blocks)}")
                    
                except Exception as e:
                    logger.warning(f"🔄 PHASE 2 fallback: parse_to_pydantic failed ({e}), using legacy method")
                    enhanced_context_blocks = context_builder.build_context_blocks_from_azure_figures(
                        azure_result, image_data
                    )
                    
                    if enhanced_context_blocks:
                        logger.info(f"Created {len(enhanced_context_blocks)} enhanced context blocks (legacy)")
                        # Convert the Dicts into Pydantic Models before assigning
                        question_data["context_blocks"] = [
                            InternalContextBlock.from_legacy_context_block(cb) for cb in enhanced_context_blocks
                        ]
                        
                        # Log context blocks with images for debugging
                        blocks_with_images = sum(1 for cb in enhanced_context_blocks if cb.get('hasImage', False))
                        logger.info(f"Context blocks with images: {blocks_with_images}/{len(enhanced_context_blocks)}")
                    else:
                        logger.warning("No enhanced context blocks were created")
                
                # A associação de figuras às questões também pode precisar ser refatorada
                # para usar os objetos pydantic, mas vamos focar no erro atual.
                processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
                enhanced_questions = AzureFigureProcessor.associate_figures_to_questions(
                    processed_figures, question_data["questions"]
                )
                question_data["questions"] = enhanced_questions
                logger.info("Questions and context blocks enhanced with figure associations")

        # 7. Construir o objeto de resposta final Pydantic
        # A lista all_categorized_images já contém os objetos Pydantic corretos
        response = InternalDocumentResponse(
            email=email,
            document_id=document_id,
            filename=filename,
            document_metadata=header_metadata,
            questions=[InternalQuestion.from_legacy_question(q) for q in question_data.get("questions", [])],
            context_blocks=question_data.get("context_blocks", []), # Now receives a list of Pydantic models
            extracted_text=extracted_text,
            provider_metadata=extracted_data.get("metadata", {}),
            all_images=all_categorized_images
        )

        logger.info(f"🔧 Final check before returning response: {len(response.document_metadata.header_images)} header images in metadata.")
        logger.info("✅ Document analysis orchestration completed successfully with Pydantic models")
        return response

    @staticmethod
    async def _extract_images_with_fallback(
        file: UploadFile,
        extracted_data: Dict[str, Any],
        document_id: str
    ) -> Dict[str, str]:
        """
        Extrai imagens usando estratégia de fallback automático.
        Esta é uma responsabilidade candidata a ser movida para um futuro ImageExtractionService.
        """
        from app.services.image_extraction import ImageExtractionOrchestrator, ImageExtractionMethod
        
        logger.info("Starting image extraction with automatic fallback")
        await file.seek(0)
        orchestrator = ImageExtractionOrchestrator()
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        
        try:
            logger.info("STEP 1: Attempting Manual PDF extraction (primary method)")
            manual_images = await orchestrator.extract_images_single_method(
                method=ImageExtractionMethod.MANUAL_PDF,
                file=file,
                document_analysis_result=azure_result,
                document_id=document_id
            )
            if manual_images:
                logger.info(f"✅ Manual PDF extraction successful: {len(manual_images)} images extracted.")
                await file.seek(0)
                return manual_images
            logger.warning("⚠️ Manual PDF extraction returned no images, attempting fallback")
        except Exception as e:
            logger.warning(f"⚠️ Manual PDF extraction failed: {str(e)}, attempting fallback")
        
        await file.seek(0)
        
        try:
            logger.info("STEP 2: Using Azure Figures fallback (secondary method)")
            azure_images = await orchestrator.extract_images_single_method(
                method=ImageExtractionMethod.AZURE_FIGURES,
                file=file,
                document_analysis_result=azure_result,
                document_id=document_id
            )
            if azure_images:
                logger.info(f"✅ Azure Figures fallback successful: {len(azure_images)} images extracted.")
                await file.seek(0)
                return azure_images
            logger.warning("⚠️ Azure Figures fallback also returned no images")
        except Exception as e:
            logger.error(f"❌ Azure Figures fallback failed: {str(e)}")
        
        logger.warning("❌ All primary image extraction methods failed, returning empty result")
        await file.seek(0)
        return {}

    # ==================================================================================
    # MÉTODOS MOCK (Mantidos para não quebrar os testes e endpoints de mock)
    # ==================================================================================
    @staticmethod
    async def process_document_mock(email: str, filename: str = None) -> Dict[str, Any]:
        """
        Delega o processamento mock para MockDocumentService.
        """
        return await MockDocumentService.process_document_mock(email, filename)

    @staticmethod
    async def process_document_with_models_mock(
        email: str = "test@mock.com",
        image_extraction_method=None
    ) -> InternalDocumentResponse:
        """
        Processa um documento mock usando modelos Pydantic.
        """
        logger.info("🔧 Processing mock document with Pydantic models")
        
        from app.services.azure_response_service import AzureResponseService
        
        azure_result = AzureResponseService.get_latest_azure_response()
        file_info = AzureResponseService.get_latest_file_info()
        extracted_data = AzureResponseService.convert_azure_response_to_extracted_data(azure_result)
        raw_image_data = extracted_data.get("image_data", {})

        header_images_pydantic, content_images_pydantic = [], []
        if isinstance(raw_image_data, dict) and raw_image_data:
            logger.info(f"🔧 MOCK: Categorizing {len(raw_image_data)} images using PURE PYDANTIC service")
            header_images_pydantic, content_images_pydantic = ImageCategorizationService.categorize_extracted_images(
                raw_image_data, azure_result, document_id=f"mock_{len(raw_image_data)}_images"
            )
        
        header_metadata = HeaderParser.parse_to_pydantic(
            header=extracted_data["text"],
            header_images=header_images_pydantic,
            content_images=content_images_pydantic
        )

        question_data = QuestionParser.extract(extracted_data["text"], raw_image_data)
        
        context_builder = RefactoredContextBlockBuilder()
        context_blocks = context_builder.build_context_blocks_from_azure_figures(
            azure_result, raw_image_data or {}
        )
        
        internal_response = InternalDocumentResponse(
            document_id=str(uuid4()),
            email=email,
            filename=file_info['filename'],
            document_metadata=header_metadata,
            questions=[InternalQuestion.from_legacy_format(q) for q in question_data.get("questions", [])],
            context_blocks=[InternalContextBlock.from_legacy_context_block(cb) for cb in context_blocks],
            extracted_text=extracted_data["text"],
            provider_metadata={
                "email": email,
                "filename": file_info['filename'],
                "processing_mode": "mock_pydantic_complete",
                "migration_status": "100_percent_pydantic"
            }
        )
        
        logger.info(f"🔧 Mock document processed with 100% Pydantic: {internal_response.document_id}")
        return internal_response