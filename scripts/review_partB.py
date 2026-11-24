"""Critical-review checks of Part B (EXPLORATORY: none of this was pre-registered).

Added on 2026-11-25, after the Part B results were known. Nothing here replaces a
pre-registered number; it tests how far those numbers can be trusted.

Checks
------
A. Rule selection. kappa = 0.34 is the best of four rules and kappa = 0.47 (X1) is the
   best of the AND-combinations, both picked on the same 59 verdicts they are scored on.
   (1) source-level bootstrap intervals; (2) leave-one-source-out selection: choose the
   best rule on 29 sources, apply it to the held-out source, pool the held-out verdicts;
   (3) a permutation test of the maximum kappa (labels shuffled between forecasts).
B. Negative control over ALL 29 cyclic source shifts, not only shift 1.
C. Which forecasts are not evaluable, and PSD fits that sit on a bound.
D. "Fitted-forecast" red-noise check. N1 and N2 both treat a chance forecast as one with
   a random phase. Real forecasts were extrapolated from the same light curve, and red
   noise has memory. We fit a sinusoid to the first 12 yr of each simulated red-noise
   light curve, forecast its next maxima, and score them. If these hit more often than
   random-phase forecasts on the same simulations, N1/N2 understate the chance rate.

Usage:  python scripts/review_partB.py        (about 10 minutes, one core)
Output: results/review_partB.json, results/review_negative_control.csv
"""
from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
from scipy import stats

from config import PARTB_END_MJD
from match import RULES, MatchSettings, score_source
from nulls import n1_random_phase_fast, p_value_upper
from partb_data import GRID, PRETEST, cohen_kappa, load_sources
from psd_fit import fit_psd
from simulate import bootstrap_sampler, emmanoulopoulos

SEED = 20261125
CAND = list(RULES[1:])
rng = np.random.default_rng(SEED)
t0 = time.time()
out = {"note": "Exploratory review checks, run 2026-11-25 after Part B results were known."}

sources, a7 = load_sources()
names = [s["name"] for s in sources]

# ------------------------------------------------------------------ verdict table
rows = []
for s in sources:
    for tp in s["t_preds"]:
        r = dict(source=s["name"], t_pred=tp)
        for rule in CAND:
            e, h, _ = score_source(s["t"], s["flux"], s["detected"], [tp], s["period"], rule,
                                   MatchSettings(), s["ref_level"])
            r[rule], r[rule + "_eval"] = int(h), int(e)
        rows.append(r)
v = pd.DataFrame(rows).merge(a7[["source", "t_pred", "supported", "predicted_epoch"]], on=["source", "t_pred"])
assert len(v) == 59

# family of AND-combinations (15 non-empty subsets of R1..R4; singles included)
combos = [c for k in range(1, 5) for c in itertools.combinations(CAND, k)]
for c in combos:
    v["&".join(c)] = v[list(c)].min(axis=1)
single_cols = CAND
combo_cols = ["&".join(c) for c in combos]
truth = v.supported.to_numpy()


def best_of(cols, idx):
    ks = [cohen_kappa(v[c].to_numpy()[idx], truth[idx]) for c in cols]
    ks = [-9 if not np.isfinite(k) else k for k in ks]
    j = int(np.argmax(ks))
    return cols[j], ks[j]


full = np.arange(len(v))
src_idx = {n: np.flatnonzero(v.source.to_numpy() == n) for n in names}
A = {}
for fam, cols in (("R1-R4", single_cols), ("AND-combinations", combo_cols)):
    name, k = best_of(cols, full)
    # (1) bootstrap of the chosen rule's kappa, and of the whole "pick the best" procedure
    kb_fixed, kb_proc = [], []
    for _ in range(4000):
        pick = rng.choice(names, len(names), replace=True)
        idx = np.concatenate([src_idx[n] for n in pick])
        kf = cohen_kappa(v[name].to_numpy()[idx], truth[idx])
        if np.isfinite(kf):
            kb_fixed.append(kf)
    # (2) leave-one-source-out selection
    held = np.zeros(len(v), int)
    chosen = []
    for n in names:
        tr = np.setdiff1d(full, src_idx[n])
        c, _ = best_of(cols, tr)
        chosen.append(c)
        held[src_idx[n]] = v[c].to_numpy()[src_idx[n]]
    k_loso = cohen_kappa(held, truth)
    # (3) permutation test of the maximum kappa over the family
    kmax = []
    for _ in range(4000):
        perm = rng.permutation(truth)
        kmax.append(max(cohen_kappa(v[c].to_numpy(), perm) for c in cols))
    A[fam] = dict(best_rule=name, kappa_in_sample=float(k),
                  kappa_bootstrap_95=[float(x) for x in np.percentile(kb_fixed, [2.5, 97.5])],
                  kappa_leave_one_source_out=float(k_loso),
                  loso_rule_counts=pd.Series(chosen).value_counts().to_dict(),
                  n_rules_in_family=len(cols),
                  perm_null_max_kappa_mean=float(np.mean(kmax)),
                  perm_null_max_kappa_95th=float(np.percentile(kmax, 95)),
                  perm_p_value=float(p_value_upper(k, kmax)))
    print(f"[{time.time()-t0:5.0f}s] A {fam}: {A[fam]}", flush=True)
A["all_combo_kappas"] = {c: float(cohen_kappa(v[c], truth)) for c in combo_cols}
A["confusion_R3"] = pd.crosstab(v.R3_high_state, v.supported).to_dict()
A["confusion_X1"] = pd.crosstab(v["R3_high_state&R4_cycle_max"], v.supported).to_dict()
out["A_rule_selection"] = A

# ------------------------------------------------------------------ B negative control, all shifts
nc = []
for shift in range(1, len(sources)):
    swapped = [{**sources[(j + shift) % len(sources)], "t_preds": s["t_preds"], "period": s["period"],
                "name": s["name"]} for j, s in enumerate(sources)]
    for rule in CAND:
        obs = np.array([score_source(x["t"], x["flux"], x["detected"], x["t_preds"], x["period"], rule,
                                     MatchSettings(), x["ref_level"])[:2] for x in swapped])
        ev, hit = n1_random_phase_fast(swapped, rule, 2000, rng)
        Hn = hit.sum(1) / np.maximum(ev.sum(1), 1)
        Ho = obs[:, 1].sum() / obs[:, 0].sum()
        nc.append(dict(shift=shift, rule=rule, H_obs=Ho, H_null_mean=float(Hn.mean()),
                       p_N1=p_value_upper(Ho, Hn)))
    print(f"[{time.time()-t0:5.0f}s] B shift {shift}", flush=True)
nc = pd.DataFrame(nc)
nc.to_csv(ROOT / "results/review_negative_control.csv", index=False)
B = {}
for rule, g in nc.groupby("rule"):
    B[rule] = dict(n_shifts=len(g), median_p=float(g.p_N1.median()), min_p=float(g.p_N1.min()),
                   frac_p_below_0p05=float((g.p_N1 < 0.05).mean()),
                   frac_p_below_0p5=float((g.p_N1 < 0.5).mean()),
                   mean_H_obs_minus_null=float((g.H_obs - g.H_null_mean).mean()),
                   ks_uniform_p=float(stats.kstest(g.p_N1, "uniform").pvalue))
B["note"] = ("The 29 shifts reuse the same light curves and forecasts, so they are not independent; "
             "the KS p-value is only a rough guide.")
out["B_negative_control_all_shifts"] = B
print(B, flush=True)

# ------------------------------------------------------------------ C bookkeeping
ne = v[v.R1_interior_max_eval == 0][["source", "predicted_epoch", "supported"]]
out["C_not_evaluable"] = ne.to_dict("records")
out["C_authors_hits_among_evaluable"] = int(v.supported[v.R1_interior_max_eval == 1].sum())
out["C_n_det_pretest_min"] = int(min((s["detected"] & PRETEST).sum() for s in sources))
psd = pd.read_csv(ROOT / "results/psd_fits.csv")
pl_beta = np.array([json.loads(p)[1] for p in psd[psd.model == "PL"].params])
out["C_PL_beta"] = dict(min=float(pl_beta.min()), median=float(np.median(pl_beta)), max=float(pl_beta.max()),
                        n_at_lower_bound=int((pl_beta < 0.01).sum()), n_at_upper_bound=int((pl_beta > 3.99).sum()))
print(out["C_not_evaluable"], out["C_PL_beta"], flush=True)

# ------------------------------------------------------------------ D fitted-forecast red-noise check
N_SIM = 400
pre_end = GRID[PRETEST][-1]


def sinus_forecasts(t, f, period):
    """Least-squares sinusoid of the given period on (t, f); maxima between pre_end and the data end."""
    w = 2 * np.pi / period
    X = np.column_stack([np.ones(t.size), np.cos(w * t), np.sin(w * t)])
    c, *_ = np.linalg.lstsq(X, f, rcond=None)
    t_max = np.arctan2(c[2], c[1]) / w                      # one maximum of the fitted sinusoid
    k = np.arange(np.ceil((pre_end - t_max) / period), np.floor((PARTB_END_MJD - t_max) / period) + 1)
    return t_max + k * period, float(np.sum((f - X @ c) ** 2))


def best_period_forecasts(t, f):
    """Scan periods 1-6 yr, keep the best-fitting sinusoid (a stand-in for a period search)."""
    best = None
    for P in np.arange(365.25, 6 * 365.25 + 1, 30.0):
        tp, rss = sinus_forecasts(t, f, P)
        if best is None or rss < best[2]:
            best = (tp, P, rss)
    return best[0], best[1]


D = {}
tot = {mode: {r: np.zeros((N_SIM, 2)) for r in CAND} for mode in ("fitted_fixed_T", "fitted_best_T", "real_forecasts")}
rngD = np.random.default_rng(SEED + 3)
for j, s in enumerate(sources):
    pre = s["detected"] & PRETEST
    fit = fit_psd(s["flux"][PRETEST], s["detected"][PRETEST], 30.0, "PL")
    sampler = bootstrap_sampler(s["flux"][pre])
    for i in range(N_SIM):
        f = emmanoulopoulos(GRID.size, 30.0, fit["psd"], sampler, rngD)
        ref = (np.median(f[pre]), np.std(f[pre]))
        tp_fix, _ = sinus_forecasts(GRID[pre], f[pre], s["period"])
        tp_best, P_best = best_period_forecasts(GRID[pre], f[pre])
        for mode, tp, P in (("fitted_fixed_T", tp_fix, s["period"]), ("fitted_best_T", tp_best, P_best),
                            ("real_forecasts", s["t_preds"], s["period"])):
            if len(tp) == 0:
                continue
            for r in CAND:
                e, h, _ = score_source(GRID, f, s["detected"], tp, P, r, MatchSettings(), ref)
                tot[mode][r][i] += (e, h)
    print(f"[{time.time()-t0:5.0f}s] D source {j+1}/30", flush=True)
for mode in tot:
    D[mode] = {}
    for r in CAND:
        H = tot[mode][r][:, 1] / np.maximum(tot[mode][r][:, 0], 1)
        D[mode][r] = dict(H_mean=float(H.mean()), H_sd=float(H.std()),
                          mean_evaluable=float(tot[mode][r][:, 0].mean()))
D["difference_fixed_T_minus_real"] = {r: D["fitted_fixed_T"][r]["H_mean"] - D["real_forecasts"][r]["H_mean"] for r in CAND}
D["difference_best_T_minus_real"] = {r: D["fitted_best_T"][r]["H_mean"] - D["real_forecasts"][r]["H_mean"] for r in CAND}
D["note"] = ("Red-noise simulations (power-law PSD fitted to each source's first 12 yr, Emmanoulopoulos "
             f"method, {N_SIM} per source). 'fitted' forecasts come from a sinusoid fitted to the simulated "
             "first 12 yr; 'real_forecasts' are the Table A7 epochs, which are unrelated to the simulation "
             "(= the N2 null). A positive difference means that forecasts extrapolated from red noise hit "
             "more often than random-phase forecasts. The sinusoid fit is only a proxy for the SSA and "
             "phase-folding forecasts of the original papers.")
out["D_fitted_forecast_check"] = D
print(json.dumps(D, indent=1), flush=True)

(ROOT / "results/review_partB.json").write_text(json.dumps(out, indent=2, default=float))
print("wrote results/review_partB.json")
