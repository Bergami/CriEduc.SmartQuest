# Instruções para o Copilot – Projeto SmartQuest

## Regra Principal

- NUNCA PODEMOS ALTERAR A ESTRUTURA DE RESPONSE DE UM ENDPOINT SEM ANTES PEDIR AUTORIZAÇÃO, APRESENTANDO TODOS OS IMPACTOS E O MOTIVO.
- Avalie como um profissional sênior todo o cenário envolvido no escopo, antes de realizar uma alteração.
- Não invente uma solução qualquer sem embasamento no contexto, o código escrito deve ser assêncial e acertivo.
- Caso não entenda algum fluxo, pergunte antes de propor uma solução.
- Sempre que for realizar uma ação, analise na solution, o fluxo e o objetivo da funcionalidade envolvida.
- Não podemos quebrar o que já está funcionando.
- Todo código escrito deve seeguir as boas práticas de programação
- Quando for identificado um error, faça uma análise completa da situação, faça uma análise do último response do azure e avalie as imagens salvas.
- Sempre faça uma análise do que foi pedido, apresente a solução e pergunte se pode ou não aplicar a solução identificada.
- O commit deve ser escritp em inglês.
- O código deve ser escrito em inglês.
- todos testes devem ser executados no ambiente virtual (env)

## Estrutura de Resposta

- Todas as respostas da API devem seguir uma estrutura JSON fixa.
- **Importante**: A estrutura não pode ser alterada sem autorização prévia.
- Para detalhes completos sobre a estrutura, consulte o arquivo dedicado:  
  [`response_structure.md`](./response_structure.md)

## Ambiente de Desenvolvimento e Testes

- O desenvolvimento e os testes deste projeto são realizados em um ambiente Windows.
- Todas as interações e execução de comandos devem ser feitas utilizando o PowerShell.
- Certifique-se de que os comandos gerados estejam compatíveis com o PowerShell, utilizando o caractere `;` para unir comandos em uma única linha, se necessário.

## Diretrizes Adicionais

- **Documentação**: Não é necessário criar arquivos de documentação (`*.md`) para cada melhoria, correção ou refatoração. Crie documentação apenas quando explicitamente solicitado.

- **Remoção de Arquivos**: Ao remover arquivos desnecessários (como arquivos de testes ou debug gerados para apoiar melhorias), execute a exclusão em um único comando para manter o histórico de alterações organizado.
