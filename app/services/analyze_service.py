import json
import os
from typing import Dict, Any
from uuid import uuid4
from pathlib import Path
from fastapi import UploadFile
from app.parsers.header_parser import HeaderParser
from app.parsers.question_parser import QuestionParser
from app.services.document_extraction_factory import DocumentExtractionFactory
from app.core.exceptions import DocumentProcessingError
from app.utils.final_result_builder import FinalResultBuilder
from app.core.constants import MockDataConstants, GeneralConstants

class AnalyzeService:
    @staticmethod
    async def process_document(file: UploadFile, email: str, use_json_fallback: bool = False) -> Dict[str, Any]:
        document_id = str(uuid4())
        print(f"🔍 DEBUG: Processando documento {file.filename} para {email}")
        print(f"🔍 DEBUG: Document ID gerado: {document_id}")

        if use_json_fallback:
            print("🔍 DEBUG: Usando fallback JSON...")
            # Carrega resultado_parser.json
            with open("resultado_parser.json", "r", encoding="utf-8") as f:
                parsed_data = json.load(f)

            parsed_data["document_id"] = document_id
            parsed_data["email"] = email
            parsed_data["filename"] = file.filename
            parsed_data["extracted_text"] = "Documento carregado via fallback JSON."

            return parsed_data

        # 🆕 USAR DOCUMENT EXTRACTION FACTORY (com Azure como padrão)
        try:
            print("🔍 DEBUG: Processing with Document Extraction Factory...")
            extracted_data = await AnalyzeService._extract_text_and_metadata_with_factory(file)
            print("✅ DEBUG: Document extraction executed successfully")
        except Exception as e:
            print(f"❌ DEBUG: Error in document extraction: {str(e)}")
            print(f"🔍 DEBUG: Error type: {type(e).__name__}")
            
            # Raise custom exception for client
            error_message = f"Failed to process document: {str(e)}"
            print(f"🚨 DEBUG: Raising DocumentProcessingError: {error_message}")
            raise DocumentProcessingError(error_message)
        
        print(f"🔍 DEBUG: Text extracted: {len(extracted_data['text'])} characters")
        print(f"🔍 DEBUG: Header: {extracted_data['header']}")
        
        print("🔍 DEBUG: Extracting questions...")
        # Verificar se temos dados de imagens
        image_data = extracted_data.get("images", {})
        if image_data:
            print(f"🔍 DEBUG: {len(image_data)} images available for context blocks")
            
        question_data = QuestionParser.extract(extracted_data["text"], image_data)
        print(f"🔍 DEBUG: Questões encontradas: {len(question_data['questions'])}")
        print(f"🔍 DEBUG: Blocos de contexto: {len(question_data['context_blocks'])}")

        result = {
            "email": email,
            "document_id": document_id,
            "filename": file.filename,
            "header": extracted_data["header"],
            "questions": question_data["questions"],
            "context_blocks": question_data["context_blocks"],
            "extracted_text": extracted_data["text"][:500],
            "provider_metadata": extracted_data.get("metadata", {})
        }
        
        print("✅ DEBUG: Resultado final montado")
        return result

    @staticmethod
    async def _extract_text_and_metadata_with_factory(file: UploadFile) -> Dict[str, Any]:
        """
        Extract text and metadata using the Document Extraction Factory.
        Supports multiple providers with automatic fallback.
        """
        # Get the configured extraction provider
        extractor = DocumentExtractionFactory.get_provider()
        provider_name = extractor.get_provider_name()
        
        print(f"🔍 DEBUG: Using extraction provider: {provider_name}")
        
        # Extract document data
        extracted_data = await extractor.extract_document_data(file)
        
        # Parse header information from extracted text
        header_data = HeaderParser.parse(extracted_data["text"])
        
        # Return structured data compatible with current system
        return {
            "text": extracted_data["text"],
            "header": header_data,
            "images": extracted_data.get("image_data", {}),  # Adiciona dados de imagens
            "metadata": {
                **extracted_data.get("metadata", {}),
                "extraction_provider": provider_name,
                "confidence": extracted_data.get("confidence", 0.0),
                "page_count": extracted_data.get("page_count", 1)
            }
        }

    @staticmethod
    async def process_document_mock(email: str, filename: str = None) -> Dict[str, Any]:
        """
        Process document using mocked data from RetornoProcessamento.json
        Does not require physical file
        """
        if filename is None:
            filename = MockDataConstants.DEFAULT_MOCK_FILENAME
            
        document_id = str(uuid4())
        debug_prefix = GeneralConstants.get_debug_prefix("info")
        print(f"{debug_prefix} Processing MOCK document {filename} for {email}")
        print(f"{debug_prefix} Generated Document ID: {document_id}")

        # Use mock data constants for file paths with fallback logic
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
            success_prefix = GeneralConstants.get_debug_prefix("success")
            print(f"{debug_prefix} Loading mock data from {json_path.name}...")
            with open(json_path, 'r', encoding=GeneralConstants.TEXT_PROCESSING["default_encoding"]) as f:
                mock_data = json.load(f)
            
            print(f"{success_prefix} Mock data loaded successfully")
            # Extract text content from mock structure - handle different JSON structures
            if "analyzeResult" in mock_data:
                # Formato antigo
                print(f"{debug_prefix} Using old format JSON structure")
                text_content = mock_data["analyzeResult"]["content"]
            else:
                # Novo formato (sem analyzeResult como chave raiz)
                print(f"{debug_prefix} Using new format JSON structure")
                text_content = mock_data.get("content", "")
            
            # Clean Azure selection marks using TextNormalizer
            from app.services.base.text_normalizer import TextNormalizer
            text_content = TextNormalizer.clean_extracted_text(text_content, "azure")

            # Process mock data same as normal method
            # First, categorize images into header and content
            header_images = []
            content_images = {}
            
            # Verificar se existem dados de imagens (figuras) no mock
            image_data = {}
            # Verificar no formato antigo ou novo
            has_figures = False
            figures = []
            
            if "analyzeResult" in mock_data and "figures" in mock_data["analyzeResult"]:
                # Formato antigo
                figures = mock_data["analyzeResult"]["figures"]
                has_figures = True
            elif "figures" in mock_data:
                # Formato novo
                figures = mock_data["figures"]
                has_figures = True
                
            if has_figures:
                print(f"{debug_prefix} Found {len(figures)} figures in mock data")
                
                # Usar o PDF real para extrair as imagens
                pdf_path = MockDataConstants.get_primary_mock_pdf_path()
                if pdf_path.exists():
                    try:
                        # Extrair imagens do PDF real usando PDFImageExtractor
                        from app.services.utils.pdf_image_extractor import PDFImageExtractor
                        
                        print(f"{debug_prefix} Extracting real images from {pdf_path}")
                        for figure in figures:
                            figure_id = figure.get("id", f"mock_figure_{len(image_data)}")
                            
                            # Extrair as regiões de bounding box
                            if "boundingRegions" in figure and figure["boundingRegions"]:
                                region = figure["boundingRegions"][0]
                                page_number = region.get("pageNumber", 1)
                                polygon = region.get("polygon", [])
                                
                                if polygon:
                                    # Extrair a imagem
                                    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                                        pdf_path=str(pdf_path),
                                        page_number=page_number,
                                        coordinates=polygon
                                    )
                                    
                                    if image_bytes:
                                        # Converter para base64
                                        base64_image = PDFImageExtractor.get_base64_image(image_bytes)
                                        
                                        # Categorizar a imagem
                                        if AnalyzeService._is_header_image(figure, mock_data):
                                            header_images.append({
                                                "content": base64_image
                                            })
                                            print(f"{debug_prefix} Figure {figure_id} categorized as HEADER image")
                                        else:
                                            content_images[figure_id] = base64_image
                                            print(f"{debug_prefix} Figure {figure_id} categorized as CONTENT image")
                                    else:
                                        # Fallback para imagem mock se extração falhar
                                        mock_image = AnalyzeService._generate_mock_image_base64()
                                        if AnalyzeService._is_header_image(figure, mock_data):
                                            header_images.append({
                                                "content": mock_image
                                            })
                                        else:
                                            content_images[figure_id] = mock_image
                                        print(f"{debug_prefix} Failed to extract real image, using mock for figure {figure_id}")
                                else:
                                    # Sem polígono, usar imagem mock
                                    mock_image = AnalyzeService._generate_mock_image_base64()
                                    if AnalyzeService._is_header_image(figure, mock_data):
                                        header_images.append({
                                            "content": mock_image
                                        })
                                    else:
                                        content_images[figure_id] = mock_image
                                    print(f"{debug_prefix} No polygon data, using mock for figure {figure_id}")
                            else:
                                # Sem boundingRegions, usar imagem mock
                                mock_image = AnalyzeService._generate_mock_image_base64()
                                if AnalyzeService._is_header_image(figure, mock_data):
                                    header_images.append({
                                        "content": mock_image
                                    })
                                else:
                                    content_images[figure_id] = mock_image
                                print(f"{debug_prefix} No boundingRegions, using mock for figure {figure_id}")
                    except Exception as e:
                        print(f"{debug_prefix} Error extracting real images: {str(e)}")
                        # Fallback para imagens mock
                        for figure in figures:
                            figure_id = figure.get("id", f"mock_figure_{len(content_images)}")
                            mock_image = AnalyzeService._generate_mock_image_base64()
                            if AnalyzeService._is_header_image(figure, mock_data):
                                header_images.append({
                                    "content": mock_image
                                })
                            else:
                                content_images[figure_id] = mock_image
                else:
                    print(f"{debug_prefix} PDF file {pdf_path} not found, using mock images")
                    # Fallback para imagens mock
                    for figure in figures:
                        figure_id = figure.get("id", f"mock_figure_{len(content_images)}")
                        mock_image = AnalyzeService._generate_mock_image_base64()
                        if AnalyzeService._is_header_image(figure, mock_data):
                            header_images.append({
                                "content": mock_image
                            })
                        else:
                            content_images[figure_id] = mock_image
                    
                print(f"{debug_prefix} Categorized {len(header_images)} header images and {len(content_images)} content images")
            
            # Now create header_data with categorized header images
            header_data = HeaderParser.parse(text_content, header_images)
            print(f"{debug_prefix} Header extracted from mock with {len(header_images)} images: {header_data}")
            print(f"{debug_prefix} Header has images key: {'images' in header_data}")
            if 'images' in header_data:
                print(f"{debug_prefix} Header images content: {header_data['images']}")
            
            print(f"{debug_prefix} Extracting questions from mock...")
            question_data = QuestionParser.extract(text_content, content_images)
            print(f"{debug_prefix} Questions found in mock: {len(question_data['questions'])}")
            print(f"{debug_prefix} Context blocks in mock: {len(question_data['context_blocks'])}")

            result = {
                "email": email,
                "document_id": document_id,
                "filename": filename,
                "header": header_data,
                "questions": question_data["questions"],
                "context_blocks": question_data["context_blocks"]
            }
            
            success_prefix = GeneralConstants.get_debug_prefix("success")
            print(f"{success_prefix} Mock processing completed")
            return result
            
        except json.JSONDecodeError as e:
            raise DocumentProcessingError(f"Error decoding mock JSON: {str(e)}")
        except Exception as e:
            raise DocumentProcessingError(f"Error loading mock data: {str(e)}")
    
    @staticmethod
    def _generate_mock_image_base64() -> str:
        """
        Gera uma imagem mock em base64 para testes
        Utilizado quando não temos o PDF original para extrair a imagem real
        """
        import base64
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Usar configurações das constantes
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
    def _is_header_image(figure, azure_result):
        """
        Determina se uma figura faz parte do cabeçalho do documento com base em sua posição
        e relação com os elementos do documento.
        
        Args:
            figure: Dicionário da figura do Azure Document Intelligence
            azure_result: Resultado completo do Azure Document Intelligence
            
        Returns:
            bool: True se a figura faz parte do cabeçalho, False caso contrário
        """
        # Verificar se a figura está na primeira página
        if not figure.get("boundingRegions"):
            return False
            
        # Pegar a primeira região (normalmente só existe uma)
        region = figure["boundingRegions"][0]
        max_page = MockDataConstants.HEADER_DETECTION["max_page_for_header"]
        if region.get("pageNumber", 0) != max_page:
            # Imagens de cabeçalho geralmente estão na primeira página
            return False
        
        # Verificar se há elementos associados ao cabeçalho
        header_elements = []
        
        # Procurar por parágrafos com role="pageHeader"
        for para in azure_result.get("paragraphs", []):
            if para.get("role") == "pageHeader":
                header_elements.append(para)
        
        # Se não houver elementos de cabeçalho, usar uma heurística baseada na posição vertical
        if not header_elements:
            # Considerar imagens no topo da primeira página como parte do cabeçalho
            # (primeiros X% da altura da página - configurado nas constantes)
            polygon = region.get("polygon", [])
            if polygon and len(polygon) >= 2:
                # Pegar coordenada Y (a segunda em cada par de coordenadas)
                y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
                avg_y = sum(y_values) / len(y_values)
                
                # Se a posição vertical média da imagem estiver no topo da página
                # (considerando que as coordenadas são normalizadas de 0 a 1)
                threshold = MockDataConstants.HEADER_DETECTION["vertical_threshold"]
                return avg_y < threshold
        else:
            # Verificar se a figura está próxima ou sobreposta a algum elemento do cabeçalho
            figure_spans = figure.get("spans", [])
            
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
                                return True
            
            # Se não houve sobreposição de spans, usar posição Y como fallback
            polygon = region.get("polygon", [])
            if polygon and len(polygon) >= 2:
                y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
                avg_y = sum(y_values) / len(y_values)
                threshold = MockDataConstants.HEADER_DETECTION["vertical_threshold"]
                return avg_y < threshold
        
        return False
