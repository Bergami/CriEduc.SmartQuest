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

# Inicializar FastAPI
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