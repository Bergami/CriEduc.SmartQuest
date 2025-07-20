# 🛠️ Scripts de Debug e Desenvolvimento

Esta pasta contém scripts de desenvolvimento e debug que foram criados durante o processo de implementação da funcionalidade de extração de figuras dos PDFs usando Azure Document Intelligence.

## 📁 Estrutura Organizada

### 🎯 **azure_figure_extraction/** 
Scripts para testar extração de figuras específicas dos PDFs

- **`test_azure_image_extraction.py`**
  - Testa extração com fator de escala 72 pontos
  - Foca na figura 2.1 da página 2
  - Versão básica sem logging detalhado

- **`test_azure_image_extraction_detailed.py`**
  - Versão com logging detalhado do script anterior
  - Mesma funcionalidade, mais informações de debug

- **`test_image_extraction.py`**
  - Teste de extração genérica de figuras
  - Testa compatibilidade entre índices Azure e PyMuPDF
  - Função `extract_specific_figure()` para debugging

- **`test_extract_page2_figure.py`**
  - Foco específico na figura da página 2
  - Análise de coordenadas normalizadas vs absolutas
  - Testes com diferentes escalas de coordenadas

### 🎯 **parser_analysis/** 🆕
Scripts para depuração de parsers de texto e questões

- **`debug_question_detection.py`**
  - Testa detecção e parsing de questões
  - Analisa regex de identificação (`QUESTÃO 01`, etc.)
  - Debug de extração de alternativas (A), (B), (C)
  - Útil para problemas de parsing de questões

- **`debug_image_detection.py`**
  - Testa detecção de referências a imagens no texto
  - Analisa como o QuestionParser processa "Analise a imagem"
  - Debug de casos onde imagens não são detectadas
  - Ferramenta para entender fluxo de detecção

- **`debug_api_check.py`**
  - Verifica API do Azure Document Intelligence
  - Inspeciona parâmetros disponíveis
  - Ferramenta para debugging de conectividade

### 🎯 **figure_enumeration/**
Scripts para processar todas as figuras detectadas em lote

- **`test_enumerate_azure_figures.py`**
  - Enumera todas as figuras do arquivo `RetornoProcessamento.json`
  - Extrai cada figura individualmente para verificação
  - Usa o arquivo JSON mais antigo

- **`test_enumerate_azure_figures_3tri.py`**
  - Versão para arquivo `azure_response_3Tri_20250716_215103.json`
  - Processa múltiplos PDFs disponíveis
  - Mais robusto e atualizado

### 🎯 **data_validation/**
Scripts para verificar integridade dos dados durante o processo

- **`test_base64_cycle.py`**
  - Testa ciclo completo: extração → base64 → reconstrução
  - Verifica se há perda de dados no processo
  - Comparação de checksums e tamanhos

- **`test_image_bytes_comparison.py`**
  - Compara byte[] gerado pelo método vs imagem salva
  - Validação de integridade dos dados
  - Verificação de corrupção de dados

### 🎯 **analysis_tools/**
Ferramentas de análise mais complexas e completas

- **`analyze_azure_figures_3tri.py`**
  - Análise completa das figuras do documento
  - Extração com múltiplas escalas automaticamente
  - Gera relatório detalhado em Markdown
  - Salva metadados, imagens e contexto textual

## 🚀 Como Usar

### Scripts Individuais
Cada script pode ser executado individualmente:

```powershell
# Executar script específico
cd "d:\Git\CriEduc.SmartQuest\tests\debug_scripts\azure_figure_extraction"
python test_azure_image_extraction.py

# Executar análise completa
cd "d:\Git\CriEduc.SmartQuest\tests\debug_scripts\analysis_tools"
python analyze_azure_figures_3tri.py
```

### Organização por Contexto
- **Durante desenvolvimento**: Use scripts de `azure_figure_extraction/`
- **Para processar múltiplas figuras**: Use `figure_enumeration/`
- **Para verificar integridade**: Use `data_validation/`
- **Para análise completa**: Use `analysis_tools/`

## 📝 Diferença dos Testes Reais

**⚠️ Importante**: Estes scripts **NÃO são testes unitários** no sentido tradicional. Eles são:

- **Scripts de desenvolvimento** para testar funcionalidades específicas
- **Ferramentas de debug** para resolver problemas de extração
- **Utilitários de análise** para verificar resultados

Os **testes reais** estão em:
- `tests/unit/` - Testes unitários com pytest
- `tests/integration/` - Testes de integração com pytest

## 🔧 Dependências

Todos os scripts dependem de:
- `PyMuPDF` (fitz) para manipulação de PDF
- `PIL` (Pillow) para processamento de imagens
- `PDFImageExtractor` do sistema principal
- Arquivos JSON de resposta do Azure Document Intelligence

## 📚 Histórico

Estes scripts foram criados durante o desenvolvimento para:
1. Entender o formato das coordenadas do Azure Document Intelligence
2. Resolver problemas de escala entre diferentes sistemas de coordenadas
3. Verificar a integridade dos dados durante extração
4. Validar resultados visualmente
5. Debugar problemas específicos de figuras

## 🎯 Quando Usar

- **Desenvolvimento**: Quando implementando novas funcionalidades
- **Debug**: Quando há problemas com extração de figuras
- **Análise**: Quando precisa analisar resultados detalhadamente
- **Verificação**: Quando quer validar integridade dos dados

---

**Nota**: Para testes automatizados e CI/CD, use os testes em `tests/unit/` e `tests/integration/`.
