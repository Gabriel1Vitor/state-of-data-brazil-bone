# State of Data Brazil — dados abertos + skill para Claude Code

As **6 edições do State of Data Brazil** (2019 a 2025/26), a maior pesquisa sobre o
mercado de trabalho em dados e IA no Brasil, feita pela [Data Hackers](https://datahackers.com.br)
em parceria com a Bain & Company. São mais de 22 mil respostas, com as colunas
**harmonizadas entre edições**, e uma skill para o [Claude Code](https://claude.com/claude-code)
que responde perguntas cruzando os anos.

**Relatórios feitos com a skill:** https://data-hackers-br.github.io/state-of-data-brazil/

- [O paradoxo do salário real](https://data-hackers-br.github.io/state-of-data-brazil/salario-real.html): a mediana geral subiu 20% acima da inflação desde 2021, mas o salário real do Júnior caiu 14%.
- [A volta ao escritório](https://data-hackers-br.github.io/state-of-data-brazil/volta-ao-escritorio.html): a presença obrigatória foi de 24% para 41% dos profissionais.
- [Radar State of Data](https://data-hackers-br.github.io/state-of-data-brazil/radar.html): painel com salários, carreira, tecnologia, IA generativa e diversidade.

## Como usar

Você precisa do Claude Code e de Python 3.9 ou mais recente. Os dados já estão no
repositório: não é preciso conta nem token do Kaggle.

```bash
git clone https://github.com/data-hackers-br/state-of-data-brazil.git
cd state-of-data-brazil
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
claude
```

Dentro do Claude Code, chame a skill com a sua pergunta:

```
/state-of-data-analyst como evoluiu o salário de cientistas de dados por nível desde 2021?
/state-of-data-analyst mulheres e homens com a mesma experiência ganham o mesmo?
/state-of-data-analyst quais linguagens cresceram mais entre analistas de dados?
```

A skill lê os dados locais, usa o mapeamento de colunas entre edições e as funções de
`scripts/sod/`, e responde com os números, o tamanho de cada amostra e as ressalvas de
metodologia.

### Sem Claude Code

A base harmonizada é um CSV comum:

```python
import pandas as pd
df = pd.read_csv("data/harmonized/state_of_data_harmonized.csv", low_memory=False)
df.groupby("ano").nivel.value_counts(normalize=True)
```

Salários vêm em faixas: para medianas, use `scripts/sod/stats.py` (interpolação dentro
da faixa e correção pelo IPCA).

## O que tem aqui

| Caminho | Conteúdo |
|---|---|
| `data/raw/<edição>/` | CSVs originais de cada edição, idênticos aos do Kaggle |
| `data/harmonized/state_of_data_harmonized.csv` | Base combinada: uma linha por respondente, colunas canônicas + derivadas |
| `data/reference/ipca_mensal.json` | IPCA mensal (IBGE), para corrigir salários pela inflação |
| `mapping/schema_map.yaml` | Nome de cada coluna em cada edição, problemas conhecidos dos dados e notas de metodologia |
| `scripts/sod/` | Funções de leitura, mediana em faixas salariais, IPCA e agrupamentos |
| `scripts/harmonize.py` | Gera a base harmonizada |
| `scripts/reports/` + `reports/templates/` | Cálculos e páginas dos relatórios publicados |
| `docs/` | Site dos relatórios (GitHub Pages) |
| `.claude/skills/state-of-data-analyst/` | A skill do Claude Code |

Para regenerar a base e os relatórios: `python scripts/build_reports.py`.

## Cuidados ao comparar edições

As perguntas e opções mudam de uma edição para outra. Os principais pontos estão em
`mapping/schema_map.yaml`; os mais importantes:

- **A amostra não é aleatória**: são as pessoas que responderam à pesquisa, e o perfil
  muda a cada ano (por exemplo, cada vez menos juniores). Compare dentro de grupos.
- **Salário vem em faixas**; a faixa mais alta ("acima de R$ 40k") não tem teto.
- **2019** usou outro questionário: não tem nível Jr/Pl/Sr e a faixa salarial vai até R$ 25k.
- **Especialista/Staff+** só existe a partir de 2025/26.
- **Correções nos dados**: em 2023 as colunas de cloud estão com os rótulos trocados; em
  2022 as colunas binárias de cloud registram a cloud preferida, não a usada. As funções
  de `scripts/sod/` já tratam esses casos.

## Contribuindo

Sugestões de análise, correções no mapeamento e novos relatórios são bem-vindos. Abra
uma issue ou um pull request. Mudanças em `mapping/schema_map.yaml` devem dizer em quais
edições a coluna foi conferida.

## Licença e citação

- **Dados**: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br). Uso livre com crédito, exceto para fins comerciais; versões modificadas dos dados devem manter a mesma licença. Detalhes e forma de citar em [`DATA_LICENSE.md`](DATA_LICENSE.md).
- **Código**: MIT ([`LICENSE`](LICENSE)).

> State of Data Brazil, edições 2019 a 2025/26. Data Hackers (em parceria com a Bain & Company a partir de 2021). Licença CC BY-NC-SA 4.0.

---

## English summary

Open data from the **State of Data Brazil** survey by Data Hackers: 6 editions
(2019–2025/26), 22k+ responses from data and AI professionals in Brazil, with columns
harmonized across editions. It ships with a [Claude Code](https://claude.com/claude-code)
skill (`/state-of-data-analyst`) that answers questions across years. It handles
salary bands, inflation adjustment (IPCA), and known data quirks. Clone the repo, run
`pip install -r requirements.txt`, open `claude` in the folder and ask. The survey
questions and data are in Portuguese. Data license: CC BY-NC-SA 4.0 (non-commercial, with
attribution, share-alike). Code: MIT.
