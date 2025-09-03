#<!--
# Autor: GPT
# Resumo: Análise das interdependências do `context_block`, verificação dos modelos Pydantic existentes,
# diagrama de dependências e estratégia de migração recomendada.
# -->

# Migração Pydantic: context_block  (GPT)
## Objetivo

Gerar uma análise completa das interdependências do `context_block`, validar a existência e aderência
do(s) modelo(s) Pydantic existente(s) e propor uma estratégia de migração segura e mensurável.


- [x] Ler documentos de `docs` e identificar artefatos relevantes (copilot_instructions.md, smartquest_architecture_guide.md)
- [x] Criar diagrama de interdependências
- [x] Salvar análise em `docs/pydantic_migration_context_block_Gemini.md` (este arquivo)
- [ ] Executar testes automatizados e endpoint principal com parâmetros indicados (recomendado como próximo passo manual/CI)

> Observação: as ações que alteram o sistema em runtime (por exemplo chamar endpoints externos) não foram executadas aqui — este arquivo documenta as descobertas e recomendações. Instruções de execução são fornecidas na seção "Como testar".

## Achados principais (resumo técnico)

- Existe um modelo interno completo: `InternalContextBlock` definido em `app/models/internal/context_models.py`.
  - Campos principais: `id`, `type: List[ContentType]`, `content: InternalContextContent`, `title`, `statement`,
    `images`, `associated_images`, `has_image`, `extraction_method`, `confidence_score`, `related_questions`, `sub_contexts`.
  - Métodos úteis: `from_legacy_context_block`, `to_legacy_format`, `add_image_association`, etc.
- Existe DTO para resposta de API: `ContextBlockDTO` em `app/dtos/responses/context_dtos.py` (e equivalentes em `app/dtos/api/context_dtos.py`).
  - Conversão disponível: `ContextBlockDTO.from_internal_context(internal_context)` — converte `InternalContextBlock` em DTO.
- Fluxo de orquestração principal: `app/services/analyze_service.py` usa `QuestionParser`, `RefactoredContextBlockBuilder` e garante conversão para Pydantic via `_ensure_pydantic_context_blocks`.
- Há suporte a duas vias: builders/refactored para retornar objetos Pydantic nativos (`parse_to_pydantic` em `RefactoredContextBlockBuilder`) e métodos legados que retornam Dicts — o serviço converte Dicts para `InternalContextBlock` quando necessário.

## Diagrama de interdependências (Mermaid)

```mermaid
flowchart TD
  A[Arquivo PDF / Texto] --> B[Extrator / AzureResponseService]
  B --> C[AnalyzeService]
  C --> D[QuestionParser]
  D --> H[ContextQuestionMapper]
  F --> I[InternalContextBlock]
  I --> J[ContextBlockDTO.from_internal_context]
<!--
Autor: GPT
Resumo: Re-análise focada nos fluxos de endpoint que impactam o `context_block`, com detalhes de comportamento,
contratos e recomendações práticas para migrar para um fluxo 100% Pydantic.
-->

# Migração Pydantic: context_block (GPT) — Análise focada em endpoints

Data: 2025-09-03

## Resumo rápido

Esta revisão reavalia o processamento do `context_block` a partir dos *endpoints* expostos pela API
e detalha o fluxo real de execução, pontos de atenção para a migração e ações concretas. Endpoints
avaliados: `/analyze_document`, `/analyze_document_with_figures`, `/analyze_document_mock`.

## Checklist objetivo

- [x] Mapear handlers dos endpoints e o fluxo de chamada entre controller -> services -> builders
- [x] Identificar pontos onde dicts e Pydantic conflitam (conversões, adapters, serialização)
- [x] Propor passos de migração por endpoint, testes e métricas a adicionar
- [ ] Implementar testes e executar cenário mock (posso executar quando autorizado)

## Fluxo geral observado (controller -> serviço -> dto)

- Controller: `app/api/controllers/analyze.py` — valida entrada, chama `DocumentExtractionService` e em seguida `AnalyzeService.process_document_with_models` (ou `process_document_with_models_mock` / orchestrator para figures).
- Extraction: `DocumentExtractionService.get_extraction_data(file, email)` — retorna `extracted_data` (pode vir do cache ou Azure conversion).
- AnalyzeService: `process_document_with_models` — realiza:
   - extração/ fallback de imagens (_extract_images_with_fallback),
   - categorização de imagens (ImageCategorizationService),
   - header parsing (HeaderParser.parse_to_pydantic),
   - question parsing (QuestionParser.extract),
   - tentativa de `RefactoredContextBlockBuilder.parse_to_pydantic(azure_result, image_data)` (PHASE 2),
   - fallback para `build_context_blocks_from_azure_figures` (legacy dicts) e conversão via `InternalContextBlock.from_legacy_context_block`.
- Adapter: `DocumentResponseAdapter.to_api_response(internal_response)` — converte `InternalDocumentResponse` para o formato que a API expõe (hoje normalmente um dict JSON).

Importante: o fluxo central já tenta produzir objetos Pydantic (PHASE 2). O problema prático é o ponto entre os builders e o adapter: dados podem voltar a dicts ou perder sub-estruturas (por exemplo `sub_contexts`, `images`) na serialização final se o adapter fizer transformações inadequadas.

## Endpoint por endpoint — fluxo, riscos e recomendações

1) /analyze_document (produção, tipado híbrido)
    - Handler: valida entrada (AnalyzeValidator), chama DocumentExtractionService e depois AnalyzeService.process_document_with_models(..., use_refactored=True).
    - Resultado: `InternalDocumentResponse` (Pydantic) é passado para `DocumentResponseAdapter.to_api_response` e retornado.
    - Riscos atuais:
       - Adapter pode reformatar os campos (por exemplo renomear `has_image`/`hasImage` ou substituir `sub_contexts` por lista de dicts sem schema).
       - Fluxos legacy ainda podem retornar dicts de context blocks; AnalyzeService usa `_ensure_pydantic_context_blocks` para mitigar, mas é necessário validar o JSON final.
    - Recomendações práticas:
       - Preferir usar `response_model=InternalDocumentResponse` no decorator do router (FastAPI cuidará da serialização Pydantic).
       - Refatorar `DocumentResponseAdapter` para ser um *thin adapter* que apenas seleciona/exclui campos sensíveis e retorna o objeto Pydantic (ou um Pydantic DTO) em vez de um dict.
       - Adicionar teste de contrato que chama o endpoint e valida que `context_blocks[].sub_contexts` existe e `image_ids` preservadas.

2) /analyze_document_with_figures (fluxo especializado, comparação de métodos)
    - Handler: aceita flags `extraction_method`, `compare_methods`, cria `DocumentProcessingOrchestrator` que executa `process_document_with_figures()`.
    - Característica: fluxo legado com lógica mais complexa e sem fallback automático consolidado; tende a retornar estruturas tipo dict para facilitar comparação.
    - Riscos:
       - Maior chance de formatos inconsistentes entre saídas quando comparar métodos; perdão de tipos (dict vs Pydantic).
    - Recomendações:
       - Implementar uma camada de normalização que converta resultados do orchestrator para `InternalDocumentResponse` (ou `List[InternalContextBlock]`) usando `InternalContextBlock.from_legacy_context_block`.
       - Se a comparação exigir saída detalhada, retornar um DTO específico com campos `method_a` e `method_b`, cada um tipado (DTO) para evitar ambiguidade.

3) /analyze_document_mock (mock, test/dev)
    - Handler: chama `AnalyzeService.process_document_with_models_mock` que monta `InternalDocumentResponse` a partir do último Azure response salvo.
    - Característica: já retorna Pydantic internamente no mock path; porém o adapter ainda pode transformar para dict.
    - Recomendações:
       - Garantir que o mock path também seja coberto por os mesmos testes de contrato (mesmos asserts para `context_blocks`).
       - Remover diferenças entre mock e produção: ambos devem retornar o mesmo shape JSON para `context_blocks`.

## Contratos e campos críticos a validar

- Interno (InternalContextBlock): id (int), type (List[ContentType] / str), content.description (List[str]), sub_contexts (Optional[List[InternalSubContext]]), associated_images/image_ids (List[str]), related_questions (List[int]), has_image (bool).
- DTO/API (ContextBlockDTO): id, type (List[str]), content.description, title, statement, has_image, image_ids, related_question_ids.

Regras de compatibilidade:
- Sempre mapear `InternalContextBlock.sub_contexts` para DTO `ContextContentDTO`/`ContextBlockDTO` sem perda de estrutura.
- Normalizar nomes (`associated_images` -> `image_ids`) no adapter de forma consistente.

## Testes sugeridos (automáticos)

- Unit: test_InternalContextBlock_from_legacy_roundtrip: criar legacy dict com sub_contexts/images e validar `from_legacy_context_block` e `to_legacy_format`.
- Integration: test_analyze_document_contract: usar TestClient no app, enviar PDF mock e validar o JSON retornado contém `context_blocks` com `sub_contexts` e `image_ids` (email = wander.bergami@gmail.com, use latest file in tests/documents).
- End-to-end: rodar `start_simple.py --use-mock` e validar uma chamada HTTP a `/analyze_document` com arquivo real, comparar shape.

## Observabilidade e métricas práticas a adicionar

- Contador por endpoint: total requests, success, fallback_used (quando parse_to_pydantic falha e legacy é usado).
- Métrica por contexto: context_blocks_count, context_blocks_with_images_count.
- Tempo de execução por fase: extraction_time, parse_time, images_extraction_time.

## Migração incremental recomendada (pragmática)

1. Garantir que `RefactoredContextBlockBuilder.parse_to_pydantic` esteja 100% coberto por testes unitários.
2. Atualizar `AnalyzeService._ensure_pydantic_context_blocks` para logar quando fizer conversão de dict->Pydantic e falhas de validação.
3. Alterar `app/api/controllers/analyze.py` para usar `response_model=...` em `/analyze_document` e retornar diretamente o Pydantic DTO (ou `InternalDocumentResponse`) após adaptar minimalmente.
4. Normalizar `DocumentResponseAdapter` para retornar Pydantic DTOs apenas (ou ser removido depois de adaptar clients).
5. Executar testes de contrato para `/analyze_document`, `/analyze_document_with_figures` e `/analyze_document_mock` em um pipeline de CI.

## Edge cases e observações finais

- Arquivos PDF com muitas figuras (alto número de imagens) podem acionar fallback different extractors; garantir que `associated_images` seja consistente.
- Campos opcionais (confidence_score, processing_notes) não devem ser removidos na serialização final, apenas documentados.
- Ao migrar, preferir manter compatibilidade com clientes removendo campos apenas em major releases.

---

Status: esta análise substitui e aprofunda o documento anterior; se aprovar, prossigo com:
- implementação de testes de integração e execução local do cenário mock (posso rodar aqui);
- ou abrir PR com as mudanças sugeridas no adapter/controller.
