"""Utilidades comuns aos scripts de relatório."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harmonize import build  # noqa: E402
from sod import data  # noqa: E402

YEARS = ["2021", "2022", "2023", "2024/25", "2025/26"]
TEMPLATES = data.ROOT / "reports" / "templates"
SITE = data.ROOT / "docs"
REPORT_DATA = data.ROOT / "reports" / "data"


def pct(a, b):
    return round(100 * a / b, 1) if b else None


def harmonized():
    """Base harmonizada em memória, com a coluna 'y' (rótulo da edição) usada pelos relatórios."""
    df = build()
    return df.assign(y=df["ano"])


def _jsonable(o):
    if hasattr(o, "item"):
        return o.item()
    raise TypeError(type(o))


def publish(name, payload):
    """Grava reports/data/<name>.json e gera docs/<name>.html a partir do template."""
    REPORT_DATA.mkdir(parents=True, exist_ok=True)
    SITE.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, ensure_ascii=False, indent=1, default=_jsonable)
    (REPORT_DATA / f"{name}.json").write_text(text + "\n", encoding="utf-8")
    template = (TEMPLATES / f"{name}.html").read_text(encoding="utf-8")
    (SITE / f"{name}.html").write_text(template.replace("__DATA__", text, 1), encoding="utf-8")
    print(f"{name}: reports/data/{name}.json, docs/{name}.html")
