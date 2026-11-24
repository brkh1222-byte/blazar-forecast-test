"""Part B: reconstruct the Peñil et al. (2026) matching rule (Q0) and calibrate the
forecast hit rate against the N1 (randomised-forecast) and N2 (red-noise) nulls.

Usage:  python scripts/run_partB.py [--quick]
Inputs: data/penil_tableA7.csv, data/penil_sources.csv, data/lcr/*.json (scripts/download_partB.py)
Outputs (results/): q0_verdicts.csv, q0_kappa.csv, partB_n1.csv, partB_n2.csv,
                    power.csv, negative_control.csv, partB_summary.json, null_draws.npz
All choices follow preregistration/predictions_2026.md.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd

from config import LCR_START_MJD, PARTB_END_MJD, PRETEST_END_MJD, DAYS_PER_YEAR
from lcr import fetch
from match import RULES, MatchSettings, score_source
from nulls import (excess_with_bootstrap, n1_grid_outcomes, n1_random_phase_fast,
                   p_value_upper, score_simulations)
from psd_fit import fit_psd
from simulate import bootstrap_sampler, emmanoulopoulos

ap = argparse.ArgumentParser()
ap.add_argument("--quick", action="store_true", help="small draw counts for a smoke test")
args = ap.parse_args()

N1_DRAWS = 1000 if args.quick else 10_000
N2_SIMS = 50 if args.quick else 1000
N_BOOT = 1000 if args.quick else 10_000
POWER_REAL = 10 if args.quick else 100
POWER_N1 = 200 if args.quick else 1000
SEED = 20261122
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
CANDIDATES = RULES[1:]                    # R1..R4; R0 is shown separately


def to_mjd(s):
    s = str(s)
    ts = pd.Timestamp(s if len(s) > 7 else s + "-15")
    return (ts - pd.Timestamp("1858-11-17")).days


def cohen_kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    po = np.mean(a == b)
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else np.nan


# ---------------------------------------------------------------- load data
a7 = pd.read_csv(ROOT / "data/penil_tableA7.csv")
meta = pd.read_csv(ROOT / "data/penil_sources.csv").set_index("source")
a7["t_pred"] = a7.predicted_epoch.map(to_mjd)

grid = np.arange(LCR_START_MJD + 16.0, PARTB_END_MJD + 0.1, 30.0)   # bin centres, 211 bins
pretest = grid < PRETEST_END_MJD


def build_source(name, period_choice="spacing"):
    lc = fetch(meta.loc[name, "fgl_name"], PARTB_END_MJD, ROOT / "data/lcr")
    flux = np.full(grid.size, np.nan)
    k = np.rint((lc["t"] - grid[0]) / 30.0).astype(int)
    ok = (k >= 0) & (k < grid.size) & lc["detected"]
    flux[k[ok]] = lc["flux"][ok]
    det = np.isfinite(flux)
    tp = np.sort(a7.loc[a7.source == name, "t_pred"].to_numpy(float))
    if period_choice == "spacing" and tp.size >= 2:
        T = float(np.mean(np.diff(tp)))
    else:
        T = float(meta.loc[name, "table1_period_yr"]) * DAYS_PER_YEAR
    pre = det & pretest
    return dict(name=name, t=grid, flux=flux, detected=det, t_preds=tp, period=T,
                ref_level=(float(np.median(flux[pre])), float(np.std(flux[pre]))))


names = list(dict.fromkeys(a7.source))            # table order, 30 sources
SRC = {pc: [build_source(n, pc) for n in names] for pc in ("spacing", "table1")}
sources = SRC["spacing"]
print(f"{len(sources)} sources, {sum(s['t_preds'].size for s in sources)} forecasts", flush=True)

# ---------------------------------------------------------------- Q0: rule reconstruction
rows = []
for s in sources:
    for tp in s["t_preds"]:
        r = dict(source=s["name"], t_pred=tp, period_d=round(s["period"], 1))
        for rule in RULES:
            e, h, res = score_source(s["t"], s["flux"], s["detected"], [tp], s["period"], rule,
                                     MatchSettings(), s["ref_level"])
            r[rule] = int(h)
            r[rule + "_eval"] = int(e)
        rows.append(r)
q0 = pd.DataFrame(rows).merge(a7[["source", "t_pred", "supported"]], on=["source", "t_pred"])
q0.to_csv(OUT / "q0_verdicts.csv", index=False)
kap = pd.DataFrame([dict(rule=r, kappa=cohen_kappa(q0[r], q0.supported),
                         agreement=float(np.mean(q0[r] == q0.supported)),
                         hits=int(q0[r].sum()), evaluable=int(q0[r + "_eval"].sum()))
                    for r in RULES])
kap.to_csv(OUT / "q0_kappa.csv", index=False)
print(kap.to_string(index=False), flush=True)

cand = kap[kap.rule.isin(CANDIDATES)].reset_index(drop=True)
best = cand.loc[cand.kappa.idxmax()]
primary = best.rule if best.kappa >= 0.7 else None
print("primary rule:", primary, flush=True)


# ---------------------------------------------------------------- N1
def n1_cell(srcs, rule, settings, rng, n_draws=N1_DRAWS):
    obs = np.array([score_source(s["t"], s["flux"], s["detected"], s["t_preds"], s["period"], rule,
                                 settings, s["ref_level"])[:2] for s in srcs])
    ev, hit = n1_random_phase_fast(srcs, rule, n_draws, rng, settings)
    H_null = hit.sum(1) / np.maximum(ev.sum(1), 1)
    H_obs = obs[:, 1].sum() / obs[:, 0].sum()
    return obs, ev, hit, H_obs, H_null


rng = np.random.default_rng(SEED)
n1_rows, keep_draws = [], {}
t0 = time.time()
cells = [("primary-grid", r, 0.20, 2, "spacing") for r in RULES]
cells += [("robust-W", r, w, 2, "spacing") for r in CANDIDATES for w in (0.10, 0.30)]
cells += [("robust-Nmin", r, 0.20, 3, "spacing") for r in CANDIDATES]
cells += [("robust-period", r, 0.20, 2, "table1") for r in CANDIDATES]
for tag, rule, w, nmin, pc in cells:
    st = MatchSettings(window_frac=w, n_min=nmin)
    obs, ev, hit, H_obs, H_null = n1_cell(SRC[pc], rule, st, rng)
    exc, ci = excess_with_bootstrap(obs[:, 1], hit, N_BOOT, rng)
    row = dict(cell=tag, rule=rule, W=w, n_min=nmin, periods=pc,
               hits=int(obs[:, 1].sum()), evaluable=int(obs[:, 0].sum()), H_obs=H_obs,
               H_null_mean=float(H_null.mean()), H_null_sd=float(H_null.std()),
               p_N1=p_value_upper(H_obs, H_null),
               p_N1_authors=p_value_upper(19 / 59, H_null) if (w, nmin, pc) == (0.20, 2, "spacing") else np.nan,
               excess_hits=exc, excess_lo=ci[0], excess_hi=ci[1])
    n1_rows.append(row)
    if (w, nmin, pc) == (0.20, 2, "spacing"):
        keep_draws[f"N1_{rule}"] = H_null
    print(f"[{time.time()-t0:6.0f}s] N1 {tag:14s} {rule:16s} H={H_obs:.3f} null={H_null.mean():.3f} p={row['p_N1']:.4f}",
          flush=True)
n1 = pd.DataFrame(n1_rows)
n1.to_csv(OUT / "partB_n1.csv", index=False)

# ---------------------------------------------------------------- N2
psd_rows, sims = [], {}
rng2 = np.random.default_rng(SEED + 1)
for model in ("PL", "BPL"):
    sims[model] = []
    for s in sources:
        pre = s["detected"] & pretest
        fit = fit_psd(s["flux"][pretest], s["detected"][pretest], 30.0, model)
        psd_rows.append(dict(source=s["name"], model=model, params=fit["params"], nll=fit["nll"]))
        sampler = bootstrap_sampler(s["flux"][pre])
        sims[model].append(np.array([emmanoulopoulos(grid.size, 30.0, fit["psd"], sampler, rng2)
                                     for _ in range(N2_SIMS)]))
    print(f"[{time.time()-t0:6.0f}s] simulated N2 {model}", flush=True)
pd.DataFrame(psd_rows).to_csv(OUT / "psd_fits.csv", index=False)

n2_rows = []
for model in ("PL", "BPL"):
    for rule in RULES:
        ev = np.zeros((N2_SIMS, len(sources)), int)
        hit = np.zeros_like(ev)
        for j, s in enumerate(sources):
            ev[:, j], hit[:, j] = score_simulations(s, sims[model][j], rule, pretest)
        H_null = hit.sum(1) / np.maximum(ev.sum(1), 1)
        H_obs = float(n1.loc[(n1.cell == "primary-grid") & (n1.rule == rule), "H_obs"].iloc[0])
        n2_rows.append(dict(model=model, rule=rule, H_obs=H_obs, H_null_mean=float(H_null.mean()),
                            H_null_sd=float(H_null.std()), p_N2=p_value_upper(H_obs, H_null),
                            p_N2_authors=p_value_upper(19 / 59, H_null)))
        keep_draws[f"N2{model}_{rule}"] = H_null
        print(f"[{time.time()-t0:6.0f}s] N2 {model} {rule:16s} null={H_null.mean():.3f} p={n2_rows[-1]['p_N2']:.4f}",
              flush=True)
pd.DataFrame(n2_rows).to_csv(OUT / "partB_n2.csv", index=False)

# ---------------------------------------------------------------- power check (primary rule, or each candidate)
power_rules = [primary] if primary else list(CANDIDATES)
pw_rows = []
rng3 = np.random.default_rng(SEED + 2)
for rule in power_rules:
    for amp in (0.25, 0.5, 1.0, 2.0):
        ps = []
        for i in range(POWER_REAL):
            inj = []
            for j, s in enumerate(sources):
                f = sims["PL"][j][i]
                sd = np.std(s["flux"][s["detected"]])
                f = f + amp * sd * np.cos(2 * np.pi * (grid - s["t_preds"][0]) / s["period"])
                pre = s["detected"] & pretest
                inj.append({**s, "flux": f, "ref_level": (np.median(f[pre]), np.std(f[pre]))})
            obs = np.array([score_source(x["t"], x["flux"], x["detected"], x["t_preds"], x["period"], rule,
                                         MatchSettings(), x["ref_level"])[:2] for x in inj])
            ev, hit = n1_random_phase_fast(inj, rule, POWER_N1, rng3, step=5.0)
            H_null = hit.sum(1) / np.maximum(ev.sum(1), 1)
            ps.append(p_value_upper(obs[:, 1].sum() / obs[:, 0].sum(), H_null))
        ps = np.array(ps)
        pw_rows.append(dict(rule=rule, amplitude_sd=amp, power=float(np.mean(ps < 0.05)),
                            n_realisations=POWER_REAL))
        print(f"[{time.time()-t0:6.0f}s] power {rule} a={amp}: {pw_rows[-1]['power']:.2f}", flush=True)
# false-positive rate: amplitude 0 (pure N2 PL light curves)
for rule in power_rules:
    ps = []
    for i in range(POWER_REAL):
        inj = []
        for j, s in enumerate(sources):
            f = sims["PL"][j][i]
            pre = s["detected"] & pretest
            inj.append({**s, "flux": f, "ref_level": (np.median(f[pre]), np.std(f[pre]))})
        obs = np.array([score_source(x["t"], x["flux"], x["detected"], x["t_preds"], x["period"], rule,
                                     MatchSettings(), x["ref_level"])[:2] for x in inj])
        ev, hit = n1_random_phase_fast(inj, rule, POWER_N1, rng3, step=5.0)
        ps.append(p_value_upper(obs[:, 1].sum() / obs[:, 0].sum(), hit.sum(1) / np.maximum(ev.sum(1), 1)))
    pw_rows.append(dict(rule=rule, amplitude_sd=0.0, power=float(np.mean(np.array(ps) < 0.05)),
                        n_realisations=POWER_REAL))
pd.DataFrame(pw_rows).to_csv(OUT / "power.csv", index=False)

# ---------------------------------------------------------------- negative control (cyclic derangement)
nc_rows = []
for rule in CANDIDATES:
    swapped = []
    for j, s in enumerate(sources):
        o = sources[(j + 1) % len(sources)]
        pre = o["detected"] & pretest
        swapped.append({**o, "t_preds": s["t_preds"], "period": s["period"], "name": s["name"]})
    obs, ev, hit, H_obs, H_null = n1_cell(swapped, rule, MatchSettings(), rng)
    nc_rows.append(dict(rule=rule, H_obs=H_obs, H_null_mean=float(H_null.mean()),
                        p_N1=p_value_upper(H_obs, H_null)))
pd.DataFrame(nc_rows).to_csv(OUT / "negative_control.csv", index=False)

np.savez_compressed(OUT / "null_draws.npz", **keep_draws)
summary = dict(n_sources=len(sources), n_forecasts=int(sum(s["t_preds"].size for s in sources)),
               primary_rule=primary, best_candidate=str(best.rule), best_kappa=float(best.kappa),
               n1_draws=N1_DRAWS, n2_sims=N2_SIMS, quick=args.quick, seed=SEED,
               partB_end_mjd=PARTB_END_MJD, pretest_end_mjd=PRETEST_END_MJD)
(OUT / "partB_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
