---
name: state-of-data-analyst
description: >
  Analisa e cruza as 6 edições da pesquisa **State of Data Brazil** (Data Hackers, 2019 a
  2025/26) — carreira, cargos, senioridade, salários, modelo de trabalho, tecnologias,
  IA generativa e diversidade na área de dados e IA no Brasil. Os dados já estão no
  repositório (data/raw/), com colunas harmonizadas entre edições via
  mapping/schema_map.yaml e funções prontas em scripts/sod/ (mediana em faixas salariais,
  correção pelo IPCA, agrupamentos). Responde perguntas comparativas entre anos.

  Use quando o usuário pedir para analisar o State of Data Brazil, comparar edições da
  pesquisa Data Hackers, ver evolução de salários/cargos/modelo de trabalho na área de
  dados no Brasil, ou cruzar informações entre os anos da pesquisa.

user-invokable: true
argument-hint: "<pergunta sobre carreira/salários na área de dados no Brasil>"
---

# State of Data Brazil — Analyst

Esta skill trabalha **só** com as 6 edições do State of Data Brazil que estão em
`data/raw/`. Não busque nem baixe outros datasets.

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

1. Use o Python do ambiente do projeto (`.venv/bin/python`, ou `python3` com
   `pip install -r requirements.txt` feito). Se as dependências faltarem, peça ao
   usuário para rodar a instalação do README.
2. Se `data/harmonized/state_of_data_harmonized.csv` não existir, gere com
   `python scripts/harmonize.py`.
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
import sys; sys.path.insert(0, "scripts")
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
- **2019** só é comparável em poucas perguntas (gênero, situação de trabalho). Não há
  nível Jr/Pl/Sr e a faixa salarial vai só até R$ 25k.
- **Staff+** só existe em 2025/26. Para comparar Sênior com anos anteriores, some Sênior + Staff+.
- Campos com `status: proposed` podem ser usados; se a conclusão depender de um deles,
  diga isso nas ressalvas.

Salve gráficos e arquivos de trabalho em `data/scratch/` (ignorado pelo git). Se o
usuário quiser algo apresentável, siga a skill `dataviz` antes de montar o gráfico.

### 4. Resumir
Feche em português: principais achados com os números, a tendência mais forte e as
ressalvas metodológicas relevantes. A amostra não é aleatória: é quem respondeu à
pesquisa da Data Hackers, o que pode enviesar pelo canal de divulgação.

## Nova edição da pesquisa
Quando sair uma edição nova, o usuário pode baixá-la do Kaggle (manualmente ou pelo
servidor MCP `kaggle`, configurado em `.mcp.json`) para `data/raw/<ano>/`. Depois:
adicionar a edição em `editions:` no schema, mapear as colunas de cada campo (confirmando
os casos ambíguos) e rodar `python scripts/harmonize.py`.

## Regras
- Nunca invente valores de coluna ou estatística: leia sempre dos arquivos.
- Nunca altere os CSVs de `data/raw/`; eles são cópias fiéis do Kaggle.
- Nunca faça upload nem altere datasets no Kaggle.
- Ao publicar resultados, cite a fonte: "State of Data Brazil, Data Hackers — CC BY-NC-SA 4.0".
