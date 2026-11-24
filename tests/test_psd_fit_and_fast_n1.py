import numpy as np

from match import MatchSettings, score_source
from nulls import n1_grid_outcomes, n1_random_phase_fast
from psd_fit import fit_psd
from simulate import psd_power_law, tk95


def test_pl_fit_recovers_slope():
    rng = np.random.default_rng(3)
    betas = []
    for _ in range(20):
        x = tk95(512, 30.0, lambda f: psd_power_law(f, 1.5), rng) + 10
        r = fit_psd(x, np.ones(x.size, bool), 30.0, "PL")
        betas.append(r["params"][1])
    assert abs(np.median(betas) - 1.5) < 0.3


def test_bpl_fit_runs():
    rng = np.random.default_rng(4)
    x = tk95(220, 30.0, lambda f: psd_power_law(f, 1.2), rng) + 10
    r = fit_psd(x, np.ones(x.size, bool), 30.0, "BPL")
    assert np.all(np.isfinite(r["psd"](np.array([1e-3, 1e-2]))))


def test_grid_matches_direct_scoring():
    rng = np.random.default_rng(5)
    t = 54700 + 30.0 * np.arange(220)
    flux = tk95(220, 30.0, lambda f: psd_power_law(f, 1.0), rng)
    det = rng.random(220) > 0.1
    src = dict(t=t, flux=flux, detected=det, t_preds=np.array([59500.0, 60300.0]), period=800.0)
    for rule in ("R1_interior_max", "R4_cycle_max"):
        deltas, ev, hit = n1_grid_outcomes(src, rule)
        for k in (0, 137, 400, len(deltas) - 1):
            e, h, _ = score_source(t, flux, det, src["t_preds"] + deltas[k], 800.0, rule, MatchSettings())
            assert (e, h) == (ev[k], hit[k])
        ev2, hit2 = n1_random_phase_fast([src], rule, 500, rng)
        assert ev2.shape == (500, 1)
