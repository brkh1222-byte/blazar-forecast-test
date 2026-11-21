# TASKS: blazar-forecast-test

**Priority: HIGH (weeks 1–2).** Work top to bottom. Each task has a "done when" check. Tick boxes in this file as tasks complete. Read PROPOSAL.md and CLAUDE.md first.

## Phase 0: Setup
- [ ] **T0.1** Create `requirements.txt` (numpy, scipy, astropy, pandas, matplotlib, emcee, requests, tqdm) and a `src/config.py` with paths.
  *Done when:* `pip install -r requirements.txt` works on a clean venv.

## Phase 1: Data
- [ ] **T1.1** Build the candidate list in `data/candidates.csv`: the 46 sources from Rico et al. 2025 (arXiv:2412.05812), with 4FGL name, common name, class (BLL/FSRQ), redshift, period ± error, and a flag for whether a forecast was published (28).
  *Done when:* 46 rows; periods match the paper's table.
- [ ] **T1.2** Write `src/download_lcr.py` to fetch **monthly** light curves from the Fermi LAT Light Curve Repository API for every candidate. Cache them as CSV under `data/lcr/`. Keep TS, flux, flux error and upper-limit flags.
  *Done when:* light curves exist for all candidates that are in the LCR (log any that are missing), covering Aug 2008 → latest.
- [ ] **T1.3** Write `notebooks/01_inspect.ipynb` to plot every light curve, with a vertical line at 2020-12-10 (the end of Rico's data).

## Phase 2: Reproduce (positive control)
- [ ] **T2.1** Write `src/periodogram.py` to compute a Lomb–Scargle periodogram on pre-2021 data, with a choice of upper-limit handling (drop / set to UL / censored).
  *Done when:* PG 1553+113 gives P ≈ 2.2 yr.
- [ ] **T2.2** Reproduce the periods for all 46 candidates. Table: ours vs Rico's.
  *Done when:* `results/period_reproduction.csv` is written; discrepancies above 10% are listed and explained.

## Phase 3: Forecasts
- [ ] **T3.1** Make our own forecasts in `src/forecast.py`: fit sinusoid plus mean (emcee) to 2008–2020 data and predict peak times for 2021–2026 with 68%/95% windows.
- [ ] **T3.2** Digitise Rico Appendix C forecasts into `data/rico_forecasts.csv` if author tables are not available. Record the digitisation uncertainty.
  *Human task:* the student emails the authors for the tables.

## Phase 4: Test
- [ ] **T4.1** Write `src/measure_peaks.py` to locate observed 2021–2026 peaks (Bayesian blocks or Gaussian fits) with uncertainties.
- [ ] **T4.2** Compute the hit/miss table of observed peaks vs forecast windows for each source.
  *Done when:* `results/forecast_test.csv` is written.
- [ ] **T4.3** Persistence test: Lomb–Scargle on post-2021 data only; compare with the pre-2021 period.

## Phase 5: Red-noise calibration (critical)
- [ ] **T5.1** Write `src/simulate.py`: fit a power-law PSD to each pre-2021 light curve, then use Emmanoulopoulos et al. 2013 simulations that match the PSD and flux PDF. Sample with the real cadence and gaps.
- [ ] **T5.2** Run the full forecast→test pipeline on at least 1,000 simulations per source to get the chance hit rate.
- [ ] **T5.3** Population test: observed hit count vs the red-noise distribution (binomial / permutation p-value).
  *Done when:* `results/population_test.json` is written and a figure is in `results/`.

## Phase 6: Paper
- [ ] **T6.1** Make the figures: (a) PG 1553+113 forecast vs observed; (b) hit rate vs red-noise distribution.
- [ ] **T6.2** Write a results summary in `paper/notes.md` (bullet facts with numbers). **The student writes the paper text personally**, because arXiv bans AI-written submissions.
- [ ] **T6.3** RNAAS LaTeX template in `paper/`.
