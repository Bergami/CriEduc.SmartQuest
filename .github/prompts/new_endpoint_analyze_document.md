# Prompt para Implementação de Novo Endpoint

## Detalhes do Endpoint

- **Tipo**: GET
- **Rota**: `/analyze/analyze_document/{id}`
- **Parâmetro**: `id` (ID do Documento)

## Objetivo

O endpoint deve permitir que os usuários recuperem informações sobre um documento que já foi processado e armazenado na coleção `analyze_documents`.

## Comportamento Esperado

1. Consultar a coleção `analyze_documents` no banco de dados MongoDB usando o parâmetro `id` fornecido.
2. Se um documento com o `id` fornecido existir, retornar seus detalhes na resposta.
3. Se nenhum documento for encontrado, retornar o status `404 Not Found`.

### Exemplo de Consulta

```javascript
// Banco de dados atual a ser usado.
use("smartquest");

// Encontrar um documento na coleção.
db.getCollection("analyze_documents").findOne({
  _id: "49ad106b-787b-4c9a-80ac-4c81388355ca", // parâmetro recebido
});
```

### Exemplo de Resposta

#### Sucesso (200 OK)

```json
{
  "_id": "49ad106b-787b-4c9a-80ac-4c81388355ca",
  "document_name": "example.pdf",
  "status": "processed",
  "analysis_results": {
    "key": "value"
  }
}
```

#### Não Encontrado (404)

```json
{
  "error": "Documento não encontrado"
}
```

## Notas de Implementação

1. **Consulta ao Banco de Dados**: Use o método `findOne` para buscar o documento pelo `_id`.
2. **Tratamento de Erros**: Garanta o tratamento adequado para casos em que o documento não seja encontrado.
3. **Estrutura da Resposta**: Siga os padrões de resposta da API existentes.
4. **Estrutura do Código**: Adote a arquitetura do projeto existente e evite duplicação de código.

## Requisitos de Teste

1. **Testes Unitários**:
   - Testar o endpoint com um `id` válido que exista no banco de dados.
   - Testar o endpoint com um `id` que não exista (esperar `404 Not Found`).
2. **Casos de Borda**:
   - Testar com formatos de `id` inválidos.
   - Testar com o parâmetro `id` ausente.

## Notas Adicionais

- Garanta que a implementação respeite os princípios SOLID.
- Use injeção de dependência para acesso ao banco de dados, facilitando os testes.
- Documente o endpoint na documentação da API.

---

## Estrutura de Arquivos

- **Controller**: Adicione a rota no arquivo de controller apropriado (por exemplo, `app/api/controllers/analyze.py`).
- **Service**: Implemente a lógica em uma classe de serviço dedicada (por exemplo, `app/services/analyze_document_service.py`).
- **Tests**: Adicione testes unitários no diretório `tests/unit`.

## Critérios de Aceitação

- O endpoint está funcional e atende aos requisitos descritos acima.
- Todos os testes passam com sucesso.
- O código segue os padrões e diretrizes de codificação do projeto.
