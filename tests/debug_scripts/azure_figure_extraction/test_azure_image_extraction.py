"""
Teste da implementação do extrator de imagens usando coordenadas do Azure Document Intelligence
com o fator de escala de 72 pontos.
"""
import sys
import os
from pathlib import Path
import fitz  # PyMuPDF

# Adicionar o diretório do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.utils.pdf_image_extractor import PDFImageExtractor

def test_extract_with_scale_factor():
    """
    Testa a extração de imagem usando o fator de escala de 72 pontos
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
    
    print(f"Extraindo imagem da página {page_number} do PDF {pdf_path}")
    print(f"Usando polígono: {polygon}")
    
    # Exibir informações sobre o PDF
    doc = fitz.open(str(pdf_path))
    print(f"Número total de páginas no PDF: {len(doc)}")
    
    if page_number <= len(doc):
        page = doc[page_number-1]  # Ajustando para 0-indexed do PyMuPDF
        width, height = page.rect.width, page.rect.height
        print(f"Dimensões da página {page_number}: {width}x{height}")
    else:
        print(f"Página {page_number} não existe no PDF")
        return
    
    # Extrair imagem usando nosso extrator atualizado com o fator de escala de 72 pontos
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,
        coordinates=polygon
    )
    
    if image_bytes:
        output_path = output_dir / "figura_2_1_scale_72.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Imagem extraída com sucesso usando fator de escala 72!")
        print(f"Imagem salva em: {output_path}")
        print(f"Tamanho da imagem: {len(image_bytes) / 1024:.2f} KB")
    else:
        print("Falha ao extrair a imagem")
    
    doc.close()

if __name__ == "__main__":
    test_extract_with_scale_factor()
