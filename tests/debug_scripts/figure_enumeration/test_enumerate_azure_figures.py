"""
Teste para enumerar todas as figuras detectadas pelo Azure Document Intelligence
e extraí-las uma a uma para verificação.
"""
import sys
import os
import json
import base64
import logging
from pathlib import Path
import fitz  # PyMuPDF
from io import BytesIO

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

def test_enumerate_all_figures():
    """
    Carrega o resultado do Azure Document Intelligence e enumera todas as figuras detectadas,
    extraindo-as uma a uma para verificação visual.
    """
    # Caminhos
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "modelo-prova.pdf"
    output_dir = current_dir / "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Carregar o resultado do Azure Document Intelligence
    json_path = current_dir / "RetornoProcessamento.json"
    if not json_path.exists():
        logger.error(f"Arquivo JSON {json_path} não encontrado")
        return
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            azure_result = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo JSON: {str(e)}")
        return
    
    # Verificar se há figuras no resultado
    figures = []
    
    # Verificar no formato antigo ou novo
    if "analyzeResult" in azure_result and "figures" in azure_result["analyzeResult"]:
        # Formato antigo
        figures = azure_result["analyzeResult"]["figures"]
    elif "figures" in azure_result:
        # Formato novo
        figures = azure_result["figures"]
    
    if not figures:
        logger.error("Nenhuma figura encontrada no resultado do Azure")
        return
    
    logger.info(f"Encontradas {len(figures)} figuras no resultado do Azure")
    
    # Extrair cada figura detectada
    for i, figure in enumerate(figures):
        figure_id = figure.get("id", f"figure_{i}")
        logger.info(f"\nProcessando figura {figure_id} ({i+1} de {len(figures)})")
        
        # Extrair as regiões de bounding box
        if "boundingRegions" not in figure or not figure["boundingRegions"]:
            logger.warning(f"Figura {figure_id} sem boundingRegions")
            continue
        
        for region_idx, region in enumerate(figure["boundingRegions"]):
            page_number = region.get("pageNumber", 1)
            polygon = region.get("polygon", [])
            
            if not polygon:
                logger.warning(f"Região {region_idx} da figura {figure_id} sem polígono")
                continue
            
            logger.info(f"Figura {figure_id}, página {page_number}, polígono: {polygon}")
            
            # Extrair a imagem
            image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                pdf_path=str(pdf_path),
                page_number=page_number,
                coordinates=polygon
            )
            
            if not image_bytes:
                logger.warning(f"Falha ao extrair imagem da figura {figure_id}")
                continue
            
            # Salvar a imagem
            output_path = output_dir / f"azure_figure_{figure_id}_page_{page_number}.jpg"
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Imagem da figura {figure_id} salva em: {output_path}")
            
            # Converter para base64 e salvar os primeiros caracteres
            base64_str = PDFImageExtractor.get_base64_image(image_bytes)
            base64_path = output_dir / f"azure_figure_{figure_id}_page_{page_number}.txt"
            with open(base64_path, "w") as f:
                f.write(base64_str[:100] + "...")  # Apenas o início para não ficar muito grande
            logger.info(f"Base64 (início) da figura {figure_id} salvo em: {base64_path}")
            
            # Verificar se corresponde ao base64 fornecido
            provided_base64_start = "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQEBAQIBAQECAgICAgQDAgICAgUEBAMEBgUGBgYFBgYGBwkIBgcJBwYGCAsICQoK"
            if base64_str.startswith(provided_base64_start):
                logger.info(f"✅ MATCH! A figura {figure_id} corresponde ao base64 fornecido")
            
    logger.info("\nProcessamento concluído")

if __name__ == "__main__":
    test_enumerate_all_figures()
