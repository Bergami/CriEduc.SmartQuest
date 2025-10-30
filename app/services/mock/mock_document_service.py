"""
Mock Document Service

Este serviço é responsável pelo processamento de documentos mock,
separando a lógica mock da lógica real de processamento do AnalyzeService.
"""
import json
import base64
from typing import Dict, Any, List
from uuid import uuid4
from pathlib import Path
from PIL import Image, ImageDraw
import io

from app.core.logging import logger
from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.core.exceptions import DocumentProcessingError
from app.core.constants import MockDataConstants, GeneralConstants


class MockDocumentService:
    """
    Serviço especializado para processamento de documentos mock.
    
    Responsabilidades:
    - Carregar dados mock de arquivos JSON
    - Extrair imagens reais do PDF usando coordenadas mock
    - Categorizar imagens em header/content
    - Processar texto e extrair informações
    """
    
    @staticmethod
    async def process_document_mock(email: str, filename: str = None) -> Dict[str, Any]:
        """
        Processa documento usando dados mock do RetornoProcessamento.json
        Não requer arquivo físico
        """
        if filename is None:
            filename = MockDataConstants.DEFAULT_MOCK_FILENAME
            
        document_id = str(uuid4())
        debug_prefix = GeneralConstants.get_debug_prefix("info")
        logger.info(f"Processing MOCK document {filename} for {email}")
        logger.info(f"Generated Document ID: {document_id}")

        # Carregar dados mock com fallback
        mock_data = MockDocumentService._load_mock_data()
        
        # Extrair conteúdo de texto
        text_content = MockDocumentService._extract_text_content(mock_data, debug_prefix)
        
        # Processar imagens
        header_images, content_images = await MockDocumentService._process_mock_images(
            mock_data, debug_prefix
        )
        
        # Processar header e questões
        header_data = HeaderParser.parse(text_content, header_images)
        
        # 🆕 Tentar usar extração SOLID se parágrafos estão disponíveis
        azure_paragraphs = mock_data.get("paragraphs", [])
        if azure_paragraphs:
            logger.info(f"🆕 MOCK: Using NEW SOLID extraction from {len(azure_paragraphs)} Azure paragraphs")
            question_data = QuestionParser.extract_from_paragraphs(azure_paragraphs, content_images)
            logger.info("✅ MOCK: SOLID-based extraction completed successfully")
        else:
            # Tentar parágrafos no formato analyzeResult (para compatibilidade)
            analyze_result = mock_data.get("analyzeResult", {})
            analyze_paragraphs = analyze_result.get("paragraphs", []) if analyze_result else []
            
            if analyze_paragraphs:
                logger.info(f"🆕 MOCK: Using NEW SOLID extraction from {len(analyze_paragraphs)} analyzeResult paragraphs")
                question_data = QuestionParser.extract_from_paragraphs(analyze_paragraphs, content_images)
                logger.info("✅ MOCK: SOLID-based extraction completed successfully")
            else:
                logger.warning("⚠️ MOCK: No Azure paragraphs available, using text-based extraction")
                # Criar parágrafos sintéticos a partir do texto
                synthetic_paragraphs = [{"content": text_content}]
                question_data = QuestionParser.extract_from_paragraphs(synthetic_paragraphs, content_images)
        
        # 🚨 CRITICAL CORRECTION: Use ContextBlockBuilder to create context_blocks in mock mode
        context_blocks = []
        try:
            from app.core.di_container import container
            from app.core.interfaces import IContextBuilder
            
            logger.info("🔧 MOCK: Creating context blocks using ContextBlockBuilder")
            
            # Resolver ContextBlockBuilder via DI
            context_builder = container.resolve(IContextBuilder)
            
            # Usar parse_to_pydantic para gerar context blocks
            azure_response = mock_data.get("analyzeResult", mock_data)
            context_blocks_pydantic = await context_builder.parse_to_pydantic(azure_response, content_images)
            
            # Converter para formato DTO para compatibilidade
            from app.dtos.responses.document_response_dto import ContextBlockDTO
            context_blocks = [
                ContextBlockDTO.from_internal_context_block(cb).dict()
                for cb in context_blocks_pydantic
            ]
            
            logger.info(f"✅ MOCK: Successfully created {len(context_blocks)} context blocks with ContextBlockBuilder")
            
        except Exception as e:
            logger.error(f"❌ MOCK: Error creating context blocks with ContextBlockBuilder: {str(e)}")
            logger.info("🔄 MOCK: Falling back to empty context blocks")
            context_blocks = []
        
        logger.info(f"Header extracted from mock with {len(header_images)} images")
        logger.info(f"Questions found in mock: {len(question_data['questions'])}")
        logger.info(f"Context blocks in mock: {len(context_blocks)}")

        result = {
            "email": email,
            "document_id": document_id,
            "filename": filename,
            "header": header_data,
            "questions": question_data["questions"],
            "context_blocks": context_blocks  # 🚨 Usar context_blocks do ContextBlockBuilder
        }
        
        logger.info("Mock processing completed")
        return result
    
    @staticmethod
    def _load_mock_data() -> Dict[str, Any]:
        """Carrega dados mock com lógica de fallback"""
        fallback_chain = MockDataConstants.get_mock_response_fallback_chain()
        json_path = None
        
        for potential_path in fallback_chain:
            if potential_path.exists():
                json_path = potential_path
                break
        
        if json_path is None:
            mock_status = MockDataConstants.validate_mock_files_exist()
            missing_files = ", ".join(mock_status["missing_files"])
            raise DocumentProcessingError(f"Mock response files not found. Missing: {missing_files}")
        
        try:
            with open(json_path, 'r', encoding=GeneralConstants.TEXT_PROCESSING["default_encoding"]) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise DocumentProcessingError(f"Error decoding mock JSON: {str(e)}")
        except Exception as e:
            raise DocumentProcessingError(f"Error loading mock data: {str(e)}")
    
    @staticmethod
    def _extract_text_content(mock_data: Dict[str, Any], debug_prefix: str) -> str:
        """Extrai conteúdo de texto do mock data"""
        # Suportar diferentes formatos JSON
        if "analyzeResult" in mock_data:
            logger.info("Using old format JSON structure")
            text_content = mock_data["analyzeResult"]["content"]
        else:
            logger.info("Using new format JSON structure")
            text_content = mock_data.get("content", "")
        
        # Limpar marcas de seleção do Azure
        from app.services.base.text_normalizer import TextNormalizer
        return TextNormalizer.clean_extracted_text(text_content, "azure")
    
    @staticmethod
    async def _process_mock_images(mock_data: Dict[str, Any], debug_prefix: str) -> tuple[List[Dict], Dict[str, str]]:
        """
        Processa imagens mock, tentando extrair imagens reais do PDF
        
        Returns:
            tuple: (header_images, content_images)
        """
        header_images = []
        content_images = {}
        
        # Extrair figuras do mock data
        figures = MockDocumentService._extract_figures_from_mock(mock_data, debug_prefix)
        
        if not figures:
            return header_images, content_images
        
        # Tentar extrair imagens reais do PDF
        pdf_path = MockDataConstants.get_primary_mock_pdf_path()
        if pdf_path.exists():
            header_images, content_images = await MockDocumentService._extract_real_images_from_pdf(
                figures, pdf_path, mock_data, debug_prefix
            )
        else:
            logger.info(f"PDF file {pdf_path} not found, using mock images")
            header_images, content_images = MockDocumentService._generate_fallback_mock_images(
                figures, mock_data, debug_prefix
            )
        
        logger.info(f"Categorized {len(header_images)} header images and {len(content_images)} content images")
        return header_images, content_images
    
    @staticmethod
    def _extract_figures_from_mock(mock_data: Dict[str, Any], debug_prefix: str) -> List[Dict]:
        """Extrai lista de figuras do mock data"""
        figures = []
        
        if "analyzeResult" in mock_data and "figures" in mock_data["analyzeResult"]:
            # Formato antigo
            figures = mock_data["analyzeResult"]["figures"]
        elif "figures" in mock_data:
            # Formato novo
            figures = mock_data["figures"]
        
        if figures:
            logger.info(f"Found {len(figures)} figures in mock data")
        
        return figures
    
    @staticmethod
    async def _extract_real_images_from_pdf(
        figures: List[Dict], 
        pdf_path: Path, 
        mock_data: Dict[str, Any], 
        debug_prefix: str
    ) -> tuple[List[Dict], Dict[str, str]]:
        """Extrai imagens reais do PDF usando coordenadas das figuras"""
        header_images = []
        content_images = {}
        
        try:
            from app.services.utils.pdf_image_extractor import PDFImageExtractor
            
            logger.info(f"Extracting real images from {pdf_path}")
            
            for figure in figures:
                figure_id = figure.get("id", f"mock_figure_{len(content_images)}")
                
                if "boundingRegions" in figure and figure["boundingRegions"]:
                    region = figure["boundingRegions"][0]
                    page_number = region.get("pageNumber", 1)
                    polygon = region.get("polygon", [])
                    
                    if polygon:
                        # Extrair a imagem real
                        image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                            pdf_path=str(pdf_path),
                            page_number=page_number,
                            coordinates=polygon
                        )
                        
                        if image_bytes:
                            base64_image = PDFImageExtractor.get_base64_image(image_bytes)
                            MockDocumentService._categorize_image(
                                figure, base64_image, figure_id, mock_data,
                                header_images, content_images, debug_prefix
                            )
                        else:
                            # Fallback para imagem mock
                            mock_image = MockDocumentService._generate_mock_image_base64()
                            MockDocumentService._categorize_image(
                                figure, mock_image, figure_id, mock_data,
                                header_images, content_images, debug_prefix
                            )
                    else:
                        # Sem polígono, usar imagem mock
                        mock_image = MockDocumentService._generate_mock_image_base64()
                        MockDocumentService._categorize_image(
                            figure, mock_image, figure_id, mock_data,
                            header_images, content_images, debug_prefix
                        )
                else:
                    # Sem boundingRegions, usar imagem mock
                    mock_image = MockDocumentService._generate_mock_image_base64()
                    MockDocumentService._categorize_image(
                        figure, mock_image, figure_id, mock_data,
                        header_images, content_images, debug_prefix
                    )
        
        except Exception as e:
            logger.error(f"Error extracting real images: {str(e)}")
            # Fallback completo para imagens mock
            header_images, content_images = MockDocumentService._generate_fallback_mock_images(
                figures, mock_data, debug_prefix
            )
        
        return header_images, content_images
    
    @staticmethod
    def _generate_fallback_mock_images(
        figures: List[Dict], 
        mock_data: Dict[str, Any], 
        debug_prefix: str
    ) -> tuple[List[Dict], Dict[str, str]]:
        """Gera imagens mock de fallback para todas as figuras"""
        header_images = []
        content_images = {}
        
        for figure in figures:
            figure_id = figure.get("id", f"mock_figure_{len(content_images)}")
            mock_image = MockDocumentService._generate_mock_image_base64()
            MockDocumentService._categorize_image(
                figure, mock_image, figure_id, mock_data,
                header_images, content_images, debug_prefix
            )
        
        return header_images, content_images
    
    @staticmethod
    def _categorize_image(
        figure: Dict, 
        base64_image: str, 
        figure_id: str, 
        mock_data: Dict[str, Any],
        header_images: List[Dict], 
        content_images: Dict[str, str], 
        debug_prefix: str
    ):
        """Categoriza uma imagem como header ou content"""
        if MockDocumentService._is_header_image(figure, mock_data):
            header_images.append({"content": base64_image})
            logger.info(f"Figure {figure_id} categorized as HEADER image")
        else:
            content_images[figure_id] = base64_image
            logger.info(f"Figure {figure_id} categorized as CONTENT image")
    
    @staticmethod
    def _generate_mock_image_base64() -> str:
        """
        Gera uma imagem mock em base64 para testes
        Utilizado quando não temos o PDF original para extrair a imagem real
        """
        config = MockDataConstants.MOCK_IMAGE_CONFIG
        
        # Criar uma imagem simples com texto
        width, height = config["width"], config["height"]
        image = Image.new("RGB", (width, height), color=config["background_color"])
        draw = ImageDraw.Draw(image)
        
        # Desenhar um retângulo
        draw.rectangle([(50, 50), (350, 250)], outline=config["border_color"], width=2)
        
        # Adicionar texto
        draw.text((150, 130), "Imagem Mock", fill=config["text_color"])
        draw.text((130, 170), "Apenas para teste", fill=config["text_color"])
        
        # Converter para base64
        buffer = io.BytesIO()
        image.save(buffer, format=config["format"])
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_str
    
    @staticmethod
    def _is_header_image(figure: Dict, azure_result: Dict) -> bool:
        """
        Determina se uma figura faz parte do cabeçalho do documento com base em sua posição
        e relação com os elementos do documento.
        """
        figure_id = figure.get("id", "unknown")
        print(f"🔍 DEBUG: Analyzing figure {figure_id} for header categorization")
        
        # Verificar se a figura está na primeira página
        if not figure.get("boundingRegions"):
            print(f"🔍 DEBUG: Figure {figure_id} has no boundingRegions - categorized as CONTENT")
            return False
            
        # Pegar a primeira região (normalmente só existe uma)
        region = figure["boundingRegions"][0]
        page_number = region.get("pageNumber", 0)
        max_page = MockDataConstants.HEADER_DETECTION["max_page_for_header"]
        
        print(f"🔍 DEBUG: Figure {figure_id} is on page {page_number}, max_page for header: {max_page}")
        
        if page_number != max_page:
            # Imagens de cabeçalho geralmente estão na primeira página
            print(f"🔍 DEBUG: Figure {figure_id} not on first page - categorized as CONTENT")
            return False
        
        # Verificar se há elementos associados ao cabeçalho
        header_elements = []
        
        # Procurar por parágrafos com role="pageHeader"
        for para in azure_result.get("paragraphs", []):
            if para.get("role") == "pageHeader":
                header_elements.append(para)
        
        print(f"🔍 DEBUG: Found {len(header_elements)} header elements in document")
        
        # Se não houver elementos de cabeçalho, usar uma heurística baseada na posição vertical
        if not header_elements:
            print(f"🔍 DEBUG: No pageHeader elements found, using position-based heuristic for figure {figure_id}")
            # Considerar imagens no topo da primeira página como parte do cabeçalho
            polygon = region.get("polygon", [])
            if polygon and len(polygon) >= 2:
                # Pegar coordenada Y (a segunda em cada par de coordenadas)
                y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
                avg_y = sum(y_values) / len(y_values)
                
                threshold = MockDataConstants.HEADER_DETECTION["vertical_threshold"]
                
                print(f"🔍 DEBUG: Figure {figure_id} position - avg_y: {avg_y:.4f}, threshold: {threshold}")
                
                is_header = avg_y < threshold
                print(f"🔍 DEBUG: Figure {figure_id} {'IS' if is_header else 'IS NOT'} in header area (position-based)")
                return is_header
            else:
                print(f"🔍 DEBUG: Figure {figure_id} has no polygon data - categorized as CONTENT")
                return False
        else:
            print(f"🔍 DEBUG: Using span-based analysis for figure {figure_id}")
            # Verificar se a figura está próxima ou sobreposta a algum elemento do cabeçalho
            figure_spans = figure.get("spans", [])
            
            print(f"🔍 DEBUG: Figure {figure_id} has {len(figure_spans)} spans")
            
            # Se a figura tiver spans, verificar se há sobreposição com os spans do cabeçalho
            if figure_spans:
                for f_span in figure_spans:
                    f_offset = f_span.get("offset", 0)
                    f_length = f_span.get("length", 0)
                    f_end = f_offset + f_length
                    
                    # Verificar sobreposição com spans do cabeçalho
                    for header_elem in header_elements:
                        for h_span in header_elem.get("spans", []):
                            h_offset = h_span.get("offset", 0)
                            h_length = h_span.get("length", 0)
                            h_end = h_offset + h_length
                            
                            # Verificar se há sobreposição
                            if (f_offset <= h_end and f_end >= h_offset):
                                print(f"🔍 DEBUG: Figure {figure_id} overlaps with header element - categorized as HEADER")
                                return True
                
                print(f"🔍 DEBUG: Figure {figure_id} has spans but no overlap with header elements")
            
            # Se não houve sobreposição de spans, usar posição Y como fallback
            polygon = region.get("polygon", [])
            if polygon and len(polygon) >= 2:
                y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
                avg_y = sum(y_values) / len(y_values)
                threshold = MockDataConstants.HEADER_DETECTION["vertical_threshold"]
                
                print(f"🔍 DEBUG: Figure {figure_id} fallback position - avg_y: {avg_y:.4f}, threshold: {threshold}")
                
                is_header = avg_y < threshold
                print(f"🔍 DEBUG: Figure {figure_id} {'IS' if is_header else 'IS NOT'} in header area (fallback position)")
                return is_header
            else:
                print(f"🔍 DEBUG: Figure {figure_id} has no polygon data for fallback - categorized as CONTENT")
        
        print(f"🔍 DEBUG: Figure {figure_id} final decision - categorized as CONTENT")
        return False

    @staticmethod
    async def process_document_mock_text_only(email: str = "test@mock.com", filename: str = None) -> Dict[str, Any]:
        """
        Processa documento mock apenas para texto e metadados, sem extração de imagens.
        Usado quando queremos processar imagens separadamente com classes isoladas.
        """
        if filename is None:
            filename = MockDataConstants.DEFAULT_MOCK_FILENAME
            
        document_id = str(uuid4())
        debug_prefix = GeneralConstants.get_debug_prefix("info")
        logger.info(f"Processing MOCK document (text only) {filename} for {email}")

        # Carregar dados mock
        mock_data = MockDocumentService._load_mock_data()
        
        # Extrair apenas conteúdo de texto
        text_content = MockDocumentService._extract_text_content(mock_data, debug_prefix)
        
        # Processar header
        header_parser = HeaderParser()
        header_result = header_parser.parse(text_content)
        
        # Processar perguntas
        question_parser = QuestionParser()
        question_result = question_parser.extract(text_content)
        questions = question_result.get("questions", [])
        
        return {
            "document_id": document_id,
            "text_content": text_content,
            "header": header_result,
            "questions": questions,
            "images": [],  # Sem imagens neste método
            "metadata": {
                "email": email,
                "filename": filename,
                "processing_mode": "mock_text_only",
                "raw_response": mock_data
            }
        }

    @staticmethod
    async def process_document_mock_images_only(pdf_path: Path) -> List[Dict]:
        """
        Extrai apenas imagens do PDF usando classe isolada ManualPDFImageExtractor.
        Usado quando queremos centralizar a lógica de extração manual nas classes isoladas.
        """
        from app.services.image.extraction.manual_pdf_extractor import ManualPDFImageExtractor
        
        logger.info(f"Extracting images from PDF using isolated ManualPDFImageExtractor: {pdf_path}")
        
        # Carregar resposta mock para coordenadas
        mock_data = MockDocumentService._load_mock_data()
        
        # Usar extrator isolado
        extractor = ManualPDFImageExtractor()
        
        # Simular UploadFile-like object do Path
        with open(pdf_path, 'rb') as file:
            file_content = file.read()
        
        # Criar mock file object
        import io
        from fastapi import UploadFile
        
        mock_file_obj = io.BytesIO(file_content)
        mock_file = UploadFile(
            filename=pdf_path.name,
            file=mock_file_obj,
            size=len(file_content),
            headers={"content-type": "application/pdf"}
        )
        
        # Extrair imagens usando classe isolada
        images = await extractor.extract_images(
            file=mock_file,
            document_analysis_result=mock_data,
            document_id="mock_manual_extraction"
        )
        
        logger.info(f"Manual extraction completed: {len(images)} images extracted")
        return images
