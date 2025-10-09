# Setup e Instalação

## 🚀 Quick Start

### **Pré-requisitos**

- Python 3.9 ou superior
- Git
- Azure Document Intelligence (opcional - tem modo mock)

### **1. Clonar Repositório**

```bash
git clone [repository-url]
cd CriEduc.SmartQuest
```

### **2. Criar Ambiente Virtual**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **3. Instalar Dependências**

```bash
pip install -r requirements.txt
```

### **4. Configurar Variáveis de Ambiente**

```bash
# Copiar templates
cp .env.example .env
cp .env-local.example .env-local

# Editar configurações (ver seção Configuração)
```

### **5. Executar Aplicação**

```bash
# Modo normal (requer Azure configurado)
python start_simple.py

# Modo mock (sem Azure)
python start_simple.py --use-mock
```

### **6. Verificar Funcionamento**

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health/

## ⚙️ Configuração Detalhada

### **Variáveis de Ambiente (.env)**

```bash
# Aplicação
APP_NAME=SmartQuest API
DEBUG=true
USE_AZURE_AI=true

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=detailed
```

### **Configurações Azure (.env-local)**

```bash
# Azure Document Intelligence
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-api-key
AZURE_DOCUMENT_INTELLIGENCE_MODEL=prebuilt-layout
AZURE_DOCUMENT_INTELLIGENCE_API_VERSION=2024-07-31-preview
```

### **Obter Credenciais Azure**

1. **Criar Resource no Azure Portal**

   - Acesse portal.azure.com
   - Crie "Document Intelligence" resource
   - Copie endpoint e key

2. **Configurar no Projeto**
   ```bash
   # Adicionar ao .env-local
   AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=seu-endpoint
   AZURE_DOCUMENT_INTELLIGENCE_KEY=sua-chave
   ```

## 🐳 Docker (Opcional)

### **Executar com Docker**

```bash
# Build da imagem
docker build -t smartquest-api .

# Executar container
docker run -p 8000:8000 smartquest-api

# Com variáveis de ambiente
docker run -p 8000:8000 --env-file .env smartquest-api
```

### **Docker Compose**

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
      - .env-local
    volumes:
      - ./logs:/app/logs
```

## 🧪 Executar Testes

### **Testes Completos**

```bash
# Todos os testes
python run_tests.py

# Com coverage
python run_tests.py --coverage

# Testes específicos
pytest tests/unit/test_parsers.py -v
```

### **Validar Configuração**

```bash
# Testar DI Container
python -c "from app.config.di_config import validate_configuration; validate_configuration()"

# Testar importação
python -c "from app.main import app; print('✅ OK')"
```

## 🔧 Desenvolvimento

### **Estrutura Recomendada**

```
CriEduc.SmartQuest/
├── venv/                    # Ambiente virtual
├── .env                     # Config local (não committar)
├── .env-local              # Config Azure (não committar)
├── logs/                   # Logs da aplicação
└── cache/                  # Cache de documentos
```

### **Comandos Úteis**

```bash
# Recarregar automaticamente (desenvolvimento)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Debug com logs detalhados
python start_simple.py --debug

# Limpar cache
rm -rf cache/documents/*
```

### **IDE Setup (VS Code)**

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

## 🔍 Troubleshooting

### **Problemas Comuns**

#### **Erro: Azure não configurado**

```bash
# Verificar configuração
python -c "from app.config.settings import settings; print(settings.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT)"

# Solução: Configurar .env-local ou usar modo mock
python start_simple.py --use-mock
```

#### **Erro: Dependências**

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

#### **Erro: Porta em uso**

```bash
# Verificar processo na porta 8000
netstat -tulpn | grep 8000

# Matar processo (Linux/Mac)
kill -9 $(lsof -t -i:8000)

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### **Logs de Debug**

```bash
# Logs da aplicação
tail -f logs/app.log

# Logs específicos
grep "ERROR" logs/app.log
grep "analyze_document" logs/app.log
```

## 📦 Deploy

### **Preparação para Produção**

```bash
# Instalar dependências de produção
pip install -r requirements.txt --no-dev

# Configurar variáveis de produção
export DEBUG=false
export LOG_LEVEL=WARNING

# Testar build
python -m compileall app/
```

### **Checklist de Deploy**

- [ ] Variáveis de ambiente configuradas
- [ ] Azure Document Intelligence funcionando
- [ ] Testes passando
- [ ] Logs configurados
- [ ] Health check respondendo
- [ ] Performance testada

## 🔐 Segurança

### **Recomendações**

- Nunca commitar .env ou .env-local
- Usar secrets management em produção
- Configurar HTTPS
- Implementar rate limiting
- Monitorar logs de segurança

### **Variáveis Sensíveis**

```bash
# Exemplos do que NÃO commitar
AZURE_DOCUMENT_INTELLIGENCE_KEY=secret-key
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET=super-secret-key
```

---

**Pronto!** Com isso você terá o SmartQuest funcionando localmente. Para problemas específicos, consulte a seção de troubleshooting ou os logs da aplicação.
