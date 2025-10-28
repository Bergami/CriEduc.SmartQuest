# Prompt: Implementação do Upload de Imagens para Azure Blob Storage

## Contexto

Atualmente, as imagens extraídas dos documentos enviados são retornadas no response como byte array (base64). Para melhorar a eficiência e escalabilidade, as imagens extraídas devem ser enviadas para um Azure Blob Storage. O sistema deverá retornar URLs públicas no lugar dos dados base64.

Dados para acesso:
URL BLOB
https://<storage-account>.blob.core.windows.net/<container>?<SAS-token>

## Requisitos Macros

### 1. Ajuste na header

- É necessário remover a propriedade "images" da header.

Atualmente:
"header": {
"school": "UMEF Saturnino Rangel Mauro VILA VELHA - ES",
"teacher": "Danielle",
"subject": "Língua Portuguesa",
"student": null,
"series": null,
"images": [
"/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAIBAQEBAQI ...
]
}

Cenário desejado
"header": {
"school": "UMEF Saturnino Rangel Mauro VILA VELHA - ES",
"teacher": "Danielle",
"subject": "Língua Portuguesa",
"student": null,
"series": null  
 }

### 2. Nova estrutura do context_blocks

Em todas as propriedades "images" presente no context_blocks, deverão aparecer as urls da imagens enviadas para o Azure Blob Storage.

Exemplo:

"context_blocks": [
{
"id": 1,
"type": ["text","image"],
"source": "exam_document",
"statement": "LEIA O TEXTO A SEGUIR",
"title": "Eu sei, mas não devia (Marina Colasanti)",
"hasImage": true,
"images": [
// Aqui deveria entrar a URL da IMAGEM
],
"contentType": "image/url",
"paragraphs": null,
"sub_contexts": null
}
]

### 3. Investigação

- Atualmente temos uma lógica que recebe byte array e tranforma em imagem jpg e salva no diretório. Quero remover essa função do sistema, não vamos mais guardar essas imagens localmente.
- Avalie se a lógica pode ser aproveitada para enviar a imagem para o Azure.

### 4. Crie um plano de ação detalhado para executarmos esses passos, aproveite para fazer uma reanálise total da situação.
