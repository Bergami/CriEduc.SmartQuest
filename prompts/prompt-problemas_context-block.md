# Prompt de Engenharia de Software para o Modelo Sonnet - Projeto SmartQuest

## 1. Objetivo Principal

Corrigir uma regressão crítica no serviço `AnalyzeService` onde os `sub_contexts` (contextos aninhados, como "TEXTO I", "TEXTO II") deixaram de ser gerados para os `context_blocks` após uma refatoração focada na migração do `HeaderParser` para Pydantic. A solução deve restaurar a funcionalidade de `sub_contexts` e, ao mesmo tempo, avançar na migração para Pydantic.

## 2. Contexto do Projeto e Análise do Problema

O SmartQuest está em um processo de migração de um fluxo baseado em dicionários Python (`Dict`) para um fluxo totalmente tipado com Pydantic. O endpoint principal, `/analyze/document`, utiliza o método `AnalyzeService.process_document_with_models`, que orquestra essa lógica.

**Análise da Causa Raiz:**

A análise dos arquivos e do fluxo de execução revela a causa do problema:

1.  **Refatoração do Header:** A migração do `HeaderParser` para Pydantic foi bem-sucedida. O `AnalyzeService` agora usa `HeaderParser.parse_to_pydantic`, que retorna um modelo `InternalDocumentMetadata`. Isso eliminou a necessidade de conversões intermediárias para o cabeçalho.
2.  **Impacto Não Intencional:** Durante essa refatoração, a chamada para o `RefactoredContextBlockBuilder`, responsável por criar os `context_blocks` avançados (incluindo `sub_contexts`), foi alterada. O método `analyze_azure_figures_dynamically` agora recebe uma lista de `InternalImageData`, que são os modelos Pydantic puros das imagens.
3.  **O Elo Perdido:** O `RefactoredContextBlockBuilder` foi projetado para trabalhar com a resposta bruta do Azure (`azure_response`), que contém a estrutura de `figures` com metadados essenciais como `spans` e `elements`. O modelo `InternalImageData` não contém essa estrutura bruta do Azure.
4.  **Falha na Conversão:** O método `_convert_internal_images_to_figure_info` dentro do `RefactoredContextBlockBuilder` tenta converter `InternalImageData` para `FigureInfo`, mas o campo crucial `azure_figure` fica como `None`, pois a informação original do Azure não está mais disponível nesse ponto do fluxo.
5.  **Consequência:** Sem os dados brutos do Azure, o `RefactoredContextBlockBuilder` não consegue realizar a análise espacial e de conteúdo necessária para agrupar figuras em sequências (TEXTO I, II, III) e, consequentemente, não cria os `sub_contexts`. Ele retorna apenas `context_blocks` de texto simples, causando a regressão.

## 3. Instruções Detalhadas para Correção (Passo a Passo)

Execute as seguintes alterações de forma precisa e na ordem especificada.

### Passo 1: Traduzir Métodos em `RefactoredContextBlockBuilder`

Primeiro, vamos melhorar a manutenibilidade traduzindo os nomes de métodos de português para inglês no arquivo `app/services/refactored_context_builder.py`.

**Arquivo a ser modificado:** `app/services/refactored_context_builder.py`

**Traduções:**

1.  `analyze_azure_figures_dynamically` -> `build_context_blocks_from_azure_figures`
2. `remove_associated_figures_from_result` -> `remove_figure_association_fields`

**Ação:** Aplique as traduções acima. Onde o nome já está em inglês, apenas confirme. Após renomear, atualize os locais onde esses métodos são chamados dentro da própria classe `RefactoredContextBlockBuilder`.

### Passo 2: Corrigir o Fluxo de Dados para o `RefactoredContextBlockBuilder`

Esta é a correção principal. Vamos garantir que a resposta completa do Azure seja passada para o builder.

**Arquivo a ser modificado:** `app/services/analyze_service.py`

**Lógica:**

1.  Localize o método `process_document_with_models`.
2.  Dentro do bloco `if use_refactored:`, encontre a chamada para `context_builder.analyze_azure_figures_dynamically`.
3.  Modifique a assinatura do método no `RefactoredContextBlockBuilder` e a chamada no `AnalyzeService` para passar o `azure_result` completo.

**Alteração em `app/services/refactored_context_builder.py`:**

Modifique a assinatura do método `analyze_azure_figures_dynamically` (que agora se chama `build_context_blocks_from_azure_figures`) para remover o parâmetro `images` e usar apenas `azure_response`. O método `_extract_figures_with_enhanced_info` já extrai as figuras da resposta do Azure, tornando o parâmetro `images` redundante e problemático.

````python
// filepath: app/services/refactored_context_builder.py
// ...existing code...
class RefactoredContextBlockBuilder:
// ...existing code...
    def build_context_blocks_from_azure_figures(
        self,
        azure_response: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Builds context blocks from Azure figures dynamically without hardcoding.
        
        Args:
            azure_response: The full response from Azure Document Intelligence.
            
        Returns:
            A list of structured context blocks.
        """
        try:
            logger.info("🔧 DYNAMIC FIGURE ANALYSIS - Starting")

            # 1. Extract figures directly from the Azure response.
            figures = self._extract_figures_with_enhanced_info(azure_response)
            logger.info(f"📊 Extracted {len(figures)} figures from Azure response")

            # 2. Extract relevant text spans.
            text_spans = self._extract_relevant_text_spans(azure_response)
// ...existing code...
// ...existing code...
    def remove_figure_association_fields(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Removes unnecessary 'associated_figures' and 'figure_ids' fields from the API result."""
// ...existing code...

Passo 3: Garantir a Conversão para Pydantic
O RefactoredContextBlockBuilder retorna uma lista de dicionários. Precisamos garantir que eles sejam convertidos para InternalContextBlock antes de serem atribuídos ao InternalDocumentResponse, que espera modelos Pydantic.

Arquivo a ser modificado: analyze_service.py

Ação: Dentro do if enhanced_context_blocks:, adicione a conversão usando o método de classe from_legacy_context_block, que já deve existir no modelo InternalContextBlock. Além disso, remova a conversão que estava sendo feita na instanciação do InternalDocumentResponse para context_blocks, pois os dados já estarão no formato correto.

(Esta alteração já foi incluída no snippet do Passo 2 para garantir a atomicidade da correção).

4. Verificação e Validação
Após aplicar as alterações:

Execute os Testes Unitários: Rode a suíte de testes para garantir que nenhuma funcionalidade existente foi quebrada, especialmente os testes relacionados a AnalyzeService e RefactoredContextBlockBuilder.
Teste Manualmente: Use o endpoint /analyze_document com um documento PDF que contenha múltiplos textos (TEXTO I, TEXTO II, etc.) e imagens. Verifique se a resposta JSON agora contém a estrutura context_blocks com sub_contexts devidamente preenchidos.
Revise o Código: Certifique-se de que as alterações seguem os padrões de nomenclatura e estilo do projeto.
Ao seguir estas instruções detalhadas, você corrigirá a regressão, melhorará a qualidade do código e dará um passo importante na migração para Pydantic, tudo de forma segura e alinhada com a arquitetura do sistema.