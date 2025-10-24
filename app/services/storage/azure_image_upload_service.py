"""
Azure Image Upload Service

Serviço responsável por fazer upload de imagens para Azure Blob Storage
e retornar URLs públicas acessíveis.
"""
import base64
import logging
import uuid
from datetime import datetime
from typing import Dict, Optional
import httpx
from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class AzureImageUploadService:
    """
    Serviço para upload de imagens para Azure Blob Storage.
    
    Converte imagens base64 para URLs públicas no Azure Blob Storage,
    seguindo padrões de nomenclatura e organização por documento.
    """
    
    def __init__(self):
        """Inicializa o serviço com configurações do settings."""
        self._settings = get_settings()
        self._logger = logging.getLogger(__name__)
    
    async def upload_images_and_get_urls(
        self,
        images_base64: Dict[str, str],
        document_id: str
    ) -> Dict[str, str]:
        """
        Faz upload de múltiplas imagens para Azure Blob Storage.
        
        Args:
            images_base64: Dicionário {image_id: base64_string}
            document_id: ID único do documento para organização
            
        Returns:
            Dicionário {image_id: public_url}
            
        Raises:
            ValueError: Se configurações Azure não estão disponíveis
            httpx.HTTPError: Se falha no upload
        """
        if not self._settings.azure_blob_enabled:
            self._logger.warning("Azure Blob Storage não está habilitado ou configurado")
            return {}
        
        if not images_base64:
            self._logger.info("Nenhuma imagem para upload")
            return {}
        
        self._logger.info(f"Iniciando upload de {len(images_base64)} imagens para Azure Blob Storage")
        
        urls_mapping = {}
        
        async with httpx.AsyncClient() as client:
            for image_id, base64_data in images_base64.items():
                try:
                    # Upload individual da imagem
                    public_url = await self._upload_single_image(
                        client=client,
                        image_id=image_id,
                        base64_data=base64_data,
                        document_id=document_id
                    )
                    
                    if public_url:
                        urls_mapping[image_id] = public_url
                        self._logger.debug(f"✅ Upload concluído: {image_id} -> {public_url}")
                    else:
                        self._logger.error(f"❌ Falha no upload da imagem: {image_id}")
                        
                except Exception as e:
                    self._logger.error(f"❌ Erro no upload da imagem {image_id}: {str(e)}")
                    continue
        
        self._logger.info(f"Upload finalizado: {len(urls_mapping)}/{len(images_base64)} imagens enviadas com sucesso")
        return urls_mapping
    
    async def _upload_single_image(
        self,
        client: httpx.AsyncClient,
        image_id: str,
        base64_data: str,
        document_id: str
    ) -> Optional[str]:
        """
        Faz upload de uma única imagem para Azure Blob Storage.
        
        Args:
            client: Cliente HTTP reutilizável
            image_id: Identificador único da imagem
            base64_data: Dados da imagem em base64
            document_id: ID do documento para organização
            
        Returns:
            URL pública da imagem ou None se falhar
        """
        try:
            # Converter base64 para bytes
            image_bytes = base64.b64decode(base64_data)
            
            # Gerar nome único para o blob
            blob_name = self._generate_blob_name(document_id, image_id)
            
            # Construir URL de upload correta (PUT direto no blob)
            upload_url = f"{self._settings.azure_blob_storage_url}/{self._settings.azure_blob_container_name}/{blob_name}?{self._settings.azure_blob_sas_token}"
            
            # Headers para upload (sem metadados personalizados para evitar problemas)
            headers = {
                'x-ms-blob-type': 'BlockBlob',
                'Content-Type': 'image/jpeg'
            }
            
            # Fazer upload via PUT request
            response = await client.put(
                url=upload_url,
                content=image_bytes,
                headers=headers,
                timeout=30.0
            )
            
            # Verificar se upload foi bem-sucedido
            if response.status_code in [200, 201]:
                # Construir URL pública COM SAS token (necessário pois acesso público não está habilitado)
                public_url = f"{self._settings.azure_blob_storage_url}/{self._settings.azure_blob_container_name}/{blob_name}?{self._settings.azure_blob_sas_token}"
                return public_url
            else:
                self._logger.error(f"Upload falhou - Status: {response.status_code}, Resposta: {response.text}")
                return None
                
        except base64.binascii.Error as e:
            self._logger.error(f"Erro ao decodificar base64 para {image_id}: {str(e)}")
            return None
        except httpx.HTTPError as e:
            self._logger.error(f"Erro HTTP no upload de {image_id}: {str(e)}")
            return None
        except Exception as e:
            self._logger.error(f"Erro inesperado no upload de {image_id}: {str(e)}")
            return None
    
    def _generate_blob_name(self, document_id: str, image_id: str) -> str:
        """
        Gera nome único para o blob no Azure Storage.
        
        Formato: documents/{document_id}/images/{timestamp}_{image_id}_{uuid}.jpg
        
        Args:
            document_id: ID do documento
            image_id: ID da imagem
            
        Returns:
            Nome único do blob
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Primeiros 8 caracteres do UUID
        
        # Sanitizar IDs para nomes de arquivo seguros
        safe_document_id = self._sanitize_filename(document_id)
        safe_image_id = self._sanitize_filename(image_id)
        
        return f"documents/{safe_document_id}/images/{timestamp}_{safe_image_id}_{unique_id}.jpg"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza string para uso seguro em nomes de arquivo.
        
        Args:
            filename: Nome original
            
        Returns:
            Nome sanitizado
        """
        # Remover caracteres problemáticos
        unsafe_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ' ']
        safe_name = filename
        
        for char in unsafe_chars:
            safe_name = safe_name.replace(char, '_')
        
        # Limitar tamanho e remover underscores duplos
        safe_name = safe_name[:50].replace('__', '_').strip('_')
        
        return safe_name if safe_name else 'unnamed'
    
    def get_service_status(self) -> Dict[str, any]:
        """
        Retorna status atual do serviço para diagnóstico.
        
        Returns:
            Dicionário com informações de configuração e status
        """
        return {
            "azure_blob_enabled": self._settings.azure_blob_enabled,
            "has_storage_url": bool(self._settings.azure_blob_storage_url),
            "has_container_name": bool(self._settings.azure_blob_container_name),
            "has_sas_token": bool(self._settings.azure_blob_sas_token),
            "enable_upload_flag": self._settings.enable_azure_blob_upload,
            "service_ready": self._settings.azure_blob_enabled
        }