from fastapi import APIRouter

# 🏗️ Importa os módulos de rota
from app.api.controllers.analyze import router as analyze_router
from app.api.controllers.health import router as health_router


# 🔗 Cria o agrupador de rotas
router = APIRouter()

# 📌 Registra cada módulo na API
router.include_router(health_router, prefix="/health", tags=["Health"])
router.include_router(analyze_router, prefix="/analyze", tags=["Analyze"])

