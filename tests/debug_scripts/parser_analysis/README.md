# 🔍 Parser Analysis Tools

Esta pasta contém ferramentas de análise e depuração específicas para os parsers do SmartQuest.

## 📂 **Arquivos Disponíveis**

### 🖼️ **debug_image_detection.py**
**Propósito**: Ferramenta para depurar a detecção de imagens no sistema QuestionParser.

**Como usar:**
```bash
cd tests/debug_scripts/parser_analysis/
python debug_image_detection.py
```

**O que faz:**
- Testa a extração de questões com referências a imagens
- Mostra como o sistema processa texto com "Analise a imagem"
- Útil para entender problemas na detecção de imagens

### ❓ **debug_question_detection.py**  
**Propósito**: Ferramenta para depurar a detecção e parsing de questões.

**Como usar:**
```bash
cd tests/debug_scripts/parser_analysis/
python debug_question_detection.py
```

**O que faz:**
- Testa regex de detecção de questões (`QUESTÃO 01`, etc.)
- Mostra como o texto é dividido em blocos
- Analisa extração de alternativas (A), (B), (C), etc.
- Útil para debugging de parsing de questões

### 🌐 **debug_api_check.py**
**Propósito**: Ferramenta para verificar se a API está funcionando corretamente.

**Como usar:**
```bash
cd tests/debug_scripts/parser_analysis/
python debug_api_check.py
```

**O que faz:**
- Verifica se a API está respondendo
- Testa endpoints básicos
- Útil para debugging de conectividade

## 🎯 **Quando Usar Essas Ferramentas**

### **Durante Desenvolvimento:**
- Implementando novos parsers
- Modificando regex de detecção
- Debugging de casos específicos

### **Durante Debugging:**
- Questões não sendo detectadas corretamente
- Problemas com detecção de imagens
- Casos edge que não passam nos testes

### **Durante Manutenção:**
- Verificar comportamento após mudanças
- Validar novos formatos de documento
- Investigar bugs reportados

## 🔧 **Estrutura dos Scripts**

Todos os scripts seguem o padrão:
```python
#!/usr/bin/env python3
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import necessário
from app.module.function import target_function

def debug_function():
    # Código de debug específico
    pass

if __name__ == "__main__":
    debug_function()
```

## 📊 **Relação com Testes**

Estes scripts são **complementares** aos testes unitários:

| Testes Unitários | Scripts Debug |
|------------------|---------------|
| ✅ Verificam comportamento esperado | 🔍 Investigam comportamento atual |
| ✅ Validam casos conhecidos | 🔍 Exploram casos desconhecidos |
| ✅ Automáticos e rápidos | 🔍 Interativos e detalhados |
| ✅ Pass/Fail binário | 🔍 Output detalhado para análise |

## 🚀 **Melhores Práticas**

1. **Execute antes de criar testes**: Use para entender o comportamento
2. **Documente descobertas**: Anote problemas encontrados
3. **Transforme em testes**: Casos interessantes viram testes unitários
4. **Mantenha atualizados**: Atualize scripts quando mudar o código

---

**📝 Criado**: 19/07/2025  
**🎯 Propósito**: Ferramentas de análise para desenvolvimento e debugging
