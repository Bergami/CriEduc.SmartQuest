try:
    import uvicorn
except ImportError:
    uvicorn = None
    
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
import dotenv

dotenv.load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

try:
    from app.config import settings
except ImportError:
    # Fallback caso config não esteja disponível
    class MockSettings:
        use_azure_ai = True
        azure_document_intelligence_endpoint = ""
        azure_document_intelligence_key = ""
        azure_document_intelligence_model = "prebuilt-layout"
        azure_document_intelligence_api_version = "2023-07-31"
    settings = MockSettings()

app = FastAPI(
    title="SmartQuest API",
    version="0.1.0",
    description="Microservice for analyzing and classifying educational assessments"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "SmartQuest API está funcionando!",
        "azure_ai_enabled": settings.use_azure_ai,
        "version": "0.1.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "azure_ai_configured": bool(settings.azure_document_intelligence_endpoint and settings.azure_document_intelligence_key),
        "azure_ai_enabled": settings.use_azure_ai
    }

# Para debug direto
if __name__ == "__main__":
    if uvicorn:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True
        )
    else:
        print("❌ Uvicorn não instalado. Execute:")
        print("pip install uvicorn[standard]==0.29.0")
        print("\nOu use o VS Code Run and Debug para executar a aplicação.")