"""
Serviço de verificação de duplicatas de documentos.

Responsabilidade única: Verificar se um documento já foi processado anteriormente
e retornar os dados existentes quando aplicável.
"""

from typing import Optional
from dataclasses import dataclass
from fastapi import UploadFile
from datetime import datetime

from app.services.persistence import ISimplePersistenceService
from app.models.persistence import DocumentStatus
from app.dtos.responses.document_response_dto import DocumentResponseDTO
from app.core.logging import structured_logger


@dataclass
class DuplicateCheckResult:
    """Resultado da verificação de duplicatas."""
    is_duplicate: bool
    should_process: bool
    file_size: int = 0
    existing_response: Optional[DocumentResponseDTO] = None
    existing_document_id: Optional[str] = None
    processed_at: Optional[datetime] = None


class DuplicateCheckService:
    """
    Serviço responsável por verificar duplicatas de documentos.
    
    Single Responsibility: Determinar se um documento é duplicata e retornar
    dados existentes quando aplicável.
    """
    
    def __init__(self, persistence_service: ISimplePersistenceService):
        self.persistence_service = persistence_service
    
    def _get_file_size(self, file: UploadFile) -> int:
        """
        Extrai o tamanho do arquivo em bytes.
        
        Nota: FastAPI's UploadFile.seek() é async e aceita apenas position.
        Usamos o SpooledTemporaryFile subjacente (file.file) que possui
        o método síncrono seek(offset, whence).
        
        Args:
            file: Arquivo FastAPI UploadFile
            
        Returns:
            Tamanho do arquivo em bytes
        """
        file.file.seek(0, 2)  # Seek to end
        size = file.file.tell()
        file.file.seek(0)  # Reset to start
        return size
    
    async def check_and_handle_duplicate(
        self,
        email: str,
        file: UploadFile
    ) -> DuplicateCheckResult:
        """
        Verifica se documento é duplicata e retorna resultado apropriado.
        
        Lógica de negócio:
        - Se COMPLETED: retorna dados existentes (não reprocessa)
        - Se FAILED: permite reprocessamento
        - Se não existe: permite processamento normal
        
        Args:
            email: Email do usuário
            file: Arquivo PDF a ser verificado
            
        Returns:
            DuplicateCheckResult com informações sobre duplicata
        """
        file_size = self._get_file_size(file)
        
        structured_logger.debug(
            "Checking for duplicate document",
            context={
                "email": email,
                "filename": file.filename,
                "file_size": file_size
            }
        )
        
        # Verificar no MongoDB
        existing_doc = await self.persistence_service.check_duplicate_document(
            email=email,
            filename=file.filename,
            file_size=file_size
        )
        
        # Caso 1: Documento não existe - processar normalmente
        if not existing_doc:
            structured_logger.debug(
                "No duplicate found - will process document",
                context={"email": email, "filename": file.filename}
            )
            return DuplicateCheckResult(
                is_duplicate=False,
                should_process=True,
                file_size=file_size
            )
        
        # Caso 2: Documento existe e está COMPLETED - retornar existente
        if existing_doc.status == DocumentStatus.COMPLETED:
            structured_logger.info(
                "Duplicate document found - returning existing data",
                context={
                    "email": email,
                    "filename": file.filename,
                    "file_size": file_size,
                    "document_id": str(existing_doc.id),
                    "processed_at": existing_doc.created_at
                }
            )
            
            # Montar response com metadados de duplicata
            response_data = existing_doc.response.copy()
            response_data.update({
                "status": "already_processed",
                "message": f"Documento já foi processado anteriormente em {existing_doc.created_at.isoformat()}",
                "from_database": True
            })
            
            existing_response = DocumentResponseDTO(**response_data)
            
            return DuplicateCheckResult(
                is_duplicate=True,
                should_process=False,
                existing_response=existing_response,
                file_size=file_size,
                existing_document_id=str(existing_doc.id),
                processed_at=existing_doc.created_at
            )
        
        # Caso 3: Documento existe mas está FAILED - permitir reprocessamento
        if existing_doc.status == DocumentStatus.FAILED:
            structured_logger.info(
                "Reprocessing previously failed document",
                context={
                    "email": email,
                    "filename": file.filename,
                    "previous_document_id": str(existing_doc.id),
                    "previous_failure": existing_doc.created_at
                }
            )
            return DuplicateCheckResult(
                is_duplicate=True,
                should_process=True,
                file_size=file_size,
                existing_document_id=str(existing_doc.id),
                processed_at=existing_doc.created_at
            )
        
        # Caso 4: Status desconhecido (PENDING, etc) - processar por segurança
        structured_logger.warning(
            "Document exists with unexpected status - will process",
            context={
                "email": email,
                "filename": file.filename,
                "status": existing_doc.status,
                "document_id": str(existing_doc.id)
            }
        )
        return DuplicateCheckResult(
            is_duplicate=True,
            should_process=True,
            file_size=file_size,
            existing_document_id=str(existing_doc.id)
        )
