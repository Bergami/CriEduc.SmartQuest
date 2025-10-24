import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import uuid4

from app.config.settings import get_settings

logger = logging.getLogger(__name__)

class DocumentStorageService:
    """
    Serviço genérico para persistir dados de documentos processados.
    Independente do provedor (Azure, AWS, etc.)
    """
    
    def __init__(self, base_path: str = "tests"):
        self.base_path = Path(base_path)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Cria estrutura de diretórios necessária"""
        directories = [
            self.base_path / "documents",
            self.base_path / "responses" / "azure",
            self.base_path / "responses" / "other_providers",
            self.base_path / "images" / "by_document",
            self.base_path / "images" / "by_provider" / "azure"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_raw_response(self, response: Dict[str, Any], filename: str, provider: str) -> Optional[str]:
        """
        Salva resposta bruta do provedor em arquivo JSON
        
        Args:
            response: Resposta do provedor (já serializada)
            filename: Nome do arquivo original
            provider: Nome do provedor (azure, aws, etc.)
            
        Returns:
            Caminho do arquivo salvo ou None se houver erro
        """
        try:
            # Gerar nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = self._sanitize_filename(filename)
            output_filename = f"{provider}_{safe_filename}_{timestamp}.json"
            
            # Caminho do arquivo
            output_path = self.base_path / "responses" / provider / output_filename
            
            # Salvar arquivo
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Resposta {provider} salva em: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro ao salvar resposta {provider}: {str(e)}")
            return None
    
    def save_document_images(self, images: Dict[str, str], document_id: str, provider: str) -> Dict[str, str]:
        """
        Salva imagens extraídas do documento (opcional via feature flag)
        
        Args:
            images: Dicionário com ID da imagem e conteúdo base64
            document_id: ID único do documento
            provider: Nome do provedor
            
        Returns:
            Dicionário com IDs das imagens e caminhos dos arquivos salvos
        """
        settings = get_settings()
        
        # ✅ Feature flag: permite desabilitar salvamento local
        if not settings.enable_local_image_saving:
            logger.info(f"💡 Local image saving disabled by feature flag - skipping save for document {document_id}")
            return {}
        
        saved_paths = {}
        
        try:
            # Criar diretório para o documento
            doc_dir = self.base_path / "images" / "by_document" / document_id
            doc_dir.mkdir(parents=True, exist_ok=True)
            
            provider_dir = self.base_path / "images" / "by_provider" / provider / document_id
            provider_dir.mkdir(parents=True, exist_ok=True)
            
            for image_id, base64_content in images.items():
                try:
                    # Decodificar base64
                    import base64
                    image_bytes = base64.b64decode(base64_content)
                    
                    # Nome do arquivo
                    image_filename = f"{image_id}.jpg"
                    
                    # Salvar em ambos os diretórios
                    doc_path = doc_dir / image_filename
                    provider_path = provider_dir / image_filename
                    
                    with open(doc_path, "wb") as f:
                        f.write(image_bytes)
                    
                    with open(provider_path, "wb") as f:
                        f.write(image_bytes)
                    
                    saved_paths[image_id] = str(doc_path)
                    
                except Exception as e:
                    logger.error(f"Erro ao salvar imagem {image_id}: {str(e)}")
                    continue
            
            logger.info(f"Salvadas {len(saved_paths)} imagens para documento {document_id}")
            return saved_paths
            
        except Exception as e:
            logger.error(f"Erro ao salvar imagens do documento {document_id}: {str(e)}")
            return {}
    
    # REMOVIDO: save_extracted_text() - funcionalidade desnecessária
    # O texto extraído já fica disponível na memória e não precisa ser persistido
    
    def save_original_document(self, file_content: bytes, filename: str, document_id: str) -> Optional[str]:
        """
        Salva documento original
        
        Args:
            file_content: Conteúdo do arquivo original
            filename: Nome do arquivo original
            document_id: ID único do documento
            
        Returns:
            Caminho do arquivo salvo ou None se houver erro
        """
        try:
            safe_filename = self._sanitize_filename(filename)
            output_filename = f"{document_id}_{safe_filename}"
            output_path = self.base_path / "documents" / output_filename
            
            with open(output_path, "wb") as f:
                f.write(file_content)
            
            logger.info(f"Documento original salvo em: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Erro ao salvar documento original: {str(e)}")
            return None
    
    def get_storage_path(self, document_type: str, document_id: str) -> str:
        """
        Retorna caminho para um tipo específico de documento
        
        Args:
            document_type: Tipo do documento (responses, images, documents)
            document_id: ID único do documento
            
        Returns:
            Caminho do diretório
        """
        return str(self.base_path / document_type / document_id)
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza nome do arquivo removendo caracteres especiais
        
        Args:
            filename: Nome do arquivo original
            
        Returns:
            Nome sanitizado
        """
        import re
        # Remove extensão e caracteres especiais
        name = Path(filename).stem
        sanitized = re.sub(r'[^\w\-_.]', '_', name)
        return sanitized[:50]  # Limitar tamanho
    
    def cleanup_old_files(self, days_old: int = 30) -> None:
        """
        Remove arquivos antigos do storage
        
        Args:
            days_old: Idade em dias para considerar arquivo antigo
        """
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=days_old)
            
            for root, dirs, files in os.walk(self.base_path):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.stat().st_mtime < cutoff_time.timestamp():
                        file_path.unlink()
                        logger.info(f"Arquivo antigo removido: {file_path}")
                        
        except Exception as e:
            logger.error(f"Erro na limpeza de arquivos antigos: {str(e)}")
