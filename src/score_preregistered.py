"""Part C: score the pre-registered Table 3 forecasts of Peñil et al. (2026).

Implements preregistration/predictions_2026.md, Sections 5 and 6, with the
clarifications listed in preregistration/2026-11-25_amendment_2.md.

What the pre-registration fixes
-------------------------------
* 13 forecasts: the first predicted peak of each (source, method) row of Table 3.
* Window = predicted month (day 15) +/- 0.20 T, T = the Table 3 period.
* Each forecast is scored ONCE, when LCR data reach 3 months past its window end.
* Rule: the Part B primary rule. Part B found none (no candidate reached
  kappa >= 0.7), so all of R1-R4 are scored and no single headline p-value is claimed.
* p_i, the chance probability of forecast i, comes from the N1 null (random common
  phase shift, 10,000 draws) on that source's own light curve.
* Test: total hits against the Poisson-binomial distribution of the p_i, one-sided,
  for the primary set (5 windows that opened after the pre-registration), the full
  set (13) and a one-forecast-per-source set (phase folding, 8).

Blinding
--------
`--score` refuses to touch a forecast before its scoring date, and downloads are
truncated at that date by `lcr.fetch` before anything is saved. `--dry-run` uses
simulated light curves only and never imports the download code.

Usage
-----
    python src/score_preregistered.py --schedule      # dates only, no data
    python src/score_preregistered.py --dry-run       # simulated data only
    python src/score_preregistered.py --score         # real data; only forecasts that are due
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DAYS_PER_YEAR, LCR_START_MJD, PRETEST_END_MJD  # noqa: E402
from match import RULES, MatchSettings, score_source  # noqa: E402
from nulls import n1_random_phase_fast  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = RULES[1:]                       # R1..R4 (Part B found no primary rule)
PREREG_DATE = pd.Timestamp("2026-11-22")     # date written in predictions_2026.md
N1_DRAWS = 10_000
SEED = 20261125
MJD0 = pd.Timestamp("1858-11-17")
GRID0 = LCR_START_MJD + 16.0                 # first bin centre of the regular 30-day grid (as Part B)
PARTB_END_MJD = 61000.0                      # data the Table 3 forecasts were made from

# LCR source names. The first five were used in Part B or checked in PROPOSAL.md Sec. 5.
# PKS 0215+015 has NOT been checked against the LCR (no Part C source is downloaded
# before its scoring date); if the name is wrong, `--score` stops with a clear error.
LCR_NAME = {
    "PG 1553+113": "4FGL J1555.7+1111",
    "S5 1044+71": "4FGL J1048.4+7143",
    "OJ 014": "4FGL J0811.4+0146",
    "S4 1144+40": "4FGL J1146.9+3958",
    "87GB 164812.2+524023": "4FGL J1649.4+5235",
    "S3 0458-02": "4FGL J0501.2-0158",
    "TXS 0518+211": "4FGL J0521.7+2112",
    "PKS 0215+015": "4FGL J0217.8+0144",
}


def to_mjd(ts):
    return (pd.Timestamp(ts) - MJD0) / pd.Timedelta(days=1)


def from_mjd(mjd):
    return MJD0 + pd.Timedelta(days=float(mjd))


def build_forecasts(csv=ROOT / "data/penil_table3_predictions.csv"):
    """The 13 pre-registered forecasts with windows and scoring dates."""
    tab = pd.read_csv(csv)
    rows = []
    for _, r in tab.iterrows():
        T = float(r.period_yr) * DAYS_PER_YEAR
        t_pred = to_mjd(f"{r.predicted_peak_1}-15")
        lo, hi = t_pred - 0.20 * T, t_pred + 0.20 * T
        score_date = (from_mjd(hi) + pd.DateOffset(months=3)).normalize() + pd.Timedelta(days=1)
        rows.append(dict(source=r.source, method=r.method, predicted=r.predicted_peak_1, period_d=T,
                         t_pred=t_pred, win_lo=lo, win_hi=hi,
                         win_lo_date=str(from_mjd(lo).date()), win_hi_date=str(from_mjd(hi).date()),
                         score_date=str(score_date.date()), score_mjd=float(to_mjd(score_date)),
                         primary=bool(from_mjd(lo) > PREREG_DATE)))
    out = pd.DataFrame(rows).sort_values(["win_lo", "source"]).reset_index(drop=True)
    out["id"] = out.source + " | " + out.method
    return out


def poisson_binomial_sf(p, k):
    """P(K >= k) for K = sum of independent Bernoulli(p_i). Exact, by convolution."""
    pmf = np.array([1.0])
    for pi in np.asarray(p, float):
        pmf = np.convolve(pmf, [1.0 - pi, pi])
    return float(pmf[int(k):].sum()) if k <= len(pmf) - 1 else 0.0


def regular_grid(t, flux, detected, end_mjd):
    """Place a light curve on the regular 30-day grid used in Part B (amendment 1, item 3)."""
    grid = np.arange(GRID0, end_mjd + 0.1, 30.0)
    out = np.full(grid.size, np.nan)
    k = np.rint((np.asarray(t, float) - GRID0) / 30.0).astype(int)
    ok = (k >= 0) & (k < grid.size) & np.asarray(detected, bool)
    out[k[ok]] = np.asarray(flux, float)[ok]
    return grid, out, np.isfinite(out)


def score_one(grid, flux, det, t_pred, period, rng, n_draws=N1_DRAWS, ref_end=PRETEST_END_MJD):
    """Score one forecast with every candidate rule; chance probability from N1.

    The R3 reference level (median, std) uses detected bins with centre < ref_end.
    Returns {rule: dict(evaluable, hit, p_chance, null_evaluable_frac)}.
    p_chance = P(hit | evaluable) over the N1 draws, matching the Part B statistic
    H = hits / evaluable. A forecast that is not evaluable does not enter the test.
    """
    pre = det & (grid < ref_end)
    ref = (float(np.median(flux[pre])), float(np.std(flux[pre]))) if pre.sum() >= 2 else None
    src = dict(t=grid, flux=flux, detected=det, t_preds=np.array([t_pred]), period=period, ref_level=ref)
    res = {}
    for rule in CANDIDATES:
        e, h, _ = score_source(grid, flux, det, [t_pred], period, rule, MatchSettings(), ref)
        ev, hit = n1_random_phase_fast([src], rule, n_draws, rng)
        n_ev = int(ev.sum())
        res[rule] = dict(evaluable=int(e), hit=int(h),
                         p_chance=float(hit.sum() / n_ev) if n_ev else float("nan"),
                         null_evaluable_frac=n_ev / n_draws)
    return res


def combine(scores, forecasts):
    """Poisson-binomial tests for the three pre-registered sets.

    scores : {forecast id: {rule: dict(evaluable, hit, p_chance)}}
    """
    sets = {"primary_5": forecasts[forecasts.primary].id,
            "all_13": forecasts.id,
            "one_per_source_phase_folding": forecasts[forecasts.method == "phase_folding"].id}
    out = {}
    for sname, ids in sets.items():
        out[sname] = {}
        for rule in CANDIDATES:
            rows = [scores[i][rule] for i in ids if i in scores]
            ev = [r for r in rows if r["evaluable"] and np.isfinite(r["p_chance"])]
            hits = sum(r["hit"] for r in ev)
            p = [r["p_chance"] for r in ev]
            out[sname][rule] = dict(n_planned=len(ids), n_scored=len(rows), n_evaluable=len(ev),
                                    hits=int(hits), expected_hits=float(np.sum(p)),
                                    p_value=poisson_binomial_sf(p, hits) if ev else float("nan"),
                                    complete=len(rows) == len(ids))
    return out


# --------------------------------------------------------------------------- real scoring
def run_score(today=None):
    from lcr import fetch                     # imported here so --dry-run never loads it

    today = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize() if today is None else pd.Timestamp(today)
    fc = build_forecasts()
    out_csv = ROOT / "results/partC_scores.csv"
    done = pd.read_csv(out_csv) if out_csv.exists() else pd.DataFrame(columns=["id"])
    rng = np.random.default_rng(SEED)
    new = []
    for _, f in fc.iterrows():
        if f.id in set(done.id):
            continue                                              # scored once, never again
        if today < pd.Timestamp(f.score_date):
            print(f"not due   {f.id:45s} scoring date {f.score_date}")
            continue
        lc = fetch(LCR_NAME[f.source], f.score_mjd, ROOT / "data/lcr")
        if lc["t"].size == 0:
            raise SystemExit(f"LCR returned no data for {f.source} ({LCR_NAME[f.source]}): check the name")
        if lc["t"].max() < f.score_mjd - 45.0:
            print(f"data short {f.id:45s} last bin MJD {lc['t'].max():.0f} < {f.score_mjd:.0f}; try later")
            Path(ROOT / "data/lcr" / f"{LCR_NAME[f.source].replace(' ', '_')}_end{f.score_mjd:.0f}.json").unlink()
            continue
        grid, flux, det = regular_grid(lc["t"], lc["flux"], lc["detected"], f.score_mjd)
        for ref_name, ref_end in (("pretest_59065", PRETEST_END_MJD), ("forecast_data_61000", PARTB_END_MJD)):
            for rule, r in score_one(grid, flux, det, f.t_pred, f.period_d, rng, ref_end=ref_end).items():
                if ref_name != "pretest_59065" and rule != "R3_high_state":
                    continue                                      # the reference level only matters for R3
                new.append(dict(id=f.id, source=f.source, method=f.method, rule=rule, ref_level=ref_name,
                                scored_on=str(today.date()), data_end_mjd=f.score_mjd, **r))
        print(f"scored    {f.id}")
    if new:
        done = pd.concat([done, pd.DataFrame(new)], ignore_index=True)
        done.to_csv(out_csv, index=False)
    if len(done):
        main = done[done.ref_level == "pretest_59065"]
        scores = {i: {r.rule: dict(evaluable=r.evaluable, hit=r.hit, p_chance=r.p_chance)
                      for r in g.itertuples()} for i, g in main.groupby("id")}
        summ = combine(scores, fc)
        (ROOT / "results/partC_summary.json").write_text(json.dumps(summ, indent=2))
        print(json.dumps(summ, indent=2))


# --------------------------------------------------------------------------- dry run
def simulate_lc(grid, rng, beta=1.2, sigma_ln=0.6, gap_frac=0.1):
    """Red-noise light curve with lognormal fluxes and random non-detections (no real data)."""
    from simulate import emmanoulopoulos, lognormal_sampler, psd_power_law

    flux = emmanoulopoulos(grid.size, 30.0, lambda f: psd_power_law(f, beta),
                           lognormal_sampler(0.0, sigma_ln), rng)
    det = rng.random(grid.size) > gap_frac
    return flux, det


def run_dry(n_rep=200, n_draws=1000, amplitudes=(0.0, 0.5, 1.0, 2.0), out=None):
    """End-to-end check on SIMULATED light curves only.

    For each amplitude a, n_rep fake "skies" are made: every source gets a red-noise
    light curve (one per source, shared by its forecasts, as in reality) plus a sinusoid
    of period T and amplitude a x (flux s.d.), peaking at that source's first forecast.
    a = 0 measures the false-positive rate of the Poisson-binomial test; a > 0 its power.
    """
    fc = build_forecasts()
    rng = np.random.default_rng(SEED + 1)
    res = {}
    example = None
    for a in amplitudes:
        pv = {s: {r: [] for r in CANDIDATES} for s in ("primary_5", "all_13", "one_per_source_phase_folding")}
        for rep in range(n_rep):
            scores, lcs = {}, {}
            for _, f in fc.iterrows():
                grid = np.arange(GRID0, f.score_mjd + 0.1, 30.0)
                if f.source not in lcs:
                    gfull = np.arange(GRID0, fc.score_mjd.max() + 0.1, 30.0)
                    fl, det = simulate_lc(gfull, rng)
                    t0 = fc[fc.source == f.source].t_pred.iloc[0]
                    fl = fl + a * np.std(fl) * np.cos(2 * np.pi * (gfull - t0) / f.period_d)
                    lcs[f.source] = (fl, det)
                fl, det = (x[:grid.size] for x in lcs[f.source])
                fl = np.where(det, fl, np.nan)
                scores[f.id] = score_one(grid, fl, det, f.t_pred, f.period_d, rng, n_draws=n_draws)
            summ = combine(scores, fc)
            if example is None:
                example = dict(amplitude=a, scores=scores, summary=summ)
            for s in pv:
                for r in CANDIDATES:
                    pv[s][r].append(summ[s][r]["p_value"])
        res[str(a)] = {s: {r: dict(frac_p_below_0p05=float(np.mean(np.array(v) < 0.05)),
                                   median_p=float(np.median(v))) for r, v in d.items()}
                       for s, d in pv.items()}
        print(f"amplitude {a}: " + "; ".join(
            f"{s} " + "/".join(f"{res[str(a)][s][r]['frac_p_below_0p05']:.2f}" for r in CANDIDATES)
            for s in pv), flush=True)
    payload = dict(note="SIMULATED DATA ONLY. No LCR data were downloaded or read.",
                   n_rep=n_rep, n1_draws=n_draws, rules=list(CANDIDATES),
                   frac_significant=res, example_first_replicate=example)
    out = ROOT / "results/partC_dryrun.json" if out is None else Path(out)
    out.write_text(json.dumps(payload, indent=2, default=float))
    return payload


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--schedule", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--score", action="store_true")
    ap.add_argument("--n-rep", type=int, default=200)
    a = ap.parse_args()
    if a.schedule:
        cols = ["source", "method", "predicted", "win_lo_date", "win_hi_date", "score_date", "primary"]
        print(build_forecasts()[cols].to_string(index=False))
    elif a.dry_run:
        run_dry(n_rep=a.n_rep)
    else:
        run_score()
