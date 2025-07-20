"""
Teste completo do ciclo de extração, conversão para base64 e reconstrução da imagem
para verificar se há perda de dados.
"""
import sys
import os
import base64
import logging
from pathlib import Path
import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image

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

def test_base64_cycle():
    """
    Testa o ciclo completo de extração, conversão para base64 e reconstrução da imagem
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
    
    # 1. Extrair imagem usando o extrator
    image_bytes = PDFImageExtractor.extract_figure_from_pdf(
        pdf_path=str(pdf_path),
        page_number=page_number,
        coordinates=polygon
    )
    
    if not image_bytes:
        logger.error("Falha ao extrair imagem")
        return
    
    # 2. Salvar imagem original para referência
    output_path_original = output_dir / "base64_cycle_original.jpg"
    with open(output_path_original, "wb") as f:
        f.write(image_bytes)
    logger.info(f"Imagem original salva em: {output_path_original}")
    
    # 3. Converter para base64
    base64_str = PDFImageExtractor.get_base64_image(image_bytes)
    logger.info(f"String base64 gerada: {len(base64_str)} caracteres")
    
    # 4. Salvar string base64 para referência
    output_path_base64 = output_dir / "base64_cycle_string.txt"
    with open(output_path_base64, "w") as f:
        f.write(base64_str[:100] + "...")
    logger.info(f"String base64 (início) salva em: {output_path_base64}")
    
    # 5. Decodificar string base64 de volta para bytes
    decoded_bytes = base64.b64decode(base64_str)
    logger.info(f"Bytes decodificados: {len(decoded_bytes)} bytes (original: {len(image_bytes)} bytes)")
    
    # 6. Salvar imagem reconstruída
    output_path_reconstructed = output_dir / "base64_cycle_reconstructed.jpg"
    with open(output_path_reconstructed, "wb") as f:
        f.write(decoded_bytes)
    logger.info(f"Imagem reconstruída salva em: {output_path_reconstructed}")
    
    # 7. Verificar se os bytes são idênticos
    if image_bytes == decoded_bytes:
        logger.info("SUCESSO: Os bytes originais e reconstruídos são IDÊNTICOS!")
    else:
        logger.warning("ERRO: Os bytes originais e reconstruídos são DIFERENTES!")
        
    # 8. Verificar visualmente se as imagens são idênticas
    try:
        # Abrir imagens com PIL para comparação
        original_img = Image.open(output_path_original)
        reconstructed_img = Image.open(output_path_reconstructed)
        
        # Verificar dimensões
        original_size = original_img.size
        reconstructed_size = reconstructed_img.size
        
        if original_size == reconstructed_size:
            logger.info(f"Dimensões das imagens são idênticas: {original_size}")
        else:
            logger.warning(f"Dimensões diferentes! Original: {original_size}, Reconstruída: {reconstructed_size}")
        
        # Comparar alguns pixels da imagem para verificação visual
        if original_size == reconstructed_size:
            points_to_check = [
                (0, 0),  # Canto superior esquerdo
                (original_size[0] // 2, original_size[1] // 2),  # Centro
                (original_size[0] - 1, original_size[1] - 1)  # Canto inferior direito
            ]
            
            all_match = True
            for pt in points_to_check:
                original_pixel = original_img.getpixel(pt)
                reconstructed_pixel = reconstructed_img.getpixel(pt)
                
                if original_pixel != reconstructed_pixel:
                    all_match = False
                    logger.warning(f"Pixel em {pt} difere! Original: {original_pixel}, Reconstruído: {reconstructed_pixel}")
            
            if all_match:
                logger.info("Verificação de pixels: Todos os pontos de amostra correspondem!")
            else:
                logger.warning("Verificação de pixels: Diferenças detectadas!")
        
    except Exception as e:
        logger.error(f"Erro na verificação visual: {str(e)}")
    
    logger.info("Teste do ciclo base64 concluído")
    
    return {
        'original_bytes_len': len(image_bytes),
        'base64_str_len': len(base64_str),
        'decoded_bytes_len': len(decoded_bytes),
        'are_identical': image_bytes == decoded_bytes
    }

if __name__ == "__main__":
    result = test_base64_cycle()
    print("\nRESUMO DO TESTE:")
    print(f"Tamanho dos bytes originais: {result['original_bytes_len']} bytes")
    print(f"Tamanho da string base64: {result['base64_str_len']} caracteres")
    print(f"Tamanho dos bytes decodificados: {result['decoded_bytes_len']} bytes")
    print(f"Os bytes são idênticos? {'SIM' if result['are_identical'] else 'NÃO'}")
