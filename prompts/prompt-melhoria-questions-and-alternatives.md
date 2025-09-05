# contexto
- É necessário reavaliar a forma de extração de questões e alternativas presente no sistema.

- Analisando o arquivo extract_alternatives_from_text.py observei uma certa complexidade desnecessária, confusa e sujeito a bugs.

# objetivo
- Temos que simplificar a maneira de obtenção das questões e das alternativas. Toda informação textual é retornada pelo Azure em uma propriedade chamada "paragraphs". A ideia é filtrar os items presente nessa estrutura e "classificar", de forma que consigamos obter questões e alternativas, quando existirem.

- O que precisamos é ter de forma clara o que caracteriza uma questão e alternativas. Essa inteligência já temos na solução, talvez seja necessário apenas um refinamento.

- O ideal seria preservar essa lógica atual e escrevermos uma nova lógica melhor em um arquivo de teste, para validarmos essa nova proposta. Basicamente esse arquivo de teste vai ler diretamente o json mais atual retornado pelo Azure ("D:\Git\CriEduc.SmartQuest\tests\responses\azure\azure_Recuperacao_20250903_134805.json") e estruturar um retorno identico ao Question que temos hoje, já no Pydantic.

- Penso que o método de obter as questões e as alternativas deveriam receber a propriedade "paragraphs". Ou seja, a partir do retorno so Azure, filtrar pelo elemento "paragraphs" e passar para o novo método responsável em extrair questões e alternativas. A partir dessa estrutura filtrar as questões, que podem por exemplo iniciar como "questão 1" e fazer o mesmo para as alternativas, buscando paragrafos posteriores a  que iniciam como uma "alternative", por exemplo a), b) e etc.
** Este exemplo dado é bem simples, dev ser levado em conta a forma de identificação de uma questão e alternativas já existentes.

***Exemplo da estrutura json***
```
"paragraphs": [
    {
      "spans": [
        {
          "offset": 0,
          "length": 30
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.8589,
            0.1047,
            1.3476,
            0.1018,
            1.349,
            0.3307,
            0.8603,
            0.3337
          ]
        }
      ],
      "content": "PREFEITURA DE VILA VELHA SEMED"
    },
    {
      "spans": [
        {
          "offset": 31,
          "length": 78
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.2454,
            0.0116,
            6.0376,
            0.0153,
            6.0368,
            0.3965,
            4.2446,
            0.3928
          ]
        }
      ],
      "content": "Prefeitura Municipal de Vila Velha UMEF Saturnino Rangel Mauro VILA VELHA - ES"
    },
    {
      "spans": [
        {
          "offset": 110,
          "length": 20
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.385,
            0.4548,
            1.4683,
            0.4566,
            1.4681,
            0.5775,
            0.3848,
            0.5757
          ]
        }
      ],
      "content": "Professora: Danielle"
    },
    {
      "spans": [
        {
          "offset": 131,
          "length": 17
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            3.3957,
            0.4278,
            4.8282,
            0.4335,
            4.8282,
            0.5932,
            3.3957,
            0.5932
          ]
        }
      ],
      "content": "Língua Portuguesa"
    },
    {
      "spans": [
        {
          "offset": 149,
          "length": 40
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.8282,
            0.4335,
            7.8587,
            0.4335,
            7.8644,
            0.981,
            4.8282,
            0.9753
          ]
        }
      ],
      "content": "ANO: 7º ano do Ensino Fundamental TURMA:"
    },
    {
      "spans": [
        {
          "offset": 190,
          "length": 44
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            3.3957,
            0.5932,
            4.8282,
            0.5932,
            4.8282,
            0.9753,
            3.3957,
            0.9753
          ]
        }
      ],
      "content": "Prova de recuperação trimestral 2º TRIMESTRE"
    },
    {
      "spans": [
        {
          "offset": 235,
          "length": 10
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3937,
            0.999,
            0.9778,
            1.0021,
            0.9772,
            1.1201,
            0.3931,
            1.117
          ]
        }
      ],
      "content": "Estudante:"
    },
    {
      "spans": [
        {
          "offset": 246,
          "length": 21
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3824,
            1.3028,
            2.0688,
            1.3018,
            2.0689,
            1.4524,
            0.3825,
            1.4534
          ]
        }
      ],
      "content": "LEIA O TEXTO A SEGUIR"
    },
    {
      "spans": [
        {
          "offset": 268,
          "length": 40
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            1.4071,
            1.4838,
            2.8644,
            1.4823,
            2.8647,
            1.8155,
            1.4075,
            1.817
          ]
        }
      ],
      "content": "Eu sei, mas não devia (Marina Colasanti)"
    },
    {
      "spans": [
        {
          "offset": 309,
          "length": 452
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3762,
            1.9824,
            3.8902,
            1.9803,
            3.891,
            3.4227,
            0.377,
            3.4247
          ]
        }
      ],
      "content": "Eu sei que a gente se acostuma. Mas não devia. A gente se acostuma a morar em apartamentos de fundos e a não ter outra vista que não as janelas ao redor. E, porque não tem vista, logo se acostuma a não olhar para fora. E, porque não olha para fora, logo se acostuma a não abrir de todo as cortinas. E, porque não abre as cortinas, logo se acostuma a acender mais cedo a luz. E, à medida que se acostuma, esquece o sol, esquece o ar, esquece a amplidão."
    },
    {
      "spans": [
        {
          "offset": 762,
          "length": 364
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3735,
            3.4243,
            3.8911,
            3.421,
            3.8923,
            4.6823,
            0.3747,
            4.6856
          ]
        }
      ],
      "content": "A gente se acostuma a acordar de manhã sobressaltado porque está na hora. A tomar o café correndo porque está atrasado. A ler o jornal no ônibus porque não pode perder o tempo da viagem. A comer sanduíche porque não dá para almoçar. A sair do trabalho porque já é noite. A cochilar no ônibus porque está cansado. A deitar cedo e dormir pesado sem ter vivido o dia."
    },
    {
      "spans": [
        {
          "offset": 1127,
          "length": 310
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3749,
            4.6909,
            3.8894,
            4.6893,
            3.8898,
            5.6567,
            0.3753,
            5.6583
          ]
        }
      ],
      "content": "A gente se acostuma a abrir o jornal e a ler sobre a guerra. E, aceitando a guerra, aceita os mortos e que haja números para os mortos. E, aceitando os números, aceita não acreditar nas negociações de paz. E, não acreditando nas negociações de paz, aceita ler todo dia da guerra, dos números, da longa duração."
    },
    {
      "spans": [
        {
          "offset": 1438,
          "length": 190
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3764,
            5.656,
            3.8879,
            5.6353,
            3.8916,
            6.2771,
            0.3802,
            6.2978
          ]
        }
      ],
      "content": "A gente se acostuma a esperar o dia inteiro e ouvir no telefone: hoje não posso ir. A sorrir para as pessoas sem receber um sorriso de volta. A ser ignorado quando precisava tanto ser visto."
    },
    {
      "spans": [
        {
          "offset": 1629,
          "length": 358
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3744,
            6.2945,
            3.8885,
            6.2892,
            3.8902,
            7.4113,
            0.3761,
            7.4166
          ]
        }
      ],
      "content": "A gente se acostuma a pagar por tudo o que deseja e o de que necessita. E a lutar para ganhar o dinheiro com que pagar. E a ganhar menos do que precisa. E a fazer fila para pagar. E a pagar mais do que as coisas valem. E a saber que cada vez pagar mais. E a procurar mais trabalho, para ganhar mais dinheiro, para ter com que pagar nas filas em que se cobra."
    },
    {
      "spans": [
        {
          "offset": 1988,
          "length": 255
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3766,
            7.4128,
            3.8901,
            7.4098,
            3.8908,
            8.2065,
            0.3773,
            8.2094
          ]
        }
      ],
      "content": "A gente se acostuma a andar na rua e ver cartazes. A abrir as revistas e ver anúncios. A ligar a televisão e assistir a comerciais. A ir ao cinema e engolir publicidade. A ser instigado, conduzido, desnorteado, lançado na infindável catarata dos produtos."
    },
    {
      "spans": [
        {
          "offset": 2244,
          "length": 406
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3708,
            8.2073,
            3.8922,
            8.2016,
            3.8943,
            9.4839,
            0.3729,
            9.4896
          ]
        }
      ],
      "content": "A gente se acostuma à poluição. Às salas fechadas de ar-condicionado e cheiro de cigarro. À luz artificial de ligeiro tremor. Ao choque que os olhos levam na luz natural. Às bactérias da água potável. À contaminação da água do mar. À lenta morte dos rios. Se acostuma a não ouvir passarinho, a não ter galo de madrugada, a temer a hidrofobia dos cães, a não colher fruta no pé, a não ter sequer uma planta."
    },
    {
      "spans": [
        {
          "offset": 2651,
          "length": 524
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            0.3767,
            9.4859,
            3.8916,
            9.4858,
            3.8917,
            11.0766,
            0.3768,
            11.0767
          ]
        }
      ],
      "content": "A gente se acostuma a coisas demais, para não sofrer. Em doses pequenas, tentando não perceber, vai afastando uma dor aqui, um ressentimento ali, uma revolta acolá. Se o cinema está cheio, a gente senta na primeira fila e torce um pouco o pescoço. Se a praia está contaminada, a gente molha só os pés e sua no resto do corpo. Se o trabalho está duro, a gente se consola pensando no fim de semana. E se no fim de semana não há muito o que fazer a gente vai dormir cedo e ainda fica satisfeito porque tem sempre sono atrasado."
    },
    {
      "spans": [
        {
          "offset": 3176,
          "length": 5
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3743,
            0.9978,
            4.6581,
            1.0012,
            4.6568,
            1.1167,
            4.3729,
            1.1133
          ]
        }
      ],
      "content": "Data:"
    },
    {
      "spans": [
        {
          "offset": 3182,
          "length": 11
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            5.8703,
            0.9926,
            6.4486,
            0.9975,
            6.4476,
            1.1223,
            5.8693,
            1.1174
          ]
        }
      ],
      "content": "Valor: 30,0"
    },
    {
      "spans": [
        {
          "offset": 3194,
          "length": 5
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            6.8706,
            1.0005,
            7.1626,
            1.0027,
            7.1617,
            1.1146,
            6.8698,
            1.1124
          ]
        }
      ],
      "content": "Nota:"
    },
    {
      "spans": [
        {
          "offset": 3200,
          "length": 301
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3599,
            1.3121,
            7.8771,
            1.3131,
            7.8769,
            2.2654,
            4.3596,
            2.2644
          ]
        }
      ],
      "content": "A gente se acostuma para não se ralar na aspereza, para preservar a pele. Se acostuma para evitar feridas, sangramentos, para esquivar-se de faca e baioneta, para poupar o peito. A gente se acostuma para poupar a vida. Que aos poucos se gasta, e que, gasta de tanto se acostumar, se perde de si mesma."
    },
    {
      "spans": [
        {
          "offset": 3502,
          "length": 428
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3644,
            2.4125,
            7.8793,
            2.4175,
            7.8772,
            3.9087,
            4.3623,
            3.9037
          ]
        }
      ],
      "content": "QUESTÃO 01. O texto de Marina Colasanti descreve diversas situações do cotidiano da sociedade contemporânea com o objetivo central de fomentar nos(as) leitores(as) uma reflexão a respeito: (2,0 pontos) a) da velocidade com que a tecnologia influencia na nossa comunicação diária e na vida dos jovens e adultos. b) do desrespeito do ser humano com a vida humilde de pessoas pertencentes a grupos sociais mais pobres na sociedade."
    },
    {
      "spans": [
        {
          "offset": 3931,
          "length": 93
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3638,
            3.9256,
            7.8735,
            3.919,
            7.8742,
            4.2521,
            4.3644,
            4.2587
          ]
        }
      ],
      "content": "c) da rotina cotidiana que nos habitua e muitas vezes não enxergamos como isso nos aprisiona."
    },
    {
      "spans": [
        {
          "offset": 4025,
          "length": 94
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3637,
            4.2669,
            7.8746,
            4.2628,
            7.875,
            4.6072,
            4.3641,
            4.6113
          ]
        }
      ],
      "content": "d) da vida contemporânea que se tornou muito mais prática com tantas atribuições no dia a dia."
    },
    {
      "spans": [
        {
          "offset": 4120,
          "length": 127
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3636,
            4.7719,
            7.8757,
            4.7812,
            7.8743,
            5.3008,
            4.3622,
            5.2915
          ]
        }
      ],
      "content": "QUESTÃO 02. A expressão \"A gente\", usada por diversas vezes para iniciar os períodos no texto de Marina Colasanti: (2,0 pontos)"
    },
    {
      "spans": [
        {
          "offset": 4248,
          "length": 157
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3611,
            5.3065,
            7.8745,
            5.2996,
            7.8758,
            5.9646,
            4.3624,
            5.9714
          ]
        }
      ],
      "content": "a) expressa a falta de conhecimento da autora em relação à formalidade da Língua Portuguesa, pois seria mais adequado se ela escrevesse: Nós nos acostumamos."
    },
    {
      "spans": [
        {
          "offset": 4406,
          "length": 185
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3624,
            5.9837,
            7.8736,
            5.9843,
            7.8735,
            6.6806,
            4.3622,
            6.6799
          ]
        }
      ],
      "content": "b) transfere para o(a) interlocutor(a) a responsabilidade de se adaptar a essa linguagem diferente e, provavelmente, desconhecida para a maior parte da população brasileira hoje em dia."
    },
    {
      "spans": [
        {
          "offset": 4592,
          "length": 211
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3645,
            6.6776,
            7.8741,
            6.6714,
            7.8753,
            7.3512,
            4.3657,
            7.3574
          ]
        }
      ],
      "content": "c) expressa a liberdade criativa dos autores brasileiros, porque todos usam esse tipo de expressão rebuscada, pouco ouvida na fala cotidiana e, por isso, causa muito estranhamento aos interlocutores desse texto."
    },
    {
      "spans": [
        {
          "offset": 4804,
          "length": 165
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3606,
            7.369,
            7.8761,
            7.3663,
            7.8766,
            8.0328,
            4.3611,
            8.0355
          ]
        }
      ],
      "content": "d) mostra a proximidade da autora com a escrita e seu entendimento da necessidade de usar, no gênero crônica, essa linguagem mais próxima da fala dos interlocutores."
    },
    {
      "spans": [
        {
          "offset": 4970,
          "length": 444
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3634,
            8.216,
            7.8793,
            8.2228,
            7.8765,
            9.6713,
            4.3606,
            9.6645
          ]
        }
      ],
      "content": "QUESTÃO 03. O último fragmento do texto de Colasanti diz: \"A gente se acostuma para não se ralar na aspereza, para preservar a pele. Se acostuma para evitar feridas, sangramentos, para esquivar-se de faca e baioneta, para poupar o peito. A gente se acostuma para poupar a vida. Que aos poucos se gasta, e que, gasta de tanto se acostumar, se perde de si mesma\". Esse trecho da crônica foi desenvolvido PREDOMINANTEMENTE utilizando: (2,0 pontos)"
    },
    {
      "spans": [
        {
          "offset": 5415,
          "length": 39
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3624,
            9.6651,
            6.8744,
            9.6616,
            6.8747,
            9.8213,
            4.3627,
            9.8249
          ]
        }
      ],
      "content": "a) uma linguagem no sentido conotativo."
    },
    {
      "spans": [
        {
          "offset": 5455,
          "length": 39
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3623,
            9.8378,
            6.8824,
            9.8366,
            6.8825,
            10.0012,
            4.3624,
            10.0024
          ]
        }
      ],
      "content": "b) uma linguagem no sentido denotativo."
    },
    {
      "spans": [
        {
          "offset": 5495,
          "length": 26
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3642,
            10.0109,
            6.0509,
            10.0099,
            6.051,
            10.1751,
            4.3642,
            10.176
          ]
        }
      ],
      "content": "c) uma linguagem regional."
    },
    {
      "spans": [
        {
          "offset": 5522,
          "length": 28
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 1,
          "polygon": [
            4.3634,
            10.1837,
            6.2025,
            10.1853,
            6.2024,
            10.3478,
            4.3633,
            10.3462
          ]
        }
      ],
      "content": "d) uma linguagem com gírias."
    },
    {
      "spans": [
        {
          "offset": 5551,
          "length": 26
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.0662,
            0.3919,
            3.1901,
            0.39,
            3.1902,
            0.5504,
            1.0663,
            0.5523
          ]
        }
      ],
      "role": "title",
      "content": "ANALISE OS TEXTO A SEGUIR:"
    },
    {
      "spans": [
        {
          "offset": 5578,
          "length": 15
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.5821,
            0.672,
            2.6814,
            0.6807,
            2.6801,
            0.8441,
            1.5808,
            0.8354
          ]
        }
      ],
      "content": "TEXTO I: charge"
    },
    {
      "spans": [
        {
          "offset": 5594,
          "length": 52
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.4418,
            1.1167,
            2.3523,
            1.1186,
            2.3517,
            1.3927,
            1.4412,
            1.3908
          ]
        }
      ],
      "content": "PRONTO, MEU FILHO! AGORA VOCÊ PODE IR PARA A ESCOLA."
    },
    {
      "spans": [
        {
          "offset": 5647,
          "length": 6
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            3.0298,
            2.59,
            3.4622,
            2.5882,
            3.4625,
            2.6648,
            3.0301,
            2.6666
          ]
        }
      ],
      "content": "CIERRE"
    },
    {
      "spans": [
        {
          "offset": 5654,
          "length": 6
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            0.6744,
            2.6823,
            1.2502,
            2.6832,
            1.2501,
            2.7591,
            0.6743,
            2.7582
          ]
        }
      ],
      "content": "Foto b"
    },
    {
      "spans": [
        {
          "offset": 5661,
          "length": 16
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.5663,
            2.8702,
            2.7003,
            2.8778,
            2.6991,
            3.0484,
            1.5651,
            3.0409
          ]
        }
      ],
      "content": "TEXTO II: charge"
    },
    {
      "spans": [
        {
          "offset": 5678,
          "length": 78
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.5866,
            3.2898,
            2.9622,
            3.2798,
            2.9651,
            3.6897,
            1.5895,
            3.6997
          ]
        }
      ],
      "content": "FOFOQUEIRA NÃO, QUERIDA! EU SOU PRODUTORA DE BIOGRAFIAS ORAIS NÃO AUTORIZADAS!"
    },
    {
      "spans": [
        {
          "offset": 5757,
          "length": 5
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            3.2012,
            3.5362,
            3.3869,
            3.5115,
            3.3945,
            3.5685,
            3.2088,
            3.5931
          ]
        }
      ],
      "content": "30.10"
    },
    {
      "spans": [
        {
          "offset": 5763,
          "length": 21
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.3741,
            4.8495,
            2.891,
            4.8578,
            2.8901,
            5.0313,
            1.3731,
            5.023
          ]
        }
      ],
      "content": "TEXTO III: propaganda"
    },
    {
      "spans": [
        {
          "offset": 5785,
          "length": 11
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            0.973,
            5.2341,
            1.8851,
            5.2754,
            1.8727,
            5.5494,
            0.9606,
            5.5082
          ]
        }
      ],
      "content": "5 novidades"
    },
    {
      "spans": [
        {
          "offset": 5797,
          "length": 79
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.0194,
            5.5492,
            2.3817,
            5.4178,
            2.4568,
            6.1962,
            1.0946,
            6.3276
          ]
        }
      ],
      "content": "para deixar você de boca aberta. Fechada Aberta Fechada Aberta Fechada. Aberta."
    },
    {
      "spans": [
        {
          "offset": 5877,
          "length": 5
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.6415,
            6.3733,
            1.6665,
            6.4394,
            1.4537,
            6.5196,
            1.4287,
            6.4535
          ]
        }
      ],
      "content": "LACTA"
    },
    {
      "spans": [
        {
          "offset": 5883,
          "length": 3
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            2.3122,
            6.5082,
            2.5177,
            6.5027,
            2.5205,
            6.6053,
            2.315,
            6.6108
          ]
        }
      ],
      "content": "BIS"
    },
    {
      "spans": [
        {
          "offset": 5887,
          "length": 3
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.9291,
            6.6455,
            1.98,
            6.7417,
            1.7322,
            6.8726,
            1.6813,
            6.7764
          ]
        }
      ],
      "content": "BIS"
    },
    {
      "spans": [
        {
          "offset": 5891,
          "length": 5
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            0.8822,
            6.7683,
            1.2113,
            6.7233,
            1.2261,
            6.8321,
            0.897,
            6.8771
          ]
        }
      ],
      "content": "LACTA"
    },
    {
      "spans": [
        {
          "offset": 5897,
          "length": 20
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.3655,
            7.1118,
            2.9002,
            7.1192,
            2.8994,
            7.2946,
            1.3646,
            7.2872
          ]
        }
      ],
      "content": "TEXTO IV: propaganda"
    },
    {
      "spans": [
        {
          "offset": 5918,
          "length": 75
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.1523,
            7.4684,
            3.2099,
            7.4448,
            3.2132,
            7.7274,
            1.1555,
            7.751
          ]
        }
      ],
      "content": "Mãe, uma flor, uma Fonte de luz. um sorriso, uma vida, um recomeço de amar."
    },
    {
      "spans": [
        {
          "offset": 5994,
          "length": 18
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            1.6725,
            7.8205,
            3.2359,
            7.8482,
            3.2321,
            8.0636,
            1.6686,
            8.0359
          ]
        }
      ],
      "content": "Feliz Dia das Mães"
    },
    {
      "spans": [
        {
          "offset": 6013,
          "length": 10
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            2.2389,
            9.78,
            3.1678,
            9.781,
            3.1677,
            9.9132,
            2.2388,
            9.9123
          ]
        }
      ],
      "content": "MAZZARELLO"
    },
    {
      "spans": [
        {
          "offset": 6024,
          "length": 29
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            2.247,
            9.9735,
            3.169,
            9.9775,
            3.1686,
            10.0591,
            2.2467,
            10.055
          ]
        }
      ],
      "content": "2971-4700 - marrerelis.com.br"
    },
    {
      "spans": [
        {
          "offset": 6054,
          "length": 277
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            0.3789,
            10.2241,
            3.8963,
            10.2375,
            3.8926,
            11.2135,
            0.3752,
            11.2001
          ]
        }
      ],
      "content": "QUESTÃO 04. As figuras de linguagem são recursos estilísticos usados para ilustrar o enunciado, tornar a comunicação mais expressiva. Nos textos I, II, III e IV, para atrair a atenção do(a) interlocutor(a), foram usadas, RESPECTIVAMETE, quais figuras de linguagem? (4,0 pontos)"
    },
    {
      "spans": [
        {
          "offset": 6332,
          "length": 60
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            4.3629,
            1.5401,
            7.8783,
            1.5448,
            7.8778,
            1.8767,
            4.3624,
            1.872
          ]
        }
      ],
      "content": "Analise a tirinha a seguir para responder à próxima questão:"
    },
    {
      "spans": [
        {
          "offset": 6393,
          "length": 42
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            4.9389,
            2.0234,
            6.1396,
            2.0254,
            6.1388,
            2.4355,
            4.9382,
            2.4335
          ]
        }
      ],
      "content": "PISO NACIONAL DOS PROFESSORES AUMENTA PARA"
    },
    {
      "spans": [
        {
          "offset": 6436,
          "length": 17
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.9439,
            2.0336,
            7.3904,
            2.0345,
            7.39,
            2.2366,
            6.9435,
            2.2357
          ]
        }
      ],
      "content": "PUXA! QUE ÓTIMO !"
    },
    {
      "spans": [
        {
          "offset": 6454,
          "length": 11
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            5.0004,
            2.4902,
            6.0739,
            2.4933,
            6.0732,
            2.7284,
            4.9998,
            2.7254
          ]
        }
      ],
      "content": "R$ 1.450,00"
    },
    {
      "spans": [
        {
          "offset": 6466,
          "length": 7
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.1048,
            2.9029,
            6.1692,
            2.8991,
            6.18,
            3.0826,
            6.1156,
            3.0864
          ]
        }
      ],
      "content": "Aluguel"
    },
    {
      "spans": [
        {
          "offset": 6474,
          "length": 22
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.1793,
            2.8453,
            6.3248,
            2.836,
            6.3428,
            3.1181,
            6.1973,
            3.1274
          ]
        }
      ],
      "content": "Transporte Alimentação"
    },
    {
      "spans": [
        {
          "offset": 6497,
          "length": 12
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.9225,
            2.8592,
            6.9876,
            2.8596,
            6.9858,
            3.1343,
            6.9207,
            3.1338
          ]
        }
      ],
      "content": "profissional"
    },
    {
      "spans": [
        {
          "offset": 6510,
          "length": 11
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            7.0059,
            2.8624,
            7.0711,
            2.8638,
            7.065,
            3.1381,
            6.9998,
            3.1367
          ]
        }
      ],
      "content": "Atualização"
    },
    {
      "spans": [
        {
          "offset": 6522,
          "length": 6
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.0738,
            3.3401,
            6.1346,
            3.3355,
            6.147,
            3.4992,
            6.0863,
            3.5038
          ]
        }
      ],
      "content": "Livros"
    },
    {
      "spans": [
        {
          "offset": 6529,
          "length": 9
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.148,
            3.2983,
            6.2165,
            3.2918,
            6.2379,
            3.5156,
            6.1694,
            3.5222
          ]
        }
      ],
      "content": "Material,"
    },
    {
      "spans": [
        {
          "offset": 6539,
          "length": 4
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.248,
            3.3487,
            6.3087,
            3.3442,
            6.3161,
            3.4443,
            6.2554,
            3.4488
          ]
        }
      ],
      "content": "Etc."
    },
    {
      "spans": [
        {
          "offset": 6544,
          "length": 5
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.698,
            3.353,
            6.7548,
            3.3522,
            6.757,
            3.4999,
            6.7002,
            3.5007
          ]
        }
      ],
      "content": "Saude"
    },
    {
      "spans": [
        {
          "offset": 6550,
          "length": 7
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.7723,
            3.3607,
            6.8317,
            3.3574,
            6.8414,
            3.5336,
            6.7821,
            3.5369
          ]
        }
      ],
      "content": "Lano de"
    },
    {
      "spans": [
        {
          "offset": 6558,
          "length": 9
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.8554,
            3.3141,
            6.9196,
            3.3158,
            6.9138,
            3.5398,
            6.8496,
            3.5381
          ]
        }
      ],
      "content": "Telefone."
    },
    {
      "spans": [
        {
          "offset": 6568,
          "length": 9
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.9312,
            3.3093,
            6.9965,
            3.3103,
            6.993,
            3.5439,
            6.9278,
            3.5429
          ]
        }
      ],
      "content": "Luz, Gas,"
    },
    {
      "spans": [
        {
          "offset": 6578,
          "length": 9
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            7.0111,
            3.3019,
            7.0759,
            3.3034,
            7.0697,
            3.5557,
            7.005,
            3.5541
          ]
        }
      ],
      "content": "Contas de"
    },
    {
      "spans": [
        {
          "offset": 6588,
          "length": 167
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            4.3622,
            4.0893,
            7.8794,
            4.1033,
            7.8767,
            4.7689,
            4.3596,
            4.7549
          ]
        }
      ],
      "content": "QUESTÃO 05. Por que é possível afirmar que o cartunista Mariano, utilizou a figura de linguagem ironia para produzir o efeito humorístico na charge acima? (5,0 pontos)"
    },
    {
      "spans": [
        {
          "offset": 6756,
          "length": 55
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            4.3624,
            6.0076,
            7.8783,
            6.0088,
            7.8782,
            6.3414,
            4.3622,
            6.3402
          ]
        }
      ],
      "content": "Leia o texto a seguir para responder à próxima questão:"
    },
    {
      "spans": [
        {
          "offset": 6812,
          "length": 20
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.385,
            6.6786,
            7.1719,
            6.6816,
            7.1701,
            7.1434,
            6.3833,
            7.1404
          ]
        }
      ],
      "content": "A VIDA PEDE PASSAGEM"
    },
    {
      "spans": [
        {
          "offset": 6833,
          "length": 31
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.6026,
            7.2117,
            7.6586,
            7.2141,
            7.6584,
            7.3109,
            6.6024,
            7.3085
          ]
        }
      ],
      "content": "NO TRANSITO, DÊ A PHIET CIÊNCIA"
    },
    {
      "spans": [
        {
          "offset": 6865,
          "length": 1
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.294,
            7.6182,
            6.3582,
            7.6185,
            6.3578,
            7.7029,
            6.2936,
            7.7026
          ]
        }
      ],
      "content": "2"
    },
    {
      "spans": [
        {
          "offset": 6867,
          "length": 53
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            6.3872,
            7.5681,
            7.0082,
            7.563,
            7.0099,
            7.7629,
            6.3889,
            7.768
          ]
        }
      ],
      "content": "FREFUTURA DE FRANCISCO BELTRÃO SHARUCH DOS LAVOSA CHE"
    },
    {
      "spans": [
        {
          "offset": 6921,
          "length": 293
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            4.3619,
            7.9171,
            7.8761,
            7.9174,
            7.876,
            8.9011,
            4.3618,
            8.9007
          ]
        }
      ],
      "content": "QUESTÃO 06. Com o intuito de alertar sobre a preferência para os veículos de emergência no trânsito, a cidade de Francisco Beltrão utiliza a frase: \"A vida pede passagem\". Por que se pode afirmar que a propaganda em questão emprega a figura de linguagem denominada personificação? (5,0 pontos)"
    },
    {
      "spans": [
        {
          "offset": 7215,
          "length": 422
        }
      ],
      "boundingRegions": [
        {
          "pageNumber": 2,
          "polygon": [
            4.3617,
            9.9933,
            7.8792,
            10.002,
            7.876,
            11.2878,
            4.3586,
            11.2792
          ]
        }
      ],
      "content": "QUESTÃO 07. A hipérbole e o eufemismo são duas figuras de linguagem contrárias em relação à definição. A partir dessa informação, analise a linguagem verbal e não verbal das propagandas abaixo; observe o que elas divulgam, identifique o uso de eufemismo ou hipérbole e, por fim, justifique, para cada uma delas, o objetivo, o motivo de usarem tais figuras de linguagem para a construção de sentido dos textos. (6,0 pontos)"
    }
  ]

```