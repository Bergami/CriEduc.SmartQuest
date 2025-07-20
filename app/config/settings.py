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
    azure_document_intelligence_api_version: str = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_API_VERSION", "2024-11-30")
    use_azure_ai: bool = os.getenv("USE_AZURE_AI", "true").lower() == "true"
    
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
    azure_document_intelligence_api_version = "2024-11-30"
    use_azure_ai = False

try:
    settings = Settings()
except Exception as e:
    print(f"⚠️ Warning: Could not load settings from .env: {e}")
    settings = MockSettings()
