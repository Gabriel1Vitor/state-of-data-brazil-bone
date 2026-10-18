"""Variáveis derivadas e agrupamentos usados em todas as análises."""
import numpy as np
import pandas as pd

SENIORIDADE = ["Júnior", "Pleno", "Sênior", "Especialista/Staff+", "Gestor"]

MODELOS = {
    "Modelo 100% remoto": "Remoto",
    "Modelo híbrido flexível (o funcionário tem liberdade para escolher quando estar no escritório presencialmente)": "Híbrido flexível",
    "Modelo híbrido com dias fixos de trabalho presencial": "Híbrido fixo",
    "Modelo 100% presencial": "Presencial",
}

VINCULOS = ["Mora no Brasil, empresa brasileira", "Mora no Brasil, empresa estrangeira", "Mora no exterior"]

EXPERIENCIA = ["Menos de 1 ano", "1 a 2 anos", "3 a 6 anos", "7 a 10 anos", "Mais de 10 anos"]


def gestor_bool(s):
    return s.map({1: True, 0: False, 1.0: True, 0.0: False, True: True, False: False})


def senioridade(df):
    """Júnior/Pleno/Sênior/Staff+ vindo da pergunta de nível, ou 'Gestor' para quem gerencia."""
    g = gestor_bool(df["gestor"])
    s = df["senioridade"].copy()
    s[g == True] = "Gestor"  # noqa: E712 (gestor pode ser NaN)
    return s


def vinculo(situacao):
    s = situacao.astype(str)
    out = np.select(
        [s.str.contains("Vivo fora do Brasil"), s.str.contains("Vivo no Brasil e trabalho remoto")],
        [VINCULOS[2], VINCULOS[1]], VINCULOS[0])
    return pd.Series(out, index=situacao.index).where(situacao.notna())


def experiencia_grupo(e):
    if pd.isna(e) or "Não tenho" in e:
        return None
    if e.startswith("Menos"):
        return "Menos de 1 ano"
    if e == "de 1 a 2 anos":
        return "1 a 2 anos"
    if e in ("de 2 a 3 anos", "de 4 a 5 anos", "de 3 a 4 anos", "de 4 a 6 anos", "de 5 a 6 anos"):
        return "3 a 6 anos"
    if e in ("de 6 a 10 anos", "de 7 a 10 anos"):
        return "7 a 10 anos"
    if e.startswith("Mais de 10"):
        return "Mais de 10 anos"


def modelo(s):
    return s.map(MODELOS)


def modelo_ideal(s):
    def f(v):
        if not isinstance(v, str):
            return None
        return next((short for full, short in MODELOS.items() if v.startswith(full[:25])), None)
    return s.map(f)


def cargo_grupo(c):
    """Cargos harmonizados. Arquiteto de Dados soma com Engenheiro de Dados."""
    if pd.isna(c):
        return None
    if c.strip() == "Analytics Engineer":
        return "Analytics Engineer"
    for key, name in [("Machine Learning", "Eng. de ML / IA"), ("Cientista de Dados", "Cientista de Dados"),
                      ("Engenheiro de Dados", "Engenheiro(a) de Dados"), ("Arquiteto de", "Engenheiro(a) de Dados"),
                      ("Analista de Dados", "Analista de Dados"), ("Analista de BI", "Analista de BI"),
                      ("Analista de Negócios", "Analista de Negócios"), ("Product Manager", "Product Manager"),
                      ("Engenheiro de Software", "Eng. de Software / Dev"), ("Desenvolvedor", "Eng. de Software / Dev")]:
        if key in c:
            return name
    return None


def porte_grupo(p):
    if pd.isna(p):
        return None
    p = p.replace(".", "")
    if p in ("de 1 a 5", "de 6 a 10", "de 11 a 50"):
        return "Até 50"
    if p in ("de 51 a 100", "de 101 a 500"):
        return "51 a 500"
    if p in ("de 501 a 1000", "de 1001 a 3000", "de 501 a 100"):
        return "501 a 3.000"
    if p == "Acima de 3000":
        return "Acima de 3.000"


def setor_grupo(s):
    if pd.isna(s):
        return None
    for key, name in [("Finanças", "Finanças e bancos"), ("Tecnologia", "Tecnologia / software"),
                      ("Consultoria", "Consultoria"), ("Varejo", "Varejo"), ("Indústria", "Indústria"),
                      ("Saúde", "Saúde"), ("Educação", "Educação"), ("Setor Público", "Setor público")]:
        if key in s:
            return name
