"""Null distributions for the forecast hit count.

A "source" is a dict with keys:
    t, flux, detected  : light curve (days, flux, bool mask of detected bins)
    t_preds            : array of predicted peak times (days)
    period             : period T (days)
    ref_level          : optional (median, std) for rule R3, from pre-test data

N1 - randomised forecasts (primary null)
    Keep every real light curve. For each source, move ALL of its predicted
    times by one common random offset delta ~ Uniform(-T/2, T/2), i.e. a random
    phase. Score with the same rule. This asks: do the real forecast phases do
    better than random phases on the very same light curves? It needs no model
    of the noise. Because each draw shifts a whole source at once and then sums
    over all sources, correlations between predictions of the same source are
    kept.

N2 - red-noise light curves
    Keep the real forecasts. Replace each light curve by a simulated red-noise
    light curve on the same time grid with the same gaps (``simulate_source``
    is supplied by the caller, e.g. an Emmanoulopoulos simulation with the PSD
    fitted to the pre-forecast data). This asks: how often would a source with
    this kind of variability, but no periodicity, hit these forecasts?
"""
from __future__ import annotations

import numpy as np

from match import MatchSettings, score_source


def observed_hits(sources, rule, settings=MatchSettings()):
    """Per-source (n_evaluable, n_hits) for the real forecasts."""
    out = []
    for s in sources:
        n_eval, n_hit, _ = score_source(s["t"], s["flux"], s["detected"], s["t_preds"],
                                        s["period"], rule, settings, s.get("ref_level"))
        out.append((n_eval, n_hit))
    return np.array(out, int)


def n1_random_phase(sources, rule, n_draws, rng, settings=MatchSettings()):
    """Returns arrays of shape (n_draws, n_sources): evaluable counts and hit counts."""
    ev = np.zeros((n_draws, len(sources)), int)
    hit = np.zeros_like(ev)
    for j, s in enumerate(sources):
        T = s["period"]
        tp = np.atleast_1d(s["t_preds"]).astype(float)
        for i in range(n_draws):
            delta = rng.uniform(-T / 2, T / 2)
            ev[i, j], hit[i, j], _ = score_source(s["t"], s["flux"], s["detected"], tp + delta,
                                                  T, rule, settings, s.get("ref_level"))
    return ev, hit


def n2_red_noise(sources, rule, n_draws, rng, simulate_source, settings=MatchSettings()):
    """simulate_source(source, rng) -> simulated flux array on source['t'].

    The real detection mask is reused, so gaps and upper-limit bins stay in the
    same places as in the data.
    """
    ev = np.zeros((n_draws, len(sources)), int)
    hit = np.zeros_like(ev)
    for j, s in enumerate(sources):
        for i in range(n_draws):
            sim = simulate_source(s, rng)
            ev[i, j], hit[i, j], _ = score_source(s["t"], sim, s["detected"], s["t_preds"],
                                                  s["period"], rule, settings, s.get("ref_level"))
    return ev, hit


def p_value_upper(observed_total, null_totals):
    """One-sided p-value P(null >= observed), with the +1 correction so p is never 0
    (North, Curtis & Sham 2002, Am. J. Hum. Genet. 71, 439, doi:10.1086/341527)."""
    null_totals = np.asarray(null_totals)
    return (1 + np.sum(null_totals >= observed_total)) / (1 + null_totals.size)


def p_value_lower(observed_total, null_totals):
    null_totals = np.asarray(null_totals)
    return (1 + np.sum(null_totals <= observed_total)) / (1 + null_totals.size)


def excess_with_bootstrap(obs_hits_per_source, null_hits, n_boot, rng, ci=(2.5, 97.5)):
    """Excess hits over the null mean, with a source-level bootstrap interval.

    obs_hits_per_source : (n_sources,) observed hits
    null_hits           : (n_draws, n_sources) null hits
    Resampling whole sources (not single predictions) respects the correlation
    between predictions of the same source.
    """
    obs = np.asarray(obs_hits_per_source, float)
    per_source_excess = obs - null_hits.mean(axis=0)
    total = per_source_excess.sum()
    n = obs.size
    boots = np.array([per_source_excess[rng.integers(0, n, n)].sum() for _ in range(n_boot)])
    return total, np.percentile(boots, ci)


# ---------------------------------------------------------------------------
# Fast N1: the outcome of a source only changes when a window edge crosses a
# bin, so we evaluate it once on a 1-day grid of offsets and then sample.
# ---------------------------------------------------------------------------
def n1_grid_outcomes(source, rule, settings=MatchSettings(), step=1.0):
    """(deltas, n_eval, n_hit) for one source on a grid of common offsets in [-T/2, T/2]."""
    T = source["period"]
    tp = np.atleast_1d(source["t_preds"]).astype(float)
    deltas = np.arange(-T / 2, T / 2 + step / 2, step)
    ev = np.zeros(deltas.size, int)
    hit = np.zeros(deltas.size, int)
    for i, d in enumerate(deltas):
        ev[i], hit[i], _ = score_source(source["t"], source["flux"], source["detected"], tp + d,
                                        T, rule, settings, source.get("ref_level"))
    return deltas, ev, hit


def n1_random_phase_fast(sources, rule, n_draws, rng, settings=MatchSettings(), step=1.0):
    """Same null as n1_random_phase, sampled from the 1-day offset grid."""
    ev = np.zeros((n_draws, len(sources)), int)
    hit = np.zeros_like(ev)
    for j, s in enumerate(sources):
        deltas, gev, ghit = n1_grid_outcomes(s, rule, settings, step)
        u = rng.uniform(-s["period"] / 2, s["period"] / 2, n_draws)
        k = np.clip(np.rint((u - deltas[0]) / step).astype(int), 0, deltas.size - 1)
        ev[:, j], hit[:, j] = gev[k], ghit[k]
    return ev, hit


def score_simulations(source, sims, rule, pretest_mask, settings=MatchSettings(), k_sigma=None):
    """Score the real forecasts of one source on each simulated flux series (rows of sims).

    The real detection mask is kept. For R3 the reference level is recomputed
    from each simulation's own pre-test detected bins, as for the real data.
    Returns arrays (n_eval, n_hit) of length len(sims).
    """
    det = source["detected"]
    pre = det & pretest_mask
    ev = np.zeros(len(sims), int)
    hit = np.zeros(len(sims), int)
    for i, f in enumerate(sims):
        ref = (np.median(f[pre]), np.std(f[pre]))
        ev[i], hit[i], _ = score_source(source["t"], f, det, source["t_preds"], source["period"],
                                        rule, settings, ref)
    return ev, hit
