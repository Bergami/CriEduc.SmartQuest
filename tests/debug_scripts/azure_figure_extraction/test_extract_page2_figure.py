import sys
import os
import json
from pathlib import Path
import fitz  # PyMuPDF

# Adicionar o diretório do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.utils.pdf_image_extractor import PDFImageExtractor

def test_extract_page2_figure():
    """
    Testa a extração específica da figura 2.1 do PDF da página 2
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
    
    # Determinar se as coordenadas são absolutas ou normalizadas
    # Isto é uma heurística: se todos valores forem <= 1.0, provavelmente são normalizados
    is_normalized = all(c <= 1.0 for c in polygon)
    print(f"Coordenadas são normalizadas: {is_normalized}")
    
    # Se as coordenadas são grandes demais para serem normalizadas, podem ser absolutas
    # mas em diferente escala (pontos vs pixels)
    might_be_scaled_absolute = any(c > width or c > height for c in polygon)
    print(f"Coordenadas podem ser escaladas absolutas: {might_be_scaled_absolute}")
    
    # Testar com coordenadas como estão (interpretando como absolutas)
    print("\nTestando extração com coordenadas interpretadas como absolutas:")
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,
        coordinates=polygon
    )
    
    if image_bytes:
        output_path = output_dir / "figura_2_1_absoluta.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Imagem salva em: {output_path}")
    else:
        print("Falha ao extrair a imagem com coordenadas absolutas")
    
    # Testar forçando tratamento como coordenadas normalizadas
    # Multiplicando por um fator para converter de volta para escala da página
    print("\nTestando extração forçando tratamento como coordenadas normalizadas:")
    # Verificando se parece ser coordenadas de pontos (72 pontos por polegada)
    # Convertendo para escala de pixels
    scale_factor = 1.0
    if might_be_scaled_absolute:
        print("Aplicando fator de escala para converter de pontos para pixels")
        # Podemos tentar diferentes fatores de escala
        scale_factor = 72.0 / 96.0  # Convertendo de pontos para pixels (aprox.)
    
    normalized_polygon = []
    for i in range(0, len(polygon), 2):
        x = polygon[i] / width * scale_factor
        y = polygon[i+1] / height * scale_factor
        normalized_polygon.append(x)
        normalized_polygon.append(y)
    
    print(f"Polígono normalizado: {normalized_polygon}")
    
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,
        coordinates=normalized_polygon
    )
    
    if image_bytes:
        output_path = output_dir / "figura_2_1_normalizada.jpg"
        with open(output_path, "wb") as f:
            f.write(image_bytes)
        print(f"Imagem salva em: {output_path}")
    else:
        print("Falha ao extrair a imagem com coordenadas normalizadas")
    
    # Abordagem direta com fitz
    print("\nTestando extração direta com PyMuPDF:")
    try:
        # Criar retângulo diretamente dos pontos do polígono
        x_values = [polygon[i] for i in range(0, len(polygon), 2)]
        y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
        
        # Obter os limites do retângulo
        x0 = min(x_values)
        y0 = min(y_values)
        x1 = max(x_values)
        y1 = max(y_values)
        
        print(f"Retângulo direto: ({x0}, {y0}, {x1}, {y1})")
        
        # Criar o retângulo
        rect = fitz.Rect(x0, y0, x1, y1)
        
        # Renderizar com alta resolução
        matrix = fitz.Matrix(3, 3)  # Fator de zoom para melhor resolução
        pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
        
        # Salvar a imagem
        output_path = output_dir / "figura_2_1_direto.jpg"
        pix.save(str(output_path))
        print(f"Imagem salva diretamente em: {output_path}")
    except Exception as e:
        print(f"Erro na extração direta: {str(e)}")
    
    # Testes adicionais com coordenadas ajustadas
    print("\nTestando com coordenadas espelhadas horizontalmente:")
    try:
        # Espelhar coordenadas X em relação à largura da página
        # Este é um teste para verificar se o sistema de coordenadas está invertido
        x_values_mirrored = [width - x for x in x_values]
        
        # Recalcular o retângulo com coordenadas espelhadas
        x0_mirror = min(x_values_mirrored)
        x1_mirror = max(x_values_mirrored)
        
        print(f"Retângulo espelhado: ({x0_mirror}, {y0}, {x1_mirror}, {y1})")
        
        # Criar o retângulo espelhado
        rect_mirror = fitz.Rect(x0_mirror, y0, x1_mirror, y1)
        
        # Renderizar com alta resolução
        matrix = fitz.Matrix(3, 3)
        pix = page.get_pixmap(matrix=matrix, clip=rect_mirror, alpha=False)
        
        # Salvar a imagem
        output_path = output_dir / "figura_2_1_espelhada.jpg"
        pix.save(str(output_path))
        print(f"Imagem espelhada salva em: {output_path}")
    except Exception as e:
        print(f"Erro na extração espelhada: {str(e)}")
    
    # Testar com coordenadas em diferentes regiões da página para encontrar a imagem correta
    print("\nTestando com varredura da página:")
    # Vamos tentar algumas regiões chave da página
    regions = [
        ("direita_superior", fitz.Rect(width*0.5, 0, width, height*0.33)),
        ("direita_meio", fitz.Rect(width*0.5, height*0.33, width, height*0.66)),
        ("direita_inferior", fitz.Rect(width*0.5, height*0.66, width, height)),
        ("esquerda_superior", fitz.Rect(0, 0, width*0.5, height*0.33)),
        ("esquerda_meio", fitz.Rect(0, height*0.33, width*0.5, height*0.66)),
        ("esquerda_inferior", fitz.Rect(0, height*0.66, width*0.5, height))
    ]
    
    for name, rect in regions:
        try:
            # Renderizar com alta resolução
            matrix = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            
            # Salvar a imagem
            output_path = output_dir / f"figura_2_1_region_{name}.jpg"
            pix.save(str(output_path))
            print(f"Região {name} salva em: {output_path}")
        except Exception as e:
            print(f"Erro ao extrair região {name}: {str(e)}")
    
    # Extrair especificamente a região direita_superior com altura ajustada para evitar o texto
    print("\nExtraindo região direita_superior ajustada:")
    try:
        # Ajustar as dimensões para focar apenas na imagem, sem incluir o texto
        # Variando a altura para encontrar o ponto ideal
        for height_percent in [0.15, 0.20, 0.25]:
            adjusted_rect = fitz.Rect(width*0.5, 0, width, height*height_percent)
            
            # Renderizar com alta resolução
            matrix = fitz.Matrix(3, 3)
            pix = page.get_pixmap(matrix=matrix, clip=adjusted_rect, alpha=False)
            
            # Salvar a imagem
            output_path = output_dir / f"figura_2_1_direita_superior_ajustada_{int(height_percent*100)}.jpg"
            pix.save(str(output_path))
            print(f"Região direita superior ajustada ({height_percent*100}%) salva em: {output_path}")
    except Exception as e:
        print(f"Erro ao extrair região ajustada: {str(e)}")
        
    # Extrair versão final refinada com margens reduzidas nos lados e parte superior
    print("\nExtraindo versão final refinada:")
    try:
        # Ajustar os limites para reduzir um pouco as laterais e parte superior
        # Usando 25% da altura, que foi o melhor resultado anterior
        # Ajustando as margens laterais (5% de cada lado) e reduzindo um pouco a parte superior (2%)
        left_margin = width * 0.55  # Aumentando o lado esquerdo em 5% da página
        right_margin = width * 0.95  # Reduzindo o lado direito em 5% da página
        top_margin = height * 0.02   # Começando um pouco mais abaixo (2% da altura)
        bottom_margin = height * 0.25  # Mantendo os 25% de altura que funcionou bem
        
        final_rect = fitz.Rect(left_margin, top_margin, right_margin, bottom_margin)
        
        # Renderizar com alta resolução
        matrix = fitz.Matrix(3, 3)
        pix = page.get_pixmap(matrix=matrix, clip=final_rect, alpha=False)
        
        # Salvar a imagem
        output_path = output_dir / "figura_2_1_versao_final.jpg"
        pix.save(str(output_path))
        print(f"Versão final refinada salva em: {output_path}")
        
        # Testar pequenas variações para encontrar a versão perfeita
        variations = [
            ("ajuste_1", fitz.Rect(width*0.53, height*0.02, width*0.97, height*0.25)),
            ("ajuste_2", fitz.Rect(width*0.55, height*0.03, width*0.95, height*0.25)),
            ("ajuste_3", fitz.Rect(width*0.57, height*0.02, width*0.93, height*0.25)),
            # Ajuste especial com parte superior ainda mais reduzida para evitar texto
            ("ajuste_4", fitz.Rect(width*0.57, height*0.04, width*0.93, height*0.25)),
            ("ajuste_5", fitz.Rect(width*0.57, height*0.05, width*0.93, height*0.25)),
            ("ajuste_6", fitz.Rect(width*0.57, height*0.06, width*0.93, height*0.25))
        ]
        
        for name, rect in variations:
            # Renderizar com alta resolução
            matrix = fitz.Matrix(3, 3)
            pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
            
            # Salvar a imagem
            output_path = output_dir / f"figura_2_1_final_{name}.jpg"
            pix.save(str(output_path))
            print(f"Variação {name} salva em: {output_path}")
        
    except Exception as e:
        print(f"Erro ao extrair versão final: {str(e)}")

if __name__ == "__main__":
    test_extract_page2_figure()
