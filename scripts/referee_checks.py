"""Checks requested by an internal referee-style review (EXPLORATORY: added 2026-11-28).

None of this was pre-registered; all of it was run after the Part B results were known.

P1. Power for less favourable signals. The registered power check gave EVERY source a sinusoid
    exactly in phase with its forecasts. Here only a fraction of the sources is periodic
    (7, 15 or 30 of 30), and in the "realistic" case the true period differs from the forecast
    period (5% r.m.s.) and the phase is off by 0.1 T r.m.s. at the end of the first 12 yr.
P2. Source-level clustering: are "all supported" / "none supported" sources more common than
    expected? For our rules the reference is N1; for the published verdicts (no rule available)
    it is a permutation of the 59 verdicts among the forecasts.
P3. Forecasts whose window (or +/-0.5 T search) runs past the end of the data are dropped.
P4. N2 with flux-ordered censoring: the registered N2 reuses the real pattern of undetected bins
    whatever the simulated flux is. Here the same NUMBER of bins is censored, but the faintest
    simulated ones, which is the opposite extreme.

Usage:  python scripts/referee_checks.py       (about 10-15 minutes, one core)
Output: results/referee_checks.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from config import PRETEST_END_MJD
from match import RULES, MatchSettings, score_source
from nulls import n1_random_phase_fast, p_value_upper, score_simulations
from partb_data import GRID, PRETEST, cohen_kappa, load_sources
from psd_fit import fit_psd
from simulate import bootstrap_sampler, emmanoulopoulos

CAND = list(RULES[1:])
SEED = 20261129
t0 = time.time()
sources, a7 = load_sources()
out = {"note": "Exploratory checks added 2026-11-28 after an internal referee-style review."}
LAST = GRID[-1]


def log(msg):
    print(f"[{time.time()-t0:5.0f}s] {msg}", flush=True)


def pooled(srcs, rule):
    obs = np.array([score_source(s["t"], s["flux"], s["detected"], s["t_preds"], s["period"], rule,
                                 MatchSettings(), s["ref_level"])[:2] for s in srcs])
    return obs


# ------------------------------------------------------------------ simulations shared by P1 and P4
N_SIM = 300
rng = np.random.default_rng(SEED)
sims = []
for s in sources:
    pre = s["detected"] & PRETEST
    fit = fit_psd(s["flux"][PRETEST], s["detected"][PRETEST], 30.0, "PL")
    sampler = bootstrap_sampler(s["flux"][pre])
    sims.append(np.array([emmanoulopoulos(GRID.size, 30.0, fit["psd"], sampler, rng) for _ in range(N_SIM)]))
log("simulated")

# ------------------------------------------------------------------ P1 power
N_REAL, N1D = 100, 1000
P1 = {}
rngp = np.random.default_rng(SEED + 1)
for scen in ("ideal", "realistic"):
    for n_per in (7, 15, 30):
        for amp in (0.5, 1.0, 2.0):
            ps = {r: [] for r in CAND}
            for i in range(N_REAL):
                periodic = set(rngp.choice(len(sources), n_per, replace=False).tolist())
                inj = []
                for j, s in enumerate(sources):
                    f = sims[j][i].copy()
                    if j in periodic:
                        T, tp0 = s["period"], s["t_preds"][0]
                        if scen == "ideal":
                            T_true, t_peak = T, tp0
                        else:
                            T_true = T * (1 + rngp.normal(0, 0.05))
                            n_back = np.ceil((tp0 - PRETEST_END_MJD) / T)       # last forecast-phase peak in the first 12 yr
                            t_peak = tp0 - n_back * T + rngp.normal(0, 0.1 * T)
                        f = f + amp * np.std(s["flux"][s["detected"]]) * np.cos(2 * np.pi * (GRID - t_peak) / T_true)
                    pre = s["detected"] & PRETEST
                    inj.append({**s, "flux": f, "ref_level": (np.median(f[pre]), np.std(f[pre]))})
                for r in CAND:
                    obs = pooled(inj, r)
                    ev, hit = n1_random_phase_fast(inj, r, N1D, rngp, step=5.0)
                    ps[r].append(p_value_upper(obs[:, 1].sum() / obs[:, 0].sum(),
                                               hit.sum(1) / np.maximum(ev.sum(1), 1)))
            P1[f"{scen} | periodic {n_per}/30 | a={amp}"] = {r: float(np.mean(np.array(v) < 0.05)) for r, v in ps.items()}
            log(f"P1 {scen} {n_per} {amp}: " + " ".join(f"{P1[f'{scen} | periodic {n_per}/30 | a={amp}'][r]:.2f}" for r in CAND))
out["P1_power"] = P1
out["P1_note"] = (f"{N_REAL} simulated samples per cell, N1 with {N1D} draws on a 5-day offset grid, power-law "
                  "red noise. Amplitude a is in units of the standard deviation of the real detected fluxes. "
                  "'realistic': true period = forecast period x (1 + N(0, 0.05)); phase error N(0, 0.1 T) at the "
                  "last forecast-phase peak before MJD 59065, so the mismatch grows with time. Binomial standard "
                  "error up to 0.05.")

# ------------------------------------------------------------------ P2 clustering
multi = [s for s in sources if s["t_preds"].size >= 2]
P2 = {}
rngc = np.random.default_rng(SEED + 2)


def extreme_frac(ev, hit):
    ok = ev >= 2
    return ((hit == ev) | (hit == 0))[ok].sum() / max(ok.sum(), 1)


for r in CAND:
    obs = pooled(multi, r)
    ev, hit = n1_random_phase_fast(multi, r, 10_000, rngc)
    null = np.array([extreme_frac(ev[i], hit[i]) for i in range(ev.shape[0])])
    o = extreme_frac(obs[:, 0], obs[:, 1])
    P2[r] = dict(n_sources=int((obs[:, 0] >= 2).sum()), observed_all_or_none_fraction=float(o),
                 null_mean=float(null.mean()), p_upper=float(p_value_upper(o, null)))
# published verdicts: permutation among forecasts
a7m = a7[a7.source.isin([s["name"] for s in multi])]
codes = a7m.source.astype("category").cat.codes.to_numpy()
sup = a7m.supported.to_numpy()


def ext_pub(v):
    tot = np.bincount(codes, weights=v)
    n = np.bincount(codes)
    return int(((tot == n) | (tot == 0)).sum())


o = ext_pub(sup)
null = np.array([ext_pub(rngc.permutation(sup)) for _ in range(10_000)])
P2["published_verdicts"] = dict(n_sources=int(len(multi)), n_forecasts=int(len(a7m)), supported=int(sup.sum()),
                                observed_all_or_none_sources=o, null_mean=float(null.mean()),
                                p_upper=float(p_value_upper(o, null)),
                                all_supported=int(sum(a7m.groupby("source").supported.agg(lambda x: x.all()))),
                                null_reference="10,000 permutations of the verdicts among these forecasts")
out["P2_source_clustering"] = P2
log(f"P2 {P2}")

# ------------------------------------------------------------------ P3 drop truncated forecasts
P3 = {}
for label, frac in (("window inside data (t_pred + 0.2T <= last bin)", 0.2), ("search inside data (t_pred + 0.5T <= last bin)", 0.5)):
    sub = []
    for s in sources:
        keep = s["t_preds"] + frac * s["period"] <= LAST
        if keep.any():
            sub.append({**s, "t_preds": s["t_preds"][keep]})
    n_fc = int(sum(x["t_preds"].size for x in sub))
    P3[label] = {"n_forecasts": n_fc, "n_sources": len(sub)}
    for r in CAND:
        verd, truth = [], []
        for x in sub:
            _, _, res = score_source(x["t"], x["flux"], x["detected"], x["t_preds"], x["period"], r,
                                     MatchSettings(), x["ref_level"])
            verd += [int(q.hit) for q in res]
            truth += [int(a7.loc[(a7.source == x["name"]) & (a7.t_pred == tp), "supported"].iloc[0]) for tp in x["t_preds"]]
        obs = pooled(sub, r)
        ev, hit = n1_random_phase_fast(sub, r, 10_000, rngc)
        Hn = hit.sum(1) / np.maximum(ev.sum(1), 1)
        Ho = obs[:, 1].sum() / obs[:, 0].sum()
        P3[label][r] = dict(kappa=float(cohen_kappa(verd, truth)), hits=int(obs[:, 1].sum()),
                            evaluable=int(obs[:, 0].sum()), H_obs=float(Ho), N1_mean=float(Hn.mean()),
                            p_N1=float(p_value_upper(Ho, Hn)), published_supported=int(np.sum(truth)))
out["P3_drop_truncated"] = P3
out["P3_note"] = ("Shifted forecasts in N1 can still reach the end of the data; this check removes the truncation "
                  "from the observed side only.")
log(f"P3 {json.dumps(P3)[:400]}")

# ------------------------------------------------------------------ P4 N2 with flux-ordered censoring
P4 = {}
H_obs = {r: (lambda o: o[:, 1].sum() / o[:, 0].sum())(pooled(sources, r)) for r in CAND}
for mode in ("real_mask", "faintest_bins_censored"):
    tot = {r: np.zeros((N_SIM, 2)) for r in CAND}
    for j, s in enumerate(sources):
        n_und = int((~s["detected"]).sum())
        for i in range(N_SIM):
            f = sims[j][i]
            if mode == "real_mask":
                det = s["detected"]
            else:
                det = np.ones(f.size, bool)
                if n_und:
                    det[np.argsort(f)[:n_und]] = False
            pre = det & PRETEST
            ref = (np.median(f[pre]), np.std(f[pre]))
            for r in CAND:
                e, h, _ = score_source(GRID, f, det, s["t_preds"], s["period"], r, MatchSettings(), ref)
                tot[r][i] += (e, h)
    P4[mode] = {}
    for r in CAND:
        Hn = tot[r][:, 1] / np.maximum(tot[r][:, 0], 1)
        P4[mode][r] = dict(H_null_mean=float(Hn.mean()), H_null_sd=float(Hn.std()),
                           p_upper=float(p_value_upper(H_obs[r], Hn)),
                           mean_evaluable=float(tot[r][:, 0].mean()))
    log(f"P4 {mode}: " + " ".join(f"{r[:2]} {P4[mode][r]['H_null_mean']:.3f} p={P4[mode][r]['p_upper']:.3f}" for r in CAND))
out["P4_N2_censoring"] = P4
out["P4_note"] = (f"Power-law N2, {N_SIM} simulations per source (the registered run used 1,000 and another seed). "
                  "'faintest_bins_censored' removes as many bins as the source has undetected bins, choosing the "
                  "faintest simulated ones.")

(ROOT / "results/referee_checks.json").write_text(json.dumps(out, indent=2))
print("wrote results/referee_checks.json")
