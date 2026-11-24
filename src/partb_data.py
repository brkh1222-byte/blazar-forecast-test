"""Shared loader for Part B (same logic as scripts/run_partB.py)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from config import DAYS_PER_YEAR, LCR_START_MJD, PARTB_END_MJD, PRETEST_END_MJD
from lcr import fetch

ROOT = Path(__file__).resolve().parents[1]
GRID = np.arange(LCR_START_MJD + 16.0, PARTB_END_MJD + 0.1, 30.0)
PRETEST = GRID < PRETEST_END_MJD


def to_mjd(s):
    s = str(s)
    ts = pd.Timestamp(s if len(s) > 7 else s + "-15")
    return (ts - pd.Timestamp("1858-11-17")).days


def cohen_kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    po = np.mean(a == b)
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else np.nan


def load_sources(period_choice="spacing"):
    a7 = pd.read_csv(ROOT / "data/penil_tableA7.csv")
    meta = pd.read_csv(ROOT / "data/penil_sources.csv").set_index("source")
    a7["t_pred"] = a7.predicted_epoch.map(to_mjd)
    out = []
    for name in dict.fromkeys(a7.source):
        lc = fetch(meta.loc[name, "fgl_name"], PARTB_END_MJD, ROOT / "data/lcr")
        flux = np.full(GRID.size, np.nan)
        k = np.rint((lc["t"] - GRID[0]) / 30.0).astype(int)
        ok = (k >= 0) & (k < GRID.size) & lc["detected"]
        flux[k[ok]] = lc["flux"][ok]
        det = np.isfinite(flux)
        tp = np.sort(a7.loc[a7.source == name, "t_pred"].to_numpy(float))
        if period_choice == "spacing" and tp.size >= 2:
            T = float(np.mean(np.diff(tp)))
        else:
            T = float(meta.loc[name, "table1_period_yr"]) * DAYS_PER_YEAR
        pre = det & PRETEST
        out.append(dict(name=name, t=GRID, flux=flux, detected=det, t_preds=tp, period=T,
                        ref_level=(float(np.median(flux[pre])), float(np.std(flux[pre])))))
    return out, a7
