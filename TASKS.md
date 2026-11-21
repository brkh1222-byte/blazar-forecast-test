# TASKS: blazar-forecast-test (v2)

**Priority: HIGH (weeks 1–2).** Work top to bottom. Each task has a "done when" check. Tick boxes as tasks complete. Read PROPOSAL.md (v2) and CLAUDE.md first.

## Phase 0: Setup
- [ ] **T0.1** Create `requirements.txt` (numpy, scipy, astropy, pandas, matplotlib, emcee, requests, tqdm) and `src/config.py`.

## Phase 1: Gate check and rules (do first)
- [ ] **T1.1 GATE.** Read Peñil et al. 2026 (arXiv:2606.15676) §8.1, Table A7 and Table 3. Write `notes/penil2026_rules.md` containing:
  - (a) the exact definitions of "high state" and "match window";
  - (b) whether they compared the hit rate with any chance baseline;
  - (c) all predicted-vs-observed peaks in a CSV, `data/penil_tableA7.csv`;
  - (d) their new predictions in `data/penil_table3_predictions.csv`.

  *Done when:* the notes answer (b) clearly. **If they already calibrated the hit rate, STOP Part B and flag it in the notes.**
- [ ] **T1.2** Build `data/candidates.csv` with the 46 Rico+2025 sources (4FGL, name, period). The list is in the research agent's report; check it against Rico Table 2.
- [ ] **T1.3 Pre-registration.** Write `preregistration/predictions_2026.md` listing:
  - the sources and predicted windows from Table 3;
  - the scoring rule;
  - the data cutoff for scoring;
  - the planned statistics.

  Commit it **before** looking at any light-curve data after 2026-06.

## Phase 2: Data and reproduction
- [ ] **T2.1** Write `src/download_lcr.py` to fetch monthly Light Curve Repository light curves for all 49 sources in Peñil et al. Cache under `data/lcr/`.
- [ ] **T2.2** Write `src/match.py` to implement the Peñil matching rule exactly.
  *Done when:* it reproduces about 19/59 hits; differences are explained in `results/reproduction.md`.

## Phase 3: Null calibration (main result)
- [ ] **T3.1** Write `src/psd_fit.py` to fit power-law and bending power-law PSDs to each source's pre-forecast data.
- [ ] **T3.2** Write `src/simulate.py`: Emmanoulopoulos et al. 2013 light curves, ≥1,000 (target 10,000) per source, matching the PSD and flux PDF. Resample to the real cadence and gaps, and apply the same upper-limit rule.
- [ ] **T3.3** Red-noise null: forecast→match on the simulations, giving a hit-count distribution.
- [ ] **T3.4** Randomised-forecast null: phase-shift and period-scramble the forecasts against the real light curves.
- [ ] **T3.5** Compute p-values for 19/59 under both nulls, plus sensitivity to window width (±0.1/0.2/0.3 period).
  *Done when:* `results/null_calibration.json` and `results/fig_hitrate_null.png` exist.

## Phase 4: Paper
- [ ] **T4.1** Write `paper/notes.md` with bullet results and numbers. **The student writes the paper text personally.**
- [ ] **T4.2** Set up the RNAAS LaTeX template in `paper/`.

## Phase 5: Part C (2027)
- [ ] **T5.1** Write `src/score_preregistered.py`, run only after the data cutoff in the pre-registration.
