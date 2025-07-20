# 🚀 Guia Rápido - Testes SmartQuest

## ⚡ **TL;DR - Comandos Essenciais**

```bash
# 🎯 Comando principal (recomendado)
python run_tests.py --coverage

# 🔍 Verificar testes específicos
python -m pytest tests/unit/test_parsers/ -v

# 📊 Relatório HTML de cobertura
python -m pytest --cov=app --cov-report=html
```

## 📋 **Checklist para Novos Desenvolvedores**

### ✅ **Setup Inicial**
- [ ] Instalar dependências: `pip install -r requirements.txt`
- [ ] Configurar ambiente: Copiar `.env.example` para `.env`
- [ ] Executar testes: `python run_tests.py --coverage`
- [ ] Verificar se 119 testes passam ✅

### ✅ **Adicionando Novos Testes**

#### **1. Convenção de Nomes**
```
✅ CORRETO: tests/unit/test_module/test_function.py
❌ ERRADO:  tests/unit/test_module/function.py
```

#### **2. Estrutura de Teste Unitário**
```python
import unittest
from app.module.function import target_function

class TestTargetFunction(unittest.TestCase):
    def test_valid_case(self):
        """Testa caso válido - descreve o que testa"""
        # Arrange
        input_data = "dados de entrada"
        expected = "resultado esperado"
        
        # Act
        result = target_function(input_data)
        
        # Assert
        self.assertEqual(result, expected)
    
    def test_invalid_case(self):
        """Testa caso inválido - None, vazio, etc."""
        self.assertIsNone(target_function(None))
        self.assertIsNone(target_function(""))

if __name__ == "__main__":
    unittest.main()
```

#### **3. Para 100% de Cobertura**
Teste todos os caminhos:
- ✅ **Entradas válidas**
- ✅ **Entradas inválidas** (None, vazio, formato incorreto)
- ✅ **Condições if/else**
- ✅ **Tratamento de exceções**
- ✅ **Valores de retorno** (return, return None)

## 🎯 **Exemplos Práticos**

### **Exemplo 1: Função Simples**
```python
# app/utils/formatter.py
def format_name(name: str) -> str:
    if not name:
        return None
    return name.strip().title()

# tests/unit/test_utils/test_formatter.py
class TestFormatName(unittest.TestCase):
    def test_valid_name(self):
        self.assertEqual(format_name("joão silva"), "João Silva")
    
    def test_empty_name(self):
        self.assertIsNone(format_name(""))
        self.assertIsNone(format_name(None))
        
    def test_whitespace_handling(self):
        self.assertEqual(format_name("  ana  "), "Ana")
```

### **Exemplo 2: Função com Regex**
```python
# app/parsers/parse_grade.py  
def parse_grade(text: str) -> Optional[float]:
    if not text:
        return None
    match = re.search(r"Nota:\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    return float(match.group(1))

# tests/unit/test_parsers/test_parse_grade.py
class TestParseGrade(unittest.TestCase):
    def test_valid_grade(self):
        self.assertEqual(parse_grade("Nota: 8.5"), 8.5)
        
    def test_no_match(self):
        self.assertIsNone(parse_grade("Sem nota aqui"))
        
    def test_empty_input(self):
        self.assertIsNone(parse_grade(""))
        self.assertIsNone(parse_grade(None))
```

## 📊 **Verificando Cobertura**

### **Comando para Arquivo Específico**
```bash
# Verificar cobertura de um arquivo específico
python -m pytest tests/unit/test_utils/test_formatter.py \
  --cov=app.utils.formatter \
  --cov-report=term-missing
```

### **Lendo o Relatório**
```
Name                    Stmts   Miss Branch BrPart   Cover   Missing
--------------------------------------------------------------------
app/utils/formatter.py      5      0      2      0  100.00%
--------------------------------------------------------------------
TOTAL                       5      0      2      0  100.00%
```

- **Stmts**: Linhas de código
- **Miss**: Linhas não cobertas  
- **Branch**: Condições (if/else)
- **Cover**: Porcentagem de cobertura
- **Missing**: Linhas específicas não cobertas

## 🚨 **Problemas Comuns**

### **1. Teste não descoberto**
```bash
# ❌ Problema: Nome não segue convenção
tests/unit/parse_student.py

# ✅ Solução: Renomear para
tests/unit/test_parse_student.py
```

### **2. Import não funciona**
```python
# ❌ Problema: Path incorreto
from parse_student import parse_student

# ✅ Solução: Path absoluto
from app.parsers.header_parser.parse_student import parse_student
```

### **3. Cobertura baixa**
```bash
# 🔍 Ver linhas não cobertas
python -m pytest --cov=app.module --cov-report=term-missing

# 📊 Ver relatório HTML detalhado
python -m pytest --cov=app --cov-report=html
# Abrir: tests/coverage/html/index.html
```

## 🏆 **Metas de Qualidade**

| Métrica | Mínimo | Bom | Excelente |
|---------|--------|-----|-----------|
| **Cobertura** | 80% | 90% | 95%+ |
| **Testes Passando** | 100% | 100% | 100% |
| **Tempo de Execução** | < 5s | < 3s | < 2s |

## 📚 **Recursos Úteis**

- **Documentação completa**: [`tests/TEST_IMPROVEMENTS.md`](tests/TEST_IMPROVEMENTS.md)
- **Configuração cobertura**: [`tests/COVERAGE_CONFIGURATION.md`](tests/COVERAGE_CONFIGURATION.md)
- **Pytest docs**: https://docs.pytest.org/
- **Coverage.py docs**: https://coverage.readthedocs.io/

---

**💡 Dica**: Execute `python run_tests.py --coverage` após cada mudança para garantir que nenhum teste quebrou!
