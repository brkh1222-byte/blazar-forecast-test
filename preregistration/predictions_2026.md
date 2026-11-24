# Pre-registration: null calibration of the Peñil et al. (2026) forecast hit rate, and a blind test of their Table 3 forecasts

**Author:** Berkh (independent student researcher). AI assistance: Claude (Anthropic) wrote the analysis code and this document at the author's direction; the author is responsible for it.
**Date:** the git commit timestamp of the commit that adds this file (2026-11-22).
**Analysis code:** `src/match.py`, `src/simulate.py`, `src/nulls.py`, `src/config.py`, `src/lcr.py` as they stand in the commit that adds this file.
**Rule:** this file is never edited after it is committed. Changes go in new dated files in `preregistration/`, giving the reason.

## 1. Data already seen (honesty statement)

- Peñil et al. (2026, arXiv:2606.15676) has been read in full, including Table A7, the per-forecast verdicts (19 of 59 supported) and Figure A1, which shows their light curves.
- PROPOSAL.md §5 records that the LCR was checked to run to a bin starting 2026-10-15 for J1048.4+7143, J0521.7+2112, J0501.2−0158 and J1649.4+5235. That check was about bin dates; the record does not say whether flux values were shown.
- Before this commit the analysis code has fetched one LCR light curve (GB6 J0043+3426, not a Part C source) only to read the response format (key names and lengths, plus the first flux value). No flux after 2026-06-14 has been inspected by the code or the AI assistant.
- Part B is retrospective: the Table A7 verdicts are already public. What this file fixes in advance is every analysis choice (rule selection, nulls, statistic, robustness grid) before our own LCR light curves are downloaded and scored.

## 2. Questions and hypotheses

- **Q0 (rule).** Among R1–R4 in `src/match.py`, one reproduces the 59 Table A7 verdicts with Cohen's κ ≥ 0.7.
- **Q1 (main).** H0: the pooled hit rate of the Table A7 forecasts is consistent with the N1 null. H1: it exceeds the null. One-sided, α = 0.05.
- **Q2 (secondary).** The same test against the N2 red-noise null.
- **Q3 (Part C).** H0: the Table 3 forecasts hit no more often than their chance probabilities. H1: they hit more often. One-sided, α = 0.05.

## 3. Rule used for scoring (decided in this order)

1. If the authors state their operational rule before the Part B results are written up, it is implemented exactly and becomes primary (recorded in an amendment).
2. Otherwise the primary rule is the candidate with the highest κ against Table A7, if κ ≥ 0.7 (ties: the rule listed first in `RULES`).
3. If no candidate reaches κ ≥ 0.7, there is no primary rule. Results are reported for all of R1–R4 and no single p-value is claimed as the answer to Q1.

R0 (as printed) is reported only to show that it cannot produce a miss.
A forecast our code finds not evaluable counts as "not supported" when computing κ.

Settings: W = 0.20T; tolerance max(60 d, 0.20T); N_min = 2 detected bins; R3 threshold = median + 1σ of the detected pre-test fluxes; R4 search ±0.5T.

## 4. Part B design

- **Sample:** the 30 sources and 59 forecasts of Table A7 (`data/penil_tableA7.csv`). A predicted month means day 15 of that month (one entry gives a full date, 2022-08-29, used as given).
- **Periods:** for a source with two or more forecasts, T = the mean spacing of its consecutive forecasts (this is the period the authors actually used to place them). For a source with one forecast, T = the first "previous" period in Peñil et al. Table 1 (`data/penil_sources.csv`). Robustness: T from Table 1 for every source.
- **Light curves:** LCR, 30-day bins, photon flux, fixed index, ts_min = 4. A bin is "detected" if it has a flux (TS ≥ 4). Data end: bins with centre ≤ MJD 61000 (2025-11-24), i.e. 17.3 yr after the LCR start, matching "17.3 years" in Peñil et al. Sec. 2. If the authors give their end date, it is used as a robustness case.
- **Pre-test data:** bins with centre < MJD 59065 (2020-08-04, 12.0 yr after the start), the "original ~12 yr dataset". Used only for the N2 noise model and the R3 reference level.
- **Statistic:** pooled hit rate H = (total hits) / (total evaluable forecasts). Total hits is reported as well. (H is used because a shifted forecast in N1 can leave the data and become non-evaluable; a total would then be biased low under the null.)
- **Primary null N1, randomised forecasts:** for each source, all its forecasts are shifted by one common δ ~ U(−T/2, T/2); each draw sums over all sources. 10,000 draws. For speed, each source's outcome is first computed on a 1-day grid of δ and each draw then rounds δ to that grid (exact, because outcomes only change when a window edge crosses a 30-day bin).
- **Secondary null N2, red-noise light curves:** Emmanoulopoulos et al. (2013) simulations on the real time grid, with the real detection mask. Flux distribution: bootstrap of the detected pre-test fluxes. PSD: power law plus constant, P = A f^−β + C, and bending power law plus constant, P = A / (1 + (f/f_b)^β) + C (the form of Peñil et al. Eq. 1), each fitted to the pre-test data by maximising the Whittle likelihood on the evenly binned series (gaps filled by linear interpolation for the fit only). 1,000 simulations per source per PSD model. In each simulation the R3 reference level is recomputed from the simulated pre-test bins.
- **p-value:** p = (1 + #{null ≥ observed}) / (1 + N).
- **Effect size:** observed hits minus null-mean hits, with a 95% source-level bootstrap interval (10,000 resamples of sources).
- **Primary cell:** primary rule (§3), N1, W = 0.20T, periods from forecast spacing.
- **Also reported:** the N1 p-value for the authors' own verdicts (19/59) against the null of the primary rule.
- **Robustness (reported, never re-chosen):** W ∈ {0.10, 0.20, 0.30}T; N_min ∈ {2, 3}; all rules R1–R4; N2 with PL and BPL; Table 1 periods.
- **Power check:** sinusoids with period T and maxima at the real forecast times are added to N2 (PL) simulations, with amplitude a × (standard deviation of the detected fluxes), a ∈ {0.25, 0.5, 1, 2}. For each a: 100 injected sample realisations, each tested with N1 (1,000 draws). Reported: the fraction with p < 0.05.
- **Negative control:** forecasts of each source are scored against the light curve of a different source (a fixed derangement by source order, period kept); the N1 p-value should be uniform-like (not small).

## 5. Part C forecasts (Peñil et al. 2026, Table 3)

Window = predicted month (day 15) ± 0.20T. Primary test = the 5 windows that open after this commit. Secondary = all 13.

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

## 6. Part C scoring

- Each forecast is scored once, when LCR data reach 3 months past its window end.
- Same rule as Part B (§3). If Part B has no primary rule, Part C is scored with all of R1–R4 and reported without a single headline p-value.
- p_i (the chance probability of each forecast) is computed at scoring time with N1 on that source's own light curve (10,000 draws).
- Test: total hits against the Poisson-binomial distribution of the p_i, one-sided α = 0.05, separately for the primary set (5) and the full set (13). A version keeping one forecast per source (phase folding) is also reported, because two forecasts of the same source are not independent.
- Until scoring, `src/lcr.py` truncates every download at MJD 61000 (Part B) or at the scoring date, so later fluxes are not saved or shown.

## 7. What would change these plans

Only the authors' clarification of their rule (§3, step 1), or a data problem (for example a source missing from the LCR). Any change is recorded in a new dated file in `preregistration/`.
