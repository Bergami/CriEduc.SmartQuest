---
applyTo: **/prompts/prompt-*.md
---

# Diretrizes para arquivos de prompt do Copilot

Instruções para criar arquivos de prompt eficazes e fáceis de manter que orientam o GitHub Copilot na entrega de resultados consistentes e de alta qualidade em qualquer repositório.

# Âmbito e Princípios

- Público-alvo: mantenedores e colaboradores que criam prompts reutilizáveis ​​para o Copilot Chat.
- Objetivos: comportamento previsível, expectativas claras, permissões mínimas e portabilidade entre repositórios.
- Referências principais: documentação do VS Code sobre arquivos de prompt e convenções específicas da organização.

# Requisitos do Frontmatter

- Inclua description(frase única, resultado prático), mode(escolha explicitamente ask, edit, ou agent) e tools(conjunto mínimo de conjuntos de ferramentas necessários para atender ao prompt).
- Declare modelquando o prompt depende de um nível de capacidade específico; caso contrário, herde o modelo ativo.
  Preserve quaisquer metadados adicionais ( language, tags, visibility, etc.) exigidos pela sua organização.
- Use aspas consistentes (aspas simples são recomendadas) e mantenha um campo por linha para facilitar a leitura e a clareza do controle de versão.

# Nomeação e posicionamento de arquivos

- Use nomes de arquivos kebab-case terminados em .prompt.md e armazene-os em .github/prompts, a menos que seu padrão de espaço de trabalho especifique outro diretório.
- Forneça um nome de arquivo curto que comunique a ação (por exemplo, generate-readme.prompt.md em vez de prompt1.prompt.md).

# strutura corporal

- Comece com um #título nivelado que corresponda à intenção do prompt para que ele apareça bem na pesquisa Quick Pick.
- Organize o conteúdo com seções previsíveis. Recomendações básicas: Missionou Primary Directive, Scope & Preconditions, Inputs, Workflow(passo a passo), Output Expectations, e Quality Assurance.
- Ajuste os nomes das seções para se adequarem ao domínio, mas mantenha o fluxo lógico: por que → contexto → entradas → ações → saídas → validação.
  Consulte prompts relacionados ou arquivos de instruções usando links relativos para auxiliar na descoberta.

# Manipulação de entrada e contexto

- Use ${input:variableName[:placeholder]} para valores obrigatórios e explique quando o usuário deve fornecê-los. Forneça padrões ou alternativas sempre que possível.
- Chame variáveis ​​contextuais como ${selection}, ${file}, ${workspaceFolder} somente quando forem essenciais e descreva como o Copilot deve interpretá-las.
- Documente como proceder quando o contexto obrigatório estiver ausente (por exemplo, “Solicitar o caminho do arquivo e parar se ele permanecer indefinido”).

# Guia de ferramentas e permissões

- Limite-se tools ao menor conjunto que permita a tarefa. Liste-os na ordem de execução preferencial quando a sequência for importante.
- Se o prompt herdar ferramentas de um modo de bate-papo, mencione esse relacionamento e informe quaisquer comportamentos críticos da ferramenta ou efeitos colaterais.
- Avise sobre operações destrutivas (criação de arquivos, edições, comandos de terminal) e inclua proteções ou etapas de confirmação no fluxo de trabalho.

# Tom e estilo de instrução

- Escreva frases diretas e imperativas direcionadas ao Copilot (por exemplo, “Analisar”, “Gerar”, “Resumir”).
- Mantenha frases curtas e inequívocas, seguindo as práticas recomendadas de tradução da Documentação do Desenvolvedor do Google para dar suporte à localização.
- Evite expressões idiomáticas, humor ou referências culturalmente específicas; prefira uma linguagem neutra e inclusiva.

# Definição de saída

- Especifique o formato, a estrutura e o local dos resultados esperados (por exemplo, “Criar docs/adr/adr-XXXX.md usando o modelo abaixo”).
- Inclua critérios de sucesso e gatilhos de falha para que o Copilot saiba quando parar ou tentar novamente.
- Forneça etapas de validação — verificações manuais, comandos automatizados ou listas de critérios de aceitação — que os revisores podem executar após executar o prompt.

# Exemplos e ativos reutilizáveis

- Incorpore exemplos bons/ruins ou "scaffolds" (modelos Markdown, stubs JSON) que o prompt deve produzir ou seguir.
- Mantenha tabelas de referência (capacidades, códigos de status, descrições de funções) em linha para manter o prompt autocontido. Atualize essas tabelas quando os recursos upstream forem alterados.
- Crie links para documentação confiável em vez de duplicar orientações longas.

# Lista de verificação de garantia de qualidade

- [ ] Os campos do Frontmatter são completos, precisos e têm o mínimo de privilégios.
- [ ] As entradas incluem espaços reservados, comportamentos padrão e fallbacks.
- [ ] O fluxo de trabalho abrange preparação, execução e pós-processamento sem lacunas.
- [ ] As expectativas de saída incluem detalhes de formatação e armazenamento.
- [ ] As etapas de validação são acionáveis ​​(comandos, verificações de diferenças, prompts de revisão).
- [ ] As políticas de segurança, conformidade e privacidade referenciadas pelo prompt estão atualizadas.
- [ ] O prompt é executado com sucesso no VS Code ( Chat: Run Prompt) usando cenários representativos.

# Orientações de manutenção

- Prompts de controle de versão junto com o código que eles afetam; atualize-os quando dependências, ferramentas ou processos de revisão forem alterados.
- Revise os prompts periodicamente para garantir que as listas de ferramentas, os requisitos do modelo e os documentos vinculados permaneçam válidos.
- Coordenar com outros repositórios: quando um prompt se mostrar amplamente útil, extraia orientações comuns em arquivos de instruções ou pacotes de prompts compartilhados.
