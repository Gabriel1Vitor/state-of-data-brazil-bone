"""A volta ao escritório: modelo de trabalho por nível, estado, salário, cargo, setor etc."""
import numpy as np
import pandas as pd

from _base import YEARS, harmonized, pct, publish
from sod import derive
from sod.stats import median

MK = ["Remoto", "Híbrido flexível", "Híbrido fixo", "Presencial"]
SEN = derive.SENIORIDADE
AK = ["Procuraria vaga 100% remota", "Procuraria vaga híbrida ou remota", "Aceitaria voltar"]


def atitude(s):
    if pd.isna(s): return None
    if "aceitar" in s: return "Aceitaria voltar"
    if "100% remoto" in s: return "Procuraria vaga 100% remota"
    return "Procuraria vaga híbrida ou remota"


def compute():
    H = harmonized()
    F = H[H.edicao != "2019"].copy()
    F["m"] = F.modelo_atual
    F["papel"] = np.where(F.gestor == True, "Liderança", np.where(F.senioridade.notna(), "Contribuidor individual", None))  # noqa: E712
    F["abroad"] = F.situacao_trabalho.astype(str).str.contains("Vivo fora do Brasil")
    F["foreign"] = F.situacao_trabalho.astype(str).str.contains("Vivo no Brasil e trabalho remoto")
    F["local"] = np.select([F.estado == "SP", F.estado == "MG", F.estado == "RJ", F.estado.notna()],
                           ["São Paulo (SP)", "Minas Gerais (MG)", "Rio de Janeiro (RJ)", "Resto do Brasil"], None)
    F.loc[F.local == "None", "local"] = None
    F["obrig"] = F.m.isin(["Híbrido fixo", "Presencial"])
    F["att"] = F.atitude_retorno_presencial.map(atitude)
    B = F[F.m.notna() & ~F.abroad]  # empregados que moram no Brasil

    def dist(g): return {k: pct((g.m == k).sum(), len(g)) for k in MK} | {"_n": int(len(g))}
    def share(g, k): return pct((g.m == k).sum(), len(g)) if len(g) >= 30 else None
    def obr(g): return pct(g.obrig.sum(), len(g)) if len(g) >= 30 else None
    def by(col, cats):
        return {c: {"remoto": [share(B[(B.y == y) & (B[col] == c)], "Remoto") for y in YEARS],
                    "obrig": [obr(B[(B.y == y) & (B[col] == c)]) for y in YEARS],
                    "n": [int(((B.y == y) & (B[col] == c)).sum()) for y in YEARS],
                    "d2526": dist(B[(B.y == "2025/26") & (B[col] == c)])} for c in cats}

    out = {"years": YEARS, "n": {y: int((B.y == y).sum()) for y in YEARS}}
    out["overall"] = {y: dist(B[B.y == y]) for y in YEARS}
    out["obrig_overall"] = [obr(B[B.y == y]) for y in YEARS]
    out["sen"] = by("nivel", SEN)
    out["local"] = by("local", ["São Paulo (SP)", "Minas Gerais (MG)", "Rio de Janeiro (RJ)", "Resto do Brasil"])
    out["papel"] = by("papel", ["Contribuidor individual", "Liderança"])
    out["role"] = by("cargo_grupo", ["Engenheiro(a) de Dados", "Cientista de Dados", "Analista de Dados", "Analista de BI", "Analytics Engineer", "Eng. de ML / IA"])
    out["porte"] = by("porte_grupo", ["Até 50", "51 a 500", "501 a 3.000", "Acima de 3.000"])
    out["setor"] = by("setor_grupo", ["Tecnologia / software", "Finanças e bancos", "Consultoria", "Varejo", "Indústria", "Saúde", "Educação", "Setor público"])
    out["genero"] = by("genero", ["Feminino", "Masculino"])

    D = B[~B.foreign]  # salário: sem quem trabalha para empresa estrangeira
    out["sal"] = {y: {s: {k: {"v": median(D[(D.y == y) & (D.nivel == s) & (D.m == k)]),
                              "n": int(D[(D.y == y) & (D.nivel == s) & (D.m == k)].salario_faixa.notna().sum())} for k in MK}
                      for s in SEN} for y in ["2024/25", "2025/26"]}
    def prem(a, b): return round(100 * (a / b - 1), 1) if a and b else None
    out["premium"] = {s: [prem(median(D[(D.y == y) & (D.nivel == s) & (D.m == "Remoto")]), median(D[(D.y == y) & (D.nivel == s) & D.obrig])) for y in YEARS]
                      for s in ["Júnior", "Pleno", "Sênior", "Gestor"]}
    out["foreign_share_remote"] = {y: pct(B[(B.y == y) & (B.m == "Remoto")].foreign.sum(), (B[B.y == y].m == "Remoto").sum()) for y in YEARS}

    out["ideal"] = {y: (lambda g: {k: pct((g == k).sum(), len(g)) for k in MK})(B[B.y == y].modelo_ideal.dropna()) for y in YEARS}
    out["ideal_matrix"] = {k: (lambda g: {j: pct((g == j).sum(), len(g)) for j in MK} | {"_n": int(len(g))})(B[(B.y == "2025/26") & (B.m == k)].modelo_ideal.dropna()) for k in MK}
    out["match"] = [pct((B[B.y == y].m == B[B.y == y].modelo_ideal).sum(), B[B.y == y].modelo_ideal.notna().sum()) for y in YEARS]

    out["att"] = {y: (lambda g: {k: pct((g == k).sum(), len(g)) for k in AK})(B[B.y == y].att.dropna()) for y in YEARS}
    out["att_by_model"] = {k: (lambda g: {a: pct((g == a).sum(), len(g)) for a in AK} | {"_n": int(len(g))})(B[(B.y == "2025/26") & (B.m == k)].att.dropna()) for k in MK}
    out["att_by_sen"] = {s: (lambda g: pct((g != "Aceitaria voltar").sum(), len(g)))(B[(B.y == "2025/26") & (B.nivel == s)].att.dropna()) for s in SEN}

    def sat(g): return pct(g.satisfeito_empresa.isin([1, 1.0, True]).sum(), g.satisfeito_empresa.notna().sum())
    def bus(g): return pct(g.plano_mudar_emprego.astype(str).str.startswith("Estou em busca").sum(), g.plano_mudar_emprego.notna().sum())
    out["sat_by_model"] = {k: {"satisf": [sat(B[(B.y == y) & (B.m == k)]) for y in YEARS], "busca": [bus(B[(B.y == y) & (B.m == k)]) for y in YEARS]} for k in MK}
    g = B[(B.y == "2025/26") & B.modelo_ideal.notna()]
    same, other = g[g.m == g.modelo_ideal], g[g.m != g.modelo_ideal]
    out["sat_match"] = {"Trabalha no modelo que considera ideal": {"satisf": sat(same), "busca": bus(same), "n": len(same)},
                        "Trabalha em outro modelo": {"satisf": sat(other), "busca": bus(other), "n": len(other)}}
    return out


if __name__ == "__main__":
    publish("volta-ao-escritorio", compute())
