"""Download the 30 Part B light curves, truncated at MJD 61000 (see src/config.py).

Usage: python scripts/download_partB.py
Writes data/lcr/<4FGL name>_end61000.json (git-ignored) and a short log.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from config import PARTB_END_MJD
from lcr import fetch

src = pd.read_csv(ROOT / "data/penil_sources.csv")
rows = []
for _, r in src.iterrows():
    try:
        lc = fetch(r.fgl_name, PARTB_END_MJD, ROOT / "data/lcr")
        rows.append(dict(source=r.source, fgl_name=r.fgl_name, n_bins=lc["t"].size,
                         n_detected=int(lc["detected"].sum()),
                         t_first=round(float(lc["t"][0]), 1), t_last=round(float(lc["t"][-1]), 1)))
    except Exception as e:  # noqa: BLE001
        rows.append(dict(source=r.source, fgl_name=r.fgl_name, error=str(e)[:120]))
    print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv(ROOT / "results/download_log.csv", index=False)
