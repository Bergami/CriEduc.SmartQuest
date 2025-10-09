"""
Document Analysis Orchestrator

Orquestrador especializado para análise completa de documentos usando
Dependency Injection com interfaces abstratas.
"""
import logging
from typing import Dict, Any, List
from uuid import uuid4
from fastapi import UploadFile

from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.core.interfaces import (
    IImageCategorizer,
    IImageExtractor,
    IContextBuilder,
    IFigureProcessor
)
from app.models.internal import (
    InternalDocumentResponse,
    InternalDocumentMetadata,
    InternalQuestion,
    InternalContextBlock,
    InternalImageData
)
from app.core.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class DocumentAnalysisOrchestrator:
    """
    Orquestrador para análise completa de documentos com Dependency Injection.

    ARQUITETURA:
    - Pipeline de análise em 7 fases especializadas
    - Dependency injection via interfaces abstratas
    - Zero acoplamento com implementações concretas
    - Auto-wiring de todas as dependências via DI Container

    Pipeline de Análise:
    1. Preparação de contexto de análise
    2. Extração e categorização de imagens
    3. Parsing de header e metadados
    4. Extração de questões dos parágrafos
    5. Construção de context blocks refatorados
    6. Associação de figuras às questões
    7. Agregação final da resposta
    """

    def __init__(self,
                 image_categorizer: IImageCategorizer,
                 image_extractor: IImageExtractor,
                 context_builder: IContextBuilder,
                 figure_processor: IFigureProcessor):
        """
        Inicializa o orquestrador com dependências injetadas via DI Container.

        Args:
            image_categorizer: Interface para categorização de imagens
            image_extractor: Interface para extração de imagens
            context_builder: Interface para construção de context blocks
            figure_processor: Interface para processamento de figuras
        """
        self._image_categorizer = image_categorizer
        self._image_extractor = image_extractor
        self._context_builder = context_builder
        self._figure_processor = figure_processor
        self._logger = logging.getLogger(__name__)

        self._logger.info("DocumentAnalysisOrchestrator initialized with DI interfaces")
        self._logger.debug(f"ImageCategorizer: {type(image_categorizer).__name__}")
        self._logger.debug(f"ImageExtractor: {type(image_extractor).__name__}")
        self._logger.debug(f"ContextBuilder: {type(context_builder).__name__}")
        self._logger.debug(f"FigureProcessor: {type(figure_processor).__name__}")

    async def orchestrate_analysis(self,
                                   extracted_data: Dict[str, Any],
                                   email: str,
                                   filename: str,
                                   file: UploadFile,
                                   use_refactored: bool = True) -> InternalDocumentResponse:
        """
        Orquestra todo o pipeline de análise de documento.

        Args:
            extracted_data: Dados brutos extraídos pelo DocumentExtractionService
            email: Email do usuário
            filename: Nome do arquivo original
            file: Objeto UploadFile para fallback de extração
            use_refactored: Flag para usar lógica de processamento avançada

        Returns:
            InternalDocumentResponse: Resposta completa estruturada

        Raises:
            DocumentProcessingError: Em caso de falha no pipeline
        """
        document_id = str(uuid4())
        self._logger.info(f"Starting document analysis orchestration for {filename} (user: {email})")

        try:
            # Phase 1: Preparação de dados básicos
            analysis_context = await self._prepare_analysis_context(
                extracted_data, email, filename, document_id
            )

            # Phase 2: Extração e categorização de imagens
            image_analysis = await self._execute_image_analysis_phase(
                file, analysis_context, document_id
            )

            # Phase 3: Parsing de header e metadados
            header_metadata = await self._execute_header_parsing_phase(
                analysis_context, image_analysis
            )

            # Phase 4: Extração de questões
            questions_and_context = await self._execute_question_extraction_phase(
                analysis_context, image_analysis
            )

            # Phase 5: Construção de context blocks refatorados
            enhanced_context_blocks = await self._execute_context_building_phase(
                analysis_context, image_analysis, use_refactored
            )

            # Phase 6: Associação de figuras (se aplicável)
            enhanced_questions = await self._execute_figure_association_phase(
                analysis_context, questions_and_context["questions"]
            )

            # Phase 7: Agregação final
            final_response = await self._aggregate_final_response(
                analysis_context,
                image_analysis,
                header_metadata,
                enhanced_questions,
                enhanced_context_blocks or questions_and_context["context_blocks"]
            )

            self._logger.info(f"Document analysis orchestration completed successfully for {filename}")
            return final_response

        except Exception as e:
            self._logger.error(f"Document analysis orchestration failed for {filename}: {str(e)}")
            raise DocumentProcessingError(f"Analysis pipeline failed: {str(e)}") from e

    async def _prepare_analysis_context(self,
                                        extracted_data: Dict[str, Any],
                                        email: str,
                                        filename: str,
                                        document_id: str) -> Dict[str, Any]:
        """Phase 1: Prepara o contexto básico para análise."""
        self._logger.info("Phase 1: Preparing analysis context")

        extracted_text = extracted_data.get("text", "")
        azure_result = extracted_data.get("metadata", {}).get("raw_response", {})

        context = {
            "extracted_text": extracted_text,
            "azure_result": azure_result,
            "email": email,
            "filename": filename,
            "document_id": document_id,
            "provider_metadata": extracted_data.get("metadata", {})
        }

        self._logger.info(f"Phase 1 complete: Context prepared with Azure result: {bool(azure_result)}")
        return context

    async def _execute_image_analysis_phase(self,
                                            file: UploadFile,
                                            analysis_context: Dict[str, Any],
                                            document_id: str) -> Dict[str, Any]:
        """Phase 2: Executa extração e categorização de imagens."""
        self._logger.info("Phase 2: Executing image analysis (extraction + categorization)")

        # 2.1: Extração com fallback usando orquestrador especializado
        image_data = await self._image_extractor.extract_with_fallback(
            file=file,
            document_analysis_result=analysis_context["azure_result"],
            document_id=f"{analysis_context['email']}_{analysis_context['filename']}"
        )

        if image_data:
            self._logger.info(f"Phase 2.1: {len(image_data)} images extracted successfully")
        else:
            self._logger.warning("Phase 2.1: No images extracted")
            image_data = {}

        # 2.2: Categorização usando interface (DIP aplicado)
        header_images_pydantic, content_images_pydantic = [], []

        if isinstance(image_data, dict) and image_data:
            self._logger.info(f"Phase 2.2: Categorizing {len(image_data)} images using Pydantic interface")

            header_images_pydantic, content_images_pydantic = self._image_categorizer.categorize_extracted_images(
                image_data,
                analysis_context["azure_result"],
                document_id=f"analyze_{len(image_data)}_images"
            )

            self._logger.info(f"Phase 2.2: Categorization complete - {len(header_images_pydantic)} header, {len(content_images_pydantic)} content")
        else:
            self._logger.info("Phase 2.2: Skipping categorization - no valid image data")

        all_categorized_images = header_images_pydantic + content_images_pydantic

        result = {
            "image_data": image_data,
            "header_images": header_images_pydantic,
            "content_images": content_images_pydantic,
            "all_images": all_categorized_images
        }

        self._logger.info("Phase 2 complete: Image analysis finished")
        return result

    async def _execute_header_parsing_phase(self,
                                            analysis_context: Dict[str, Any],
                                            image_analysis: Dict[str, Any]) -> InternalDocumentMetadata:
        """Phase 3: Executa parsing do header e metadados."""
        self._logger.info("Phase 3: Executing header parsing")

        header_metadata = HeaderParser.parse_to_pydantic(
            header=analysis_context["extracted_text"],
            header_images=image_analysis["header_images"],
            content_images=image_analysis["content_images"]
        )

        self._logger.info("Phase 3 complete: Header metadata parsed")
        return header_metadata

    async def _execute_question_extraction_phase(self,
                                                 analysis_context: Dict[str, Any],
                                                 image_analysis: Dict[str, Any]) -> Dict[str, List]:
        """Phase 4: Executa extração de questões dos parágrafos Azure."""
        self._logger.info("Phase 4: Executing question extraction")

        azure_result = analysis_context["azure_result"]
        image_data = image_analysis["image_data"]

        # Extrair parágrafos Azure
        azure_paragraphs = azure_result.get("paragraphs", []) if azure_result else []

        questions = []
        context_blocks = []

        if azure_paragraphs:
            self._logger.info(f"Phase 4.1: Processing {len(azure_paragraphs)} Azure paragraphs")

            # Preparar parágrafos no formato esperado
            paragraph_list = [{"content": p.get("content", "")} for p in azure_paragraphs if p.get("content")]

            # Extrair usando método eficiente
            raw_data = QuestionParser.extract_from_paragraphs(paragraph_list, image_data)

            # Converter para Pydantic com validação
            for i, q in enumerate(raw_data.get("questions", [])):
                try:
                    if not q.get("question"):
                        self._logger.warning(f"Question {i+1} has empty content, skipping")
                        continue

                    pydantic_q = InternalQuestion.from_legacy_question(q)
                    questions.append(pydantic_q)
                    self._logger.debug(f"Question {i+1} converted: {len(pydantic_q.content.statement)} chars")
                except Exception as e:
                    self._logger.error(f"Error converting question {i+1}: {e}")
                    continue

            for i, cb in enumerate(raw_data.get("context_blocks", [])):
                try:
                    pydantic_cb = InternalContextBlock.from_legacy_context_block(cb)
                    context_blocks.append(pydantic_cb)
                except Exception as e:
                    self._logger.warning(f"Error converting context block {i+1}: {e}")
                    continue

            self._logger.info(f"Phase 4: Extracted {len(questions)} questions, {len(context_blocks)} context blocks")
        else:
            self._logger.error("Phase 4: No Azure paragraphs available - cannot extract questions")
            raise ValueError("Azure paragraphs are required for SOLID extraction")

        return {
            "questions": questions,
            "context_blocks": context_blocks
        }

    async def _execute_context_building_phase(self,
                                              analysis_context: Dict[str, Any],
                                              image_analysis: Dict[str, Any],
                                              use_refactored: bool) -> List[InternalContextBlock]:
        """Phase 5: Executa construção de context blocks refatorados."""
        if not use_refactored:
            self._logger.info("Phase 5: Skipped - refactored context building disabled")
            return None

        self._logger.info("Phase 5: Executing refactored context building")

        azure_result = analysis_context["azure_result"]
        image_data = image_analysis["image_data"]

        if not azure_result:
            self._logger.warning("Phase 5: No Azure result - skipping enhanced context building")
            return None

        try:
            self._logger.info("Phase 5.1: Using parse_to_pydantic() - Native Pydantic Interface")

            enhanced_context_blocks = self._context_builder.parse_to_pydantic(azure_result, image_data)

            blocks_with_images = sum(1 for cb in enhanced_context_blocks if cb.has_images)
            self._logger.info(f"Phase 5: Created {len(enhanced_context_blocks)} context blocks ({blocks_with_images} with images)")

            return enhanced_context_blocks

        except Exception as e:
            self._logger.warning(f"Phase 5: parse_to_pydantic failed ({e}), using legacy method")

            enhanced_context_blocks_dict = self._context_builder.build_context_blocks_from_azure_figures(
                azure_result, image_data
            )

            if enhanced_context_blocks_dict:
                context_blocks = [
                    InternalContextBlock.from_legacy_context_block(cb)
                    for cb in enhanced_context_blocks_dict
                ]
                self._logger.info(f"Phase 5: Created {len(context_blocks)} context blocks (legacy method)")
                return context_blocks
            else:
                self._logger.warning("Phase 5: No enhanced context blocks created")
                return None

    async def _execute_figure_association_phase(self,
                                                analysis_context: Dict[str, Any],
                                                questions: List[InternalQuestion]) -> List[InternalQuestion]:
        """Phase 6: Executa associação de figuras às questões."""
        self._logger.info("Phase 6: Executing figure association")

        try:
            images = analysis_context.get("categorized_images", [])
            context_blocks = analysis_context.get("context_blocks", [])

            # Processar figuras através da interface
            figure_results = await self._figure_processor.process_figures(images, context_blocks)

            # Extrair questões melhoradas dos resultados
            enhanced_questions = figure_results.get("enhanced_questions", questions)

            self._logger.info("Phase 6: Questions enhanced with figure associations")
            return enhanced_questions

        except Exception as e:
            self._logger.warning(f"Phase 6: Figure association failed: {e}, proceeding without enhancement")
            return questions

    async def _aggregate_final_response(self,
                                        analysis_context: Dict[str, Any],
                                        image_analysis: Dict[str, Any],
                                        header_metadata: InternalDocumentMetadata,
                                        questions: List[InternalQuestion],
                                        context_blocks: List[InternalContextBlock]) -> InternalDocumentResponse:
        """Phase 7: Agrega todos os resultados na resposta final."""
        self._logger.info("Phase 7: Aggregating final response")

        response = InternalDocumentResponse(
            email=analysis_context["email"],
            document_id=analysis_context["document_id"],
            filename=analysis_context["filename"],
            document_metadata=header_metadata,
            questions=questions,
            context_blocks=context_blocks,
            extracted_text=analysis_context["extracted_text"],
            provider_metadata=analysis_context["provider_metadata"],
            all_images=image_analysis["all_images"]
        )

        self._logger.info(f"Phase 7 complete: Final response aggregated with {len(questions)} questions, {len(context_blocks)} context blocks")
        return response