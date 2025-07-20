import sys
import os
import json
from pathlib import Path
import fitz  # PyMuPDF
import math

# Adicionar o diretório do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def debug_azure_coordinates():
    """
    Teste para entender como as coordenadas da API Azure Document Intelligence
    se relacionam com as coordenadas do PyMuPDF
    """
    # Caminhos
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "modelo-prova.pdf"
    output_dir = current_dir / "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Coordenadas da figura 2.1 do JSON
    # pageNumber: 2, polygon: [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
    polygon = [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
    page_number = 2  # Página 2 como reportado pelo Azure (1-indexed)
    
    print(f"Analisando coordenadas Azure para a página {page_number} do PDF {pdf_path}")
    print(f"Coordenadas originais: {polygon}")
    
    # Abrir o documento para obter informações sobre a página
    doc = fitz.open(str(pdf_path))
    if page_number > len(doc):
        print(f"Página {page_number} não existe no PDF")
        return
        
    page = doc[page_number-1]  # Ajustando para 0-indexed
    
    # Obter dimensões da página
    width, height = page.rect.width, page.rect.height
    print(f"Dimensões da página {page_number}: {width}x{height}")
    
    # Investigar o sistema de coordenadas
    x_values = [polygon[i] for i in range(0, len(polygon), 2)]
    y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
    
    print("\n=== Análise das coordenadas originais ===")
    print(f"Valores X: {x_values}")
    print(f"Valores Y: {y_values}")
    print(f"Min X: {min(x_values)}, Max X: {max(x_values)}")
    print(f"Min Y: {min(y_values)}, Max Y: {max(y_values)}")
    
    # Verificar se são coordenadas normalizadas (0-1)
    is_normalized = all(0 <= x <= 1 for x in x_values + y_values)
    print(f"São coordenadas normalizadas (0-1): {is_normalized}")
    
    # Verificar proporções em relação às dimensões da página
    print("\n=== Análise de proporções ===")
    x_prop_width = [(x / width) for x in x_values]
    y_prop_height = [(y / height) for y in y_values]
    print(f"Proporções X em relação à largura: {x_prop_width}")
    print(f"Proporções Y em relação à altura: {y_prop_height}")
    
    # Testar diferentes sistemas de coordenadas
    # 1. Considerar como valores em polegadas (72 pontos = 1 polegada)
    print("\n=== Análise como pontos (72 pontos = 1 polegada) ===")
    x_inches = [x for x in x_values]
    y_inches = [y for y in y_values]
    print(f"Como polegadas - X: {x_inches}")
    print(f"Como polegadas - Y: {y_inches}")
    
    # Converter para pontos para pixels
    dpi = 96  # DPI padrão para exibição
    x_pixels = [x * (dpi / 72) for x in x_values]
    y_pixels = [y * (dpi / 72) for y in y_values]
    print(f"Convertido para pixels (96 dpi) - X: {x_pixels}")
    print(f"Convertido para pixels (96 dpi) - Y: {y_pixels}")
    
    # 2. Testar com valores espelhados horizontalmente
    print("\n=== Análise com valores X espelhados ===")
    x_mirrored = [width - x for x in x_values]
    print(f"Valores X espelhados: {x_mirrored}")
    print(f"Min X espelhado: {min(x_mirrored)}, Max X espelhado: {max(x_mirrored)}")
    
    # 3. Testar com diferentes unidades de medida
    print("\n=== Análise com diferentes unidades ===")
    # PDF usa pontos como unidade (72 pontos = 1 polegada)
    # Vamos tentar diferentes escalas
    scales = [0.1, 1, 10, 72, 96, 100]
    
    for scale in scales:
        x_scaled = [x * scale for x in x_values]
        y_scaled = [y * scale for y in y_values]
        print(f"\nEscala {scale}:")
        print(f"X escalado: min={min(x_scaled)}, max={max(x_scaled)}")
        print(f"Y escalado: min={min(y_scaled)}, max={max(y_scaled)}")
        
        # Verificar se esses valores fariam sentido em termos de porcentagem da página
        x_perc_width = [min(100, max(0, (x * scale / width) * 100)) for x in x_values]
        y_perc_height = [min(100, max(0, (y * scale / height) * 100)) for y in y_values]
        print(f"X como % da largura: {[f'{p:.1f}%' for p in x_perc_width]}")
        print(f"Y como % da altura: {[f'{p:.1f}%' for p in y_perc_height]}")
        
    # Agora vamos verificar a região direita_superior que sabemos que contém a imagem
    print("\n=== Região conhecida que contém a imagem ===")
    # Baseado no teste anterior, sabemos que estes valores funcionam
    known_rect = fitz.Rect(width*0.57, height*0.06, width*0.93, height*0.25)
    print(f"Retângulo conhecido: {known_rect}")
    print(f"Em pixels: x0={known_rect.x0}, y0={known_rect.y0}, x1={known_rect.x1}, y1={known_rect.y1}")
    print(f"Largura: {known_rect.width}, Altura: {known_rect.height}")
    print(f"Proporção da página: {known_rect.x0/width*100:.1f}% a {known_rect.x1/width*100:.1f}% da largura")
    print(f"                    {known_rect.y0/height*100:.1f}% a {known_rect.y1/height*100:.1f}% da altura")
    
    # Vamos fazer uma verificação de distância entre as coordenadas Azure e nossa região conhecida
    print("\n=== Análise de distância entre coordenadas Azure e região conhecida ===")
    
    # Calcular as coordenadas centrais da região conhecida
    known_center_x = (known_rect.x0 + known_rect.x1) / 2
    known_center_y = (known_rect.y0 + known_rect.y1) / 2
    print(f"Centro da região conhecida: ({known_center_x}, {known_center_y})")
    
    # Para cada possível interpretação das coordenadas Azure, calcular o centro e a distância
    # até o centro da região conhecida
    for scale in [0.1, 1, 10, 72, 96, 100]:
        # Coordenadas normais
        x_scaled = [x * scale for x in x_values]
        y_scaled = [y * scale for y in y_values]
        center_x = sum(x_scaled) / len(x_scaled)
        center_y = sum(y_scaled) / len(y_scaled)
        distance = math.sqrt((center_x - known_center_x)**2 + (center_y - known_center_y)**2)
        
        print(f"Escala {scale}:")
        print(f"  Centro: ({center_x:.1f}, {center_y:.1f}), Distância: {distance:.1f}")
        
        # Coordenadas com X espelhado
        x_mirrored_scaled = [(width - x) * scale for x in x_values]
        center_x_mirrored = sum(x_mirrored_scaled) / len(x_mirrored_scaled)
        distance_mirrored = math.sqrt((center_x_mirrored - known_center_x)**2 + (center_y - known_center_y)**2)
        
        print(f"  Centro espelhado: ({center_x_mirrored:.1f}, {center_y:.1f}), Distância: {distance_mirrored:.1f}")
    
    # Por fim, vamos extrair a imagem usando diferentes interpretações das coordenadas
    # e salvá-las para comparação visual
    print("\n=== Extraindo imagens com diferentes interpretações ===")
    
    # Função auxiliar para extrair imagem com coordenadas escaladas
    def extract_with_scale(scale, mirror_x=False):
        x_vals = [x * scale for x in x_values]
        y_vals = [y * scale for y in y_values]
        
        if mirror_x:
            x_vals = [width - x for x in x_vals]
            
        # Calcular o retângulo delimitador
        x0 = max(0, min(x_vals))
        y0 = max(0, min(y_vals))
        x1 = min(width, max(x_vals))
        y1 = min(height, max(y_vals))
        
        rect = fitz.Rect(x0, y0, x1, y1)
        
        # Se o retângulo for muito pequeno, ampliá-lo
        if rect.width < 10 or rect.height < 10:
            x_center = (x0 + x1) / 2
            y_center = (y0 + y1) / 2
            x0 = max(0, x_center - 150)
            y0 = max(0, y_center - 150)
            x1 = min(width, x_center + 150)
            y1 = min(height, y_center + 150)
            rect = fitz.Rect(x0, y0, x1, y1)
            
        print(f"Retângulo com escala {scale}{' espelhado' if mirror_x else ''}: {rect}")
        
        try:
            matrix = fitz.Matrix(3, 3)  # Zoom 3x
            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            output_path = output_dir / f"debug_scale_{scale}{'_mirrored' if mirror_x else ''}.jpg"
            pix.save(str(output_path))
            print(f"Imagem salva em: {output_path}")
        except Exception as e:
            print(f"Erro ao extrair imagem: {str(e)}")
    
    # Testar diferentes escalas
    for scale in [1, 10, 72, 96, 100]:
        extract_with_scale(scale, mirror_x=False)
        extract_with_scale(scale, mirror_x=True)
    
    # Extrair a região conhecida para comparação
    try:
        matrix = fitz.Matrix(3, 3)
        pix = page.get_pixmap(matrix=matrix, clip=known_rect, alpha=False)
        output_path = output_dir / "debug_known_region.jpg"
        pix.save(str(output_path))
        print(f"Região conhecida salva em: {output_path}")
    except Exception as e:
        print(f"Erro ao extrair região conhecida: {str(e)}")
    
    # Fechar o documento
    doc.close()

if __name__ == "__main__":
    debug_azure_coordinates()
