"""Download Fermi LAT Light Curve Repository (LCR) light curves.

LCR: Abdollahi et al. 2023, ApJS 265, 31. API endpoint (queryDB.php) returns
JSON with lists of [MET, value] pairs: 'ts' (every bin), 'flux' (bins with
TS >= ts_min), 'flux_upper_limits' (other bins), 'flux_error' ([MET, lo, hi]).
We use 30-day ('monthly') bins, photon flux (E > 100 MeV), fixed photon index,
ts_min = 4 (about 2 sigma), matching Peñil et al. (2026, Sec. 2).

BLINDING: `fetch` truncates the light curve at `end_mjd` BEFORE anything is
saved or returned, so later fluxes are never written to disk or shown.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import requests

from config import MET_ZERO_MJD, PARTB_END_MJD

URL = "https://fermi.gsfc.nasa.gov/ssc/data/access/lat/LightCurveRepository/queryDB.php"


def met_to_mjd(met):
    return MET_ZERO_MJD + np.asarray(met, float) / 86400.0


def _query(name, retries=3):
    params = dict(typeOfRequest="lightCurveData", source_name=name, cadence="monthly",
                  flux_type="photon", index_type="fixed", ts_min=4)
    for k in range(retries):
        try:
            r = requests.get(URL, params=params, timeout=120)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError):
            if k == retries - 1:
                raise
            time.sleep(5 * (k + 1))


def fetch(name, end_mjd=PARTB_END_MJD, cache_dir="data/lcr"):
    """Return dict(t, flux, flux_err, detected, ts) truncated at end_mjd (bin centre <= end_mjd)."""
    cache = Path(cache_dir) / f"{name.replace(' ', '_')}_end{end_mjd:.0f}.json"
    if cache.exists():
        d = json.loads(cache.read_text())
        return {k: np.array(v) for k, v in d.items()}
    raw = _query(name)
    t_all = met_to_mjd([p[0] for p in raw["ts"]])
    ts = np.array([p[1] for p in raw["ts"]], float)
    keep = t_all <= end_mjd                       # truncate FIRST
    t = t_all[keep]
    flux = np.full(t.size, np.nan)
    err = np.full(t.size, np.nan)
    pos = {round(x, 3): i for i, x in enumerate(t)}
    for (met, f), (_, lo, hi) in zip(raw["flux"], raw["flux_error"]):
        i = pos.get(round(float(met_to_mjd(met)), 3))
        if i is not None:
            flux[i] = f
            err[i] = 0.5 * (hi - lo)
    out = dict(t=t, flux=flux, flux_err=err, detected=np.isfinite(flux), ts=ts[keep])
    del raw                                        # the untruncated response is never stored
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps({k: np.asarray(v).tolist() for k, v in out.items()}))
    return out
