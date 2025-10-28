# SmartQuest - Developer Guide

Guia completo para desenvolvimento e contribuição no projeto SmartQuest.

## 🚀 Quick Start Development

### 📋 **Pré-requisitos**

- **Python 3.9+** instalado
- **Docker Desktop** rodando
- **Git** configurado
- **IDE** (VS Code recomendado)

### ⚡ **Setup Rápido (5 minutos)**

```bash
# 1. Clone e entre no diretório
git clone <repository-url>
cd SmartQuest

# 2. Configure ambiente
cp .env-local.template .env-local
# Edite .env-local com suas credenciais Azure

# 3. Suba o ambiente completo
docker-compose up -d

# 4. Execute migrações MongoDB
python scripts/run_migrations.py

# 5. Teste a API
curl http://localhost:8000/health
```

**✅ Pronto!** API rodando em `http://localhost:8000`

## 🔧 Ambiente de Desenvolvimento

### 🐳 **Docker-First Approach**

```yaml
# docker-compose.yml - Ambiente completo
services:
  smartquest-api: # API FastAPI
  mongodb: # MongoDB 7.0
  mongo-express: # Interface web MongoDB (opcional)
```

### 📦 **Python Environment**

```bash
# Virtual environment (alternativa local)
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Desenvolvimento local (sem Docker)
python -m uvicorn app.main:app --reload --port 8000
```

### 🗂️ **Variáveis de Ambiente**

```bash
# .env-local (desenvolvimento)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=your-endpoint
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-key
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=smartquest
DEBUG=true

# Note: MongoDB e Azure Blob Storage são OBRIGATÓRIOS (sem feature flags)
```

## 🏗️ Estrutura do Projeto

### 📁 **Diretórios Principais**

```bash
SmartQuest/
├── app/                    # Código principal da aplicação
│   ├── api/               # Endpoints FastAPI
│   ├── services/          # Business logic + DI Container
│   ├── models/            # Models Pydantic
│   ├── core/              # Configurações e exceções
│   └── utils/             # Utilitários gerais
├── scripts/               # Scripts de automação
│   ├── run_migrations.py  # Migrações MongoDB
│   └── migrations/        # Scripts de migração
├── tests/                 # Testes automatizados
│   ├── unit/             # Testes unitários
│   ├── integration/      # Testes de integração
│   └── fixtures/         # Dados de teste
├── docs/                  # Documentação especializada
└── cache/                # Cache local de documentos
```

### 🧩 **Padrão de Organização**

```python
# Exemplo: app/services/analyze_service.py
class AnalyzeService(IAnalyzeService):
    """
    🎯 Responsibility: Orchestrate document analysis
    🔌 Dependencies: Injected via DI Container
    🧪 Tests: tests/unit/services/test_analyze_service.py
    """
```

## 🧪 Testing & Quality

### ⚡ **Executar Testes**

```bash
# Todos os testes
python -m pytest

# Testes específicos
python -m pytest tests/unit/services/
python -m pytest tests/integration/

# Com coverage
python -m pytest --cov=app --cov-report=html

# Testes rápidos (sem integração)
python -m pytest -m "not integration"
```

### 📊 **Coverage Report**

```bash
# Gerar relatório HTML
python -m pytest --cov=app --cov-report=html
# Visualizar: tests/coverage/htmlcov/index.html
```

### 🔍 **Code Quality**

```bash
# Linting
python -m flake8 app/
python -m black app/ --check

# Type checking
python -m mypy app/

# Security
python -m bandit -r app/
```

## 🔄 MongoDB Development

### 🗄️ **Database Management**

```bash
# Executar migrações
python scripts/run_migrations.py

# Status das migrações
python scripts/run_migrations.py --status

# Reset database (cuidado!)
python scripts/run_migrations.py --reset
```

### 📊 **MongoDB Tools**

```bash
# Mongo Shell (via Docker)
docker exec -it smartquest-mongodb-1 mongosh

# Interface Web (Mongo Express)
# http://localhost:8081
```

### 📋 **Collections Overview**

| Collection              | Docs | Propósito             |
| ----------------------- | ---- | --------------------- |
| `analyze_documents`     | ~1K  | Resultados de análise |
| `azure_processing_data` | ~500 | Métricas Azure        |
| `migrations`            | 3    | Controle de versão DB |

## 🔧 Development Workflows

### 🌟 **Feature Development**

```bash
# 1. Branch feature
git checkout -b feature/nova-funcionalidade

# 2. Desenvolvimento
# - Código + testes
# - Migrações se necessário

# 3. Quality check
python -m pytest
python -m flake8 app/

# 4. Commit e push
git add .
git commit -m "feat: nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### 🐛 **Bug Fixing**

```bash
# 1. Reproduzir bug
python -m pytest tests/test_specific_bug.py -v

# 2. Fix + test
# - Correção
# - Teste regressão

# 3. Validação
python -m pytest  # Todos os testes passando
```

### 📦 **Release Process**

```bash
# 1. Merge para main
git checkout main
git pull origin main

# 2. Tag release
git tag v1.2.0
git push origin v1.2.0

# 3. Deploy (futuro)
# CI/CD pipeline automático
```

## 📝 Debugging & Development Tips

### 🐞 **Debug API Local**

```python
# VS Code launch.json
{
    "name": "SmartQuest API",
    "type": "python",
    "request": "launch",
    "program": "-m uvicorn app.main:app --reload",
    "envFile": "${workspaceFolder}/.env-local",
    "console": "integratedTerminal"
}
```

### 🔍 **Debug MongoDB**

```bash
# Verificar dados via shell
docker exec -it smartquest-mongodb-1 mongosh
> use smartquest
> db.analyze_documents.find().limit(5)
> db.migrations.find()
```

### 📊 **Health Checks**

```bash
# Status geral
curl http://localhost:8000/health

# Status MongoDB específico
curl http://localhost:8000/health/database

# Logs da aplicação
docker logs smartquest-smartquest-api-1 -f
```

### ⚡ **Performance Debugging**

```python
# Adicionar timing logs
import time
start_time = time.time()
# ... código ...
logger.info(f"Operation took {time.time() - start_time:.2f}s")
```

## 🚀 Development Best Practices

### ✅ **Code Standards**

- **Type Hints**: Sempre use type annotations
- **Docstrings**: Documente classes e métodos públicos
- **Error Handling**: Use hierarchy de exceções customizada
- **Testing**: Escreva testes para toda lógica de negócio

### 🏗️ **Architecture Guidelines**

- **DI Container**: Use injeção de dependência
- **Interface Segregation**: Prefira interfaces específicas
- **Single Responsibility**: Uma classe, uma responsabilidade
- **Clean Code**: Nomes descritivos, funções pequenas

### 📊 **Performance Tips**

- **Async/Await**: Use para I/O operations
- **Caching**: Implemente cache para operações custosas
- **Database**: Indices apropriados no MongoDB
- **Memory**: Monitore uso de memória em large files

## 🛠️ Useful Commands

### 📋 **Daily Development**

```bash
# Subir ambiente
docker-compose up -d

# Logs em tempo real
docker-compose logs -f smartquest-api

# Restart apenas API
docker-compose restart smartquest-api

# Parar ambiente
docker-compose down

# Clean rebuild
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

### 🗄️ **Database Operations**

```bash
# Backup MongoDB
docker exec smartquest-mongodb-1 mongodump --db smartquest --out /tmp/backup

# Restore MongoDB
docker exec smartquest-mongodb-1 mongorestore --db smartquest /tmp/backup/smartquest

# Collection stats
docker exec -it smartquest-mongodb-1 mongosh --eval "db.analyze_documents.stats()"
```

## 🆘 Troubleshooting

### 🔧 **Problemas Comuns**

| Problema                     | Solução                           |
| ---------------------------- | --------------------------------- |
| `Connection refused MongoDB` | `docker-compose up -d mongodb`    |
| `Azure key invalid`          | Verificar `.env-local`            |
| `Port 8000 busy`             | `docker-compose down`             |
| `Import errors`              | `pip install -r requirements.txt` |

### 📞 **Getting Help**

- **Logs**: Sempre verifique logs primeiro
- **Health endpoints**: Use `/health` para diagnóstico
- **Documentation**: Consulte `docs/` para detalhes técnicos
- **Tests**: Execute testes para validar ambiente

---

**🚀 Happy Coding!** | **SmartQuest v2.0-dev** | **Última atualização: Outubro 2025**
