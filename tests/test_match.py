"""Checks of the matching rules on synthetic light curves where the answer is known."""
import numpy as np
import pytest

from match import RULES, score_prediction
from simulate import psd_power_law, tk95

DT = 30.0
T = 3.0 * 365.25          # 3-yr period
t = np.arange(0, 17 * 365.25, DT)
det = np.ones_like(t, bool)


def test_R0_as_printed_can_never_miss():
    """The rule exactly as printed in Peñil et al. (2026) Sec. 8.1 always matches."""
    rng = np.random.default_rng(0)
    n_eval = 0
    for _ in range(500):
        flux = tk95(t.size, DT, lambda f: psd_power_law(f, 1.5), rng)
        tp = rng.uniform(0.3 * T, t[-1] - 0.3 * T)
        r = score_prediction(t, flux, det, tp, T, "R0_as_printed")
        n_eval += r.evaluable
        assert r.hit or not r.evaluable
    assert n_eval == 500


@pytest.mark.parametrize("rule", RULES)
def test_peak_on_prediction_is_a_hit(rule):
    flux = 1.0 + np.cos(2 * np.pi * (t - 5 * 365.25) / T)   # peak at day 5*365.25
    assert score_prediction(t, flux, det, 5 * 365.25, T, rule).hit


@pytest.mark.parametrize("rule", ["R1_interior_max", "R2_local_max", "R4_cycle_max"])
def test_trough_on_prediction_is_a_miss(rule):
    flux = 1.0 + np.cos(2 * np.pi * (t - 5 * 365.25) / T)
    trough = 5 * 365.25 + T / 2
    assert not score_prediction(t, flux, det, trough, T, rule).hit


def test_gap_makes_prediction_not_evaluable():
    flux = np.ones_like(t)
    gap = det.copy()
    tp = 8 * 365.25
    gap[np.abs(t - tp) <= 0.2 * T] = False
    gap[np.argmin(np.abs(t - tp))] = True                     # only one detection left
    assert not score_prediction(t, flux, gap, tp, T).evaluable


def test_R3_uses_external_reference_level():
    flux = 1.0 + np.cos(2 * np.pi * (t - 5 * 365.25) / T)
    # a threshold above the peak means no high state
    assert not score_prediction(t, flux, det, 5 * 365.25, T, "R3_high_state", ref_level=(2.5, 0.1)).hit
