from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class ContextBlockImageProcessor:
    """
    Utilitário para enriquecer blocos de contexto com imagens extraídas
    """
    
    @staticmethod
    def enrich_context_blocks_with_images(
        context_blocks: List[Dict[str, Any]], 
        image_data: Dict[str, str],
        page_mapping: Optional[Dict[int, List[Dict[str, Any]]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Adiciona dados de imagens aos blocos de contexto relevantes
        
        Args:
            context_blocks: Lista de blocos de contexto
            image_data: Dicionário de imagens em base64 (id -> base64_data)
            page_mapping: Mapeamento opcional de página -> figuras para ajudar na associação
            
        Returns:
            Lista enriquecida de blocos de contexto
        """
        if not image_data:
            # Nenhuma imagem disponível
            return context_blocks
            
        logger.info(f"Enriching context blocks with {len(image_data)} available images")
        
        # Clonar blocos para não modificar o original
        enriched_blocks = []
        
        for block in context_blocks:
            # Clonar bloco
            enriched_block = {**block}
            
            # Se o bloco é marcado como tendo imagem, tentar encontrar a imagem correspondente
            if block.get("hasImage"):
                # Por enquanto, simplesmente pegar a primeira imagem disponível
                # Em uma implementação mais sofisticada, faríamos o matching correto
                if image_data:
                    # Pegar o primeiro ID de imagem
                    image_id = next(iter(image_data.keys()))
                    
                    # Adicionar a imagem ao bloco
                    enriched_block["content"] = image_data[image_id]
                    enriched_block["contentType"] = "image/jpeg;base64"
                    
                    # Remover essa imagem do dicionário para não usá-la novamente
                    image_data.pop(image_id)
                    
                    logger.info(f"Added image {image_id} to context block {block.get('id')}")
                
            # Adicionar o bloco à lista
            enriched_blocks.append(enriched_block)
        
        return enriched_blocks
        
    @staticmethod
    def save_images_to_file(image_data: Dict[str, str], output_dir: str):
        """
        Salva as imagens em formato JPG no diretório especificado
        
        Args:
            image_data: Dicionário de imagens em base64 (id -> base64_data)
            output_dir: Diretório onde salvar as imagens
        """
        import os
        import base64
        from pathlib import Path
        
        if not image_data:
            logger.info("No images to save")
            return
            
        # Criar o diretório se não existir
        output_path = Path(output_dir)
        os.makedirs(output_path, exist_ok=True)
        
        # Salvar cada imagem
        for image_id, base64_data in image_data.items():
            try:
                # Decodificar base64
                image_bytes = base64.b64decode(base64_data)
                
                # Salvar como arquivo
                output_file = output_path / f"image_{image_id}.jpg"
                with open(output_file, "wb") as f:
                    f.write(image_bytes)
                    
                logger.info(f"Image {image_id} saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving image {image_id}: {str(e)}")
