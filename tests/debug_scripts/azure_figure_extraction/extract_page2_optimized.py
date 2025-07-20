import sys
import os
import fitz  # PyMuPDF
from pathlib import Path

# Adicionar o diretório do projeto ao path para importar os módulos
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def extract_page2_figure_optimized(pdf_path, output_dir):
    """
    Função para extrair a figura da página 2 do PDF utilizando as coordenadas otimizadas
    
    Args:
        pdf_path: Caminho para o arquivo PDF
        output_dir: Diretório para salvar a imagem extraída
    
    Returns:
        Caminho para a imagem extraída ou None se falhar
    """
    try:
        # Criar diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Abrir o PDF
        doc = fitz.open(pdf_path)
        
        # Verificar se o PDF tem a página 2
        if len(doc) < 2:
            print(f"PDF não tem página 2: {pdf_path}")
            return None
        
        # Obter a página 2 (indexada como 1 no PyMuPDF)
        page = doc[1]
        width, height = page.rect.width, page.rect.height
        
        # Definir as coordenadas otimizadas para a figura da página 2
        # Com base nos testes, estas são as melhores coordenadas para evitar texto
        left_margin = width * 0.57    # 57% da largura da página
        right_margin = width * 0.93   # 93% da largura da página
        top_margin = height * 0.05    # 5% da altura da página
        bottom_margin = height * 0.25 # 25% da altura da página
        
        # Criar retângulo para recortar a imagem
        rect = fitz.Rect(left_margin, top_margin, right_margin, bottom_margin)
        
        # Renderizar com alta resolução
        matrix = fitz.Matrix(3, 3)  # Fator de zoom 3x para melhor qualidade
        pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
        
        # Salvar a imagem
        output_path = os.path.join(output_dir, "figura_pagina2_otimizada.jpg")
        pix.save(output_path)
        
        doc.close()
        
        print(f"Imagem da página 2 extraída com sucesso: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Erro ao extrair figura da página 2: {str(e)}")
        return None

if __name__ == "__main__":
    # Pasta atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminho para o PDF
    pdf_path = os.path.join(current_dir, "modelo-prova.pdf")
    
    # Diretório para salvar as imagens extraídas
    output_dir = os.path.join(current_dir, "extracted_images")
    
    # Extrair figura da página 2
    extract_page2_figure_optimized(pdf_path, output_dir)
