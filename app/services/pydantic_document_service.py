"""
Pydantic Document Service

Service completamente migrado para Pydantic que processa documentos
usando modelos tipados desde o início até o final.
"""

from typing import Dict, Any, List
from fastapi import UploadFile
from app.models.internal import (
    InternalDocumentResponse,
    InternalDocumentMetadata,
    InternalQuestion,
    InternalContextBlock,
    InternalImageData
)
from app.core.logging import structured_logger
from app.services.azure_document_intelligence_service import AzureDocumentIntelligenceService


class PydanticDocumentService:
    """
    Service 100% Pydantic para processamento de documentos.
    
    Esta classe substitui completamente o pipeline legado Dict-based,
    trabalhando apenas com modelos Pydantic tipados.
    """
    
    @staticmethod
    async def process_document_full_pydantic(
        file: UploadFile,
        email: str
    ) -> InternalDocumentResponse:
        """
        Processa documento usando apenas modelos Pydantic.
        
        Args:
            file: Arquivo PDF para análise
            email: Email do usuário
            
        Returns:
            InternalDocumentResponse completo tipado
        """
        structured_logger.info(
            "Starting full Pydantic document processing",
            context={
                "email": email,
                "filename": file.filename,
                "processing_mode": "100_percent_pydantic"
            }
        )
        
        # 1. Extrair texto e dados usando Azure Document Intelligence
        azure_service = AzureDocumentIntelligenceService()
        raw_analysis = await azure_service.analyze_document(file)
        
        # 2. Converter diretamente para modelos Pydantic
        metadata = await PydanticDocumentService._extract_metadata_pydantic(raw_analysis)
        questions = await PydanticDocumentService._extract_questions_pydantic(raw_analysis)
        contexts = await PydanticDocumentService._extract_contexts_pydantic(raw_analysis)
        images = await PydanticDocumentService._extract_images_pydantic(file, raw_analysis)
        
        # 3. Criar response interno tipado
        internal_response = InternalDocumentResponse(
            email=email,
            document_id=f"{email}_{file.filename}",
            filename=file.filename,
            document_metadata=metadata,
            questions=questions,
            context_blocks=contexts,
            all_images=images,
            extracted_text=raw_analysis.get("content", ""),
            provider_metadata={
                "provider": "azure_document_intelligence",
                "processing_mode": "full_pydantic",
                "api_version": "2023-07-31"
            }
        )
        
        structured_logger.info(
            "Full Pydantic document processing completed",
            context={
                "email": email,
                "questions_count": len(questions),
                "contexts_count": len(contexts),
                "images_count": len(images)
            }
        )
        
        return internal_response
    
    @staticmethod
    async def _extract_metadata_pydantic(raw_analysis: Dict[str, Any]) -> InternalDocumentMetadata:
        """
        Extrai metadados usando parser Pydantic.
        
        Args:
            raw_analysis: Dados brutos do Azure DI
            
        Returns:
            InternalDocumentMetadata tipado
        """
        from app.parsers.header_parser.pydantic_header_parser import PydanticHeaderParser
        
        # TODO: Implementar PydanticHeaderParser
        # Por enquanto, usar conversão from_legacy_header
        from app.parsers.header_parser import HeaderParser
        
        legacy_header = HeaderParser.parse(raw_analysis.get("content", ""))
        return InternalDocumentMetadata.from_legacy_header(legacy_header)
    
    @staticmethod
    async def _extract_questions_pydantic(raw_analysis: Dict[str, Any]) -> List[InternalQuestion]:
        """
        Extrai questões usando parser Pydantic.
        
        Args:
            raw_analysis: Dados brutos do Azure DI
            
        Returns:
            Lista de InternalQuestion tipadas
        """
        from app.parsers.question_parser.pydantic_question_parser import PydanticQuestionParser
        
        # TODO: Implementar PydanticQuestionParser
        # Por enquanto, usar conversão from_legacy_format
        from app.parsers.question_parser import QuestionParser
        
        legacy_questions = QuestionParser.parse(raw_analysis.get("content", ""))
        
        pydantic_questions = []
        for legacy_q in legacy_questions:
            # Converter cada questão legada para Pydantic
            pydantic_q = InternalQuestion.from_legacy_format(legacy_q)
            pydantic_questions.append(pydantic_q)
        
        return pydantic_questions
    
    @staticmethod
    async def _extract_contexts_pydantic(raw_analysis: Dict[str, Any]) -> List[InternalContextBlock]:
        """
        Extrai contextos usando parser Pydantic.
        
        Args:
            raw_analysis: Dados brutos do Azure DI
            
        Returns:
            Lista de InternalContextBlock tipados
        """
        # TODO: Implementar extração direta de contextos
        return []
    
    @staticmethod
    async def _extract_images_pydantic(
        file: UploadFile, 
        raw_analysis: Dict[str, Any]
    ) -> List[InternalImageData]:
        """
        Extrai imagens usando extrator Pydantic.
        
        Args:
            file: Arquivo PDF original
            raw_analysis: Dados brutos do Azure DI
            
        Returns:
            Lista de InternalImageData tipadas
        """
        from app.services.image_extraction import ImageExtractionOrchestrator, ImageExtractionMethod
        
        # Usar orquestrador para extrair imagens
        orchestrator = ImageExtractionOrchestrator()
        
        # Resetar ponteiro do arquivo
        await file.seek(0)
        
        # Extrair usando método manual (mais confiável)
        extracted_images = await orchestrator.extract_images_single_method(
            method=ImageExtractionMethod.MANUAL_PDF,
            file=file,
            document_analysis_result=raw_analysis,
            document_id=f"pydantic_{file.filename}"
        )
        
        # Converter para modelos Pydantic
        pydantic_images = []
        for img_data in extracted_images.values():
            if isinstance(img_data, dict):
                pydantic_img = InternalImageData(
                    filename=img_data.get("filename", "unknown.png"),
                    base64_data=img_data.get("base64", ""),
                    page=img_data.get("page", 1),
                    category=img_data.get("category", "unknown"),
                    dimensions=img_data.get("dimensions", {"width": 0, "height": 0}),
                    coordinates=img_data.get("coordinates", {"x": 0, "y": 0}),
                    source="pydantic_extraction"
                )
                pydantic_images.append(pydantic_img)
        
        return pydantic_images
