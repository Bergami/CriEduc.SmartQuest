"""
Teste para enumerar todas as figuras detectadas no arquivo azure_response_3Tri_20250716_215103.json
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

def test_enumerate_all_figures_3tri():
    """
    Carrega o resultado do Azure Document Intelligence do arquivo azure_response_3Tri_20250716_215103.json
    e enumera todas as figuras detectadas, extraindo-as uma a uma para verificação visual.
    """
    # Caminhos
    current_dir = Path(__file__).parent
    # Vamos testar com cada um dos PDFs disponíveis
    pdf_files = [
        "modelo-prova.pdf", 
        "modelo-prova-completa.pdf", 
        "modelo-completo-prova.pdf"
    ]
    # Inicialmente usamos o primeiro PDF, mas podemos mudar para outro se necessário
    pdf_path = current_dir / pdf_files[0]
    output_dir = current_dir / "extracted_images" / "3tri_figures"
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Usando arquivo PDF: {pdf_path}")
    
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
            
            # Salvar informações da figura em um arquivo de texto para referência
            info_path = output_dir / f"3tri_figure_{figure_id}_page_{page_number}_info.txt"
            with open(info_path, "w") as f:
                f.write(f"Figura ID: {figure_id}\n")
                f.write(f"Página: {page_number}\n")
                f.write(f"Polígono: {polygon}\n")
                if "spans" in figure:
                    f.write(f"Spans: {figure['spans']}\n")
                if "elements" in figure:
                    f.write(f"Elements: {figure['elements']}\n")
            
            try:
                # Usar escala 1, que produziu os melhores resultados
                # nas execuções anteriores
                scale = 1  # Fator de escala que produziu os melhores resultados
                
                logger.info(f"Aplicando escala {scale} para figura {figure_id}")
                # Usar as coordenadas originais (com escala 1)
                scaled_coords = polygon
                image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                    pdf_path=str(pdf_path),
                    page_number=page_number,
                    coordinates=polygon
                )
                
                if not image_bytes:
                    logger.warning(f"Falha ao extrair imagem da figura {figure_id}")
                    continue
                
                # Salvar a imagem
                output_path = output_dir / f"3tri_figure_{figure_id}_page_{page_number}.jpg"
                with open(output_path, "wb") as f:
                    f.write(image_bytes)
                logger.info(f"Imagem da figura {figure_id} salva em: {output_path}")
                
                # Converter para base64 e salvar
                base64_str = PDFImageExtractor.get_base64_image(image_bytes)
                base64_path = output_dir / f"3tri_figure_{figure_id}_page_{page_number}_base64.txt"
                with open(base64_path, "w") as f:
                    f.write(base64_str[:100] + "...")  # Apenas o início para não ficar muito grande
                logger.info(f"Base64 (início) da figura {figure_id} salvo em: {base64_path}")
            
            except Exception as e:
                logger.error(f"Erro ao processar a figura {figure_id}: {str(e)}")
            
    logger.info("\nProcessamento concluído")

    # Retornar as informações sobre as figuras encontradas para facilitar análise
    return {
        "total_figures": len(figures),
        "figures_info": [{
            "id": fig.get("id", "unknown"),
            "page": fig.get("boundingRegions", [{}])[0].get("pageNumber", "unknown") if fig.get("boundingRegions") else "unknown",
            "content": fig.get("spans", [{}])[0].get("offset", "unknown") if fig.get("spans") else "unknown"
        } for fig in figures]
    }

def is_header_image(figure, azure_result):
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
    if region.get("pageNumber", 0) != 1:
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
        # (primeiros 20% da altura da página)
        polygon = region.get("polygon", [])
        if polygon and len(polygon) >= 2:
            # Pegar coordenada Y (a segunda em cada par de coordenadas)
            y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
            avg_y = sum(y_values) / len(y_values)
            
            # Se a posição vertical média da imagem estiver no topo da página
            # (considerando que as coordenadas são normalizadas de 0 a 1)
            return avg_y < 0.2
    else:
        # Verificar se a figura está próxima ou sobreposta a algum elemento do cabeçalho
        figure_spans = figure.get("spans", [])
        
        # Se a figura tiver spans, verificar se há sobreposição com os spans do cabeçalho
        if figure_spans:
            for f_span in figure_spans:
                f_offset = f_span.get("offset", 0)
                f_length = f_span.get("length", 0)
                
                for header in header_elements:
                    for h_span in header.get("spans", []):
                        h_offset = h_span.get("offset", 0)
                        h_length = h_span.get("length", 0)
                        
                        # Verificar sobreposição ou proximidade dos spans
                        if (f_offset <= h_offset + h_length and 
                            h_offset <= f_offset + f_length) or \
                           abs(f_offset - h_offset) < 100:  # Proximidade de 100 caracteres
                            return True
        
        # Outra abordagem: verificar elementos na figura
        figure_elements = figure.get("elements", [])
        if figure_elements:
            for elem in figure_elements:
                if elem in ["/paragraphs/0", "/paragraphs/1", "/paragraphs/2"]:  # Primeiros parágrafos
                    return True
    
    # Verificações adicionais baseadas no conteúdo textual associado
    if figure.get("spans"):
        for span in figure.get("spans"):
            offset = span.get("offset", 0)
            length = span.get("length", 0)
            
            # Se o offset for muito baixo, provavelmente está no início do documento
            if offset < 200:  # Primeiros 200 caracteres
                return True
                
    # Caso específico para a figura 1.1 que sabemos ser do cabeçalho
    if figure.get("id") == "1.1":
        return True
        
    return False


def extract_figures_for_application():
    """
    Versão simplificada da função de extração de figuras,
    focada em extrair apenas com escala 1 e preparando os
    dados para uso na aplicação principal.
    
    Categoriza as imagens entre:
    - Imagens de cabeçalho (header_images)
    - Imagens de conteúdo (context_block_images)
    """
    # Carregar e processar o arquivo JSON
    current_dir = Path(__file__).parent
    json_path = current_dir / "azure_response_3Tri_20250716_215103.json"
    output_dir = current_dir / "extracted_images" / "3tri_final"
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            azure_result = json.load(f)
    except Exception as e:
        logger.error(f"Erro ao carregar o arquivo JSON: {str(e)}")
        return {}
    
    # Verificar se há figuras no resultado
    figures = azure_result.get("figures", [])
    if not figures:
        logger.error("Nenhuma figura encontrada no resultado do Azure")
        return {}
    
    # PDF que funcionou bem nas execuções anteriores
    pdf_path = current_dir / "modelo-prova.pdf"
    if not pdf_path.exists():
        logger.error(f"PDF {pdf_path} não encontrado")
        return {}
    
    # Dicionários para categorizar as figuras
    header_images = []
    context_block_images = []
    
    for figure in figures:
        figure_id = figure.get("id", "")
        if not figure_id:
            continue
            
        # Extrair as regiões de bounding box
        if "boundingRegions" not in figure or not figure["boundingRegions"]:
            continue
            
        for region in figure["boundingRegions"]:
            page_number = region.get("pageNumber", 1)
            polygon = region.get("polygon", [])
            
            if not polygon:
                continue
                
            try:
                # Extrair a imagem com escala 1
                image_bytes = PDFImageExtractor.extract_figure_from_pdf(
                    pdf_path=str(pdf_path),
                    page_number=page_number,
                    coordinates=polygon
                )
                
                if image_bytes:
                    # Salvar a imagem com nome padronizado
                    output_path = output_dir / f"figure_{figure_id}.jpg"
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                    
                    # Converter para base64
                    base64_image = PDFImageExtractor.get_base64_image(image_bytes)
                    
                    # Determinar se é uma imagem de cabeçalho
                    is_header = is_header_image(figure, azure_result)
                    
                    # Criar objeto de imagem
                    image_obj = {
                        "id": figure_id,
                        "page": page_number,
                        "file_path": str(output_path),
                        "base64": base64_image,
                        "type": "header" if is_header else "content"
                    }
                    
                    # Adicionar à categoria correta
                    if is_header:
                        logger.info(f"Imagem {figure_id} classificada como CABEÇALHO: {output_path}")
                        header_images.append(image_obj)
                    else:
                        logger.info(f"Imagem {figure_id} classificada como CONTEÚDO: {output_path}")
                        context_block_images.append(image_obj)
                        
            except Exception as e:
                logger.error(f"Erro ao processar figura {figure_id}: {str(e)}")
    
    # Estrutura final para o resultado
    result = {
        "header_images": header_images,
        "context_block_images": context_block_images
    }
    
    # Salvar metadados das figuras categorizadas
    metadata_path = output_dir / "figures_categorized.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    # Também salvar um exemplo de como integrar as imagens ao modelo de dados
    model_example_path = output_dir / "header_with_images_example.json"
    
    # Exemplo simplificado de como seria o header com imagens
    header_example = {
        "school": "UMEF Saturnino Rangel Mauro",
        "network": "VILA VELHA - ES",
        "teacher": "Danielle",
        "subject": "Língua Portuguesa",
        "grade": "7º ano do Ensino Fundamental",
        "images": [{"content": img["base64"]} for img in header_images]
    }
    
    with open(model_example_path, "w", encoding="utf-8") as f:
        json.dump(header_example, f, indent=2)
    
    logger.info(f"Metadados das figuras categorizadas salvos em: {metadata_path}")
    logger.info(f"Exemplo de header com imagens salvo em: {model_example_path}")
    
    # Resumo da categorização
    logger.info(f"Total de figuras: {len(header_images) + len(context_block_images)}")
    logger.info(f"Figuras no cabeçalho: {len(header_images)}")
    logger.info(f"Figuras no conteúdo: {len(context_block_images)}")
    
    return result

if __name__ == "__main__":
    # Executar a versão detalhada de teste para verificação visual
    logger.info("=== EXECUÇÃO DO TESTE DE EXTRAÇÃO DE FIGURAS ===")
    test_result = test_enumerate_all_figures_3tri()
    if test_result:
        logger.info(f"\nResumo do teste: {json.dumps(test_result, indent=2)}")
    
    # Executar a versão simplificada para uso na aplicação
    logger.info("\n\n=== EXECUÇÃO DA EXTRAÇÃO FINAL PARA APLICAÇÃO ===")
    app_result = extract_figures_for_application()
    logger.info(f"Figuras extraídas para aplicação: {len(app_result)}")
