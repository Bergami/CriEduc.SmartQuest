"""
Análise detalhada das figuras detectadas no arquivo azure_response_3Tri_20250716_215103.json
Extrai as figuras, suas propriedades e relações com o texto do documento.
"""
import sys
import os
import json
import base64
import logging
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='3tri_figures_analysis.log',
    filemode='w'
)
logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

# Adicionar o diretório do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.utils.pdf_image_extractor import PDFImageExtractor

def analyze_figures_in_document():
    """
    Análise detalhada das figuras detectadas no documento,
    extraindo-as e analisando suas propriedades e relações com o texto.
    """
    # Caminhos
    current_dir = Path(__file__).parent
    pdf_files = [
        "modelo-prova.pdf", 
        "modelo-prova-completa.pdf", 
        "modelo-completo-prova.pdf"
    ]
    
    # Pasta principal para resultados da análise
    analysis_dir = current_dir / "figures_analysis_3tri"
    if os.path.exists(analysis_dir):
        shutil.rmtree(analysis_dir)  # Limpar análises anteriores
    os.makedirs(analysis_dir, exist_ok=True)
    
    # Subpastas para cada tipo de análise
    images_dir = analysis_dir / "images"
    text_context_dir = analysis_dir / "text_context"
    metadata_dir = analysis_dir / "metadata"
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(text_context_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    
    # Arquivo de resumo
    summary_file = analysis_dir / "figures_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write("# Análise de Figuras - Azure Document Intelligence\n\n")
        f.write("Data: 17/07/2025\n\n")
        f.write("## Resumo das Figuras Encontradas\n\n")
    
    # Carregar o resultado do Azure Document Intelligence
    json_path = current_dir / "azure_response_3Tri_20250716_215103.json"
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
    
    # Verificar no formato do novo arquivo
    if "figures" in azure_result:
        figures = azure_result["figures"]
    
    if not figures:
        logger.error("Nenhuma figura encontrada no resultado do Azure")
        return
    
    logger.info(f"Encontradas {len(figures)} figuras no resultado do Azure")
    
    # Adicionar ao resumo
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write(f"Total de figuras encontradas: **{len(figures)}**\n\n")
        f.write("| ID | Página | Conteúdo Associado | Dimensões |\n")
        f.write("|----|---------|--------------------|----------|\n")
    
    # Extrair cada figura detectada
    successful_extractions = []
    
    for i, figure in enumerate(figures):
        figure_id = figure.get("id", f"figure_{i}")
        logger.info(f"\nProcessando figura {figure_id} ({i+1} de {len(figures)})")
        
        # Extrair informações detalhadas da figura
        figure_info = {
            "id": figure_id,
            "index": i,
            "spans": figure.get("spans", []),
            "elements": figure.get("elements", []),
            "text_content": "",
            "extractions": []
        }
        
        # Extrair conteúdo textual associado à figura
        if "spans" in figure and figure["spans"]:
            for span in figure["spans"]:
                offset = span.get("offset", 0)
                length = span.get("length", 0)
                
                # Extrair texto do documento usando offset e length
                text_content_path = text_context_dir / f"figure_{figure_id}_text.txt"
                with open(text_content_path, "w", encoding="utf-8") as f:
                    if "contentFormat" in azure_result and azure_result["contentFormat"] == "text":
                        try:
                            # Encontrar o texto no documento usando offset e length
                            # Primeiro, concatenar todo o texto dos parágrafos
                            all_text = ""
                            for para in azure_result.get("paragraphs", []):
                                if "content" in para:
                                    all_text += para["content"] + "\n"
                            
                            if offset < len(all_text):
                                text_slice = all_text[offset:offset+length]
                                figure_info["text_content"] = text_slice
                                f.write(f"Texto associado à figura {figure_id}:\n\n")
                                f.write(text_slice)
                                logger.info(f"Texto associado à figura {figure_id} extraído")
                        except Exception as e:
                            logger.error(f"Erro ao extrair texto para figura {figure_id}: {str(e)}")
        
        # Extrair as regiões de bounding box
        if "boundingRegions" not in figure or not figure["boundingRegions"]:
            logger.warning(f"Figura {figure_id} sem boundingRegions")
            continue
        
        # Para cada PDF disponível, tentar extrair a figura
        for pdf_file in pdf_files:
            pdf_path = current_dir / pdf_file
            if not pdf_path.exists():
                logger.warning(f"PDF {pdf_file} não encontrado, pulando")
                continue
                
            logger.info(f"Tentando extração da figura {figure_id} do arquivo {pdf_file}")
            
            for region_idx, region in enumerate(figure["boundingRegions"]):
                page_number = region.get("pageNumber", 1)
                polygon = region.get("polygon", [])
                
                if not polygon:
                    logger.warning(f"Região {region_idx} da figura {figure_id} sem polígono")
                    continue
                
                logger.info(f"Figura {figure_id}, página {page_number}, polígono: {polygon}")
                
                # Salvar metadados da figura
                metadata_path = metadata_dir / f"figure_{figure_id}_metadata.json"
                with open(metadata_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "figure_id": figure_id,
                        "page_number": page_number,
                        "polygon": polygon,
                        "spans": figure.get("spans", []),
                        "elements": figure.get("elements", [])
                    }, f, indent=2)
                
                # Tentar extrair a figura com diferentes escalas
                scales_to_try = [1, 0.01]
                
                for scale in scales_to_try:
                    try:
                        # Aplicar escala às coordenadas
                        scaled_coords = [coord * scale for coord in polygon]
                        
                        # Extrair a imagem
                        image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                            pdf_path=str(pdf_path),
                            page_number=page_number,
                            coordinates=scaled_coords
                        )
                        
                        if image_bytes:
                            # Salvar a imagem
                            output_filename = f"figure_{figure_id}_page_{page_number}_{pdf_file.split('.')[0]}_scale_{scale}.jpg"
                            output_path = images_dir / output_filename
                            
                            with open(output_path, "wb") as f:
                                f.write(image_bytes)
                            
                            # Obter dimensões da imagem
                            img = Image.open(BytesIO(image_bytes))
                            width, height = img.size
                            
                            logger.info(f"Imagem da figura {figure_id} extraída de {pdf_file} com escala {scale}. Dimensões: {width}x{height}")
                            
                            figure_info["extractions"].append({
                                "pdf": pdf_file,
                                "scale": scale,
                                "path": str(output_path),
                                "width": width,
                                "height": height
                            })
                            
                            # Adicionar à lista de extrações bem-sucedidas
                            successful_extractions.append({
                                "figure_id": figure_id,
                                "pdf": pdf_file,
                                "scale": scale,
                                "path": str(output_path),
                                "page": page_number,
                                "width": width,
                                "height": height,
                                "text": figure_info["text_content"]
                            })
                    
                    except Exception as e:
                        logger.error(f"Erro ao extrair figura {figure_id} de {pdf_file} com escala {scale}: {str(e)}")
        
        # Atualizar o resumo com informações desta figura
        best_extraction = None
        if figure_info["extractions"]:
            # Pegar a extração com maior área de imagem
            best_extraction = max(figure_info["extractions"], key=lambda x: x["width"] * x["height"])
        
        with open(summary_file, "a", encoding="utf-8") as f:
            text_preview = figure_info["text_content"][:50] + "..." if figure_info["text_content"] else "N/A"
            dimensions = f"{best_extraction['width']}x{best_extraction['height']}" if best_extraction else "N/A"
            f.write(f"| {figure_id} | {page_number} | {text_preview} | {dimensions} |\n")
    
    # Adicionar informações detalhadas ao resumo
    with open(summary_file, "a", encoding="utf-8") as f:
        f.write("\n## Detalhes das Extrações\n\n")
        
        for i, extraction in enumerate(successful_extractions):
            f.write(f"### Figura {extraction['figure_id']} (Página {extraction['page']})\n\n")
            f.write(f"- **Arquivo PDF:** {extraction['pdf']}\n")
            f.write(f"- **Escala:** {extraction['scale']}\n")
            f.write(f"- **Dimensões:** {extraction['width']}x{extraction['height']}\n")
            f.write(f"- **Caminho:** {extraction['path']}\n")
            
            # Caminho relativo para a imagem
            rel_path = os.path.relpath(extraction['path'], start=str(analysis_dir))
            f.write(f"\n![Figura {extraction['figure_id']}]({rel_path})\n\n")
            
            if extraction['text']:
                f.write("**Texto associado:**\n\n")
                f.write("```\n")
                f.write(extraction['text'])
                f.write("\n```\n\n")
            
            f.write("---\n\n")
    
    logger.info(f"\nProcessamento concluído. Resumo salvo em: {summary_file}")
    logger.info(f"Total de figuras extraídas com sucesso: {len(successful_extractions)}")
    
    # Retornar as informações sobre as figuras encontradas para facilitar análise
    return {
        "total_figures": len(figures),
        "successful_extractions": len(successful_extractions),
        "figures_info": successful_extractions
    }

if __name__ == "__main__":
    result = analyze_figures_in_document()
    if result:
        logger.info(f"\nResumo das figuras encontradas: {json.dumps(result, indent=2)}")
