Execução do Caso de uso principal: /analyze/analyze_document

curl -X 'POST' \
 'http://127.0.0.1:8000/analyze/analyze_document?email=wander.bergami%40gmail.com' \
 -H 'accept: application/json' \
 -H 'Content-Type: multipart/form-data' \
 -F 'file=@Recuperacao.pdf;type=application/pdf'

Response:
{
"email": "wander.bergami@gmail.com",
"document_id": "32674f3c-b5c8-4cc3-8c76-d8c716132a60",
"filename": "Recuperacao.pdf",
"header": {
"school": "UMEF Saturnino Rangel Mauro VILA VELHA - ES",
"teacher": "Danielle",
"subject": "Língua Portuguesa",
"student": null,
"series": null
},
"questions": [
{
"number": 1,
"question": "O texto de Marina Colasanti descreve diversas situações do cotidiano da sociedade contemporânea com o objetivo central de fomentar nos(as) leitores(as) uma reflexão a respeito: (2,0 pontos)",
"alternatives": [
{
"letter": "a",
"text": "da velocidade com que a tecnologia influencia na nossa comunicação diária e na vida dos jovens e adultos"
},
{
"letter": "b",
"text": "do desrespeito do ser humano com a vida humilde de pessoas pertencentes a grupos sociais mais pobres na sociedade"
},
{
"letter": "c",
"text": "da rotina cotidiana que nos habitua e muitas vezes não enxergamos como isso nos aprisiona."
},
{
"letter": "d",
"text": "da vida contemporânea que se tornou muito mais prática com tantas atribuições no dia a dia."
}
],
"hasImage": false,
"context_id": null
},
{
"number": 2,
"question": "A expressão \"A gente\", usada por diversas vezes para iniciar os períodos no texto de Marina Colasanti: (2,0 pontos)",
"alternatives": [
{
"letter": "a",
"text": "expressa a falta de conhecimento da autora em relação à formalidade da Língua Portuguesa, pois seria mais adequado se ela escrevesse: Nós nos acostumamos."
},
{
"letter": "b",
"text": "transfere para o(a) interlocutor(a) a responsabilidade de se adaptar a essa linguagem diferente e, provavelmente, desconhecida para a maior parte da população brasileira hoje em dia."
},
{
"letter": "c",
"text": "expressa a liberdade criativa dos autores brasileiros, porque todos usam esse tipo de expressão rebuscada, pouco ouvida na fala cotidiana e, por isso, causa muito estranhamento aos interlocutores desse texto."
},
{
"letter": "d",
"text": "mostra a proximidade da autora com a escrita e seu entendimento da necessidade de usar, no gênero crônica, essa linguagem mais próxima da fala dos interlocutores."
}
],
"hasImage": false,
"context_id": null
},
{
"number": 3,
"question": "O último fragmento do texto de Colasanti diz: \"A gente se acostuma para não se ralar na aspereza, para preservar a pele. Se acostuma para evitar feridas, sangramentos, para esquivar-se de faca e baioneta, para poupar o peito. A gente se acostuma para poupar a vida. Que aos poucos se gasta, e que, gasta de tanto se acostumar, se perde de si mesma\". Esse trecho da crônica foi desenvolvido PREDOMINANTEMENTE utilizando: (2,0 pontos)",
"alternatives": [
{
"letter": "a",
"text": "uma linguagem no sentido conotativo."
},
{
"letter": "b",
"text": "uma linguagem no sentido denotativo."
},
{
"letter": "c",
"text": "uma linguagem regional."
},
{
"letter": "d",
"text": "uma linguagem com gírias."
}
],
"hasImage": false,
"context_id": null
},
{
"number": 4,
"question": "As figuras de linguagem são recursos estilísticos usados para ilustrar o enunciado, tornar a comunicação mais expressiva. Nos textos I, II, III e IV, para atrair a atenção do(a) interlocutor(a), foram usadas, RESPECTIVAMETE, quais figuras de linguagem? (4,0 pontos)",
"alternatives": [],
"hasImage": false,
"context_id": null
},
{
"number": 5,
"question": "Por que é possível afirmar que o cartunista Mariano, utilizou a figura de linguagem ironia para produzir o efeito humorístico na charge acima? (5,0 pontos)",
"alternatives": [],
"hasImage": false,
"context_id": null
},
{
"number": 6,
"question": "Com o intuito de alertar sobre a preferência para os veículos de emergência no trânsito, a cidade de Francisco Beltrão utiliza a frase: \"A vida pede passagem\". Por que se pode afirmar que a propaganda em questão emprega a figura de linguagem denominada personificação? (5,0 pontos)",
"alternatives": [],
"hasImage": false,
"context_id": null
},
{
"number": 7,
"question": "A hipérbole e o eufemismo são duas figuras de linguagem contrárias em relação à definição. A partir dessa informação, analise a linguagem verbal e não verbal das propagandas abaixo; observe o que elas divulgam, identifique o uso de eufemismo ou hipérbole e, por fim, justifique, para cada uma delas, o objetivo, o motivo de usarem tais figuras de linguagem para a construção de sentido dos textos. (6,0 pontos)",
"alternatives": [],
"hasImage": false,
"context_id": null
}
],
"context_blocks": [
{
"id": 1,
"type": [
"text"
],
"source": "exam_document",
"statement": "LEIA O TEXTO A SEGUIR",
"title": "Eu sei, mas não devia (Marina Colasanti)",
"hasImage": false,
"images": [],
"contentType": null,
"paragraphs": [
"Eu sei que a gente se acostuma. Mas não devia. A gente se acostuma a morar em apartamentos de fundos e a não ter outra vista que não as janelas ao redor. E, porque não tem vista, logo se acostuma a não olhar para fora. E, porque não olha para fora, logo se acostuma a não abrir de todo as cortinas. E, porque não abre as cortinas, logo se acostuma a acender mais cedo a luz. E, à medida que se acostuma, esquece o sol, esquece o ar, esquece a amplidão.",
"A gente se acostuma a acordar de manhã sobressaltado porque está na hora. A tomar o café correndo porque está atrasado. A ler o jornal no ônibus porque não pode perder o tempo da viagem. A comer sanduíche porque não dá para almoçar. A sair do trabalho porque já é noite. A cochilar no ônibus porque está cansado. A deitar cedo e dormir pesado sem ter vivido o dia.",
"A gente se acostuma a abrir o jornal e a ler sobre a guerra. E, aceitando a guerra, aceita os mortos e que haja números para os mortos. E, aceitando os números, aceita não acreditar nas negociações de paz. E, não acreditando nas negociações de paz, aceita ler todo dia da guerra, dos números, da longa duração.",
"A gente se acostuma a esperar o dia inteiro e ouvir no telefone: hoje não posso ir. A sorrir para as pessoas sem receber um sorriso de volta. A ser ignorado quando precisava tanto ser visto.",
"A gente se acostuma a pagar por tudo o que deseja e o de que necessita. E a lutar para ganhar o dinheiro com que pagar. E a ganhar menos do que precisa. E a fazer fila para pagar. E a pagar mais do que as coisas valem. E a saber que cada vez pagar mais. E a procurar mais trabalho, para ganhar mais dinheiro, para ter com que pagar nas filas em que se cobra.",
"A gente se acostuma a andar na rua e ver cartazes. A abrir as revistas e ver anúncios. A ligar a televisão e assistir a comerciais. A ir ao cinema e engolir publicidade. A ser instigado, conduzido, desnorteado, lançado na infindável catarata dos produtos.",
"A gente se acostuma à poluição. Às salas fechadas de ar-condicionado e cheiro de cigarro. À luz artificial de ligeiro tremor. Ao choque que os olhos levam na luz natural. Às bactérias da água potável. À contaminação da água do mar. À lenta morte dos rios. Se acostuma a não ouvir passarinho, a não ter galo de madrugada, a temer a hidrofobia dos cães, a não colher fruta no pé, a não ter sequer uma planta.",
"A gente se acostuma a coisas demais, para não sofrer. Em doses pequenas, tentando não perceber, vai afastando uma dor aqui, um ressentimento ali, uma revolta acolá. Se o cinema está cheio, a gente senta na primeira fila e torce um pouco o pescoço. Se a praia está contaminada, a gente molha só os pés e sua no resto do corpo. Se o trabalho está duro, a gente se consola pensando no fim de semana. E se no fim de semana não há muito o que fazer a gente vai dormir cedo e ainda fica satisfeito porque tem sempre sono atrasado.",
"A gente se acostuma para não se ralar na aspereza, para preservar a pele. Se acostuma para evitar feridas, sangramentos, para esquivar-se de faca e baioneta, para poupar o peito. A gente se acostuma para poupar a vida. Que aos poucos se gasta, e que, gasta de tanto se acostumar, se perde de si mesma."
],
"sub_contexts": null
},
{
"id": 2,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 1",
"hasImage": false,
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/1.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
],
"contentType": "image/url",
"paragraphs": [
"LEIA O TEXTO A SEGUIR"
],
"sub_contexts": null
},
{
"id": 3,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 2",
"hasImage": false,
"images": [],
"contentType": null,
"paragraphs": [
"ANALISE OS TEXTO A SEGUIR:",
"TEXTO I: charge",
"PRONTO, MEU FILHO! AGORA VOCÊ PODE IR PARA A ESCOLA.",
"CIERRE",
"Foto b"
],
"sub_contexts": [
{
"sequence": "i",
"type": "text",
"title": "TEXTO i",
"content": "Content for sequence i",
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/2.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
]
}
]
},
{
"id": 4,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 3",
"hasImage": false,
"images": [],
"contentType": null,
"paragraphs": [
"TEXTO II: charge",
"FOFOQUEIRA NÃO, QUERIDA! EU SOU PRODUTORA DE BIOGRAFIAS ORAIS NÃO AUTORIZADAS!",
"30.10",
"TEXTO III: propaganda"
],
"sub_contexts": [
{
"sequence": "ii",
"type": "text",
"title": "TEXTO ii",
"content": "Content for sequence ii",
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/3.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
]
},
{
"sequence": "iii",
"type": "text",
"title": "TEXTO iii",
"content": "Content for sequence iii",
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/3.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
]
}
]
},
{
"id": 5,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 4",
"hasImage": false,
"images": [],
"contentType": null,
"paragraphs": [
"para deixar você de boca aberta. Fechada Aberta Fechada Aberta Fechada. Aberta.",
"LACTA",
"LACTA",
"TEXTO IV: propaganda"
],
"sub_contexts": [
{
"sequence": "iv",
"type": "text",
"title": "TEXTO iv",
"content": "Content for sequence iv",
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/4.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
]
}
]
},
{
"id": 6,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 5",
"hasImage": false,
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/5.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
],
"contentType": "image/url",
"paragraphs": [
"Mãe, uma flor, uma Fonte de luz. um sorriso, uma vida, um recomeço de amar.",
"MAZZARELLO"
],
"sub_contexts": null
},
{
"id": 7,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 6",
"hasImage": false,
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/6.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
],
"contentType": "image/url",
"paragraphs": [
"Analise a tirinha a seguir para responder à próxima questão:",
"Aluguel",
"profissional",
"Livros",
"Saude",
"Lano de",
"Contas de"
],
"sub_contexts": null
},
{
"id": 8,
"type": [
"image"
],
"source": "exam_document",
"statement": null,
"title": "Context 7",
"hasImage": false,
"images": [
"https://crieducstorage.blob.core.windows.net/crieduc-documents/documents/tests/images/32674f3c-b5c8-4cc3-8c76-d8c716132a60/7.jpg?sp=racwdl&st=2025-10-20T16:23:40Z&se=2026-10-21T00:38:40Z&spr=https&sv=2024-11-04&sr=c&sig=0ybRfUveCI7GnHm9DxgR%2Fd82oKDGnXba8QgqaqFkC2M%3D"
],
"contentType": "image/url",
"paragraphs": [
"Leia o texto a seguir para responder à próxima questão:"
],
"sub_contexts": null
},
{
"id": 9,
"type": [
"text"
],
"source": "exam_document",
"statement": null,
"title": "Instructions",
"hasImage": false,
"images": [],
"contentType": null,
"paragraphs": [
"LEIA O TEXTO A SEGUIR",
"ANALISE OS TEXTO A SEGUIR:",
"TEXTO I: charge",
"TEXTO II: charge",
"TEXTO III: propaganda",
"TEXTO IV: propaganda",
"Analise a tirinha a seguir para responder à próxima questão:",
"Leia o texto a seguir para responder à próxima questão:",
"QUESTÃO 07. A hipérbole e o eufemismo são duas figuras de linguagem contrárias em relação à definição. A partir dessa informação, analise a linguagem verbal e não verbal das propagandas abaixo; observe o que elas divulgam, identifique o uso de eufemismo ou hipérbole e, por fim, justifique, para cada uma delas, o objetivo, o motivo de usarem tais figuras de linguagem para a construção de sentido dos textos. (6,0 pontos)"
],
"sub_contexts": null
}
]
}
