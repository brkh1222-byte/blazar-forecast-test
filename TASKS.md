# TASKS: blazar-forecast-test (v2)

**Priority: HIGH (weeks 1–2).** Work top to bottom. Each task has a "done when" check. Tick boxes as tasks complete. Read PROPOSAL.md (v2) and CLAUDE.md first.

> **Status check of 2026-11-25 (session 2).** Each box below was ticked only after its "done when"
> condition was checked on that date; the indented *Status* lines say what was found. Working
> mode changed (see CLAUDE.md): Claude runs the project and drafts the paper, the researcher
> edits it afterwards. Current state and next steps: `notes/STATUS.md`.

## Phase 0: Setup
- [x] **T0.1** Create `requirements.txt` (numpy, scipy, astropy, pandas, matplotlib, emcee, requests, tqdm) and `src/config.py`.
  - *Status:* both exist; versions pinned; a fresh `.venv` built from it runs all tests (27 pass).

## Phase 1: Gate check and rules (do first)
- [x] **T1.1 GATE.** Read Peñil et al. 2026 (arXiv:2606.15676) §8.1, Table A7 and Table 3. Write `notes/penil2026_rules.md` containing:
  - (a) the exact definitions of "high state" and "match window";
  - (b) whether they compared the hit rate with any chance baseline;
  - (c) all predicted-vs-observed peaks in a CSV, `data/penil_tableA7.csv`;
  - (d) their new predictions in `data/penil_table3_predictions.csv`.

  *Done when:* the notes answer (b) clearly. **If they already calibrated the hit rate, STOP Part B and flag it in the notes.**
  - *Status:* done twice. Re-done on 2026-11-25 from the arXiv LaTeX source: **no chance baseline; gate passed.** Both CSVs match the source tables exactly (script comparison).
- [ ] **T1.2** Build `data/candidates.csv` with the 46 Rico+2025 sources (4FGL, name, period). The list is in the research agent's report; check it against Rico Table 2.
  - *Status:* **not done and no longer needed.** Part B uses the 30 sources of Table A7 (`data/penil_sources.csv`, checked against Peñil et al. Table 1). Rico et al. Table 2 was never checked.
- [x] **T1.3 Pre-registration.** Write `preregistration/predictions_2026.md` listing:
  - the sources and predicted windows from Table 3;
  - the scoring rule;
  - the data cutoff for scoring;
  - the planned statistics.

  Commit it **before** looking at any light-curve data after 2026-06.
  - *Status:* written 2026-11-22; committed by the researcher on 2026-11-24 (`6d53da4`). No light-curve bin after MJD 60998 (2025-11) is in the cache, so the condition holds for Part C. **Caveat:** for Part B the plan and the results are in the same public commit; see amendment 2 (drafted, waiting for the researcher to commit).

## Phase 2: Data and reproduction
- [x] **T2.1** Write `src/download_lcr.py` to fetch monthly Light Curve Repository light curves for all 49 sources in Peñil et al. Cache under `data/lcr/`.
  - *Status:* done for the **30** sources that have forecasts (the other 19 are not used). The code is `src/lcr.py` + `scripts/download_partB.py`, not `src/download_lcr.py`.
- [ ] **T2.2** Write `src/match.py` to implement the Peñil matching rule exactly.
  *Done when:* it reproduces about 19/59 hits; differences are explained in `results/reproduction.md`.
  - *Status:* **"done when" not met.** `src/match.py` exists, but the rule as printed cannot produce a miss, and none of four candidate rules reproduces the verdicts (best κ = 0.34; hits 27–47 of 56 instead of 19 of 59). Differences are explained in `results/reproduction.md`. Closing this needs the authors' rule (email drafted, not sent).

## Phase 3: Null calibration (main result)
- [x] **T3.1** Write `src/psd_fit.py` to fit power-law and bending power-law PSDs to each source's pre-forecast data.
  - *Status:* done (`results/psd_fits.csv`). No power-law fit is on a bound; some bending-power-law fits are (see `notes/STATUS.md`).
- [x] **T3.2** Write `src/simulate.py`: Emmanoulopoulos et al. 2013 light curves, ≥1,000 (target 10,000) per source, matching the PSD and flux PDF. Resample to the real cadence and gaps, and apply the same upper-limit rule.
  - *Status:* done with 1,000 per source and per PSD model (not 10,000).
- [x] **T3.3** Red-noise null: forecast→match on the simulations, giving a hit-count distribution.
  - *Status:* done as pre-registered (N2: the real forecasts scored on simulations). It does not re-forecast from each simulation; an exploratory check of that (`scripts/review_partB.py`, part D) finds a 0–3 point effect.
- [x] **T3.4** Randomised-forecast null: phase-shift and period-scramble the forecasts against the real light curves.
  - *Status:* phase shift done (N1). Period scrambling was replaced in the pre-registration by the negative control (forecasts scored on another source's light curve).
- [x] **T3.5** Compute p-values for 19/59 under both nulls, plus sensitivity to window width (±0.1/0.2/0.3 period).
  *Done when:* `results/null_calibration.json` and `results/fig_hitrate_null.png` exist.
  - *Status:* both files exist (created 2026-11-25 by `scripts/make_null_calibration.py` and `scripts/make_figure.py`; the numbers date from the 2026-11-22 run and were reproduced byte-for-byte on 2026-11-25).

## Phase 4: Paper
- [x] **T4.1** Write `paper/notes.md` with bullet results and numbers. Claude drafts the paper text; the researcher edits it afterwards (policy of 2026-11-25; authorship and the AI-use statement are placeholders).
  - *Status:* done, with the source file of every number in the draft.
- [x] **T4.2** Set up the RNAAS LaTeX template in `paper/`.
  - *Status:* `paper/paper.tex` uses AASTeX 6.31. It is now a full-length draft (about 3,000 words), longer than RNAAS allows; **never compiled** (no LaTeX on this machine).

## Phase 5: Part C (2027)
- [ ] **T5.1** Write `src/score_preregistered.py`, run only after the data cutoff in the pre-registration.
  - *Status:* **written and tested on simulated data** (`results/partC_dryrun.json`, `tests/test_partc.py`); **not run on real data.** First scoring date 2027-01-28; last 2030-01-15. Tick when the first real scoring has been run.
