"""Leitura dos CSVs brutos e do mapeamento canônico (mapping/schema_map.yaml)."""
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "mapping" / "schema_map.yaml"


@lru_cache(maxsize=1)
def schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def editions():
    """Chaves das edições em ordem cronológica: '2019', '2021', ..., '2025-2026'."""
    return list(schema()["editions"])


def label(ed):
    """Rótulo de exibição da edição ('2024-2025' -> '2024/25')."""
    return schema()["editions"][ed]["label"]


@lru_cache(maxsize=None)
def raw(ed):
    """DataFrame bruto de uma edição, exatamente como publicado no Kaggle."""
    path = ROOT / schema()["editions"][ed]["file"]
    return pd.read_csv(path, low_memory=False)


def column(ed, field):
    """Série de um campo canônico numa edição (toda nula se a edição não tem a pergunta).

    Rótulos antigos são convertidos para o formato recente pelo `value_maps` do schema
    (mapa da edição e, se houver, o mapa "*", que vale para todas).
    """
    col = schema()["fields"][field]["columns"].get(ed)
    df = raw(ed)
    if col is None:
        return pd.Series(np.nan, index=df.index, name=field)
    s = df[col].rename(field)
    maps = (schema().get("value_maps") or {}).get(field, {})
    mapping = {**maps.get("*", {}), **maps.get(ed, {})}
    return s.replace(mapping) if mapping else s


def frame(fields, eds=None):
    """Base empilhada (uma linha por respondente) com colunas canônicas + 'edicao' e 'ano'."""
    parts = []
    for ed in eds or editions():
        f = pd.DataFrame({k: column(ed, k).values for k in fields})
        f.insert(0, "ano", label(ed))
        f.insert(0, "edicao", ed)
        parts.append(f)
    return pd.concat(parts, ignore_index=True)


def _option_label(col, prefix):
    m = re.match(r"\('[^']*', '(.*)'\)", col)
    if m:  # 2019-2023: tupla ('P4_d_3 ', 'Python')
        return m.group(1).strip()
    return col[len(prefix):].split("_", 1)[-1].strip()  # 2024+: '4.d.3_Python'


def multiselect(ed, name):
    """Colunas binárias de uma pergunta multi-seleção, com os rótulos já corrigidos.

    Retorna None se a pergunta não for comparável naquela edição (prefixo null no
    schema). Os rótulos seguem o formato das edições recentes: as edições antigas são
    convertidas pelo mapa `labels` do schema, e opções sem equivalente ficam de fora. Linhas que não marcaram nenhuma opção ficam com zeros: use
    `answered = df.sum(axis=1) > 0` como denominador.
    """
    spec = schema()["multiselect"][name]
    prefix = spec["prefix"].get(ed)
    if prefix is None:
        return None
    df = raw(ed)
    cols = [c for c in df.columns if c.startswith(prefix)
            and not re.match(r"\('P4_[a-z]_[a-z]_", c)]  # 2021 tem subperguntas aninhadas
    fixes = (spec.get("fixes") or {}).get(ed, {})
    labels = (spec.get("labels") or {}).get(ed, {})  # rótulos antigos -> formato recente
    out = {}
    for c in cols:
        lab = _option_label(c, prefix)
        lab = fixes.get(lab, lab)
        if lab in labels:
            if labels[lab] is None:  # opção sem equivalente nas edições recentes
                continue
            lab = labels[lab]
        v = df[c].fillna(0).astype(float)
        out[lab] = np.maximum(out[lab], v) if lab in out else v
    return pd.DataFrame(out)


def multiselect_text(ed, name):
    """Texto bruto de uma multi-seleção quando o dataset não traz colunas binárias confiáveis."""
    col = (schema()["multiselect"][name].get("text_column") or {}).get(ed)
    return None if col is None else raw(ed)[col]
