"""Compara os dados recalculados de um relatório com os números já publicados.

Uso:  python scripts/reports/check_golden.py radar data/_golden/radar.json
"""
import importlib
import json
import sys


def diff(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                yield f"{path}/{k}: só em {'gabarito' if k in b else 'novo'}"
            else:
                yield from diff(a[k], b[k], f"{path}/{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            yield f"{path}: tamanho {len(a)} != {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            yield from diff(x, y, f"{path}[{i}]")
    elif isinstance(a, float) or isinstance(b, float):
        if a is None or b is None or abs(a - b) > 0.051:
            yield f"{path}: {a} != {b}"
    elif isinstance(a, int) and isinstance(b, int) and not isinstance(a, bool):
        # valores em R$ corrigidos pela inflação podem variar ±R$ 1–2 por arredondamento do índice
        if abs(a - b) > max(0, 0.001 * abs(b)):
            yield f"{path}: {a} != {b}"
    elif a != b:
        yield f"{path}: {a!r} != {b!r}"


if __name__ == "__main__":
    name, golden = sys.argv[1], sys.argv[2]
    new = json.loads(json.dumps(importlib.import_module(name).compute(), default=lambda o: o.item()))
    old = json.load(open(golden, encoding="utf-8"))
    problems = list(diff(new, old))
    print("\n".join(problems[:40]) if problems else f"{name}: idêntico ao gabarito")
    sys.exit(1 if problems else 0)
