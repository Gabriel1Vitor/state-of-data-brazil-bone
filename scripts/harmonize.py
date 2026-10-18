"""Gera a base harmonizada das 6 edições: uma linha por respondente, colunas canônicas.

Uso:  python scripts/harmonize.py
Saída: data/harmonized/state_of_data_harmonized.csv

Os nomes de coluna de cada edição vêm de mapping/schema_map.yaml. As colunas derivadas
(senioridade com 'Gestor', vínculo, grupos de experiência/cargo/porte/setor, limites da
faixa salarial) seguem as regras de scripts/sod/derive.py e scripts/sod/stats.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sod import data, derive, stats  # noqa: E402


def build():
    fields = list(data.schema()["fields"])
    df = data.frame(fields)
    df["gestor"] = derive.gestor_bool(df["gestor"])
    df = stats.add_bounds(df)
    df["nivel"] = derive.senioridade(df)
    df["vinculo"] = derive.vinculo(df["situacao_trabalho"])
    df["experiencia_grupo"] = df["tempo_experiencia_dados"].map(derive.experiencia_grupo)
    df["modelo_atual"] = derive.modelo(df["modelo_trabalho_atual"])
    df["modelo_ideal"] = derive.modelo_ideal(df["modelo_trabalho_ideal"])
    df["cargo_grupo"] = df["cargo_atual"].map(derive.cargo_grupo)
    df["porte_grupo"] = df["tamanho_empresa"].map(derive.porte_grupo)
    df["setor_grupo"] = df["setor_empresa"].map(derive.setor_grupo)
    # 2019 tem outras categorias de cargo/experiência; os grupos derivados só valem de 2021 em diante
    for c in ["experiencia_grupo", "cargo_grupo", "vinculo"]:
        df.loc[df.edicao == "2019", c] = None
    return df


if __name__ == "__main__":
    out = data.ROOT / "data" / "harmonized" / "state_of_data_harmonized.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df = build()
    df.to_csv(out, index=False)
    print(f"{len(df)} linhas, {df.shape[1]} colunas -> {out.relative_to(data.ROOT)}")
    print(df.groupby("ano", sort=False).size().to_string())
