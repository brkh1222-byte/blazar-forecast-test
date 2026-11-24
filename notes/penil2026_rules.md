# T1.1 gate notes: Peñil et al. 2026, Section 8

Paper: Peñil, Rico, Domínguez, Ajello, Buson & Adhikari 2026, MNRAS 550, stag1141
(arXiv:2606.15676 v1). Read in the arXiv v1 PDF on 2026-11-22.

## (a) Definitions, quoted from Section 8.1

- "Each prediction is evaluated within a symmetric window [t_pred − W, t_pred + W] with W = 0.20T."
- "A prediction is considered evaluable only if the window contains at least N_min = 2 measurements."
- "we define the observed cycle-associated peak as the maximum flux within the window, occurring at t_obs."
- "We classify the prediction as compatible with the new data if the peak timing satisfies
  |t_obs − t_pred| ≤ Δt_tol, with Δt_tol = max(60 d, 0.20T)"
- The forecasts tested are those of Rico et al. (2025) and Peñil et al. (2025c, MNRAS 543, 2880),
  "using the newly available ∼6 yr of monitoring beyond the original ∼12 yr dataset".
- Light curves (Section 2): LCR 30-day bins, keeping bins with ≥ 2σ detection.

**Problem:** t_obs is inside the window, so |t_obs − t_pred| ≤ 0.20T ≤ Δt_tol always.
As printed, the rule cannot produce a miss, yet 40/59 are marked ✗. `tests/test_match.py`
demonstrates this. The real rule must be reconstructed (Q0) or obtained from the authors.

## (b) Chance baseline?

**None.** There is no simulated, shuffled or binomial baseline for the forecast hit rate
anywhere in the paper. Simulations (Emmanoulopoulos-type, 150,000 per source; Timmer & König
trials calibration) are used only for periodogram significance. Section 9 uses forecast
consistency as supporting evidence for the final candidate list.
**Gate passed: Part B goes ahead.**

## (c) and (d)

- Table A7 → `data/penil_tableA7.csv` (59 forecasts, 19 ✓, 30 sources; 7 full / 15 none / 8 mixed).
- Table 3 → `data/penil_table3_predictions.csv`.
- Note: the text says the new forecasts "are reported in Table A7", but they are in Table 3.
  The Table 3 caption says "≥3σ" but lists six sources at 2.0–2.5σ.
