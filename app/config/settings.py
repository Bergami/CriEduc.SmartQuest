import os
from pathlib import Path
from pydantic import BaseSettings

# Carregar variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    
    # Procurar os arquivos .env na raiz do projeto
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    env_local_path = project_root / ".env-local"
    
    # Carregar primeiro o .env (configurações públicas)
    if env_path.exists():
        load_dotenv(env_path)
    
    # Carregar depois o .env-local (configurações sensíveis - sobrescreve o .env)
    if env_local_path.exists():
        load_dotenv(env_local_path, override=True)
    
except ImportError:
    # python-dotenv não instalado, usar variáveis de ambiente do sistema
    pass

class Settings(BaseSettings):
    # General configurations
    app_name: str = "SmartQuest API"
    debug: bool = False
    
    # Document extraction provider configuration
    document_extraction_provider: str = os.getenv("DOCUMENT_EXTRACTION_PROVIDER", "azure")
    
    # Azure AI Document Intelligence
    azure_document_intelligence_endpoint: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "")
    azure_document_intelligence_key: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "")
    azure_document_intelligence_model: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_MODEL", "prebuilt-layout")
    azure_document_intelligence_api_version: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_VERSION", "2023-07-31")
    use_azure_ai: bool = os.getenv("USE_AZURE_AI", "true").lower() == "true"
    
    # ================================
    # 🆕 MONGODB CONFIGURATION  
    # ================================
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_database: str = os.getenv("MONGODB_DATABASE", "smartquest")
    mongodb_connection_timeout: int = int(os.getenv("MONGODB_CONNECTION_TIMEOUT", "10000"))
    
    # ================================
    # 🆕 AZURE BLOB STORAGE CONFIGURATION
    # ================================
    azure_blob_storage_url: str = os.getenv("AZURE_BLOB_STORAGE_URL", "")
    azure_blob_container_name: str = os.getenv("AZURE_BLOB_CONTAINER_NAME", "")
    azure_blob_sas_token: str = os.getenv("AZURE_BLOB_SAS_TOKEN", "")
    enable_azure_blob_upload: bool = os.getenv("ENABLE_AZURE_BLOB_UPLOAD", "true").lower() == "true"
    
    # ================================
    # 🆕 FEATURE FLAGS
    # ================================
    enable_mongodb_persistence: bool = os.getenv("ENABLE_MONGODB_PERSISTENCE", "true").lower() == "true"
    
    @property
    def azure_blob_sas_url(self) -> str:
        """Constrói URL completa com SAS token para upload"""
        if not self.azure_blob_storage_url or not self.azure_blob_container_name or not self.azure_blob_sas_token:
            return ""
        return f"{self.azure_blob_storage_url}/{self.azure_blob_container_name}?{self.azure_blob_sas_token}"
    
    @property
    def azure_blob_enabled(self) -> bool:
        """Verifica se Azure Blob Storage está configurado e habilitado"""
        return (
            self.enable_azure_blob_upload and 
            bool(self.azure_blob_storage_url) and 
            bool(self.azure_blob_container_name) and 
            bool(self.azure_blob_sas_token)
        )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Mock settings for when .env is not available
class MockSettings:
    app_name = "SmartQuest API (Mock)"
    debug = True
    document_extraction_provider = "azure"
    azure_document_intelligence_endpoint = ""
    azure_document_intelligence_key = ""
    azure_document_intelligence_model = "prebuilt-layout"
    azure_document_intelligence_api_version = "2023-07-31"
    use_azure_ai = False
    
    # 🆕 MongoDB Mock Settings
    mongodb_url = "mongodb://localhost:27017"
    mongodb_database = "smartquest"
    mongodb_connection_timeout = 10000
    enable_mongodb_persistence = False
    
    # 🆕 Azure Blob Storage Mock Settings
    azure_blob_storage_url = ""
    azure_blob_container_name = "mock-container"
    azure_blob_sas_token = ""
    enable_azure_blob_upload = False
    
    @property
    def azure_blob_sas_url(self) -> str:
        """Mock sempre retorna string vazia"""
        return ""
    
    @property
    def azure_blob_enabled(self) -> bool:
        """Mock sempre desabilitado"""
        return False

try:
    settings = Settings()
except Exception as e:
    print(f"⚠️ Warning: Could not load settings from .env: {e}")
    settings = MockSettings()

def get_settings():
    """Factory function para obter configurações."""
    return settings
