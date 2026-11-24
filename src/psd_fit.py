"""Fit a power spectral density (PSD) model to an evenly binned light curve.

Method: the Whittle likelihood. For an evenly sampled series the periodogram
value I(f_j) at each Fourier frequency is (approximately) the model P(f_j)
times an independent chi-squared variable with 2 degrees of freedom divided by
2. That gives  -ln L = sum_j [ ln P(f_j) + I(f_j) / P(f_j) ],  which we
minimise (Whittle 1953; Vaughan 2010, MNRAS 402, 307, Sec. 2).

Models (f in 1/day):
    PL  : P(f) = A f^(-beta) + C
    BPL : P(f) = A / (1 + (f / f_b)^beta) + C     (form of Peñil et al. 2026, Eq. 1)
C is the flat (white) noise level from measurement errors.

Gaps (undetected bins) are filled by linear interpolation for the FIT ONLY.
This slightly reddens the spectrum; it affects only the noise model used for
the secondary null N2.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize


def fill_gaps(flux, detected):
    x = np.asarray(flux, float).copy()
    det = np.asarray(detected, bool)
    i = np.arange(x.size)
    x[~det] = np.interp(i[~det], i[det], x[det])
    return x


def periodogram(x, dt):
    x = np.asarray(x, float) - np.mean(x)
    n = x.size
    f = np.fft.rfftfreq(n, dt)
    p = 2.0 * dt / n * np.abs(np.fft.rfft(x)) ** 2
    keep = slice(1, -1) if n % 2 == 0 else slice(1, None)   # drop f=0 and Nyquist
    return f[keep], p[keep]


def _pl(theta, f):
    logA, beta, logC = theta
    return 10 ** logA * f ** (-beta) + 10 ** logC


def _bpl(theta, f):
    logA, logfb, beta, logC = theta
    return 10 ** logA / (1.0 + (f / 10 ** logfb) ** beta) + 10 ** logC


def _whittle(model, bounds):
    def nll(theta, f, I):
        for v, (lo, hi) in zip(theta, bounds):
            if not lo <= v <= hi:
                return 1e30
        P = model(theta, f)
        return np.sum(np.log(P) + I / P)
    return nll


def fit_psd(flux, detected, dt=30.0, model="PL"):
    """Return dict(model, params, psd) where psd(f) is a callable PSD shape."""
    x = fill_gaps(flux, detected)
    f, I = periodogram(x, dt)
    lI = np.log10(np.mean(I))
    if model == "PL":
        bounds = [(lI - 15, lI + 15), (0.0, 4.0), (lI - 8, lI + 4)]
        # start: A f^-beta equals the mean periodogram level at the lowest frequency
        starts = [[lI + b * np.log10(f[0]), b, lI - 1] for b in (0.5, 1.0, 1.5, 2.0)]
        fun = _pl
    else:
        bounds = [(lI - 6, lI + 6), (np.log10(f[0]) - 1, np.log10(f[-1])), (0.0, 6.0), (lI - 8, lI + 4)]
        starts = [[lI + 1, lfb, b, lI - 1] for lfb in (np.log10(f[0]), np.log10(f[0]) + 0.7)
                  for b in (1.0, 2.0, 3.0)]
        fun = _bpl
    nll = _whittle(fun, bounds)
    best = None
    for s0 in starts:
        r = minimize(nll, s0, args=(f, I), method="Nelder-Mead",
                     options=dict(maxiter=4000, xatol=1e-4, fatol=1e-6))
        if best is None or r.fun < best.fun:
            best = r
    theta = best.x
    return dict(model=model, params=theta.tolist(), nll=float(best.fun),
                psd=lambda ff, th=theta: fun(th, ff))
