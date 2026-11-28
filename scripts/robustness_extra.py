"""Extra robustness checks of Part B (EXPLORATORY: added 2026-11-28, after the results were known).

None of these cells was in the pre-registered robustness grid. They vary choices that the
plan fixed by assumption because Peñil et al. (2026) do not state them, and they probe how
much single sources and Monte Carlo noise move the answers.

A. Data end date: MJD 60800, 60900, 61000 (plan: 61000).
B. Day of the month assumed for a forecast given as a month: 1, 15, 28 (plan: 15).
C. R3 threshold: median + k s.d. with k = 0.5, 1, 1.5, 2 (plan: 1), and the reference level
   taken from the whole light curve instead of the first 12 yr.
D. Leave one source out: N1 p-value of each rule without each source in turn.
E. Monte Carlo stability: N1 p-values for five other seeds.
F. R4 calibrated on the negative control: the excess of R4 over its N1 mean compared with the
   excesses of the 29 unrelated forecast/light-curve pairings (results/review_negative_control.csv).
G. Two-sided reading of the N2 results (the plan was one-sided).
H. Source-level pattern (all / none / mixed forecasts supported) for each rule.

Usage:  python scripts/robustness_extra.py     (a few minutes, one core)
Output: results/robustness_extra.json, results/robustness_extra.csv
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

from config import DAYS_PER_YEAR, LCR_START_MJD, PARTB_END_MJD, PRETEST_END_MJD
from lcr import fetch
from match import RULES, MatchSettings, score_source
from nulls import n1_random_phase_fast, p_value_upper
from partb_data import cohen_kappa

CAND = list(RULES[1:])
SEED = 20261128
N1_DRAWS = 10_000
t0 = time.time()
a7 = pd.read_csv(ROOT / "data/penil_tableA7.csv")
meta = pd.read_csv(ROOT / "data/penil_sources.csv").set_index("source")
names = list(dict.fromkeys(a7.source))


def to_mjd(s, day):
    s = str(s)
    ts = pd.Timestamp(s if len(s) > 7 else f"{s}-{day:02d}")     # a full date is used as given
    return (ts - pd.Timestamp("1858-11-17")).days


def load(end_mjd=PARTB_END_MJD, day=15, ref="pretest"):
    """Same construction as src/partb_data.load_sources, with the end date, day and R3 reference variable."""
    grid = np.arange(LCR_START_MJD + 16.0, end_mjd + 0.1, 30.0)
    out = []
    for name in names:
        lc = fetch(meta.loc[name, "fgl_name"], PARTB_END_MJD, ROOT / "data/lcr")   # cached file only
        flux = np.full(grid.size, np.nan)
        k = np.rint((lc["t"] - grid[0]) / 30.0).astype(int)
        ok = (k >= 0) & (k < grid.size) & lc["detected"]
        flux[k[ok]] = lc["flux"][ok]
        det = np.isfinite(flux)
        rows = a7[a7.source == name]
        tp = np.array([to_mjd(e, day) for e in rows.predicted_epoch], float)
        order = np.argsort(tp)
        tp, sup = tp[order], rows.supported.to_numpy()[order]
        T = float(np.mean(np.diff(tp))) if tp.size >= 2 else float(meta.loc[name, "table1_period_yr"]) * DAYS_PER_YEAR
        sel = det & (grid < PRETEST_END_MJD) if ref == "pretest" else det
        out.append(dict(name=name, t=grid, flux=flux, detected=det, t_preds=tp, period=T, supported=sup,
                        ref_level=(float(np.median(flux[sel])), float(np.std(flux[sel])))))
    return out


def evaluate(srcs, rule, settings=MatchSettings(), seed=SEED, n_draws=N1_DRAWS):
    verd, truth, obs = [], [], []
    for s in srcs:
        e, h, res = score_source(s["t"], s["flux"], s["detected"], s["t_preds"], s["period"], rule,
                                 settings, s["ref_level"])
        verd += [int(r.hit) for r in res]
        truth += list(s["supported"])
        obs.append((e, h))
    obs = np.array(obs)
    ev, hit = n1_random_phase_fast(srcs, rule, n_draws, np.random.default_rng(seed), settings)
    Hn = hit.sum(1) / np.maximum(ev.sum(1), 1)
    Ho = obs[:, 1].sum() / obs[:, 0].sum()
    return dict(kappa=float(cohen_kappa(verd, truth)), hits=int(obs[:, 1].sum()), evaluable=int(obs[:, 0].sum()),
                H_obs=float(Ho), N1_mean=float(Hn.mean()), N1_sd=float(Hn.std()), p_N1=float(p_value_upper(Ho, Hn)))


rows = []


def add(check, setting, srcs, rules=CAND, settings=MatchSettings(), **kw):
    for r in rules:
        rows.append(dict(check=check, setting=setting, rule=r, **evaluate(srcs, r, settings, **kw)))
    print(f"[{time.time()-t0:5.0f}s] {check} {setting}", flush=True)


base = load()
add("baseline", "plan (end 61000, day 15, k=1)", base)
for end in (60800.0, 60900.0):
    add("A_end_date", f"end MJD {end:.0f}", load(end_mjd=end))
for day in (1, 28):
    add("B_day_of_month", f"day {day}", load(day=day))
for k in (0.5, 1.5, 2.0):
    add("C_R3_threshold", f"k = {k}", base, rules=["R3_high_state"], settings=MatchSettings(high_state_k=k))
add("C_R3_threshold", "k = 1, reference from whole light curve", load(ref="all"), rules=["R3_high_state"])
for i, n in enumerate(names):
    add("D_leave_one_source_out", n, [s for s in base if s["name"] != n])
for seed in (1, 2, 3, 4, 5):
    add("E_seed", f"seed {seed}", base, seed=seed)
df = pd.DataFrame(rows)
df.to_csv(ROOT / "results/robustness_extra.csv", index=False)

out = {"note": "Exploratory robustness checks added 2026-11-28; see scripts/robustness_extra.py."}
b = df[df.check == "baseline"].set_index("rule")
# the baseline must reproduce the pre-registered run (different seed, so p within Monte Carlo noise)
n1 = pd.read_csv(ROOT / "results/partB_n1.csv")
n1 = n1[n1.cell == "primary-grid"].set_index("rule")
out["baseline_check"] = {r: dict(hits_match=bool(b.loc[r, "hits"] == n1.loc[r, "hits"]),
                                 H_obs_match=bool(abs(b.loc[r, "H_obs"] - n1.loc[r, "H_obs"]) < 1e-12),
                                 p_this_seed=float(b.loc[r, "p_N1"]), p_registered_run=float(n1.loc[r, "p_N1"]))
                         for r in CAND}
for chk in ("A_end_date", "B_day_of_month", "C_R3_threshold"):
    out[chk] = {f"{r.setting} | {r.rule}": dict(kappa=r.kappa, hits=r.hits, evaluable=r.evaluable, H_obs=r.H_obs,
                                                N1_mean=r.N1_mean, p_N1=r.p_N1)
                for r in df[df.check == chk].itertuples()}
ab = df[df.check.isin(["A_end_date", "B_day_of_month", "C_R3_threshold"])]
out["ABC_summary"] = dict(n_cells=int(len(ab)), min_p=float(ab.p_N1.min()), max_p=float(ab.p_N1.max()),
                          max_kappa=float(ab.kappa.max()),
                          cell_of_min_p=ab.loc[ab.p_N1.idxmin(), ["check", "setting", "rule"]].to_dict(),
                          cell_of_max_kappa=ab.loc[ab.kappa.idxmax(), ["check", "setting", "rule"]].to_dict())
d = df[df.check == "D_leave_one_source_out"]
out["D_leave_one_source_out"] = {
    r: dict(min_p=float(g.p_N1.min()), source_removed_at_min=g.loc[g.p_N1.idxmin(), "setting"],
            max_p=float(g.p_N1.max()), source_removed_at_max=g.loc[g.p_N1.idxmax(), "setting"],
            kappa_min=float(g.kappa.min()), kappa_max=float(g.kappa.max()))
    for r, g in d.groupby("rule")}
e = df[df.check == "E_seed"]
out["E_seed"] = {r: dict(min_p=float(g.p_N1.min()), max_p=float(g.p_N1.max())) for r, g in e.groupby("rule")}

# F: R4 excess against the negative-control excesses
nc = pd.read_csv(ROOT / "results/review_negative_control.csv")
out["F_negative_control_calibration"] = {}
for r in CAND:
    g = nc[nc.rule == r]
    exc = (g.H_obs - g.H_null_mean).to_numpy()
    obs_exc = float(n1.loc[r, "H_obs"] - n1.loc[r, "H_null_mean"])
    out["F_negative_control_calibration"][r] = dict(
        observed_excess=obs_exc, control_excess_mean=float(exc.mean()), control_excess_sd=float(exc.std(ddof=1)),
        n_control=int(exc.size), n_control_at_least_observed=int((exc >= obs_exc).sum()),
        empirical_p=float((1 + (exc >= obs_exc).sum()) / (1 + exc.size)))
out["F_note"] = ("The 29 control pairings share light curves and forecasts, so they are not independent; "
                 "the smallest possible empirical p is 1/30.")

# G: two-sided reading of N2
draws = np.load(ROOT / "results/null_draws.npz")
out["G_two_sided_N2"] = {}
for m in ("PL", "BPL"):
    for r in CAND:
        Hn = draws[f"N2{m}_{r}"]
        Ho = float(n1.loc[r, "H_obs"])
        pu = (1 + np.sum(Hn >= Ho)) / (1 + Hn.size)
        pl = (1 + np.sum(Hn <= Ho)) / (1 + Hn.size)
        out["G_two_sided_N2"][f"{m} | {r}"] = dict(p_upper=float(pu), p_lower=float(pl),
                                                    p_two_sided=float(min(1.0, 2 * min(pu, pl))))

# H: source-level pattern
q0 = pd.read_csv(ROOT / "results/q0_verdicts.csv")


def pattern(col):
    g = q0.groupby("source")[col].agg(["sum", "count"])
    return dict(all=int((g["sum"] == g["count"]).sum()), none=int((g["sum"] == 0).sum()),
                mixed=int(((g["sum"] > 0) & (g["sum"] < g["count"])).sum()))


out["H_source_level"] = {"published": pattern("supported"), **{r: pattern(r) for r in CAND}}
(ROOT / "results/robustness_extra.json").write_text(json.dumps(out, indent=2, default=str))
print(json.dumps({k: v for k, v in out.items() if k not in ("A_end_date", "B_day_of_month", "C_R3_threshold")},
                 indent=1, default=str))
