# 🧪 Debug Scripts

Esta pasta contém scripts de debug organizados por categoria. **Estes arquivos não são enviados para o repositório** (incluídos no .gitignore).

## 📁 Estrutura

```
tests/debug/
├── azure_checks/           # Scripts para verificar configurações do Azure
│   ├── check_azure_version.py      # Verifica versão exata do Azure sendo usada
│   └── check_azure_paragraphs.py   # Verifica parágrafos extraídos do Azure
│
├── context_analysis/       # Scripts para análise de blocos de contexto
│   ├── debug_context_block_3.py    # Analisa context_block específico (ID=3)
│   ├── debug_all_context_blocks.py # Analisa todos os context blocks
│   ├── debug_sub_contexts.py       # Analisa sub-contextos
│   └── analyze_paragraph_context.py # Analisa contexto de parágrafos
│
├── figure_analysis/        # Scripts para análise de figuras
│   ├── debug_figure_association.py # Debug associação de figuras com texto
│   └── debug_missing_figures.py    # Debug de figuras faltantes
│
├── image_analysis/         # Scripts para análise de qualidade de imagens
│   └── analyze_image_quality.py    # Compara qualidade entre métodos de extração
│
└── debug_orchestrator_direct.py   # Debug direto do orchestrator
```

## 🎯 Propósito

Estes scripts são ferramentas de desenvolvimento para:
- **Depuração**: Identificar problemas específicos nos algoritmos
- **Análise**: Comparar diferentes métodos de processamento
- **Validação**: Verificar configurações e resultados intermediários
- **Desenvolvimento**: Testar mudanças antes da implementação

## 🚫 Nota Importante

**Estes arquivos não são enviados para o repositório** para manter o projeto limpo e focado apenas no código de produção. Eles são úteis durante o desenvolvimento mas não fazem parte da aplicação final.

## 🔧 Como Usar

1. Execute os scripts diretamente do VS Code ou terminal
2. Certifique-se de que o ambiente virtual está ativado
3. Os scripts assumem que você está na raiz do projeto

Exemplo:
```bash
# Ativar ambiente virtual
.\.venv\Scripts\activate

# Executar script de debug
python tests/debug/azure_checks/check_azure_version.py
```

## 📝 Documentação dos Scripts

### Azure Checks
- **check_azure_version.py**: Verifica configurações exatas do Azure Document Intelligence
- **check_azure_paragraphs.py**: Analisa estrutura de parágrafos extraídos

### Context Analysis  
- **debug_context_block_3.py**: Análise específica de um block de contexto
- **debug_all_context_blocks.py**: Análise abrangente de todos os blocks
- **debug_sub_contexts.py**: Análise de sub-contextos dentro dos blocks
- **analyze_paragraph_context.py**: Análise de contexto baseada em parágrafos

### Figure Analysis
- **debug_figure_association.py**: Debug da associação entre figuras e texto
- **debug_missing_figures.py**: Identifica figuras que não foram extraídas corretamente

### Image Analysis
- **analyze_image_quality.py**: Compara dimensões, tamanhos e qualidade entre métodos de extração

### Orchestrator
- **debug_orchestrator_direct.py**: Debug direto do orchestrator de processamento

---

💡 **Dica**: Se um script for considerado essencial para produção, ele deve ser movido para `tests/unit/` ou `tests/integration/` com testes apropriados.
