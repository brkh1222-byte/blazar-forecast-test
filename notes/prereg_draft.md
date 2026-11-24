# DRAFT pre-registration — not yet committed

> **Read this before committing.** This is a draft for Berkh to check, edit and own.
> When it is final, copy it to `preregistration/predictions_2026.md`, fill every
> `[STUDENT: …]` item, and commit it **before** downloading any Light Curve Repository
> data. After that commit, the file is never edited; changes go in new dated
> amendment files (CLAUDE.md rule).

**Title:** Null calibration of the Peñil et al. (2026) forecast hit rate, and a
blind test of their Table 3 forecasts
**Author:** Berkh (independent student researcher); mentor [STUDENT: name, if co-registering]
**Date of commit:** [STUDENT: filled automatically by the git commit timestamp]
**Analysis code:** `src/match.py`, `src/simulate.py`, `src/nulls.py` at commit [STUDENT: hash of the commit that adds this file]

## 1. Data already seen (honesty statement)

[STUDENT: State exactly what Fermi LAT Light Curve Repository (LCR) data you have
looked at so far. PROPOSAL.md §5 says the LCR was "verified to run to a bin starting
2026-10-15" for J1048.4+7143, J0521.7+2112, J0501.2−0158 and J1649.4+5235. Did that
check show flux values or plots, or only bin dates? Write it down plainly.]

No flux after 2026-06-14 (the arXiv date of Peñil et al. 2026) will be looked at for the
Part C sources until each forecast's scoring date in §6.

## 2. Hypotheses

- **Q0 (rule).** Among the candidate rules R1–R4 in `src/match.py`, one reproduces the 59
  Table A7 verdicts with Cohen's κ ≥ 0.7.
- **Q1 (main).** H0: the number of supported forecasts is consistent with the null.
  H1: it exceeds the null. One-sided, α = 0.05.
- **Q3 (Part C).** H0: Table 3 forecasts hit no more often than their chance probabilities.
  H1: they hit more often. One-sided, α = 0.05.

## 3. Rule used for scoring (decided in this order)

1. If the authors state their operational rule before the Part B analysis is run, implement
   it exactly; it is primary.
2. Otherwise the primary rule is the candidate with the highest κ against Table A7, if
   κ ≥ 0.7 (ties: the rule listed first in `RULES`).
3. If no candidate reaches κ ≥ 0.7, there is no primary rule: results are reported for
   all of R1–R4, and no single p-value is claimed.

Rule R0 (as printed) is reported only to document that it cannot produce a miss.

Settings: W = 0.20T, tolerance max(60 d, 0.20T), N_min = 2 detected bins, R3 threshold
median + 1σ of the pre-test light curve, R4 search ±0.5T.

## 4. Part B design

- **Sample:** the 30 sources and 59 forecasts of Peñil et al. Table A7 (`data/penil_tableA7.csv`).
  Predicted month → day 15 of that month.
- **Periods:** from Rico et al. (2025) and Peñil et al. (2025c). [STUDENT: confirm the source
  table for each period before the analysis.]
- **Light curves:** LCR, 30-day bins, photon flux, fixed index; a bin is "detected" if
  TS ≥ 4. Data end: the end date of Peñil et al. if the authors give it; otherwise
  [STUDENT/MENTOR: decide and write the default date here].
- **Primary null:** N1, randomised forecasts. Each source's forecasts are shifted by one common
  offset δ ~ U(−T/2, T/2). 10,000 draws.
- **Secondary null:** N2, Emmanoulopoulos et al. (2013) light curves. PSD = power law and bending
  power law, each fitted to data before the test interval. Flux distribution = bootstrap of
  the detected pre-test fluxes. The real gaps are kept. 1,000 draws per source.
- **Statistic:** total hits over all evaluable forecasts. p = (1 + #{null ≥ observed}) / (1 + N).
- **Effect size:** observed hits minus null mean, with a 95% source-level bootstrap interval
  (10,000 resamples).
- **Primary cell:** primary rule (§3), N1, W = 0.20T.
- **Robustness (reported, never re-chosen):** W ∈ {0.10, 0.20, 0.30}T; PL vs BPL (N2);
  N_min ∈ {2, 3}; all rules R1–R4.
- **Power check:** inject sinusoids into N2 light curves at amplitudes of 0.25, 0.5, 1 and 2 × the
  light-curve standard deviation, and report the detection rate at α = 0.05.

## 5. Part C forecasts (Peñil et al. 2026, Table 3)

Window = predicted month (day 15) ± 0.20T. Primary test = the 5 windows that open after
this commit. Secondary = all 13.

| Source | Method | Predicted | Window | Opens after commit? |
|---|---|---|---|---|
| S5 1044+71 | SSA-R | 2026-03 | 2025-08-01 – 2026-10-27 | no |
| TXS 0518+211 | phase folding | 2026-03 | 2025-08-01 – 2026-10-27 | no |
| S5 1044+71 | phase folding | 2026-04 | 2025-09-01 – 2026-11-27 | no |
| S3 0458−02 | phase folding | 2026-10 | 2025-12-27 – 2027-08-03 | no |
| 87GB 164812.2+524023 | phase folding | 2026-10 | 2026-02-23 – 2027-06-06 | no |
| S4 1144+40 | phase folding | 2027-05 | 2026-10-01 – 2027-12-27 | no |
| PG 1553+113 | SSA-R | 2027-03 | 2026-10-13 – 2027-08-15 | no |
| OJ 014 | phase folding | 2027-09 | 2026-11-12 – 2028-07-18 | no |
| S4 1144+40 | SSA-R | 2027-08 | 2027-01-01 – 2028-03-28 | **yes** |
| PG 1553+113 | phase folding | 2027-06 | 2027-01-13 – 2027-11-15 | **yes** |
| OJ 014 | SSA-R | 2028-05 | 2027-07-13 – 2029-03-18 | **yes** |
| TXS 0518+211 | SSA-R | 2028-08 | 2028-01-02 – 2029-03-29 | **yes** |
| PKS 0215+015 | phase folding | 2029-02 | 2028-06-19 – 2029-10-14 | **yes** |

[STUDENT: if the commit happens after 2026-12-31, re-check the last column.]

## 6. Part C scoring

- Each forecast is scored once, when LCR data reach 3 months past its window end.
- Same rule as Part B (§3).
- p_i (the chance probability of each forecast) is computed at scoring time with N1 on that
  source's own light curve, using 10,000 draws.
- Test: total hits against the Poisson-binomial distribution of the p_i, one-sided α = 0.05.
  This is done separately for the primary set (5) and the full set (13).
- Two windows from the same source (phase folding and SSA-R) are not independent. The full-set
  test therefore also reports a version that keeps one forecast per source (phase folding).

## 7. What would change these plans

Only the authors' clarification of their rule (§3, step 1), or a data problem. Any change will
be recorded in a new dated file in `preregistration/`, giving the reason.
