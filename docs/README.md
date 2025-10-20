# SmartQuest

Sistema inteligente de análise de documentos PDF para extração automática de questões e context blocks educacionais.

## 📋 Sobre o Projeto

SmartQuest é uma ferramenta desenvolvida para automatizar a análise de avaliações educacionais em formato PDF. O sistema utiliza Azure Document Intelligence para extrair texto e imagens, processando automaticamente questões, alternativas e metadados de provas e testes educacionais.

O projeto faz parte do ecossistema CriEduc e foi criado para auxiliar educadores e plataformas educacionais na digitalização e análise automatizada de conteúdo educacional, permitindo insights rápidos sobre estrutura e conteúdo de avaliações.

**⚠️ STATUS: Projeto em desenvolvimento ativo - Não publicado em produção**

## ✨ Funcionalidades Principais

- 📄 **Análise de PDFs**: Processamento automático de documentos educacionais
- ❓ **Extração de Questões**: Identificação e estruturação de questões e alternativas
- 🖼️ **Processamento de Imagens**: Categorização e extração de imagens (header/content)
- 💾 **Persistência MongoDB**: Armazenamento automático de todos os resultados
- 🔄 **Sistema de Cache**: Cache inteligente para otimização de performance
- 🏗️ **Arquitetura Moderna**: DI Container, SOLID principles, Clean Architecture
- 🧪 **Cobertura de Testes**: Suite completa de testes unitários e integração

## 🚀 Quick Start

### 🐳 **Recomendado: Docker Setup**

```bash
# 1. Clonar repositório
git clone https://github.com/Bergami/CriEduc.SmartQuest.git
cd CriEduc.SmartQuest

# 2. Configurar ambiente
cp .env-local.example .env-local
# Editar .env-local com suas credenciais Azure

# 3. Subir infraestrutura
docker-compose up -d

# 4. Aplicar migrações
cd scripts && python run_migrations.py

# 5. Acessar aplicação
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 🐍 **Alternativo: Setup Manual**

```bash
# 1. Ambiente Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Dependências
pip install -r requirements.txt

# 3. Configuração
cp .env-local.example .env-local
# Configurar credenciais Azure e MongoDB

# 4. Executar
python start_simple.py
```

## 📚 Documentação

### 📖 **Documentação Especializada**

- 🏗️ **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura técnica e tecnologias
- 👨‍💻 **[DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)** - Guia completo de desenvolvimento
- 🧪 **[tests/README.md](tests/README.md)** - Documentação de testes

### 🔗 **Links Úteis**

- 📊 **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- ❤️ **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
- 🗄️ **DB Health**: [http://localhost:8000/health/database](http://localhost:8000/health/database)

## ⚙️ Configuração Mínima

### 🔑 **Variáveis Essenciais (.env-local)**

```bash
# Azure Document Intelligence (obrigatório)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-service.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your-api-key

# MongoDB (Docker configura automaticamente)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=smartquest
ENABLE_MONGODB_PERSISTENCE=true
```

## 🧪 Testes Rápidos

```bash
# Executar todos os testes
python run_tests.py

# Testes com coverage
python run_tests.py --coverage

# Apenas testes unitários
pytest tests/unit/ -v
```

## 📊 Status do Projeto

| Componente               | Status                | Observações              |
| ------------------------ | --------------------- | ------------------------ |
| 🔌 **API Core**          | ✅ Funcional          | FastAPI + Pydantic       |
| 💾 **MongoDB**           | ✅ Implementado       | Persistência + Migrações |
| ☁️ **Azure Integration** | ✅ Funcional          | Document Intelligence    |
| 🧪 **Testing**           | ✅ Completo           | 100+ testes              |
| 🐳 **Docker**            | ✅ Configurado        | Desenvolvimento          |
| 🚀 **Produção**          | ⏳ Em desenvolvimento | Não publicado            |

## 👨‍💻 Desenvolvimento

### 🔧 **Comandos Úteis**

```bash
# Desenvolver com hot-reload
uvicorn app.main:app --reload

# Executar migrações
cd scripts && python run_migrations.py

# Limpar cache
python cache_manager_cli.py clear

# Verificar saúde
curl http://localhost:8000/health
```

## 📞 Suporte & Contato

### 🐛 **Problemas/Issues**

1. Verificar health checks: `/health` e `/health/database`
2. Consultar logs em `logs/`
3. Executar testes: `python run_tests.py`

### 👤 **Autor**

**Wander Vinicius Bergami**  
Parte do ecossistema CriEduc - Tecnologia Educacional

### 📧 **Contato para Desenvolvimento**

- 🔧 Issues técnicos: GitHub Issues
- 💡 Sugestões: Pull Requests
- 📖 Documentação: Consultar arquivos em `/docs`

---

**⚡ SmartQuest - Transformando análise de documentos educacionais** | **v2.0-dev** | **🚧 Em desenvolvimento ativo**
