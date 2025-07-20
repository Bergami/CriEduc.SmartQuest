import fitz  # PyMuPDF
import os
import logging
import base64
from typing import Optional, Dict, Any, List, Tuple
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class PDFImageExtractor:
    """
    Classe responsável por extrair imagens de documentos PDF usando as coordenadas
    obtidas da resposta do Azure Document Intelligence
    """

    @staticmethod
    def extract_figure_from_pdf(
        pdf_path: str, 
        page_number: int, 
        coordinates: List[float]
    ) -> Optional[bytes]:
        """
        Extrai uma figura específica de um documento PDF usando coordenadas
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            page_number: Número da página (1-indexed, como retornado pelo Azure)
            coordinates: Lista de coordenadas do polígono [x1, y1, x2, y2, x3, y3, x4, y4]
                       Formato Azure Document Intelligence: 
                       [Superior-esquerdo X, Y, Superior-direito X, Y, 
                        Inferior-direito X, Y, Inferior-esquerdo X, Y]
                       As coordenadas são em pontos PDF (72 pontos = 1 polegada)
            
        Returns:
            Bytes da imagem extraída ou None se falhar
        """
        try:
            # Abrir o documento
            doc = fitz.open(pdf_path)
            
            # Ajustar page_number para 0-indexed (PyMuPDF usa 0-indexed)
            page_idx = page_number - 1
            
            if page_idx < 0 or page_idx >= len(doc):
                logger.error(f"Página {page_number} não encontrada no PDF {pdf_path}")
                return None
                
            # Obter a página
            page = doc[page_idx]
            
            # Obter dimensões da página
            width, height = page.rect.width, page.rect.height
            logger.info(f"Dimensões da página {page_number}: {width}x{height}")
            
            # Verificar o formato das coordenadas
            if len(coordinates) < 8:
                logger.error(f"Formato inválido de coordenadas: {coordinates}. Esperando 8 valores para o polígono.")
                return None
            
            # Verificar o formato das coordenadas do Azure Document Intelligence
            # As coordenadas do Azure são em pontos PDF (72 pontos = 1 polegada)
            
            logger.info(f"Coordenadas originais: {coordinates}")
            
            # Extrair os valores de x e y do polígono
            x_values = [coordinates[i] for i in range(0, len(coordinates), 2)]
            y_values = [coordinates[i+1] for i in range(0, len(coordinates), 2)]
            
            # Aplicar o fator de escala de 72 pontos (padrão PDF)
            # O Azure Document Intelligence retorna coordenadas em pontos PDF,
            # onde 72 pontos = 1 polegada
            scale_factor = 72
            x_values = [x * scale_factor for x in x_values]
            y_values = [y * scale_factor for y in y_values]
            
            logger.info(f"Coordenadas escaladas com fator {scale_factor}: X={x_values}, Y={y_values}")
                
            # Calcular o retângulo delimitador
            x0 = max(0, min(x_values))
            y0 = max(0, min(y_values))
            x1 = min(width, max(x_values))
            y1 = min(height, max(y_values))
            
            # Verificar se o retângulo tem tamanho suficiente
            if x1 - x0 < 10 or y1 - y0 < 10:
                logger.warning(f"Retângulo muito pequeno: {x0},{y0},{x1},{y1} - Ampliando")
                # Ampliar para pelo menos 300x300 ou tamanho adequado
                x_center = (x0 + x1) / 2
                y_center = (y0 + y1) / 2
                x0 = max(0, x_center - 150)
                y0 = max(0, y_center - 150)
                x1 = min(width, x_center + 150)
                y1 = min(height, y_center + 150)
            
            rect = fitz.Rect(x0, y0, x1, y1)
            logger.info(f"Retângulo de recorte final: {rect}")
            
            # Renderizar a parte da página como uma imagem com alta resolução
            matrix = fitz.Matrix(3, 3)  # Fator de zoom para melhor resolução (3x)
            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            
            logger.info(f"Imagem extraída com dimensões: {pix.width}x{pix.height}")
            
            # Converter para bytes
            img_bytes = BytesIO()
            pix.pil_save(img_bytes, format="JPEG", quality=95)  # Alta qualidade
            img_bytes.seek(0)
            
            doc.close()
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Erro ao extrair imagem do PDF: {str(e)}", exc_info=True)
            # Registrar informações adicionais para depuração
            logger.error(f"PDF: {pdf_path}, Página: {page_number}, Coordenadas: {coordinates}")
            return None
            
    @staticmethod
    def extract_figures_from_azure_result(
        pdf_path: str, 
        azure_result: Dict[str, Any]
    ) -> Dict[str, bytes]:
        """
        Extrai todas as figuras identificadas na resposta do Azure Document Intelligence
        
        Args:
            pdf_path: Caminho para o arquivo PDF original
            azure_result: Resultado JSON do Azure Document Intelligence
            
        Returns:
            Dicionário com ID da figura como chave e bytes da imagem como valor
        """
        extracted_figures = {}
        
        if "figures" not in azure_result:
            logger.warning("Nenhuma figura encontrada no resultado do Azure")
            return extracted_figures
        
        logger.info(f"Processando {len(azure_result['figures'])} figuras do resultado do Azure")
            
        for figure in azure_result["figures"]:
            figure_id = figure.get("id")
            
            if not figure_id:
                logger.warning("Figura sem ID encontrada, ignorando")
                continue
                
            # Obter regiões de delimitação da figura
            if not figure.get("boundingRegions"):
                logger.warning(f"Figura {figure_id} sem boundingRegions, ignorando")
                continue
                
            for region in figure["boundingRegions"]:
                page_number = region.get("pageNumber")
                polygon = region.get("polygon")
                
                if not page_number or not polygon:
                    logger.warning(f"Região sem página ou polígono para figura {figure_id}")
                    continue
                
                logger.info(f"Processando figura {figure_id} na página {page_number}")
                logger.info(f"Polígono: {polygon}")
                    
                # Extrair a imagem
                image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                    pdf_path=pdf_path,
                    page_number=page_number,
                    coordinates=polygon
                )
                
                if image_bytes:
                    extracted_figures[figure_id] = image_bytes
                    size_kb = len(image_bytes) / 1024
                    logger.info(f"Figura {figure_id} extraída com sucesso. Tamanho: {size_kb:.2f} KB")
                else:
                    logger.warning(f"Falha ao extrair figura {figure_id}")
                    
        logger.info(f"Total de figuras extraídas: {len(extracted_figures)} de {len(azure_result['figures'])}")
        return extracted_figures
        
    @staticmethod
    def get_base64_image(image_bytes: bytes) -> str:
        """
        Converte bytes de imagem para string base64
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            String base64 da imagem
        """
        if not image_bytes:
            return ""
            
        return base64.b64encode(image_bytes).decode('utf-8')
