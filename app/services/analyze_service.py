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
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})
        
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

        # 5. Extrair questões - CORREÇÃO CRÍTICA: Usar parágrafos diretamente
        azure_paragraphs = azure_result.get("paragraphs", []) if azure_result else []
        
        # 🔧 CORREÇÃO: Usar extract_from_paragraphs diretamente (mais eficiente e preciso)
        if azure_paragraphs:
            logger.info(f"🔧 CORREÇÃO: Using extract_from_paragraphs directly from {len(azure_paragraphs)} Azure paragraphs")
            
            # Preparar parágrafos no formato esperado
            paragraph_list = [{"content": p.get("content", "")} for p in azure_paragraphs if p.get("content")]
            
            # Extrair usando método que funciona corretamente
            raw_data = QuestionParser.extract_from_paragraphs(paragraph_list, image_data)
            
            # Converter para Pydantic manualmente com validação
            from app.models.internal.question_models import InternalQuestion
            from app.models.internal.context_models import InternalContextBlock
            
            questions = []
            for i, q in enumerate(raw_data.get("questions", [])):
                try:
                    # 🔍 DEBUG: Log detalhado da questão antes da conversão
                    logger.info(f"🔍 DEBUG Question {i+1}: number={q.get('number')}, question_length={len(q.get('question', ''))}, alternatives={len(q.get('alternatives', []))}")
                    logger.debug(f"🔍 DEBUG Question {i+1} content: {q}")
                    
                    if not q.get("question"):
                        logger.warning(f"⚠️ Question {i+1} has empty content, skipping")
                        continue
                        
                    pydantic_q = InternalQuestion.from_legacy_question(q)
                    questions.append(pydantic_q)
                    logger.info(f"✅ Question {i+1} converted: {len(pydantic_q.content.statement)} chars, {len(pydantic_q.options)} options")
                except Exception as e:
                    logger.error(f"❌ Error converting question {i+1}: {e}")
                    continue
            
            context_blocks = []
            for i, cb in enumerate(raw_data.get("context_blocks", [])):
                try:
                    pydantic_cb = InternalContextBlock.from_legacy_context_block(cb)
                    context_blocks.append(pydantic_cb)
                except Exception as e:
                    logger.warning(f"⚠️ Error converting context block {i+1}: {e}")
                    continue
            
            logger.info(f"🔧 CORREÇÃO: Successfully extracted {len(questions)} questions, {len(context_blocks)} context blocks")
            
        elif azure_result and "paragraphs" in azure_result:
            backup_paragraphs = azure_result["paragraphs"]
            logger.info(f"🔧 CORREÇÃO: Using extract_from_paragraphs from {len(backup_paragraphs)} backup Azure paragraphs")
            
            # Mesmo processo para backup paragraphs
            paragraph_list = [{"content": p.get("content", "")} for p in backup_paragraphs if p.get("content")]
            raw_data = QuestionParser.extract_from_paragraphs(paragraph_list, image_data)
            
            from app.models.internal.question_models import InternalQuestion
            from app.models.internal.context_models import InternalContextBlock
            
            questions = [
                InternalQuestion.from_legacy_question(q) 
                for q in raw_data.get("questions", [])
                if q.get("question")  # Apenas questões com conteúdo
            ]
            
            context_blocks = [
                InternalContextBlock.from_legacy_context_block(cb) 
                for cb in raw_data.get("context_blocks", [])
            ]
            
            logger.info(f"🔧 CORREÇÃO: Successfully extracted {len(questions)} questions from backup paragraphs")
            
        else:
            logger.error("❌ CRITICAL: No Azure paragraphs available - cannot extract questions using SOLID")
            # Sistema agora exige parágrafos Azure - não há mais fallback
            raise ValueError("Azure paragraphs are required for SOLID extraction. Document processing failed.")
            
        logger.info(f"Questions found: {len(questions)}")
        logger.info(f"Context blocks found: {len(context_blocks)}")

        # 6. Processar melhorias da versão refatorada (se aplicável)
        if use_refactored:
            logger.info("🚀 Using REFACTORED version with PHASE 2 Pydantic improvements")
            logger.info(f"🔍 CRITICAL DEBUG: azure_result exists: {bool(azure_result)}")
            logger.info(f"🔍 CRITICAL DEBUG: azure_result keys: {list(azure_result.keys()) if azure_result else 'EMPTY'}")
            
            if azure_result:
                # PHASE 2: Use native Pydantic interface
                context_builder = RefactoredContextBlockBuilder()
                
                # Log para debugging
                logger.info(f"Building context blocks with Azure result and {len(image_data) if image_data else 0} images")
                
                # Try new Pydantic method first, fallback to legacy if needed
                try:
                    logger.info("🔥 PHASE 2: Using parse_to_pydantic() - Native Pydantic Interface")
                    logger.info(f"🔍 DEBUG: Azure result keys: {list(azure_result.keys()) if azure_result else 'None'}")
                    logger.info(f"🔍 DEBUG: Image data type: {type(image_data)}, size: {len(image_data) if image_data else 0}")
                    
                    enhanced_context_blocks = context_builder.parse_to_pydantic(azure_result, image_data)
                    logger.info(f"🔍 DEBUG: parse_to_pydantic returned {len(enhanced_context_blocks)} blocks")
                    
                    # ✅ FASE 1: Substituir context blocks por versão enhanced
                    context_blocks = enhanced_context_blocks
                    logger.info(f"✅ PHASE 2 SUCCESS: Created {len(enhanced_context_blocks)} context blocks using native Pydantic")
                    
                    # Log context blocks with images for debugging
                    blocks_with_images = sum(1 for cb in enhanced_context_blocks if cb.has_images)
                    logger.info(f"Context blocks with images: {blocks_with_images}/{len(enhanced_context_blocks)}")
                    
                except Exception as e:
                    logger.warning(f"🔄 PHASE 2 fallback: parse_to_pydantic failed ({e}), using legacy method")
                    enhanced_context_blocks_dict = context_builder.build_context_blocks_from_azure_figures(
                        azure_result, image_data
                    )
                    
                    if enhanced_context_blocks_dict:
                        logger.info(f"Created {len(enhanced_context_blocks_dict)} enhanced context blocks (legacy)")
                        # Convert the Dicts into Pydantic Models before assigning
                        context_blocks = [
                            InternalContextBlock.from_legacy_context_block(cb) for cb in enhanced_context_blocks_dict
                        ]
                        
                        # Log context blocks with images for debugging
                        blocks_with_images = sum(1 for cb in enhanced_context_blocks_dict if cb.get('hasImage', False))
                        logger.info(f"Context blocks with images: {blocks_with_images}/{len(enhanced_context_blocks_dict)}")
                    else:
                        logger.warning("No enhanced context blocks were created")
            else:
                logger.error("🚨 CRITICAL: azure_result is EMPTY - RefactoredContextBlockBuilder will NOT be executed")
                logger.error(f"🚨 extracted_data keys: {list(extracted_data.keys())}")
                logger.error(f"🚨 metadata keys: {list(extracted_data.get('metadata', {}).keys())}")
                
            # 🆕 FASE 02: Figure association using native Pydantic interface
            try:
                processed_figures = AzureFigureProcessor.process_figures_from_azure_response(azure_result)
                
                logger.info("🆕 FASE 02: Using native Pydantic figure association (no legacy conversion)")
                # ✅ FASE 02: Use new Pydantic native method - no Dict conversion needed
                questions = AzureFigureProcessor.associate_figures_to_pydantic_questions(
                    processed_figures, questions
                )
                logger.info("✅ FASE 02: Questions enhanced with figure associations using native Pydantic")
            except Exception as e:
                logger.warning(f"🔄 FASE 02: Figure association failed: {e}, proceeding without enhancement")

        # 7. Construir o objeto de resposta final Pydantic
        # A lista all_categorized_images já contém os objetos Pydantic corretos
        response = InternalDocumentResponse(
            email=email,
            document_id=document_id,
            filename=filename,
            document_metadata=header_metadata,
            questions=questions,  # ✅ FASE 1: Direto Pydantic - sem conversão
            context_blocks=context_blocks,  # ✅ FASE 1: Direto Pydantic - sem conversão
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
    # 🧹 MÉTODOS MOCK REMOVIDOS
    # Removidos após confirmação de que o endpoint principal está funcionando
    # ==================================================================================

    # ==================================================================================
    # DEPRECATED METHODS - Removed after FASE 1 migration
    # ==================================================================================
    # _ensure_pydantic_context_blocks() - No longer needed with native Pydantic extraction