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
        document_id: str,
        document_guid: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Faz upload de múltiplas imagens para Azure Blob Storage.
        
        Args:
            images_base64: Dicionário {image_id: base64_string}
            document_id: ID único do documento para organização
            document_guid: GUID único do documento (gerado se não fornecido)
            
        Returns:
            Dicionário {image_id: public_url}
            
        Raises:
            ValueError: Se configurações Azure não estão disponíveis
            httpx.HTTPError: Se falha no upload
        """
        # Validar disponibilidade do Azure Blob Storage
        if not self._settings.azure_blob_enabled:
            error_msg = "Azure Blob Storage is unavailable or not configured"
            self._logger.error({
                "event": "azure_blob_unavailable",
                "operation": "upload_images",
                "status": "error",
                "message": error_msg,
                "config_status": self.get_service_status()
            })
            raise ValueError(error_msg)
        
        if not images_base64:
            self._logger.info({
                "event": "no_images_to_upload",
                "status": "info",
                "document_id": document_id
            })
            return {}
        
        # Gerar GUID único do documento se não fornecido
        if not document_guid:
            document_guid = str(uuid.uuid4())
            self._logger.info({
                "event": "document_guid_generated",
                "document_guid": document_guid,
                "document_id": document_id
            })
        
        self._logger.info({
            "event": "upload_started",
            "status": "info",
            "images_count": len(images_base64),
            "document_id": document_id,
            "document_guid": document_guid
        })
        
        urls_mapping = {}
        sequence = 1
        
        async with httpx.AsyncClient() as client:
            for image_id, base64_data in images_base64.items():
                try:
                    # Upload individual da imagem
                    public_url = await self._upload_single_image(
                        client=client,
                        image_id=image_id,
                        base64_data=base64_data,
                        document_id=document_id,
                        document_guid=document_guid,
                        sequence=sequence
                    )
                    
                    if public_url:
                        urls_mapping[image_id] = public_url
                        self._logger.debug({
                            "event": "image_uploaded",
                            "status": "success",
                            "image_id": image_id,
                            "url": public_url,
                            "sequence": sequence
                        })
                        sequence += 1
                    else:
                        self._logger.error({
                            "event": "image_upload_failed",
                            "status": "error",
                            "image_id": image_id
                        })
                        
                except Exception as e:
                    self._logger.error({
                        "event": "image_upload_error",
                        "status": "error",
                        "image_id": image_id,
                        "error": str(e)
                    })
                    continue
        
        self._logger.info({
            "event": "upload_completed",
            "status": "success",
            "uploaded_count": len(urls_mapping),
            "total_count": len(images_base64),
            "document_id": document_id
        })
        return urls_mapping
    
    async def _upload_single_image(
        self,
        client: httpx.AsyncClient,
        image_id: str,
        base64_data: str,
        document_id: str,
        document_guid: str,
        sequence: int
    ) -> Optional[str]:
        """
        Faz upload de uma única imagem para Azure Blob Storage.
        
        Args:
            client: Cliente HTTP reutilizável
            image_id: Identificador único da imagem
            base64_data: Dados da imagem em base64
            document_id: ID do documento para logs
            document_guid: GUID único do documento
            sequence: Número sequencial da imagem no documento
            
        Returns:
            URL pública da imagem ou None se falhar
        """
        try:
            # Converter base64 para bytes
            image_bytes = base64.b64decode(base64_data)
            
            # Gerar nome único para o blob com novo padrão
            blob_name = self._generate_blob_name(document_guid, sequence)
            
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
    
    def _generate_blob_name(self, document_guid: str, sequence: int) -> str:
        """
        Gera nome único para o blob no Azure Storage seguindo o padrão aprovado.
        
        Formato: documents/tests/images/{document_guid}/{sequence}.jpg
        
        Args:
            document_guid: GUID único do documento
            sequence: Número sequencial da imagem (1, 2, 3...)
            
        Returns:
            Nome único do blob
        """
        # Sanitizar GUID para nomes de arquivo seguros
        safe_guid = self._sanitize_filename(document_guid)
        
        return f"documents/tests/images/{safe_guid}/{sequence}.jpg"
    
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
    
    async def health_check(self) -> bool:
        """
        Verifica se o Azure Blob Storage está configurado e acessível.
        
        Faz uma requisição GET simples para verificar conectividade com o container.
        
        Returns:
            True se o serviço está saudável, False caso contrário
        """
        try:
            if not self._settings.azure_blob_enabled:
                logger.debug("Azure Blob Storage não está habilitado")
                return False
            
            # Construir URL do container
            base_url = self._settings.azure_blob_storage_url.rstrip('/')
            container = self._settings.azure_blob_container_name
            
            # URL de verificação: lista blobs com max 1 resultado
            check_url = f"{base_url}/{container}?restype=container&comp=list&maxresults=1"
            
            # Adicionar SAS token se disponível
            if self._settings.azure_blob_sas_token:
                sas = self._settings.azure_blob_sas_token.lstrip('?')
                check_url = f"{check_url}&{sas}"
            
            # Fazer requisição GET para verificar acesso
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(check_url)
                
                # 200 = OK, 404 = container não encontrado mas credenciais válidas
                is_healthy = response.status_code in [200, 404]
                
                if is_healthy:
                    logger.debug(f"Azure Blob Storage health check OK (status: {response.status_code})")
                else:
                    logger.warning(f"Azure Blob Storage health check failed (status: {response.status_code})")
                
                return is_healthy
                
        except httpx.TimeoutException:
            logger.warning("Azure Blob Storage health check timeout")
            return False
        except Exception as e:
            logger.warning(f"Azure Blob Storage health check error: {e}")
            return False
