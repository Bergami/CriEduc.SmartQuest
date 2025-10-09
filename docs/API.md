# API Documentation

## Health Check Endpoint

### GET /health/

**Descrição:** Endpoint de health check consolidado que retorna status da API, configurações e informações do serviço.

**Resposta:**

```json
{
  "status": "healthy",
  "message": "SmartQuest API is running",
  "service": {
    "name": "SmartQuest API",
    "version": "0.1.0",
    "description": "Microservice for analyzing and classifying educational assessments"
  },
  "configuration": {
    "azure_ai_configured": true,
    "azure_ai_enabled": true
  },
  "endpoints": {
    "health": "/health/ - Health check and API status",
    "analyze": "/analyze/analyze_document - Document analysis endpoint"
  }
}
```

## Document Analysis Endpoint

### POST /analyze/analyze_document

**Descrição:** Endpoint principal para análise de documentos PDF educacionais.

**Parâmetros:**

- `email` (query): Email do usuário
- `file` (form-data): Arquivo PDF para análise

**Resposta:** Objeto DocumentResponseDTO com questões extraídas e categorizadas.

---

## Mudanças Implementadas (FASE 1)

### ANTES:

- `/` (GET) - Root endpoint redundante
- `/health` (GET) - Health check específico
- Duplicação no router (health_router incluído 2x)

### DEPOIS:

- `/health/` (GET) - Endpoint consolidado único
- Informações mais estruturadas e completas
- Router limpo sem duplicações

### Benefícios:

✅ Redução de endpoints: 2 → 1 (-50%)  
✅ Padronização REST (health check em /health/)  
✅ Informações mais organizadas e completas  
✅ Eliminação de duplicação no router  
✅ Manutenibilidade melhorada
