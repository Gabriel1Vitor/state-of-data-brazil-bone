# Licença dos dados

Os dados deste repositório (`data/raw/`, `data/harmonized/` e `reports/data/`) são
publicados pela **Data Hackers** sob a licença
**[Creative Commons Atribuição-NãoComercial-CompartilhaIgual 4.0 Internacional (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.pt-br)**.

Você pode copiar, redistribuir, adaptar e criar análises a partir dos dados, desde que:

- **dê o crédito**, citando a fonte como abaixo e indicando se fez alterações;
- **não use para fins comerciais** (por exemplo, revender os dados ou usá-los em um
  produto ou serviço pago). Para uso comercial, fale com a Data Hackers:
  falecom@datahackers.com.br;
- **compartilhe pela mesma licença**: se você distribuir uma versão modificada ou uma
  base derivada dos dados, ela também precisa ser publicada sob CC BY-NC-SA 4.0.
  Análises, gráficos e relatórios feitos com os dados podem ter a licença que você quiser,
  desde que deem o crédito.

## Como citar

> State of Data Brazil, edições 2019 a 2025/26. Data Hackers (em parceria com a Bain &
> Company a partir de 2021). Disponível em https://github.com/data-hackers-br/state-of-data-brazil.
> Licença CC BY-NC-SA 4.0.

## Edições incluídas

| Edição  | Arquivo                                          | Período de coleta        | Respostas | Dataset original no Kaggle |
|---------|--------------------------------------------------|--------------------------|-----------|----------------------------|
| 2019    | `data/raw/2019/data_hackers_survey_2019.csv`     | novembro de 2019         | 1.765     | [datahackers/pesquisa-data-hackers-2019](https://www.kaggle.com/datasets/datahackers/pesquisa-data-hackers-2019) |
| 2021    | `data/raw/2021/state_of_data_2021.csv`           | 18/out a 6/dez de 2021   | 2.645     | [datahackers/state-of-data-2021](https://www.kaggle.com/datasets/datahackers/state-of-data-2021) |
| 2022    | `data/raw/2022/state_of_data_2022.csv`           | 10/out a 28/nov de 2022  | 4.271     | [datahackers/state-of-data-2022](https://www.kaggle.com/datasets/datahackers/state-of-data-2022) |
| 2023    | `data/raw/2023/state_of_data_2023.csv`           | 16/out a 6/dez de 2023   | 5.293     | [datahackers/state-of-data-brazil-2023](https://www.kaggle.com/datasets/datahackers/state-of-data-brazil-2023) |
| 2024/25 | `data/raw/2024-2025/state_of_data_2024_2025.csv` | 14/out a 18/dez de 2024  | 5.217     | [datahackers/state-of-data-brazil-20242025](https://www.kaggle.com/datasets/datahackers/state-of-data-brazil-20242025) |
| 2025/26 | `data/raw/2025-2026/state_of_data_2025_2026.csv` | 20/out a 22/dez de 2025  | 3.495     | [datahackers/state-of-data-brazil-2025-2026](https://www.kaggle.com/datasets/datahackers/state-of-data-brazil-2025-2026) |

Os CSVs são idênticos aos publicados no Kaggle; só os nomes dos arquivos mudaram.
Os dados foram anonimizados pela Data Hackers antes da publicação (alguns outliers
removidos e estados com poucas respostas agregados por região).

## Histórico de licenças

Até outubro de 2026, as edições no Kaggle usavam licenças diferentes (CC BY-NC-SA 4.0,
CC BY-NC-SA 3.0 IGO, CC BY-NC 4.0 e ODbL 1.0). Para permitir uma base combinada única,
a Data Hackers, detentora dos dados, passou a licenciar todas as edições sob
CC BY-NC-SA 4.0, aqui e no Kaggle.
Cópias obtidas antes dessa mudança continuam válidas sob a licença original.

## Dados de referência

`data/reference/ipca_mensal.json` traz o IPCA mensal do IBGE (SIDRA, tabela 1737,
variável 63), usado para corrigir salários pela inflação. É informação pública do IBGE.

O código do repositório (pasta `scripts/`, templates e skill) usa outra licença: veja `LICENSE`.
