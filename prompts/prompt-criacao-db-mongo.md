# Contexto

- Atualmente o response não é persistido, precisamos armazenar as informações que são retornadas pelo endpoint principal - /analyze/analyze_document - em uma base de dados.

## Objetivo

- A base de dados que eu quero utilizar nessa solução é o mongo db, preciso adicionar o response do endpoint - "/analyze/analyze_document" em um banco de dados mongo.

## Requisitos

- Antes de propor algo, faça uma análise de toda a solução com foco no que está sendo solicitado.
- Criar uma nova branch com base na main.
- Nome da tabela: "analyze_document" --
- Campos: Id, created_at, user_email, file_name, response

Id --> deve ser um Guid
created_at --> data hora atual
user_email --> e-mail informado no request
file_name --> nome do documento enviado
response --> response no formato json

📁 Nome de Coleções (Tabelas)

- ✅ Use nomes no plural: users, products, orders
- ✅ Use snake_case ou kebab-case: user_profiles, order_items
- ✅ Seja descritivo e específico: evite nomes genéricos como data ou info
- ❌ Evite nomes muito longos ou ambíguos
  Exemplo bom: customer_orders
  Exemplo ruim: co ou data

Nome de Campos (Colunas)

- ✅ Use camelCase: firstName, createdAt, isActive
- ✅ Seja consistente em todo o projeto
- ✅ Evite abreviações desnecessárias: prefira emailAddress a eml
- ❌ Não use espaços, caracteres especiais ou letras maiúsculas no início
  Exemplo bom: productPrice
  Exemplo ruim: Product_Price ou product price

## Considerações

- Preciso que a nomenclatura para collections e dos campos estejam adequadas ao padrão do mongo.
- Preciso que essa camada de dados esteja isolada.

### Pendências

- Pretendo instalar o mongo no docker, talvez seria interessante termos um arquivo "docker-compose.yml" para criar toda essa estrutura.
- O arquivo docker-compose.yml pode ficar na raiz do projeto
- Acredito que seria uma boa prática criar os scripts de criação da base de dados e da tabela por meio do docker compose.

## Clarificação

- Caso alguma informação não esteja clara, sempre pergunte antes de executar.
