"""O paradoxo do salário real: salários corrigidos pelo IPCA por nível, experiência, gênero e vínculo."""
import numpy as np

from _base import YEARS, harmonized, publish
from sod import derive
from sod.stats import band_quantile as q, deflator, ipca_accumulated

SEN = derive.SENIORIDADE
EG = derive.EXPERIENCIA
V = derive.VINCULOS
BK = ["Até R$ 4k", "R$ 4k a 8k", "R$ 8k a 12k", "R$ 12k a 20k", "Acima de R$ 20k"]
FINE = ["Menos de 1 ano", "de 1 a 2 anos", "de 3 a 4 anos", "de 5 a 6 anos", "de 7 a 10 anos", "Mais de 10 anos"]


def band(lo):
    if lo < 4000: return BK[0]
    if lo < 8000: return BK[1]
    if lo < 12000: return BK[2]
    if lo < 20000: return BK[3]
    return BK[4]


def compute():
    H = harmonized()
    S = H[(H.edicao != "2019") & H.sal_min.notna()].copy()
    S["sen"], S["eg"], S["exp"], S["vinc"] = S.nivel, S.experiencia_grupo, S.tempo_experiencia_dados, S.vinculo
    BR = S[S.vinc != V[2]].assign(band=lambda d: d.sal_min.map(band))
    DOM = S[S.vinc == V[0]]
    DEF = {y: deflator(y) for y in YEARS}
    real = lambda v, y: None if v is None else round(v * DEF[y])
    out = {"years": YEARS, "deflator": {y: round(DEF[y], 4) for y in YEARS}, "ipca_acum": round(ipca_accumulated(), 1)}

    out["overall"] = {k: [q(BR[BR.y == y], p) for y in YEARS] for k, p in [("p25", .25), ("p50", .5), ("p75", .75)]}
    out["overall_real"] = {k: [real(v, y) for v, y in zip(vals, YEARS)] for k, vals in out["overall"].items()}
    out["overall_n"] = [int((BR.y == y).sum()) for y in YEARS]

    out["sen_nom"] = {s: [q(DOM[(DOM.y == y) & (DOM.sen == s)]) for y in YEARS] for s in SEN}
    out["sen_real"] = {s: [real(v, y) for v, y in zip(out["sen_nom"][s], YEARS)] for s in SEN}
    out["sen_n"] = {s: [int(((DOM.y == y) & (DOM.sen == s)).sum()) for y in YEARS] for s in SEN}
    out["bands"] = {y: {k: round(100 * (BR[BR.y == y].band == k).mean(), 1) for k in BK} for y in YEARS}

    out["exp_nom"] = {e: [q(DOM[(DOM.y == y) & (DOM.eg == e)]) for y in YEARS] for e in EG}
    out["exp_real"] = {e: [real(v, y) for v, y in zip(out["exp_nom"][e], YEARS)] for e in EG}
    out["exp_n"] = {e: [int(((DOM.y == y) & (DOM.eg == e)).sum()) for y in YEARS] for e in EG}
    out["exp_fine"] = {y: [(lambda g: {"k": e, "v": q(g), "p25": q(g, .25), "p75": q(g, .75), "n": len(g)})(DOM[(DOM.y == y) & (DOM.exp == e)]) for e in FINE]
                       for y in ["2024/25", "2025/26"]}

    def cohort(y0, e0, y1, e1):
        a = q(DOM[(DOM.y == y0) & (DOM.exp == e0)]); b = q(DOM[(DOM.y == y1) & (DOM.exp == e1)])
        return {"from": f"{e0} em {y0}", "to": f"{e1} em {y1}", "a_nom": a, "b_nom": b, "a_real": real(a, y0), "b_real": real(b, y1),
                "n_a": int(((DOM.y == y0) & (DOM.exp == e0)).sum()), "n_b": int(((DOM.y == y1) & (DOM.exp == e1)).sum())}
    out["cohorts"] = [cohort("2021", "de 1 a 2 anos", "2025/26", "de 5 a 6 anos"), cohort("2021", "Menos de 1 ano", "2025/26", "de 3 a 4 anos"),
                      cohort("2022", "de 1 a 2 anos", "2025/26", "de 3 a 4 anos")]

    G = DOM[DOM.genero.isin(["Feminino", "Masculino"])]
    def ratio(g):
        w = q(g[g.genero == "Feminino"]); m = q(g[g.genero == "Masculino"])
        return round(100 * w / m, 1) if w and m else None
    def adjusted(g):  # média das razões dentro de nível x experiência, ponderada pelo nº de mulheres
        num = den = 0
        for _, c in g.groupby(["sen", "eg"]):
            w, m = c[c.genero == "Feminino"], c[c.genero == "Masculino"]
            if len(w) >= 10 and len(m) >= 10:
                wm, mm = q(w, min_n=10), q(m, min_n=10)
                if wm and mm:
                    num += len(w) * wm / mm; den += len(w)
        return round(100 * num / den, 1) if den else None
    out["gap_raw"] = [ratio(G[G.y == y]) for y in YEARS]
    out["gap_adj"] = [adjusted(G[G.y == y]) for y in YEARS]
    out["gap_exp"] = {e: [ratio(G[(G.y == y) & (G.eg == e)]) if ((G.y == y) & (G.eg == e) & (G.genero == "Feminino")).sum() >= 30 else None for y in YEARS] for e in EG}
    out["top_share"] = {n: [round(100 * (G[(G.y == y) & (G.genero == g)].sal_min >= 20000).mean(), 1) for y in YEARS] for n, g in [("Mulheres", "Feminino"), ("Homens", "Masculino")]}
    out["women_share_by_band_2526"] = {k: round(100 * (G[(G.y == "2025/26") & (G.sal_min.map(band) == k)].genero == "Feminino").mean(), 1) for k in BK}
    out["gap_n"] = [int(((G.y == y) & (G.genero == "Feminino")).sum()) for y in YEARS]

    out["vinc_med"] = {v: [q(S[(S.y == y) & (S.vinc == v)]) for y in YEARS] for v in V}
    out["vinc_med_real"] = {v: [real(x, y) for x, y in zip(out["vinc_med"][v], YEARS)] for v in V}
    out["vinc_n"] = {v: [int(((S.y == y) & (S.vinc == v)).sum()) for y in YEARS] for v in V}
    out["vinc_top40"] = {v: [round(100 * np.isinf(S[(S.y == y) & (S.vinc == v)].sal_max).mean(), 1) for y in YEARS] for v in V}
    out["foreign_share"] = [round(100 * (S[S.y == y].vinc == V[1]).mean(), 1) for y in YEARS]
    s26 = S[S.y == "2025/26"]
    out["foreign_by_sen_2526"] = {s: {"dom": q(s26[(s26.sen == s) & (s26.vinc == V[0])]), "ext": q(s26[(s26.sen == s) & (s26.vinc == V[1])], min_n=20),
                                      "n_ext": int(((s26.sen == s) & (s26.vinc == V[1])).sum())} for s in SEN}
    fs = s26[s26.vinc == V[1]]
    out["foreign_profile_2526"] = {"sen": {s: round(100 * (fs.sen == s).mean(), 1) for s in SEN}, "mulheres": round(100 * (fs.genero == "Feminino").mean(), 1), "n": len(fs)}

    b26 = BR[BR.y == "2025/26"]; top = b26[b26.sal_min >= 20000]
    out["top20"] = {"n": len(top), "share_all": round(100 * len(top) / len(b26), 1),
                    "sen": {s: round(100 * (top.sen == s).mean(), 1) for s in SEN},
                    "foreign": round(100 * (top.vinc == V[1]).mean(), 1), "foreign_all": round(100 * (b26.vinc == V[1]).mean(), 1),
                    "women": round(100 * (top.genero == "Feminino").mean(), 1), "women_all": round(100 * (b26.genero == "Feminino").mean(), 1),
                    "sudeste": round(100 * (top.regiao == "Sudeste").mean(), 1), "sudeste_all": round(100 * (b26.regiao == "Sudeste").mean(), 1)}
    out["spread"] = [round(a / b, 2) if a and b else None for a, b in zip(out["overall"]["p75"], out["overall"]["p25"])]
    out["sen_spread"] = [round(a / b, 2) if a and b else None for a, b in zip(out["sen_nom"]["Sênior"], out["sen_nom"]["Júnior"])]
    out["sr_staff_real_2526"] = real(q(DOM[(DOM.y == "2025/26") & DOM.sen.isin(["Sênior", "Especialista/Staff+"])]), "2025/26")
    out["exp7_share"] = [round(100 * DOM[DOM.y == y].eg.isin(["7 a 10 anos", "Mais de 10 anos"]).mean(), 1) for y in YEARS]
    out["jr_share"] = [round(100 * (DOM[DOM.y == y].sen == "Júnior").mean(), 1) for y in YEARS]
    return out


if __name__ == "__main__":
    publish("salario-real", compute())
