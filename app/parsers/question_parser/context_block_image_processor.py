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
        image_data: Any,  # Aceita dict ou list
        page_mapping: Optional[Dict[int, List[Dict[str, Any]]]] = None,
        azure_image_urls: Optional[Dict[str, str]] = None  # Novo parâmetro para URLs do Azure
    ) -> List[Dict[str, Any]]:
        """
        Adiciona dados de imagens aos blocos de contexto relevantes
        
        Args:
            context_blocks: Lista de blocos de contexto
            image_data: Dicionário de imagens em base64 (id -> base64_data)
            page_mapping: Mapeamento opcional de página -> figuras para ajudar na associação
            azure_image_urls: Dicionário de URLs do Azure Blob Storage (id -> url)
            
        Returns:
            Lista enriquecida de blocos de contexto
        """
        # Priorizar Azure URLs se disponíveis
        if azure_image_urls:
            logger.info(f"Enriching context blocks with {len(azure_image_urls)} Azure image URLs")
            return ContextBlockImageProcessor._enrich_with_azure_urls(context_blocks, azure_image_urls)
        
        if not image_data:
            # Nenhuma imagem disponível
            return context_blocks
        
        # Ajuste: converte lista para dict se necessário
        if isinstance(image_data, list):
            image_data = {str(i): img for i, img in enumerate(image_data)}
        elif not isinstance(image_data, dict):
            logger.error(f"image_data should be dict or list, got {type(image_data).__name__}")
            return context_blocks
            
        logger.info(f"Enriching context blocks with {len(image_data)} available base64 images")
        
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
                    
                    logger.info(f"Added base64 image {image_id} to context block {block.get('id')}")
                
            # Adicionar o bloco à lista
            enriched_blocks.append(enriched_block)
        
        return enriched_blocks
    
    @staticmethod
    def _enrich_with_azure_urls(
        context_blocks: List[Dict[str, Any]], 
        azure_image_urls: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Enriquece context blocks com URLs do Azure Blob Storage
        
        Args:
            context_blocks: Lista de blocos de contexto
            azure_image_urls: Dicionário de URLs do Azure (id -> url)
            
        Returns:
            Lista enriquecida de blocos de contexto
        """
        enriched_blocks = []
        available_urls = dict(azure_image_urls)  # Cópia para modificar
        
        for block in context_blocks:
            # Clonar bloco
            enriched_block = {**block}
            
            # Se o bloco já tem azure_image_urls, preservar
            if block.get("azure_image_urls"):
                enriched_block["contentType"] = "image/url"
                logger.debug(f"Context block {block.get('id')} already has Azure URLs")
            # Se o bloco é marcado como tendo imagem, tentar encontrar URL correspondente
            elif block.get("hasImage") and available_urls:
                # Pegar a primeira URL disponível
                image_id = next(iter(available_urls.keys()))
                azure_url = available_urls.pop(image_id)
                
                # Adicionar a URL ao bloco
                enriched_block["azure_image_urls"] = [azure_url]
                enriched_block["contentType"] = "image/url"
                enriched_block["images"] = []  # Limpar base64 para economizar memória
                
                logger.info(f"Added Azure URL {image_id} to context block {block.get('id')}")
            
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
        
        # Converter lista para dict se necessário
        if isinstance(image_data, list):
            image_data = {str(i): img for i, img in enumerate(image_data)}
        elif not isinstance(image_data, dict):
            logger.error(f"image_data should be dict or list, got {type(image_data).__name__}")
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
