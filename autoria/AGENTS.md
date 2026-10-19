# Autoria de desafios do kata

Este diretório é a fonte dos desafios. O app nunca lê daqui: ele usa só `data/desafios.db`,
gerado por `autoria/build.py`, que guarda os casos ocultos como **hash** da saída esperada.
As soluções de referência (`solucao.py`) só existem aqui. **O usuário combinou consigo mesmo
não abrir esta pasta.** Não cole soluções em conversas, commits ou mensagens que ele vá ler.

## Regras do kata (o que um desafio precisa respeitar)

- Um desafio por dia, 10–20 minutos para quem está no nível. Foco é lógica, não API.
- Enunciado curto: 2–4 linhas, sem história, sem enrolação. Use `código` entre crases.
- A progressão é contínua: cada desafio deve se apoiar em algo anterior, declarado em `usa`.
  O app mostra esses desafios como atalhos para a solução que o próprio usuário escreveu.
- 10 arcos de 10 dias. O dia 7 de cada arco é revisão (mistura conceitos); o dia 10 é o chefão.
  Arcos: 1 condicionais · 2 laços · 3 strings · 4 listas · 5 dicionários/conjuntos ·
  6 recursão · 7 busca e ordenação · 8 dois ponteiros/janela/prefixo · 9 pilha/fila/matriz/grade ·
  10 guloso e programação dinâmica. Desafios a partir do 101 podem abrir novos arcos.

## Estrutura de um desafio

```
autoria/desafios/NNN-slug/
  desafio.toml     metadados, enunciado, exemplos, testes, dicas, conceito
  solucao.py       def resolver(...) de referência (nunca vai para o banco)
  gerador.py       opcional: def gerar(rng) -> [entradas]  (rng = random.Random(id))
```

A pasta se chama exatamente `{id:03d}-{slug}`. Os ids são contínuos (1..N, sem buracos).

### desafio.toml

```toml
id = 101
slug = "exemplo"
titulo = "Título curto"
arco = 11                 # (id - 1) // 10 + 1
nivel = 5                 # 1–10, sobe devagar dentro do arco
tags = ["listas", "laço"]
usa = [31, 45]            # só ids anteriores
assinatura = "def resolver(nums: list, alvo: int) -> int"   # sem ':' no fim
enunciado = """
Duas a quatro linhas. `código` entre crases.
"""
exemplos = [              # visíveis: o app mostra entrada → saída
  { entrada = [[1, 2, 3], 4] },     # entrada = lista de argumentos de resolver
]
testes = [                # ocultos (ou use gerador.py, ou ambos); mínimo 5
  [[], 0],
  [[5], 5],
]
dicas = [                 # exatamente 3, da mais leve à mais direta
  "Uma pergunta que aponta a direção.",
  "A ideia/estrutura certa.",
  "Quase o código.",
]
referencias = [           # liberadas depois de resolver
  { titulo = "Nome da página", url = "https://..." },
]
conceito = """
Um parágrafo curto: por que funciona, onde isso aparece no mundo real.
Quebras de linha simples viram espaço.
"""
[criterios]               # opcional
proibido = ["sorted", "sort"]   # nomes/atributos/imports barrados por AST
recursivo = true                # exige uma função que chama a si mesma
tempo = 4                       # segundos para todos os casos (padrão 5)
```

`saida` nos exemplos é opcional; se presente, o build confere com a solução.

## Validação

```
python3 autoria/build.py          # valida tudo e grava data/desafios.db
python3 autoria/build.py --so 101 # valida só um, sem gravar
```

O build recusa o desafio quando:
- falta campo, a pasta tem nome errado, `usa` aponta para o futuro ou não há 3 dicas;
- a solução de referência quebra os próprios `criterios`, dá erro ou estoura o tempo;
- a saída não é determinística (roda duas vezes);
- o esqueleto vazio (`pass`) passa em todos os casos;
- todos os casos ocultos têm a mesma resposta (dá para chutar);
- os ids não são contínuos.

## Boas práticas

- Inclua casos de borda nos ocultos: vazio, um elemento, negativos, repetidos, limites.
- Quando o objetivo é a complexidade (busca binária, janela, DP), use `gerador.py` com entradas
  grandes e um `tempo` que reprova a solução ingênua mas aprova a esperada com folga (teste as duas).
- Retornos devem ser `int`, `float`, `str`, `bool`, `list`, `dict` ou `None`. Tuplas viram listas;
  floats são arredondados em 6 casas. Para conjuntos, peça uma lista ordenada.
- Quando a resposta pode variar (vários pares válidos etc.), especifique o desempate no enunciado.
- Prefira português sem acentos nas strings de saída (`"impar"`, `"invalido"`): menos atrito para digitar.
