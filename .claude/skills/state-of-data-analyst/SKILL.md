---
name: state-of-data-analyst
description: >
  Analisa e cruza as 6 edições da pesquisa **State of Data Brazil** (Data Hackers, 2019 a
  2025/26) — carreira, cargos, senioridade, salários, modelo de trabalho, tecnologias,
  IA generativa e diversidade na área de dados e IA no Brasil. Usa os dados e o código do
  repositório público data-hackers-br/state-of-data-brazil, com colunas harmonizadas entre
  edições via mapping/schema_map.yaml e funções prontas em scripts/sod/ (mediana em faixas
  salariais, correção pelo IPCA, agrupamentos). Responde perguntas comparativas entre anos.

  Use quando o usuário pedir para analisar o State of Data Brazil, comparar edições da
  pesquisa Data Hackers, ver evolução de salários/cargos/modelo de trabalho na área de
  dados no Brasil, ou cruzar informações entre os anos da pesquisa.

user-invocable: true
argument-hint: "<pergunta sobre carreira/salários na área de dados no Brasil>"
---

# State of Data Brazil — Analista

Esta skill trabalha **só** com as 6 edições do State of Data Brazil do repositório
[data-hackers-br/state-of-data-brazil](https://github.com/data-hackers-br/state-of-data-brazil).
Não busque nem baixe outros datasets.

## Onde estão os arquivos

Os dados e o código (`data/`, `scripts/`, `mapping/`) ficam numa pasta que esta skill
chama de `RAIZ`. Descubra a `RAIZ` nesta ordem e use a primeira que se aplicar:

1. **Plugin do Claude Code:** `${CLAUDE_PLUGIN_ROOT}`. Se esse caminho foi substituído
   pelo Claude Code (não começa com cifrão e chaves) e contém `mapping/schema_map.yaml`,
   ele é a `RAIZ`. Não escreva arquivos dentro dela: ela é trocada a cada atualização.
2. **Repositório clonado:** se o projeto aberto contém `mapping/schema_map.yaml` e
   `scripts/sod/`, a `RAIZ` é a pasta do projeto.
3. **Repositório anexado** (por exemplo, no Claude pelo navegador): se o usuário
   forneceu o ZIP deste repositório, extraia-o na pasta de trabalho da sessão e use
   como `RAIZ` a pasta interna que contém `mapping/schema_map.yaml`, `scripts/sod/`
   e `data/`. O ZIP do GitHub tem uma pasta externa `state-of-data-brazil-<revisão>`;
   não confunda a pasta de extração com a raiz do projeto. Reutilize uma extração
   válida já disponível na sessão, sem baixar outra cópia.
4. **Skill instalada sozinha** (por `npx skills`, no Codex ou copiando só esta pasta):
   a `RAIZ` é `~/.cache/state-of-data-brazil`. Se ela não existir, avise o usuário que vai
   baixar uma cópia do repositório público (cerca de 80 MB, uma única vez) e rode
   `git clone --depth 1 https://github.com/data-hackers-br/state-of-data-brazil.git ~/.cache/state-of-data-brazil`.
   Sem `git`, baixe e descompacte
   `https://github.com/data-hackers-br/state-of-data-brazil/archive/refs/heads/main.zip` no
   mesmo lugar, deixando `mapping/`, `scripts/` e `data/` diretamente dentro da
   pasta de cache. Se o ambiente bloquear acesso à rede, explique o bloqueio e peça
   o ZIP como anexo ou indique como executar a análise localmente. Não repita
   tentativas de download sem uma mudança nas condições. Para atualizar um cache
   clonado com Git: `git -C ~/.cache/state-of-data-brazil pull`; se veio de ZIP,
   use uma nova extração.

Antes de analisar, confirme que a `RAIZ` contém `mapping/schema_map.yaml`,
`scripts/sod/` e os arquivos de dados necessários. Uma pasta de cache existente,
mas incompleta, não basta. Se faltar algum arquivo, informe o que falta para
continuar com a cópia completa do repositório.

Todos os caminhos citados daqui em diante são relativos à `RAIZ`.

| Edição  | Chave       | Arquivo                                          | Respostas |
|---------|-------------|--------------------------------------------------|-----------|
| 2019    | `2019`      | `data/raw/2019/data_hackers_survey_2019.csv`     | 1.765     |
| 2021    | `2021`      | `data/raw/2021/state_of_data_2021.csv`           | 2.645     |
| 2022    | `2022`      | `data/raw/2022/state_of_data_2022.csv`           | 4.271     |
| 2023    | `2023`      | `data/raw/2023/state_of_data_2023.csv`           | 5.293     |
| 2024/25 | `2024-2025` | `data/raw/2024-2025/state_of_data_2024_2025.csv` | 5.217     |
| 2025/26 | `2025-2026` | `data/raw/2025-2026/state_of_data_2025_2026.csv` | 3.495     |

Não existe edição 2020 (a pesquisa pulou esse ano).

## Antes de começar

1. **Python com pandas, numpy e pyyaml.**
   - Com repositório anexado: primeiro confira se o Python do ambiente já importa
     `pandas`, `numpy` e `yaml`; para gráficos, confira também `matplotlib`.
     Reutilize esse interpretador quando as dependências estiverem disponíveis.
     Não crie um ambiente vazio que exija downloads em uma sessão sem rede.
     Se faltar uma biblioteca, informe qual é e indique a instalação local com
     `requirements.txt`; o ZIP traz os dados e o código, não as dependências Python.
   - No repositório clonado: use `.venv/bin/python` (ou `python3`, se as dependências
     já estiverem instaladas). Se faltarem, peça ao usuário para rodar a instalação do README.
   - No modo plugin: use um ambiente próprio em `${CLAUDE_PLUGIN_DATA}/venv`, que sobrevive
     a atualizações. Se ele não existir, avise o usuário que vai criá-lo e rode
     `python3 -m venv "${CLAUDE_PLUGIN_DATA}/venv" && "${CLAUDE_PLUGIN_DATA}/venv/bin/pip" install -r "${CLAUDE_PLUGIN_ROOT}/requirements.txt"`.
   - Na skill instalada sozinha: use `~/.cache/state-of-data-brazil/.venv`. Se não existir,
     crie com `python3 -m venv ~/.cache/state-of-data-brazil/.venv` e instale
     `~/.cache/state-of-data-brazil/requirements.txt` com o `pip` desse ambiente.
2. A base harmonizada já vem pronta em `data/harmonized/state_of_data_harmonized.csv`.
   Só no repositório clonado, se ela não existir, gere com `python scripts/harmonize.py`.
3. Leia `mapping/schema_map.yaml` — em especial `methodology_notes` e as `notes` dos
   campos que a pergunta envolve. Ele lista as armadilhas conhecidas dos dados.

## Fluxo de trabalho

### 1. Partir da base harmonizada
`data/harmonized/state_of_data_harmonized.csv` tem uma linha por respondente das 6
edições, com `edicao`, `ano` (rótulo: 2019, 2021, …, 2024/25, 2025/26), os campos
canônicos do schema e colunas derivadas prontas:

- `nivel`: Júnior / Pleno / Sênior / Especialista/Staff+ / Gestor (gestor vem da pergunta "atua como gestor")
- `sal_min`, `sal_max`: limites em R$ da faixa salarial (`sal_max = inf` na faixa aberta do topo)
- `vinculo`: mora no Brasil com empresa brasileira / empresa estrangeira / mora no exterior
- `experiencia_grupo`, `cargo_grupo`, `porte_grupo`, `setor_grupo`, `modelo_atual`, `modelo_ideal`

Para código novo, prefira importar as funções em vez de reescrever a lógica:

```python
import sys; sys.path.insert(0, "<RAIZ>/scripts")
from harmonize import build          # base harmonizada em memória
from sod import data, derive, stats  # data.raw(ed), data.multiselect(ed, nome), stats.median(df), stats.deflator(ano)
```

### 2. Se a pergunta precisar de um campo que não está no schema
Inspecione as colunas e uma amostra de valores em cada edição (`data.raw(ed)`), proponha
o mapeamento e **confirme os casos ambíguos com o usuário** antes de salvar em
`mapping/schema_map.yaml` (com `status: proposed`). Atualize só o que a pergunta exige.
Registre nas `notes` qualquer mudança de opções de resposta entre edições.

Perguntas de múltipla escolha (linguagens, cloud, BI) ficam em `multiselect:` no schema.
Use `data.multiselect(ed, nome)`, que já aplica as correções conhecidas, e use como
denominador quem marcou pelo menos uma opção.

### 3. Analisar
- **Salário:** os valores vêm em faixas. Use `stats.median` / `stats.band_quantile`
  (interpolação dentro da faixa, mínimo de 30 respostas). Nunca use média. Para comparar
  anos em termos reais, multiplique por `stats.deflator(ano)` (R$ de nov/2025, IPCA do IBGE).
- **Separe mercados:** quem trabalha para empresa estrangeira ou mora no exterior ganha
  em outro patamar. Para nível, experiência ou gênero, use só `vinculo == "Mora no Brasil, empresa brasileira"`.
- **Compare dentro de grupos:** o perfil da amostra muda a cada edição (cada vez menos
  juniores). Uma mediana geral pode subir mesmo com todos os níveis caindo. Antes de
  concluir sobre o mercado, confira por nível e por experiência.
- **Informe o N** de cada edição e grupo. Sinalize grupos pequenos.
- **2019** usou outro questionário. Não há nível Jr/Pl/Sr e a faixa salarial vai só até
  R$ 25k, então 2019 fica fora de comparações de salário e senioridade. São comparáveis:
  gênero, situação de trabalho, estado, formação, porte da empresa, cargo, tempo de
  experiência (em grupos) e linguagens, cloud e BI (já convertidos para os rótulos
  recentes). Região também, com a ressalva de que 2019 só identifica Sudeste e Sul.
- **Staff+** só existe em 2025/26. Para comparar Sênior com anos anteriores, some Sênior + Staff+.
- Campos com `status: proposed` podem ser usados; se a conclusão depender de um deles,
  diga isso nas ressalvas.

Salve gráficos e arquivos de trabalho em `data/scratch/` no repositório clonado (ignorado
pelo git). No navegador, use a pasta de saídas oferecida pelo ambiente e disponibilize
os arquivos para download. Nos demais modos, use uma pasta `state-of-data/` no diretório
atual do usuário.
Se o usuário quiser algo apresentável e a skill `dataviz` estiver disponível, siga-a
antes de montar o gráfico. Ela é opcional: se não estiver disponível, use Matplotlib,
com título, unidades, N por grupo, fonte e ressalvas relevantes. Confira a imagem
gerada para evitar rótulos sobrepostos ou cortados.

### 4. Resumir
Feche em português: principais achados com os números, a tendência mais forte e as
ressalvas metodológicas relevantes. A amostra não é aleatória: é quem respondeu à
pesquisa da Data Hackers, o que pode enviesar pelo canal de divulgação.

## Nova edição da pesquisa
Isso vale só para quem mantém o repositório clonado. Quando sair uma edição nova, baixe-a
do Kaggle para `data/raw/<ano>/`, manualmente ou pelo servidor MCP do Kaggle
(`claude mcp add --transport http kaggle https://www.kaggle.com/mcp`, com o token pessoal
em escopo `local`, nunca no git). Depois: adicione a edição em `editions:` no schema,
mapeie as colunas de cada campo (confirmando os casos ambíguos) e rode
`python scripts/harmonize.py`.

## Regras
- Nunca invente valores de coluna ou estatística: leia sempre dos arquivos.
- Nunca altere os CSVs de `data/raw/`; eles são cópias fiéis do Kaggle.
- Nunca faça upload nem altere datasets no Kaggle.
- Ao publicar resultados, cite a fonte: "State of Data Brazil, Data Hackers — CC BY-NC-SA 4.0".
