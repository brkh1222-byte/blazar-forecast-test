"""Red-noise light-curve simulation.

Two generators:

* ``tk95`` (Timmer & König 1995, A&A 300, 707): draws random Fourier
  amplitudes whose expected power follows a chosen power spectral density
  (PSD), with random phases. The result is Gaussian, so it cannot reproduce the
  skewed (roughly lognormal) flux distribution of gamma-ray blazars.

* ``emmanoulopoulos`` (Emmanoulopoulos, McHardy & Papadakis 2013, MNRAS 433,
  907): starts from a sample of fluxes with the right distribution and
  iteratively reshapes it so that its Fourier amplitudes match a TK95
  realisation, while keeping exactly the right flux values. The output has
  (approximately) the target PSD AND exactly the target flux distribution.

Both generators simulate a series ``oversample`` times longer than needed and
cut out a piece. This keeps "red-noise leakage" (power from periods longer than
the observation) in the simulation, as in real data.

PSD models (frequency f in 1/day):
    power law:          P(f) = A f^(-beta)
    bending power law:  P(f) = A f^(-alpha_lo) / (1 + (f/f_b)^(alpha_hi - alpha_lo))
Only the PSD SHAPE matters here: amplitudes are rescaled by the flux sampling.
"""
from __future__ import annotations

import numpy as np


def psd_power_law(f, beta):
    return f ** (-beta)


def psd_bending(f, alpha_lo, alpha_hi, f_bend):
    return f ** (-alpha_lo) / (1.0 + (f / f_bend) ** (alpha_hi - alpha_lo))


def tk95(n, dt, psd, rng, oversample=10):
    """Gaussian red-noise series of length n with sampling dt (days).

    psd : callable P(f) giving the PSD shape.
    Returns zero-mean, unit-variance values.
    """
    N = n * oversample
    f = np.fft.rfftfreq(N, dt)[1:]                    # skip f = 0 (the mean)
    amp = np.sqrt(0.5 * psd(f))
    re, im = rng.normal(size=f.size), rng.normal(size=f.size)
    if N % 2 == 0:
        im[-1] = 0.0                                  # Nyquist term must be real
    spec = np.concatenate([[0.0], amp * (re + 1j * im)])
    x = np.fft.irfft(spec, N)
    start = rng.integers(0, N - n + 1)                # random cut keeps leakage
    x = x[start:start + n]
    return (x - x.mean()) / x.std()


def emmanoulopoulos(n, dt, psd, flux_sampler, rng, oversample=10, max_iter=200, tol=1e-8):
    """Red-noise series with the given PSD shape and flux distribution.

    flux_sampler : callable (size, rng) -> array of fluxes drawn from the target
        distribution (for example a bootstrap of the observed detected fluxes,
        or a fitted lognormal).

    Algorithm (Emmanoulopoulos et al. 2013, Section 2.2):
      1. x_norm = TK95 series with the target PSD; keep its Fourier amplitudes A.
      2. x_sim  = n_long draws from the target flux distribution (white noise).
      3. Repeat: take the phases of x_sim, combine them with the amplitudes A,
         inverse-transform to x_adj; then replace x_sim by the target flux
         values sorted into the rank order of x_adj ("amplitude adjustment").
         Stop when x_sim no longer changes.
    """
    N = n * oversample
    x_norm = tk95(N, dt, psd, rng, oversample=1)
    A = np.abs(np.fft.rfft(x_norm))
    values = np.sort(flux_sampler(N, rng))           # target fluxes, sorted
    x_sim = rng.permutation(values)
    for _ in range(max_iter):
        phase = np.angle(np.fft.rfft(x_sim))
        x_adj = np.fft.irfft(A * np.exp(1j * phase), N)
        ranks = np.argsort(np.argsort(x_adj))
        x_new = values[ranks]
        if np.allclose(x_new, x_sim, atol=tol, rtol=0):
            break
        x_sim = x_new
    start = rng.integers(0, N - n + 1)
    return x_sim[start:start + n]


def bootstrap_sampler(observed_flux):
    """Flux sampler that redraws (with replacement) from observed detected fluxes."""
    obs = np.asarray(observed_flux, float)
    return lambda size, rng: rng.choice(obs, size=size, replace=True)


def lognormal_sampler(mu, sigma):
    return lambda size, rng: rng.lognormal(mu, sigma, size=size)
