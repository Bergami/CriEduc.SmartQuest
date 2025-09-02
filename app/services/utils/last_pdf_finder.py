"""
Last PDF Finder

Utilitário para encontrar o PDF processado mais recentemente em tests/documents
"""
import os
import glob
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class LastPDFFinder:
    """
    Encontra o PDF processado mais recentemente para usar com Azure response salvo.
    
    Esta classe é usada pelo processo process_document_with_azure_response quando
    precisamos extrair imagens manualmente mas só temos o Azure response (sem PDF original).
    """
    
    @staticmethod
    def get_last_processed_pdf() -> Optional[str]:
        """
        Encontra o PDF mais recentemente modificado em tests/documents
        
        Returns:
            Caminho absoluto para o PDF mais recente, ou None se não encontrar
        """
        try:
            # Definir diretório de documentos
            project_root = Path(__file__).parent.parent.parent.parent
            documents_dir = project_root / "tests" / "documents"
            
            logger.info(f"Looking for PDFs in: {documents_dir}")
            
            if not documents_dir.exists():
                logger.warning(f"Diretório de documentos não existe: {documents_dir}")
                return None
            
            # Buscar todos os arquivos .pdf
            pdf_pattern = str(documents_dir / "*.pdf")
            pdf_files = glob.glob(pdf_pattern)
            
            logger.info(f"Found {len(pdf_files)} PDF files")
            
            if not pdf_files:
                logger.warning(f"Nenhum arquivo PDF encontrado em: {documents_dir}")
                return None
            
            # Encontrar o mais recente baseado na data de modificação
            latest_pdf = max(pdf_files, key=os.path.getmtime)
            
            logger.info(f"PDF mais recente encontrado: {latest_pdf}")
            return latest_pdf
            
        except Exception as e:
            logger.error(f"Erro ao buscar último PDF: {str(e)}")
            return None
    
    @staticmethod
    def save_pdf_for_later_use(file_content: bytes, filename: str, email: str) -> Optional[str]:
        """
        Salva PDF para uso futuro com Azure response
        
        Args:
            file_content: Conteúdo do arquivo PDF
            filename: Nome original do arquivo
            email: Email do usuário (para logging)
            
        Returns:
            Caminho onde o arquivo foi salvo, ou None se falhou
        """
        try:
            # Definir diretório de documentos
            project_root = Path(__file__).parent.parent.parent.parent
            documents_dir = project_root / "tests" / "documents"
            
            # Criar diretório se não existir
            documents_dir.mkdir(parents=True, exist_ok=True)
            
            # Gerar nome único preservando extensão
            base_name = Path(filename).stem
            extension = Path(filename).suffix
            
            if not extension.lower() == '.pdf':
                extension = '.pdf'
            
            # Criar nome com timestamp para evitar conflitos
            import time
            timestamp = int(time.time())
            safe_filename = f"{timestamp}_{base_name}{extension}"
            
            # Caminho completo
            pdf_path = documents_dir / safe_filename
            
            # Salvar arquivo
            with open(pdf_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"PDF salvo para uso futuro: {pdf_path} (usuário: {email})")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"Erro ao salvar PDF para uso futuro: {str(e)}")
            return None
    
    @staticmethod
    def get_pdf_info(pdf_path: str) -> dict:
        """
        Obtém informações sobre um PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Dict com informações do arquivo
        """
        try:
            if not os.path.exists(pdf_path):
                return {"error": "Arquivo não existe"}
            
            stat = os.stat(pdf_path)
            
            return {
                "path": pdf_path,
                "filename": os.path.basename(pdf_path),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "modified_time": stat.st_mtime,
                "exists": True
            }
            
        except Exception as e:
            return {"error": str(e)}
