"""
Teste para verificar o byte[] gerado pelo método extract_figure_from_pdf e comparar
com a imagem salva diretamente.
"""
import sys
import os
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

def test_byte_array_content():
    """
    Testa o conteúdo do byte[] retornado pelo extrator e compara com a imagem salva diretamente
    """
    # Caminhos
    current_dir = Path(__file__).parent
    pdf_path = current_dir / "modelo-prova.pdf"
    output_dir = current_dir / "extracted_images"
    os.makedirs(output_dir, exist_ok=True)
    
    # Coordenadas da figura 2.1 do JSON
    polygon = [4.783, 0.7453, 7.5413, 0.7457, 7.5403, 2.8879, 4.782, 2.8874]
    page_number = 2
    
    logger.info(f"Extraindo imagem da página {page_number} do PDF {pdf_path}")
    
    # 1. Extrair usando o método da classe PDFImageExtractor
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,
        coordinates=polygon
    )
    
    if image_bytes:
        # Salvar o resultado do método como imagem
        output_path_method = output_dir / "figura_2_1_from_method.jpg"
        with open(output_path_method, "wb") as f:
            f.write(image_bytes)
        logger.info(f"Imagem extraída pelo método salva em: {output_path_method}")
        logger.info(f"Tamanho do byte[]: {len(image_bytes)} bytes")
        
        # Salvar também o conteúdo como base64 para verificação
        base64_content = base64.b64encode(image_bytes).decode('utf-8')
        base64_path = output_dir / "figura_2_1_from_method.txt"
        with open(base64_path, "w") as f:
            f.write(base64_content[:100] + "...")  # Apenas o início para não ficar muito grande
        logger.info(f"Conteúdo base64 (primeiros 100 caracteres) salvo em: {base64_path}")
        
    else:
        logger.error("Falha ao extrair a imagem pelo método")
        return
    
    # 2. Extrair diretamente usando PyMuPDF para comparação
    try:
        doc = fitz.open(str(pdf_path))
        page = doc[page_number-1]
        
        # Extrair valores X e Y
        x_values = [polygon[i] for i in range(0, len(polygon), 2)]
        y_values = [polygon[i+1] for i in range(0, len(polygon), 2)]
        
        # Aplicar fator de escala de 72 pontos
        scale_factor = 72
        x_values = [x * scale_factor for x in x_values]
        y_values = [y * scale_factor for y in y_values]
        
        # Criar retângulo delimitador
        x0 = min(x_values)
        y0 = min(y_values)
        x1 = max(x_values)
        y1 = max(y_values)
        
        rect = fitz.Rect(x0, y0, x1, y1)
        logger.info(f"Retângulo direto: {rect}")
        
        # Extrair com mesmos parâmetros que o método usa
        matrix = fitz.Matrix(3, 3)
        pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
        
        # Salvar como imagem - corrigindo o método de salvamento
        output_path_direct = output_dir / "figura_2_1_direct.jpg"
        pix.save(str(output_path_direct))
        logger.info(f"Imagem extraída diretamente salva em: {output_path_direct}")
        
        # Vamos usar BytesIO e pil_save como o método original
        img_bytes = BytesIO()
        pix.pil_save(img_bytes, format="JPEG", quality=95)
        img_bytes.seek(0)
        direct_bytes = img_bytes.getvalue()
        logger.info(f"Tamanho do byte[] direto: {len(direct_bytes)} bytes")
        
        # Verificar se os conteúdos são iguais
        if image_bytes == direct_bytes:
            logger.info("Os bytes[] são IDÊNTICOS!")
            
            # Verificar a conversão para base64
            base64_method = PDFImageExtractor.get_base64_image(image_bytes)
            base64_direct = base64.b64encode(direct_bytes).decode('utf-8')
            
            if base64_method == base64_direct:
                logger.info("As strings base64 também são IDÊNTICAS!")
            else:
                logger.warning("As strings base64 são DIFERENTES!")
                
            # Salvar a string base64 para verificação
            base64_method_path = output_dir / "figura_2_1_base64_method.txt"
            with open(base64_method_path, "w") as f:
                f.write(base64_method[:100] + "...")
            logger.info(f"Base64 do método salvo em: {base64_method_path}")
            
            # Comparar os tamanhos das strings base64
            logger.info(f"Tamanho da string base64 do método: {len(base64_method)}")
            logger.info(f"Tamanho da string base64 direta: {len(base64_direct)}")
            
        else:
            logger.warning("Os bytes[] são DIFERENTES!")
            
            # Salvar os bytes diretos como imagem para comparação
            output_path_direct_bytes = output_dir / "figura_2_1_direct_bytes.jpg"
            with open(output_path_direct_bytes, "wb") as f:
                f.write(direct_bytes)
            logger.info(f"Imagem dos bytes diretos salva em: {output_path_direct_bytes}")
            
            # Salvar também o conteúdo direto como base64 para verificação
            base64_direct = base64.b64encode(direct_bytes).decode('utf-8')
            base64_direct_path = output_dir / "figura_2_1_direct_bytes.txt"
            with open(base64_direct_path, "w") as f:
                f.write(base64_direct[:100] + "...")
            logger.info(f"Conteúdo base64 direto salvo em: {base64_direct_path}")
            
            # Verificar se há diferenças na imagem gerada pelos bytes
            if len(image_bytes) == len(direct_bytes):
                logger.info("Os arrays de bytes têm o mesmo tamanho, mas conteúdo diferente")
                # Contar quantos bytes são diferentes
                diff_count = sum(1 for a, b in zip(image_bytes, direct_bytes) if a != b)
                diff_percentage = (diff_count / len(image_bytes)) * 100
                logger.info(f"Número de bytes diferentes: {diff_count} ({diff_percentage:.2f}%)")
            else:
                logger.info(f"Os arrays de bytes têm tamanhos diferentes: {len(image_bytes)} vs {len(direct_bytes)}")
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Erro ao extrair imagem diretamente: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_byte_array_content()
