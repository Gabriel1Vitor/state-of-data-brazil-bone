"""Estatística para salários em faixas e correção pela inflação (IPCA)."""
import json
import re
from functools import lru_cache

import numpy as np
import pandas as pd

from .data import ROOT

# Rótulos com erro de digitação no dataset (uma linha cada).
_BAND_FIXES = {
    "de R$ 101/mês a R$ 2.000/mês": "de R$ 1.001/mês a R$ 2.000/mês",
    "de R$ 25.001/mês a R$ 3000/mês": "de R$ 25.001/mês a R$ 30.000/mês",
}


def band_bounds(label):
    """Limites (inferior, superior) em R$ de uma faixa salarial. A faixa aberta do topo tem superior = inf."""
    if pd.isna(label):
        return (np.nan, np.nan)
    label = _BAND_FIXES.get(label, label)
    nums = [float(x.replace(".", "")) for x in re.findall(r"R\$ ([\d.]+)", label)]
    if label.startswith("Menos"):
        return (0.0, nums[0])
    if label.startswith("Acima"):
        return (nums[0] - 1, np.inf)
    return (nums[0] - 1, nums[1])


def add_bounds(df, col="salario_faixa"):
    b = df[col].map(band_bounds)
    return df.assign(sal_min=[x[0] for x in b], sal_max=[x[1] for x in b])


def band_quantile(df, p=0.5, min_n=30):
    """Quantil interpolado linearmente dentro da faixa (colunas sal_min/sal_max).

    Retorna None com menos de `min_n` respostas. Se o quantil cair na faixa aberta do
    topo, retorna o limite inferior dela (o valor real é maior ou igual).
    """
    g = df.dropna(subset=["sal_min"])
    n = len(g)
    if n < min_n:
        return None
    counts = g.groupby(["sal_min", "sal_max"]).size().sort_index()
    target, cum = n * p, 0
    for (lo, hi), k in counts.items():
        if cum + k >= target:
            return round(lo if np.isinf(hi) else lo + (target - cum) / k * (hi - lo))
        cum += k


def median(df, min_n=30):
    return band_quantile(df, 0.5, min_n)


@lru_cache(maxsize=1)
def _ipca_index():
    with open(ROOT / "data" / "reference" / "ipca_mensal.json", encoding="utf-8") as f:
        monthly = json.load(f)["mensal"]
    idx, out = 1.0, {}
    for month, pct in sorted(monthly.items()):
        idx *= 1 + pct / 100
        out[month] = idx
    return out


# Mês de referência de preços de cada edição (meio do período de coleta, out–dez).
REFERENCE_MONTH = {"2021": "2021-11", "2022": "2022-11", "2023": "2023-11",
                   "2024/25": "2024-11", "2025/26": "2025-11"}


def deflator(ano, base="2025/26"):
    """Fator que leva R$ da edição `ano` para R$ do mês de referência de `base`."""
    i = _ipca_index()
    return i[REFERENCE_MONTH[base]] / i[REFERENCE_MONTH[ano]]


def ipca_accumulated(start="2021", end="2025/26"):
    i = _ipca_index()
    return (i[REFERENCE_MONTH[end]] / i[REFERENCE_MONTH[start]] - 1) * 100
