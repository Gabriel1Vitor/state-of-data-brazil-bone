"""Radar State of Data Brazil: painel geral (salários, carreira, tecnologia, IA, diversidade)."""
import re

import numpy as np
import pandas as pd

from _base import YEARS, data, harmonized, pct, publish
from sod import derive
from sod.stats import median

SEN = derive.SENIORIDADE
ROLE_LABEL = {"Engenheiro(a) de Dados": "Eng. de Dados / Arquiteto"}


def compute():
    H = harmonized()
    R = H[H.edicao != "2019"].copy()
    R["abroad"] = R.situacao_trabalho.astype(str).str.contains("Vivo fora do Brasil") | (R.regiao == "Exterior")
    BR = R[~R.abroad]
    out = {"years": YEARS, "n": {data.label(e): len(data.raw(e)) for e in data.editions()}}

    # salários
    out["sal_sen"] = {s: [median(BR[(BR.y == y) & (BR.nivel == s)]) for y in YEARS] for s in SEN}
    out["sal_sen_n"] = {s: [int(BR[(BR.y == y) & (BR.nivel == s)].salario_faixa.notna().sum()) for y in YEARS] for s in SEN}
    out["sal_overall"] = {y: median(BR[BR.y == y]) for y in YEARS}
    rr = []
    for r in BR.cargo_grupo.dropna().unique():
        a = median(BR[(BR.y == "2022") & (BR.cargo_grupo == r)])
        b = median(BR[(BR.y == "2025/26") & (BR.cargo_grupo == r)])
        n = int(BR[(BR.y == "2025/26") & (BR.cargo_grupo == r)].salario_faixa.notna().sum())
        if b:
            rr.append({"role": ROLE_LABEL.get(r, r), "v2022": a, "v2025": b, "n": n})
    out["sal_role"] = sorted(rr, key=lambda x: -x["v2025"])

    def ratio(g):
        w = median(g[g.genero == "Feminino"]); m = median(g[g.genero == "Masculino"])
        return round(100 * w / m, 1) if w and m else None
    L4 = ["Júnior", "Pleno", "Sênior", "Gestor"]
    out["gap"] = {s: [ratio(BR[(BR.y == y) & (BR.nivel == s)]) for y in YEARS] for s in L4}
    out["gap_n_fem"] = {s: [int(BR[(BR.y == y) & (BR.nivel == s) & (BR.genero == "Feminino")].salario_faixa.notna().sum()) for y in YEARS] for s in L4}

    def vinc(s):
        if pd.isna(s): return None
        if "Vivo no Brasil e trabalho remoto" in s: return "Remoto para empresa estrangeira"
        if "CLT" in s: return "CLT"
        if "CNPJ" in s: return "PJ / empreendedor"
        if "Servidor" in s: return "Servidor público"
        if "Estagi" in s: return "Estágio"
    v = BR[BR.y == "2025/26"].assign(v=lambda d: d.situacao_trabalho.map(vinc))
    out["sal_vinc"] = sorted([{"k": k, "v": median(g), "n": int(g.salario_faixa.notna().sum())} for k, g in v.groupby("v")], key=lambda x: -x["v"])
    reg = BR[BR.y == "2025/26"]
    out["sal_reg"] = sorted([{"k": k, "v": median(g), "n": int(g.salario_faixa.notna().sum())} for k, g in reg.groupby("regiao") if median(g)], key=lambda x: -x["v"])

    # carreira
    out["sen_mix"] = {}
    for y in YEARS:
        g = R[(R.y == y) & R.nivel.notna()]
        out["sen_mix"][y] = {s: pct((g.nivel == s).sum(), len(g)) for s in SEN}
    MOD = {"Remoto": "100% remoto", "Híbrido flexível": "Híbrido flexível", "Híbrido fixo": "Híbrido com dias fixos", "Presencial": "100% presencial"}
    out["modelo"] = {}
    for y in YEARS:
        g = R[R.y == y].modelo_atual.map(MOD).dropna()
        out["modelo"][y] = {k: pct((g == k).sum(), len(g)) for k in MOD.values()}
    out["satisf"] = [pct(R[R.y == y].satisfeito_empresa.isin([1, 1.0, True]).sum(), R[R.y == y].satisfeito_empresa.notna().sum()) for y in YEARS]
    out["buscando"] = [pct(R[R.y == y].plano_mudar_emprego.astype(str).str.startswith("Estou em busca").sum(), R[R.y == y].plano_mudar_emprego.notna().sum()) for y in YEARS]
    out["so_exterior"] = [pct(R[R.y == y].plano_mudar_emprego.astype(str).str.contains("apenas fora").sum(), R[R.y == y].plano_mudar_emprego.notna().sum()) for y in YEARS]
    out["layoff"] = {"anos": ["2022", "2023", "2024", "2025"],
                     "empresa": [pct(R[R.y == y].layoff.astype(str).str.startswith("Sim").sum(), R[R.y == y].layoff.notna().sum()) for y in YEARS[1:]],
                     "afetado": [pct(R[R.y == y].layoff.astype(str).str.contains("eu fui afetado").sum(), R[R.y == y].layoff.notna().sum()) for y in YEARS[1:]]}
    out["desemprego"] = {}
    for y in ["2019"] + YEARS:
        s = H[H.y == y].situacao_trabalho
        out["desemprego"][y] = pct(s.astype(str).str.startswith("Desempregado, buscando").sum(), s.notna().sum())

    # tecnologia
    def shares(name, targets, norm, eds):
        res = {t: [] for t in targets}; yrs = []
        for ed in eds:
            y = data.label(ed); yrs.append(y)
            if name == "cloud_trabalho" and ed == "2022":
                raw = data.multiselect_text(ed, name).dropna()
                full = {"AWS": "Amazon Web Services (AWS)", "Azure": "Azure (Microsoft)", "GCP": "Google Cloud (GCP)", "On-premise / sem cloud": "Servidores On Premise"}
                for t in targets:
                    res[t].append(pct(raw.str.contains(full[t], regex=False).sum(), len(raw)))
                continue
            ms = data.multiselect(ed, name)
            base = ms.sum(axis=1) > 0
            grouped = {}
            for c in ms.columns:
                grouped.setdefault(norm(c), []).append(c)
            for t in targets:
                cs = grouped.get(t)
                res[t].append(pct(ms.loc[base, cs].max(axis=1).sum(), base.sum()) if cs else None)
        return {"years": yrs, "series": res}
    def nbi(n):
        if "Looker Studio" in n or "Data Studio" in n: return "Looker Studio"
        if n.startswith("Qlik"): return "Qlik"
        if "Excel" in n: return "Só Excel/planilhas"
        if "PowerBI" in n: return "Power BI"
        return n
    ncl = lambda n: {"Amazon Web Services (AWS)": "AWS", "Google Cloud (GCP)": "GCP", "Azure (Microsoft)": "Azure", "Servidores On Premise/Não utilizamos Cloud": "On-premise / sem cloud"}.get(n, n)
    out["lang"] = shares("linguagens_trabalho", ["Python", "SQL", "R"], str.strip, ["2021", "2022", "2023", "2024-2025"])
    out["cloud"] = shares("cloud_trabalho", ["AWS", "Azure", "GCP", "On-premise / sem cloud"], ncl, ["2021", "2022", "2023", "2024-2025", "2025-2026"])
    out["bi"] = shares("bi_trabalho", ["Power BI", "Looker Studio", "Tableau", "Metabase", "Só Excel/planilhas"], nbi, ["2021", "2023", "2024-2025", "2025-2026"])

    def ai(s):
        if pd.isna(s): return None
        if "Não utilizo" in s: return "Não usa"
        if "empresa em que trabalho paga" in s: return "Empresa paga"
        if "pago do meu próprio bolso" in s: return "Paga do próprio bolso"
        if "Copilot" in s or "AI para código" in s: return "Só IA de código"
        if "gratuitas" in s: return "Só gratuitas"
    AIK = ["Empresa paga", "Paga do próprio bolso", "Só IA de código", "Só gratuitas", "Não usa"]
    out["ai"], out["ai_code"] = {}, []
    for y in ["2023", "2024/25", "2025/26"]:
        s = R[R.y == y].uso_ia_generativa; cat = s.map(ai).dropna()
        out["ai"][y] = {k: pct((cat == k).sum(), len(cat)) for k in AIK} | {"_n": int(len(cat))}
        out["ai_code"].append(pct(s.dropna().astype(str).str.contains("Copilot|AI para código").sum(), s.notna().sum()))

    # diversidade
    out["mulheres"] = {}
    for y in ["2019"] + YEARS:
        s = H[H.y == y].genero.dropna(); out["mulheres"][y] = pct((s == "Feminino").sum(), len(s))
    out["raca"] = {}
    for y in YEARS[1:]:
        s = R[R.y == y].raca.dropna(); s = s[s != "Prefiro não informar"]
        out["raca"][y] = {"Negras (pretas + pardas)": pct(s.isin(["Preta", "Parda"]).sum(), len(s)), "Pretas": pct((s == "Preta").sum(), len(s)), "Brancas": pct((s == "Branca").sum(), len(s))}
    out["pcd"] = {y: pct((R[R.y == y].pcd == "Sim").sum(), R[R.y == y].pcd.notna().sum()) for y in YEARS[1:]}
    out["regiao"] = {}
    for y in YEARS:
        s = R[R.y == y].regiao.dropna(); s = s[s != "Exterior"]
        out["regiao"][y] = {k: pct((s == k).sum(), len(s)) for k in ["Sudeste", "Sul", "Nordeste", "Centro-oeste", "Norte"]}
    out["fem_sen"] = {}
    for y in ["2022", "2025/26"]:
        g = R[(R.y == y) & R.genero.isin(["Feminino", "Masculino"])]
        out["fem_sen"][y] = {s: pct((g[g.nivel == s].genero == "Feminino").sum(), (g.nivel == s).sum()) for s in SEN}
    out["prejud"] = {"mulheres_genero": [], "negros_raca": []}
    for y in YEARS[1:]:
        g = R[(R.y == y) & R.experiencia_prejudicada.notna()]
        w = g[g.genero == "Feminino"]; b = g[g.raca.isin(["Preta", "Parda"])]
        out["prejud"]["mulheres_genero"].append(pct(w.experiencia_prejudicada.str.contains("identidade de gênero").sum(), len(w)))
        out["prejud"]["negros_raca"].append(pct(b.experiencia_prejudicada.str.contains("Cor/Raça").sum(), len(b)))
    has = R.experiencia_prejudicada.notna()
    out["prejud"]["n_w"] = [int(((R.y == y) & has & (R.genero == "Feminino")).sum()) for y in YEARS[1:]]
    out["prejud"]["n_b"] = [int(((R.y == y) & has & R.raca.isin(["Preta", "Parda"])).sum()) for y in YEARS[1:]]
    out["_prejud_men_answered"] = [int(((R.y == y) & has & (R.genero == "Masculino") & (R.raca == "Branca")).sum()) for y in YEARS[1:]]
    return out


if __name__ == "__main__":
    publish("radar", compute())
