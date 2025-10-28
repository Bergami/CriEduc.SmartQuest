try:
    import uvicorn
except ImportError:
    uvicorn = None
    
import logging
from contextlib import asynccontextmanager
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

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia lifecycle da aplicação FastAPI.
    
    - Startup: Inicializa conexões e recursos
    - Shutdown: Fecha conexões e limpa recursos
    """
    # Startup
    logger.info("🚀 Starting SmartQuest API...")
    
    # Inicializa conexão MongoDB via DI Container
    try:
        from app.core.di_container import container
        from app.services.infrastructure.mongodb_connection_service import MongoDBConnectionService
        
        if container.is_registered(MongoDBConnectionService):
            mongo_service = container.resolve(MongoDBConnectionService)
            # Testa conexão durante startup
            await mongo_service.get_database()
            logger.info("✅ MongoDB connection initialized")
        else:
            logger.warning("⚠️ MongoDBConnectionService not registered in DI Container")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize MongoDB: {e}")
        # Não bloqueia startup - deixa health check reportar o problema
    
    logger.info("✅ SmartQuest API started successfully")
    
    yield  # Aplicação rodando
    
    # Shutdown
    logger.info("🛑 Shutting down SmartQuest API...")
    
    try:
        from app.core.di_container import container
        from app.services.infrastructure.mongodb_connection_service import MongoDBConnectionService
        
        if container.is_registered(MongoDBConnectionService):
            mongo_service = container.resolve(MongoDBConnectionService)
            await mongo_service.close()
            logger.info("✅ MongoDB connection closed")
            
    except Exception as e:
        logger.error(f"❌ Error closing MongoDB connection: {e}")
    
    logger.info("✅ SmartQuest API shutdown complete")


# Inicializar FastAPI com lifecycle management
app = FastAPI(
    title="SmartQuest API",
    version="0.1.0",
    description="Microservice for analyzing and classifying educational assessments",
    lifespan=lifespan
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