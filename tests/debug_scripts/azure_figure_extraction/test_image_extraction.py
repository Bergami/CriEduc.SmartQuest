import os
import json
import sys
from pathlib import Path

# Adicionar o diretório raiz ao sys.path para importar os módulos da aplicação
sys.path.append(str(Path(__file__).parent.parent))

from app.services.utils.pdf_image_extractor import PDFImageExtractor

def extract_specific_figure():
    """
    Testa a extração de uma figura específica da página 2 do PDF
    """
    # Caminhos
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "modelo-prova.pdf"
    output_dir = current_dir / "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Coordenadas da figura 2.1 do JSON (página 2)
    # As coordenadas podem estar em formato absoluto ou normalizado
    polygon = [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
    page_number = 2  # 0-indexed na biblioteca PyMuPDF, mas 1-indexed na resposta Azure
    
    print(f"Extraindo imagem da página {page_number} do PDF {pdf_path}")
    print(f"Usando coordenadas: {polygon}")
    
    # Tentativa com página 2 (contando a partir de 1 como na API Azure)
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,  # 2 como na resposta da Azure
        coordinates=polygon
    )
    
    if image_bytes:
        # Salvar a imagem
        output_path = output_dir / "figura_pagina2_azure_index.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Imagem salva em: {output_path}")
    else:
        print("Falha ao extrair a imagem com índice Azure")
    
    # Tentativa com página 1 (0-indexed como no PyMuPDF)
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number-1,  # Ajustando para 0-indexed do PyMuPDF
        coordinates=polygon
    )
    
    if image_bytes:
        # Salvar a imagem
        output_path = output_dir / "figura_pagina2_pymupdf_index.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Imagem salva em: {output_path}")
    else:
        print("Falha ao extrair a imagem com índice PyMuPDF")

def main():
    # Caminhos de arquivo
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "modelo-prova.pdf"
    json_path = current_dir / "azure_response_3Tri_20250716_215103.json"
    output_dir = current_dir / "extracted_images"
    
    # Criar diretório para imagens extraídas se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar o resultado do Azure
    with open(json_path, "r", encoding="utf-8") as f:
        azure_result = json.load(f)
    
    # Extrair figuras do PDF
    extracted_figures = PDFImageExtractor.extract_figures_from_azure_result(
        pdf_path=str(pdf_path),
        azure_result=azure_result
    )
    
    # Salvar as imagens extraídas
    for figure_id, img_bytes in extracted_figures.items():
        # Salvar como arquivo PNG
        output_path = output_dir / f"figure_{figure_id}.png"
        with open(output_path, "wb") as img_file:
            img_file.write(img_bytes)
        print(f"Imagem {figure_id} salva em {output_path}")
    
    print(f"Total de imagens extraídas: {len(extracted_figures)}")

if __name__ == "__main__":
    # main()
    extract_specific_figure()
