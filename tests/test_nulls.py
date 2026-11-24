"""The N1 null must flag real periodic forecasts and not flag random ones."""
import numpy as np

from nulls import n1_random_phase, observed_hits, p_value_upper
from simulate import psd_power_law, tk95

DT = 30.0
T = 2.5 * 365.25
t = np.arange(0, 17 * 365.25, DT)
det = np.ones_like(t, bool)
test_preds = 12 * 365.25 + T * np.arange(2)        # two forecasts in the "new data"


def _sources(periodic, rng, n_src=20):
    out = []
    for _ in range(n_src):
        noise = tk95(t.size, DT, lambda f: psd_power_law(f, 1.5), rng)
        phase0 = rng.uniform(0, T)
        signal = 1.5 * np.cos(2 * np.pi * (t - phase0) / T) if periodic else 0.0
        # forecasts placed on the signal's true peaks after day 12*365.25
        k0 = np.ceil((12 * 365.25 - phase0) / T)
        preds = phase0 + T * (k0 + np.arange(2))
        out.append(dict(t=t, flux=noise + signal, detected=det, t_preds=preds, period=T))
    return out


def test_n1_detects_real_periodicity():
    rng = np.random.default_rng(4)
    src = _sources(True, rng)
    obs = observed_hits(src, "R4_cycle_max")[:, 1].sum()
    _, hits = n1_random_phase(src, "R4_cycle_max", 500, rng)
    assert p_value_upper(obs, hits.sum(axis=1)) < 0.01


def test_n1_does_not_flag_pure_red_noise_on_average():
    rng = np.random.default_rng(5)
    ps = []
    for _ in range(20):
        src = _sources(False, rng, n_src=10)
        obs = observed_hits(src, "R4_cycle_max")[:, 1].sum()
        _, hits = n1_random_phase(src, "R4_cycle_max", 200, rng)
        ps.append(p_value_upper(obs, hits.sum(axis=1)))
    ps = np.array(ps)
    # with no signal, p-values should be spread out, not piled up near 0
    assert np.mean(ps < 0.05) <= 0.2
    assert 0.3 < np.median(ps) < 0.75
