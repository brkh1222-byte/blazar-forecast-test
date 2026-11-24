"""Exploratory (NOT pre-registered): rule X1 = R3 AND R4, chosen after seeing Q0.
See preregistration/2026-11-22_amendment_1.md. Writes results/exploratory_X1.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np

from match import MatchSettings, score_source
from nulls import n1_random_phase_fast, p_value_upper, score_simulations
from partb_data import GRID, PRETEST, cohen_kappa, load_sources
from psd_fit import fit_psd
from simulate import bootstrap_sampler, emmanoulopoulos

RULE, SEED = "X1_high_and_cycle", 20261123
sources, a7 = load_sources()
rng = np.random.default_rng(SEED)
verd, ev_obs, hit_obs = [], [], []
for s in sources:
    for tp in s["t_preds"]:
        e, h, _ = score_source(s["t"], s["flux"], s["detected"], [tp], s["period"], RULE,
                               MatchSettings(), s["ref_level"])
        verd.append(h)
truth = [int(a7.loc[(a7.source == s["name"]) & (a7.t_pred == tp), "supported"].iloc[0])
         for s in sources for tp in s["t_preds"]]
obs = np.array([score_source(s["t"], s["flux"], s["detected"], s["t_preds"], s["period"], RULE,
                             MatchSettings(), s["ref_level"])[:2] for s in sources])
H_obs = obs[:, 1].sum() / obs[:, 0].sum()
ev, hit = n1_random_phase_fast(sources, RULE, 10_000, rng)
H1 = hit.sum(1) / np.maximum(ev.sum(1), 1)
res = dict(rule=RULE, kappa=cohen_kappa(verd, truth), hits=int(obs[:, 1].sum()),
           evaluable=int(obs[:, 0].sum()), H_obs=H_obs, N1_mean=float(H1.mean()),
           N1_sd=float(H1.std()), p_N1=p_value_upper(H_obs, H1),
           p_N1_authors=p_value_upper(19 / 59, H1))
for model in ("PL", "BPL"):
    evs, hits = [], []
    for s in sources:
        pre = s["detected"] & PRETEST
        fit = fit_psd(s["flux"][PRETEST], s["detected"][PRETEST], 30.0, model)
        sims = np.array([emmanoulopoulos(GRID.size, 30.0, fit["psd"], bootstrap_sampler(s["flux"][pre]), rng)
                         for _ in range(1000)])
        e, h = score_simulations(s, sims, RULE, PRETEST)
        evs.append(e); hits.append(h)
    H2 = np.sum(hits, 0) / np.maximum(np.sum(evs, 0), 1)
    res[f"N2{model}_mean"] = float(H2.mean())
    res[f"p_N2{model}"] = p_value_upper(H_obs, H2)
    res[f"p_N2{model}_authors"] = p_value_upper(19 / 59, H2)
np.savez_compressed(ROOT / "results/null_draws_X1.npz", N1=H1)
(ROOT / "results/exploratory_X1.json").write_text(json.dumps(res, indent=2))
print(json.dumps(res, indent=2))
