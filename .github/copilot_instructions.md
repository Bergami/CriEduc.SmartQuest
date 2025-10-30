---
applyTo: "**"
---

# Instruções para o Copilot – Projeto SmartQuest

## Regra principal

- NUNCA PODEMOS ALTERAR A ESTRUTURA DE RESPONSE DE UM ENDPOINT SEM ANTES PEDIR AUTORIZAÇÃO, APRESENTANDO TODOS OS IMPACTOS E O MOTIVO.
- Avalie como um profissional sênior todo o cenário envolvido no escopo, antes de realizar uma alteração.
- Não invente uma solução qualquer sem embasamento no contexto, o código escrito deve ser assêncial e acertivo.
- Caso não entenda algum fluxo, pergunte antes de propor uma solução.
- Sempre que for realizar uma ação, analise na solution, o fluxo e o objetivo da funcionalidade envolvida.
- Não podemos quebrar o que já está funcionando.
- Todo código escrito deve seeguir as boas práticas de programação
- Quando for identificado um error, faça uma análise completa da situação, faça uma análise do último response do azure e avalie as imagens salvas.
- Sempre faça uma análise do que foi pedido, apresente a solução e pergunte se pode ou não aplicar a solução identificada.
- Sempre que gerar arquivos para debugar algo temporariamente, delete assim que concluir o objetivo.
- É proíbido pegar trecho de textos para definir regras. Exemplo: " if 'Eu sei, mas não devia' in content and 'Marina Colasanti' in content:"

## Instruções Python

- Seguir o padrão PEP8 para formatação e nomes.
- Escreva comentários claros e concisos para cada função.
- Garanta que as funções tenham nomes descritivos e incluam dicas de tipo.
- Forneça docstrings seguindo as convenções do PEP 257.
- Use o typingmódulo para anotações de tipo (por exemplo, List[str], Dict[str, int]).
- Divida funções complexas em funções menores e mais gerenciáveis.
- Utilize o princípio SOLID

## Estrutura com FastAPI

- Usar os decoradores `@app.get`, `@app.post`, etc. para definir rotas.
- Criar modelos de entrada e saída com `pydantic.BaseModel`.
- Sempre utilizar o parâmetro `response_model` para garantir estrutura fixa de resposta.
- Separar rotas em módulos (ex: `routes/usuario.py`, `routes/produto.py`).

## Convenções de Nomenclatura

- Funções e variáveis: snake_case
- Classes: PascalCase
- Constantes: UPPER_CASE
- Rotas: substantivos no plural (ex: /usuarios, /produtos)

## Alterações no Código

- Sempre antes de fazer uma modificação analise todo o contexto que envolve a alteração.
- Sempre que algo não tiver claro, busque esclarecer a questão com perguntas detalhadas.
- Sempre que for fazer uma modificação, apresente o motivo e a melhoria que irá trazer.
- Sempre aguarde a autorização para executar a modificação.
- Após alterar o código certifique que não adicionou funcionalidades duplicadas.
- Após alterar o código certifique que não adicinou excesso de complexidade ou que feriu padrões de qualidade de software, como o SOLID.
- Nunca deixe códigos obsoletos no sistema, se não é mais necessário apague.
- Não utilize a nomenclatura "legacy ou refactored", se precisarmos refatorar ou migrar uma funcionalidade significa que não vamos precisar manter a versão antiga. Se tiver dúvida sempre me pergunte, assim podemos analisar juntos.

## Para rodar scripts no terminal

- Use sintaxe do PowerShell
- Não use emoji no PowerShell e nem em arquivos de testes

## Estrutura da Resposta

- Todas as respostas da API devem seguir uma estrutura JSON fixa.
- Exemplo de resposta para o endpoint `/analyze/analyze_document`:
- Atualmente o sistema salva em tests informações relevantes para análise, como:
  -- images/by_provider (imagens presentes no documento)
  -- responses/azure (estrutura retornada pelo azure)
- Observação: Este modelo apresenta a saída esperada após um processamento de uma prova.
- A estrutura não pode sofrer alteração

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
        {
          "letter": "A",
          "text": "colocou o feijão em um sapato."
        },
        {
          "letter": "B",
          "text": "cozinhou o feijão."
        },
        {
          "letter": "C",
          "text": "desceu a montanha correndo."
        },
        {
          "letter": "D",
          "text": "sumiu da vista do oponente."
        },
        {
          "letter": "E",
          "text": "tirou seu sapato."
        }
      ],
      "hasImage": false,
      "context_id": 1
    },
    {
      "number": 2,
      "question": "No trecho “-Antes de colocá-LOS no sapato, eu OS cozinhei\", os termos destacados referem- se",
      "alternatives": [
        {
          "letter": "A",
          "text": "aos sapatos."
        },
        {
          "letter": "B",
          "text": "aos problemas."
        },
        {
          "letter": "C",
          "text": "aos discípulos."
        },
        {
          "letter": "D",
          "text": "aos vencedores."
        },
        {
          "letter": "E",
          "text": "aos feijões."
        }
      ],
      "hasImage": false,
      "context_id": 1
    },
    {
      "number": 3,
      "question": "No texto \"Feijões ou Problemas?\", qual é o conflito gerador do enredo?",
      "alternatives": [
        {
          "letter": "A",
          "text": "A necessidade do monge em encontrar um sucessor."
        },
        {
          "letter": "B",
          "text": "A solução encontrada pelo discípulo vencedor."
        },
        {
          "letter": "C",
          "text": "A subida dos discípulos a uma grande montanha."
        },
        {
          "letter": "D",
          "text": "O desafio proposto pelo mestre aos seus discípulos."
        },
        {
          "letter": "E",
          "text": "O sofrimento do discípulo ao ver o oponente vencer."
        }
      ],
      "hasImage": false,
      "context_id": 1
    },
    {
      "number": 4,
      "question": "O autor justifica o fato de os ecologistas referirem-se aos parques nacionais como \"arcas de Noé para o futuro\" da seguinte maneira:",
      "alternatives": [
        {
          "letter": "A",
          "text": "Porque são áreas preservadas da caça e pesca indiscriminadas."
        },
        {
          "letter": "B",
          "text": "Porque ocupam espaços administrativamente delimitados pelo Instituto Brasileiro de Desenvolvimento Florestal."
        },
        {
          "letter": "C",
          "text": "Porque espécies animais e vegetais que estão se extinguindo em outras regiões têm preservada sua sobrevivência nesses parques."
        },
        {
          "letter": "D",
          "text": "Porque nesses parques colecionam-se casais de espécies animais e vegetais em extinção noutras áreas."
        },
        {
          "letter": "E",
          "text": "Porque há agentes florestais incumbidos de zelar pelos animais e vegetais dos parques."
        }
      ],
      "hasImage": false,
      "context_id": 3
    },
    {
      "number": 5,
      "question": "A respeito dos incêndios referidos pelo autor, depreende-se do texto que",
      "alternatives": [
        {
          "letter": "A",
          "text": "embora tivessem ameaçado espécie de animais e vegetais raras, apresentaram um lado positivo."
        },
        {
          "letter": "B",
          "text": "foram provocados pela rigorosa estiagem do inverno, no Centro-Sul, e pela seca prolongada no sertão nordestino."
        },
        {
          "letter": "C",
          "text": "não foram combatidos com presteza e eficiência pelos bombeiros."
        },
        {
          "letter": "D",
          "text": "só foram debelados por providenciais chuvas que eventualmente vieram a cair sobre os parques."
        },
        {
          "letter": "E",
          "text": "destruíram parte da flora e fauna das reservas, desfigurando sua paisagem."
        }
      ],
      "hasImage": false,
      "context_id": 2
    },
    {
      "number": 6,
      "question": "No trecho, segundo parágrafo, \"[ ... ] ELAS logo caíram em desuso\", o pronome em destaque retoma",
      "alternatives": [
        {
          "letter": "A",
          "text": "diferenças."
        },
        {
          "letter": "B",
          "text": "cabeleiras."
        },
        {
          "letter": "C",
          "text": "perucas."
        },
        {
          "letter": "D",
          "text": "classes sociais."
        },
        {
          "letter": "E",
          "text": "cabeças raspadas."
        }
      ],
      "hasImage": false,
      "context_id": 4
    },
    {
      "number": 7,
      "question": "Qual é a informação principal do texto \"Diabetes sem freio\"?",
      "alternatives": [
        {
          "letter": "A",
          "text": "A diabetes associada a problemas cardíacos."
        },
        {
          "letter": "B",
          "text": "O crescimento da epidemia de diabetes no mundo."
        },
        {
          "letter": "C",
          "text": "A estimativa de adultos portadores de diabetes."
        },
        {
          "letter": "D",
          "text": "O percentual de mortes no mundo."
        },
        {
          "letter": "E",
          "text": "O percentual de problemas cardíacos."
        }
      ],
      "hasImage": false,
      "context_id": 5
    },
    {
      "number": 8,
      "question": "Sobre o texto analisado acima, podemos afirmar corretamente que:",
      "alternatives": [
        {
          "letter": "A",
          "text": "Não transmite nenhum sentido para leitor devido os diversos desvios de ortografia."
        },
        {
          "letter": "B",
          "text": "Trata-se um aviso, e, apesar da escrita inadequada, transmite sentido para o leitor."
        },
        {
          "letter": "C",
          "text": "Não há nenhum problema com a escrita, já que o leitor compreende a mensagem."
        },
        {
          "letter": "D",
          "text": "A escrita deste texto está de acordo com a situação de comunicação, já que não há nenhum problema de ortografia."
        },
        {
          "letter": "E",
          "text": "Não há problema com a ortografia, mas por tratar-se de um texto rebuscado dificulta o entendimento do leitor"
        }
      ],
      "hasImage": false,
      "context_id": 6
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
        "Reza a lenda que um monge, próximo de se aposentar, precisava encontrar um sucessor. Entre seus discípulos, dois já haviam dado mostras de que eram os mais aptos, mas apenas um o poderia. Para sanar as dúvidas, o mestre lançou um desafio, para pôr a sabedoria dos dois à prova: ambos receberiam alguns grãos de feijão, que deveriam colocar dentro dos sapatos, para então empreender a subida de uma grande montanha.",
        "Dia e hora marcados, começa a prova. Nos primeiros quilômetros, um dos discípulos começou a mancar. No meio da subida, parou e tirou os sapatos. As bolhas em seus pés já sangravam, causando imensa dor. Ficou para trás, observando seu oponente sumir de vista.",
        "Prova encerrada, todos de volta ao pé da montanha, para ouvir do monge o óbvio anúncio. Após o festejo, o derrotado aproxima-se do vencedor e pergunta como é que ele havia conseguido subir e descer com os feijões nos sapatos.",
        "- Antes de colocá-los no sapato, eu os cozinhei.",
        "Carregando feijões, ou problemas, há sempre um jeito mais fácil de levar a vida. Problemas são inevitáveis. Já a duração do sofrimento, é você quem determina. (Disponível em: Acesso em: 13 mar. 2011)"
      ],
      "title": "FEIJÕES OU PROBLEMAS?",
      "hasImage": false
    },
    {
      "id": 2,
      "type": ["text"],
      "source": "exam_document",
      "statement": "Leia o texto a seguir para responder as duas próximas questões.",
      "paragraphs": [
        "PARQUES EM CHAMAS",
        "Saudados por ecologistas como arcas de Noé para o futuro, por serem repositórios de espécies animais e vegetais em extinção acelerada noutras áreas do país, alguns dos 25 parques nacionais do Brasil tiveram, na semana passada, a sua paisagem mutilada pelo fogo. A rigorosa estiagem que acompanha o inverno no Centro- Sul ressecou a vegetação e abriu caminho para que as chamas tragassem 6 dos 33 quilômetros quadrados do Parque Nacional da Tijuca, pegado à cidade do Rio de Janeiro, e convertessem em carvão 10% dos 300 quilômetros quadrados do Parque Nacional do Itatiaia, na divisa de Minas Gerais com o Estado do Rio. Contido pelos bombeiros já no fim de semana, na Tijuca, e abafado por uma providencial chuva no Itatiaia, na quarta-feira o fogo pipocou em outro extremo do país. Naquele dia, o incêndio começou no Parque da Serra da Capivara, no sertão do Piauí, calcinado há seis anos pela seca, e avançou pela caatinga, que esconde as pinturas rupestres inscritas na rocha, há pelo menos 31.500 anos, pelo homem brasileiro pré-histórico. (Isto é, 22 ago. 1984. In: Compreensão e interpretação de textos. Coleção Concursos públicos vol. 9. Barueri: Gold, 2008.)"
      ],
      "title": "PARQUES EM CHAMAS",
      "hasImage": false
    },
    {
      "id": 3,
      "type": ["text"],
      "source": "exam_document",
      "statement": "LEIA O TEXTO A SEGUIR",
      "paragraphs": [
        "POR QUE TODO MUNDO USAVA PERUCA NA EUROPA DOS SÉCULOS XVII E XVIII?",
        "Não era todo mundo, apenas os aristocratas. A moda começou com Luís XIV (1638-1715), rei da França. Durante seu governo, o monarca adotou a peruca pelo mesmo motivo que muita gente usa o acessório ainda hoje: esconder a calvície. O resto da nobreza gostou da ideia e o costume pegou. A peruca passou a indicar, então, as diferenças sociais entre as classes, tornando- se sinal de status e prestígio. Também era comum espalhar talco ou farinha de trigo sobre as cabeleiras falsas para imitar o cabelo branco dos idosos. Mas, por mais elegante que parecesse ao pessoal da época, a moda das perucas também era nojenta. \"Proliferava todo tipo de bicho, de baratas a camundongos, nesses cabelos postiços\", afirma o estilista João Braga, professor de História da Moda das Faculdades SENAC, em São Paulo.",
        "Em 1789, com a Revolução Francesa, veio a guilhotina, que extirpou a maioria das cabeças com perucas. Símbolo de uma nobreza que se desejava exterminar, elas logo caíram em desuso. Sua origem, porém, era muito mais velha do que a monarquia francesa. No Egito antigo, homens e mulheres de todas as classes sociais já exibiam adornos de fibra de papiro - na verdade, disfarce para as cabeças raspadas por causa de uma epidemia de piolhos. Hoje, as perucas de cachos brancos, típicas da nobreza europeia, sobrevivem apenas nos tribunais ingleses, onde compõem a indumentária oficial dos juízes. (Disponível em: http://mumdoestranho.abril.com.br/historia/pergunta 285920.shtmal. Acesso em: 27 mar. 2010. Adaptado)"
      ],
      "title": "POR QUE TODO MUNDO USAVA PERUCA NA EUROPA DOS SÉCULOS XVII E XVIII?",
      "hasImage": false
    },
    {
      "id": 4,
      "type": ["text"],
      "source": "exam_document",
      "statement": "Leia este texto",
      "paragraphs": [
        "DIABETES SEM FREIO",
        "A respeitada revista médica inglesa \"The Lancet\" chamou a atenção, em editorial, para o crescimento da epidemia de diabetes no mundo. A estimativa é de que atuais 246 milhões de adultos portadores da doença se transformem em 380 milhões em 2025. O problema é responsável por 6% do total de mortes no mundo, sendo 50% devido a problemas cardíacos - doença associada à diabetes. (Galileu, n. 204, jul. 2008, p. 14.)"
      ],
      "title": "DIABETES SEM FREIO",
      "hasImage": false
    },
    {
      "id": 5,
      "type": ["text", "image"],
      "source": "exam_document",
      "statement": "Analise a imagem abaixo",
      "paragraphs": ["FAVOR NÃO DEXAR OBIGETOS NO CORREDOR"],
      "title": "FAVOR NÃO DEXAR OBIGETOS NO CORREDOR",
      "hasImage": true,
      "contentType": "image/jpeg;base64",
      "sub_contexts": [
        {
          "sequence": "I",
          "type": "charge",
          "title": "TEXTO I: charge",
          "content": "ANALISE OS TEXTO A SEGUIR:\nCIERRE\nFoto b\nPRONTO, MEU FILHO! AGORA VOCÊ PODE IR PARA A ESCOLA.",
          "images": [
            // URL da imagem
          ]
        },
        {
          "sequence": "II",
          "type": "charge",
          "title": "TEXTO II: charge",
          "content": "30.10\nFOFOQUEIRA NÃO, QUERIDA! EU SOU PRODUTORA DE BIOGRAFIAS ORAIS NÃO AUTORIZADAS!\nTEXTO III: propaganda",
          "images": [
            // URL da imagem
          ]
        },
        {
          "sequence": "III",
          "type": "charge",
          "title": "TEXTO III: propaganda",
          "content": "30.10\nFOFOQUEIRA NÃO, QUERIDA! EU SOU PRODUTORA DE BIOGRAFIAS ORAIS NÃO AUTORIZADAS!\nTEXTO II: charge",
          "images": [
            // URL da imagem
          ]
        },
        {
          "sequence": "IV",
          "type": "propaganda",
          "title": "TEXTO IV: propaganda",
          "content": "BIS\nLACTA\npara deixar você de boca aberta. Fechada Aberta Fechada Aberta Fechada. Aberta.",
          "images": [
            // URL da imagem
          ]
        }
      ]
    },
    {
      "id": 6,
      "type": ["text"],
      "source": "exam_document",
      "statement": "Leia a crônica e depois resolva as próximas questões.",
      "paragraphs": [
        "PRAIA (Rubem Braga)",
        "Acordo cedo e vejo o mar se espreguiçando; o sol acabou de nascer. Vou para a praia; é bom chegar a esta hora em que a areia que o mar lavou ainda está limpinha, sem marca de nenhum pé. A manhã está nítida no ar leve; dou um mergulho e essa água salgada me faz bem, limpa de todas as coisas da noite.",
        "Era assim, pelas seis e meia, sete horas que a gente ia para a praia em Marataízes. Naquele tempo, diziam que era bom para a saúde; não sei se ainda dizem. Para mim, tem um sabor tão antigo e todo novo, essa praia bem de manhã. Para um lado e outro diviso apenas dois ou três vultos distantes. Por que não vem mais gente à praia? Muita gente, é claro, tem de estar na cidade cedo; mas há um número imenso de funcionários e pessoas de muitas profissões que nesta cidade onde se dorme tão cedo parece ter algum preconceito contra acordar cedo. Basta olhar qualquer edifício de Copacabana e Ipanema; às dez horas começam a se apagar as luzes, e meia hora depois da última sessão de cinema há edifícios inteiros completamente às escuras. O grosso da população ressona. provincianamente às onze horas. Mas para vir à praia todo mundo parece ter medo de ser provinciano.",
        "O leve calor do sol me reconforta. Chega uma senhora gorda com dois meninos e duas meninas. Senta- se no raso, e as duas crianças menores sobem pelos seus ombros e sua cabeça, chutam água e espuma, todos se riem na maior felicidade. Suas roupas de banho não são elegantes; devem ser como eu, gente do interior. Aparece depois um rapaz; mas é um atleta. Faz alguns"
      ],
      "title": "PRAIA (Rubem Braga)",
      "hasImage": false
    }
  ]
}
```

## Casos extremos e testes

- Sempre inclua casos de teste para caminhos críticos do aplicativo.
- Considere casos extremos comuns, como entradas vazias, tipos de dados inválidos e grandes conjuntos de dados.
- Inclua comentários para casos extremos e o comportamento esperado nesses casos.
- Escreva testes unitários para funções e documente-os com docstrings explicando os casos de teste.
- Os testes devem ser escritos no diretório "CriEduc.SmartQuest\tests\unit\*"
