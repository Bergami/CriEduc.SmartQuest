"""
Teste detalhado da implementação do extrator de imagens usando coordenadas do Azure Document Intelligence
com o fator de escala de 72 pontos. Inclui logs adicionais para depuração.
"""
import sys
import os
import logging
from pathlib import Path
import fitz  # PyMuPDF

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar o diretório do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.utils.pdf_image_extractor import PDFImageExtractor

def test_extract_with_scale_factor():
    """
    Testa a extração de imagem usando o fator de escala de 72 pontos com logs detalhados
    """
    # Caminhos
    current_dir = Path(__file__).parent
    # Corrigir o caminho para apontar para tests/fixtures/pdfs/
    pdf_path = current_dir.parent.parent / "fixtures" / "pdfs" / "modelo-prova.pdf"
    output_dir = current_dir / "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Coordenadas da figura 2.1 do JSON
    # pageNumber: 2, polygon: [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
    polygon = [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
    page_number = 2  # Página 2 como reportado pelo Azure (1-indexed)
    
    logger.info(f"Extraindo imagem da página {page_number} do PDF {pdf_path}")
    logger.info(f"Usando polígono: {polygon}")
    
    # Exibir informações sobre o PDF
    doc = fitz.open(str(pdf_path))
    logger.info(f"Número total de páginas no PDF: {len(doc)}")
    
    if page_number <= len(doc):
        page = doc[page_number-1]  # Ajustando para 0-indexed do PyMuPDF
        width, height = page.rect.width, page.rect.height
        logger.info(f"Dimensões da página {page_number}: {width}x{height}")
    else:
        logger.error(f"Página {page_number} não existe no PDF")
        return
    
    # Simular o processamento para ver o que acontece com as coordenadas
    x_values = [polygon[i] for i in range(0, len(polygon), 2)]
    y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
    
    logger.info(f"X values originais: {x_values}")
    logger.info(f"Y values originais: {y_values}")
    
    # Aplicar o fator de escala manualmente para verificar
    scale_factor = 72
    x_scaled = [x * scale_factor for x in x_values]
    y_scaled = [y * scale_factor for y in y_values]
    
    logger.info(f"X values escalados (72): {x_scaled}")
    logger.info(f"Y values escalados (72): {y_scaled}")
    
    # Calcular o retângulo delimitador manualmente
    x0 = max(0, min(x_scaled))
    y0 = max(0, min(y_scaled))
    x1 = min(width, max(x_scaled))
    y1 = min(height, max(y_scaled))
    
    logger.info(f"Retângulo calculado manualmente: ({x0}, {y0}, {x1}, {y1})")
    
    # Extrair imagem usando nosso extrator atualizado com o fator de escala de 72 pontos
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,
        coordinates=polygon
    )
    
    if image_bytes:
        output_path = output_dir / "figura_2_1_scale_72_detailed.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        logger.info(f"Imagem extraída com sucesso usando fator de escala 72!")
        logger.info(f"Imagem salva em: {output_path}")
        logger.info(f"Tamanho da imagem: {len(image_bytes) / 1024:.2f} KB")
    else:
        logger.error("Falha ao extrair a imagem")
    
    doc.close()

if __name__ == "__main__":
    test_extract_with_scale_factor()
