# Estrutura de Resposta – Projeto SmartQuest

## Regras Gerais
- A estrutura de resposta deve ser consistente em todos os endpoints.
- Alterações na estrutura só podem ser feitas com autorização e análise de impacto.
- Certifique-se de que os dados estejam completos e sigam o modelo definido.

## Exemplo de Estrutura JSON

```json
{
  "email": "wander.bergami@gmail.com",
  "document_id": "a76da854-096a-4da1-969f-be60167000ee",
  "filename": "mock_document.pdf",
  "header": {
    "network": "PREFEITURA DE VILA VELHA SEMED",
    "school": "UMEF Saturnino Rangel Mauro VILA VELHA - ES",
    "city": "Marataízes",
    "teacher": "Danielle",
    "subject": "Língua Portuguesa",
    "exam_title": "Prova Trimestral",
    "trimester": "3º TRIMESTRE",
    "grade": "7º ano do Ensino Fundamental",
    "class": null,
    "student": null,
    "grade_value": "12,0",
    "date": null
  },
  "questions": [
    {
      "number": 1,
      "question": "Nesse texto, o discípulo que venceu a prova porque",
      "alternatives": [
        { "letter": "A", "text": "colocou o feijão em um sapato." },
        { "letter": "B", "text": "cozinhou o feijão." },
        { "letter": "C", "text": "desceu a montanha correndo." },
        { "letter": "D", "text": "sumiu da vista do oponente." },
        { "letter": "E", "text": "tirou seu sapato." }
      ],
      "hasImage": false,
      "context_id": 1
    }
  ],
  "context_blocks": [
    {
      "id": 1,
      "type": ["text"],
      "source": "exam_document",
      "statement": "Após ler atentamente o texto a seguir, responda as três próximas questões.",
      "paragraphs": [
        "FEIJÕES OU PROBLEMAS?",
        "Reza a lenda que um monge, próximo de se aposentar, precisava encontrar um sucessor..."
      ],
      "title": "FEIJÕES OU PROBLEMAS?",
      "hasImage": false
    }
  ]
}
```

## Observações
- Certifique-se de que os campos obrigatórios estejam sempre presentes.
- Valide os dados antes de enviá-los para garantir conformidade com o modelo.