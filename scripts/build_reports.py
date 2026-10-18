"""Regenera a base harmonizada e os 3 relatórios publicados em docs/ (GitHub Pages).

Uso:  python scripts/build_reports.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [HERE / "harmonize.py"] + [HERE / "reports" / f for f in ("radar.py", "volta_ao_escritorio.py", "salario_real.py")]

for step in STEPS:
    subprocess.run([sys.executable, str(step)], check=True, cwd=step.parent)
