"""The simulators must reproduce the target PSD slope and (for EMP) the flux distribution."""
import numpy as np

from simulate import bootstrap_sampler, emmanoulopoulos, lognormal_sampler, psd_power_law, tk95

DT, N = 30.0, 512


def _mean_slope(gen, n_real=200):
    f = np.fft.rfftfreq(N, DT)[1:]
    P = np.zeros(f.size)
    for _ in range(n_real):
        x = gen()
        P += np.abs(np.fft.rfft(x - x.mean()))[1:] ** 2
    band = (f > 2 / (N * DT)) & (f < 0.25 / DT)     # avoid the lowest and highest bins
    return np.polyfit(np.log10(f[band]), np.log10(P[band]), 1)[0]


def test_tk95_recovers_slope():
    rng = np.random.default_rng(1)
    for beta in (1.0, 1.5, 2.0):
        slope = _mean_slope(lambda: tk95(N, DT, lambda f: psd_power_law(f, beta), rng))
        assert abs(slope + beta) < 0.25, (beta, slope)


def test_emmanoulopoulos_keeps_flux_values_and_slope():
    rng = np.random.default_rng(2)
    sampler = lognormal_sampler(0.0, 0.8)
    x = emmanoulopoulos(N, DT, lambda f: psd_power_law(f, 1.5), sampler, rng)
    assert np.all(x > 0)                            # lognormal fluxes stay positive
    slope = _mean_slope(lambda: emmanoulopoulos(N, DT, lambda f: psd_power_law(f, 1.5), sampler, rng),
                        n_real=60)
    assert abs(slope + 1.5) < 0.4, slope


def test_bootstrap_sampler_only_returns_observed_values():
    rng = np.random.default_rng(3)
    obs = np.array([1.0, 2.0, 5.0])
    draws = bootstrap_sampler(obs)(100, rng)
    assert set(np.unique(draws)) <= set(obs)
