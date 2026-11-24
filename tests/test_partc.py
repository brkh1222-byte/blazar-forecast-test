"""Part C scoring code: windows, the Poisson-binomial test, and the blinding guard.
No test here touches the network or real light curves."""
import itertools

import numpy as np
import pandas as pd
import pytest

import score_preregistered as sp


def test_thirteen_forecasts_and_five_primary():
    fc = sp.build_forecasts()
    assert len(fc) == 13 and fc.id.is_unique
    assert set(fc[fc.primary].id) == {
        "S4 1144+40 | ssa_r", "PG 1553+113 | phase_folding", "OJ 014 | ssa_r",
        "TXS 0518+211 | ssa_r", "PKS 0215+015 | phase_folding"}
    assert (fc.method == "phase_folding").sum() == 8


@pytest.mark.parametrize("fid,lo,hi", [
    # window dates printed in preregistration/predictions_2026.md Sec. 5 (within one day: rounding)
    ("S5 1044+71 | ssa_r", "2025-08-01", "2026-10-27"),
    ("S3 0458-02 | phase_folding", "2025-12-27", "2027-08-03"),
    ("PG 1553+113 | phase_folding", "2027-01-13", "2027-11-15"),
    ("PKS 0215+015 | phase_folding", "2028-06-19", "2029-10-14"),
])
def test_windows_match_preregistration(fid, lo, hi):
    f = sp.build_forecasts().set_index("id").loc[fid]
    assert abs((pd.Timestamp(f.win_lo_date) - pd.Timestamp(lo)).days) <= 1
    assert abs((pd.Timestamp(f.win_hi_date) - pd.Timestamp(hi)).days) <= 1
    assert pd.Timestamp(f.score_date) >= pd.Timestamp(hi) + pd.DateOffset(months=3)


def test_poisson_binomial_against_brute_force():
    p = [0.1, 0.45, 0.7, 0.3]
    for k in range(6):
        brute = sum(np.prod([pi if b else 1 - pi for pi, b in zip(p, bits)])
                    for bits in itertools.product([0, 1], repeat=4) if sum(bits) >= k)
        assert sp.poisson_binomial_sf(p, k) == pytest.approx(brute)
    assert sp.poisson_binomial_sf(p, 0) == pytest.approx(1.0)


def test_score_refuses_forecasts_that_are_not_due(monkeypatch, tmp_path, capsys):
    """Before the first scoring date nothing may be fetched."""
    import lcr

    def boom(*a, **k):
        raise AssertionError("fetch must not be called before the scoring date")

    monkeypatch.setattr(lcr, "fetch", boom)
    monkeypatch.setattr(sp, "ROOT", tmp_path)
    (tmp_path / "results").mkdir()
    monkeypatch.setattr(sp, "build_forecasts", lambda: _fc)
    sp.run_score(today="2027-01-27")            # one day before the earliest scoring date
    assert "not due" in capsys.readouterr().out
    assert not (tmp_path / "results/partC_scores.csv").exists()


_fc = sp.build_forecasts()


def test_dry_run_detects_strong_signal_and_not_noise(tmp_path):
    out = sp.run_dry(n_rep=12, n_draws=200, amplitudes=(0.0, 2.0), out=tmp_path / "dry.json")
    fs = out["frac_significant"]
    assert fs["2.0"]["all_13"]["R4_cycle_max"]["frac_p_below_0p05"] >= 0.75
    assert fs["0.0"]["all_13"]["R4_cycle_max"]["frac_p_below_0p05"] <= 0.34
