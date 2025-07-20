# 🧪 SmartQuest - Sistema de Testes

## Visão Geral

O SmartQuest possui um sistema completo de testes unitários e de integração, implementado seguindo as melhores práticas de testing do Python com pytest, similar às práticas de teste utilizadas em C#.

## 📁 Estrutura de Testes

```
tests/
├── unit/                      # Testes unitários
│   ├── test_parsers/         # Testes dos parsers
│   │   ├── test_header_parser.py
│   │   └── test_question_parser.py
│   ├── test_services/        # Testes dos serviços
│   │   └── test_analyze_service.py
│   └── test_validators/      # Testes dos validadores
│       └── test_analyze_validator.py
├── integration/              # Testes de integração
│   ├── test_api/            # Testes da API
│   │   └── test_endpoints.py
│   └── test_azure/          # Testes Azure
│       └── test_azure_integration.py
├── fixtures/                 # Dados de teste
│   ├── __init__.py
│   ├── test_data.py         # Provedores de dados
│   └── sample_documents/    # Documentos de exemplo
│       └── sample_exam.pdf
└── coverage/                # Relatórios de cobertura
    ├── html/               # Relatório HTML
    └── coverage.xml        # Relatório XML
```

## 🚀 Como Executar os Testes

### 1. Executar TODOS os Testes

```powershell
# Usando o script Python
python run_tests.py

# Usando o script PowerShell
.\run_tests.ps1

# Usando pytest diretamente
python -m pytest tests/
```

### 2. Executar Apenas Testes Unitários

```powershell
# Usando o script Python
python run_tests.py --unit

# Usando o script PowerShell
.\run_tests.ps1 -Unit

# Usando pytest diretamente
python -m pytest tests/unit/ -v
```

### 3. Executar Apenas Testes de Integração

```powershell
# Usando o script Python
python run_tests.py --integration

# Usando o script PowerShell
.\run_tests.ps1 -Integration

# Usando pytest diretamente
python -m pytest tests/integration/ -v
```

### 4. Executar com Relatório de Cobertura

```powershell
# Usando o script Python
python run_tests.py --coverage

# Usando o script PowerShell
.\run_tests.ps1 -Coverage

# Usando pytest diretamente
python -m pytest tests/ --cov=app --cov-report=html
```

### 5. Executar Testes Rápidos (Sem Testes Lentos)

```powershell
# Usando o script Python
python run_tests.py --fast

# Usando o script PowerShell
.\run_tests.ps1 -Fast

# Usando pytest diretamente
python -m pytest tests/ -m "not slow"
```

## 📊 Relatórios de Cobertura

Os relatórios de cobertura são gerados em:
- **HTML**: `tests/coverage/html/index.html`
- **XML**: `tests/coverage/coverage.xml`
- **Terminal**: Saída direta no terminal

### Visualizar Relatório de Cobertura

```powershell
# Abrir relatório HTML no navegador
start tests/coverage/html/index.html

# Ou usar o comando
python -m coverage html
```

## 🏷️ Marcadores de Teste

O sistema utiliza marcadores para categorizar os testes:

- `@pytest.mark.unit`: Testes unitários
- `@pytest.mark.integration`: Testes de integração
- `@pytest.mark.slow`: Testes que demoram mais tempo
- `@pytest.mark.azure`: Testes que dependem do Azure
- `@pytest.mark.mock`: Testes que usam dados mock

### Executar por Marcador

```powershell
# Executar apenas testes unitários
python -m pytest -m unit

# Executar apenas testes de integração
python -m pytest -m integration

# Pular testes lentos
python -m pytest -m "not slow"

# Executar apenas testes Azure
python -m pytest -m azure
```

## 🔧 Configuração

### Arquivo de Configuração (`pytest.ini`)

```ini
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--cov=app",
    "--cov-report=html:tests/coverage/html",
    "--cov-report=term-missing",
    "--cov-fail-under=80"
]
```

### Dependências de Teste

```
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
```

## 📝 Escrevendo Novos Testes

### 1. Testes Unitários

```python
import unittest
from unittest.mock import patch, Mock
from app.services.example_service import ExampleService

class TestExampleService(unittest.TestCase):
    
    def setUp(self):
        """Configurar fixtures para cada teste"""
        self.service = ExampleService()
    
    def test_method_success(self):
        """Testar método com sucesso"""
        result = self.service.method()
        self.assertEqual(result, expected_value)
    
    def test_method_with_mock(self):
        """Testar método com mock"""
        with patch('app.services.example_service.dependency') as mock_dep:
            mock_dep.return_value = mock_value
            result = self.service.method()
            self.assertEqual(result, expected_value)
```

### 2. Testes de Integração

```python
import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAPIIntegration(unittest.TestCase):
    
    def setUp(self):
        """Configurar client de teste"""
        self.client = TestClient(app)
    
    def test_endpoint_success(self):
        """Testar endpoint com sucesso"""
        response = self.client.get("/endpoint")
        self.assertEqual(response.status_code, 200)
        self.assertIn("expected_key", response.json())
```

## 🎯 Melhores Práticas

### 1. Nomenclatura
- Arquivos de teste: `test_*.py`
- Classes de teste: `Test*`
- Métodos de teste: `test_*`

### 2. Organização
- Um arquivo de teste por módulo
- Agrupar testes relacionados em classes
- Usar `setUp()` para configuração comum

### 3. Asserções
- Usar asserções específicas (`assertEqual`, `assertIn`, etc.)
- Incluir mensagens descritivas quando necessário
- Testar tanto casos de sucesso quanto de falha

### 4. Mocks
- Usar mocks para dependências externas
- Isolar o código sendo testado
- Verificar chamadas de mock quando apropriado

### 5. Dados de Teste
- Usar fixtures para dados de teste
- Manter dados de teste no diretório `fixtures/`
- Reutilizar dados entre testes quando possível

## 🔍 Debugging de Testes

### Executar Teste Específico

```powershell
# Executar apenas um arquivo de teste
python -m pytest tests/unit/test_parsers/test_header_parser.py -v

# Executar apenas uma classe de teste
python -m pytest tests/unit/test_parsers/test_header_parser.py::TestHeaderParser -v

# Executar apenas um método de teste
python -m pytest tests/unit/test_parsers/test_header_parser.py::TestHeaderParser::test_parse_returns_dict -v
```

### Saída Detalhada

```powershell
# Saída muito verbose
python -m pytest tests/ -vv

# Mostrar stdout
python -m pytest tests/ -s

# Mostrar traceback completo
python -m pytest tests/ --tb=long
```

## 📈 Métricas de Qualidade

### Cobertura de Código
- **Meta**: Mínimo 80% de cobertura
- **Atual**: Relatório disponível em `tests/coverage/html/index.html`

### Tipos de Teste
- **Testes Unitários**: Testam componentes individuais
- **Testes de Integração**: Testam interação entre componentes
- **Testes de API**: Testam endpoints da API
- **Testes do Azure**: Testam integração com Azure Document Intelligence

## 🚨 Solução de Problemas

### Problemas Comuns

1. **Testes falhando por dependências**
   ```powershell
   pip install -r requirements.txt
   pip install pytest pytest-asyncio pytest-cov pytest-mock
   ```

2. **Erro de import**
   - Verificar se o PYTHONPATH está configurado corretamente
   - Verificar se os arquivos `__init__.py` estão presentes

3. **Testes lentos**
   - Usar `-m "not slow"` para pular testes lentos
   - Usar `--fast` nos scripts personalizados

4. **Problemas de cobertura**
   - Verificar se todos os arquivos estão sendo incluídos
   - Usar `--cov-report=term-missing` para ver linhas não cobertas

## 🔄 Integração Contínua

O sistema de testes está preparado para integração com CI/CD:

```yaml
# Exemplo para GitHub Actions
- name: Run Tests
  run: |
    python -m pytest tests/ --cov=app --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./tests/coverage/coverage.xml
```

## 📚 Recursos Adicionais

- [Documentação do pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Desenvolvido com ❤️ pela equipe SmartQuest**

*Sistema de testes implementado seguindo padrões de qualidade similares aos utilizados em C# e outras linguagens enterprise.*
