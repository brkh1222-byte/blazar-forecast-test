# paper/notes.md — results in bullets, and the source of every number in paper.tex

Written 2026-11-25 (session 2). Each number in `paper/paper.tex` was checked against the file
named here on that date. `results/null_calibration.json` collects most of them in one place
(regenerate with `scripts/make_null_calibration.py`). If a result file changes, re-check this list.

## Results in bullets

- The rule printed in Peñil et al. (2026) Sec. 8.1 cannot produce a miss (R0: 56 of 56 evaluable).
- No chance baseline for the forecast hit rate exists in their paper (gate T1.1, `notes/penil2026_rules.md`).
- None of four rules fixed in advance reproduces their 59 verdicts: best κ = 0.34 (R3). No primary rule.
- Chance hit rate (N1) is 42–79% depending on the rule; observed rates are 2–6 points higher; p = 0.17–0.36.
- Red-noise null (N2): p = 0.12–0.98. Smallest p of 20 pre-specified N1 tests: 0.055.
- Power at half the flux scatter: 89–100%. False-positive rate 1–7%. Negative control p = 0.76–0.93.
- Exploratory X1 (R3 AND R4): κ = 0.47, chance rate 29% (N1), observed 29%; published 32% is consistent.
- Exploratory checks: κ of R3 not inflated by selection; N1 is lenient for R4; fitted forecasts on red
  noise gain 0–3 points over random-phase forecasts.
- Part C: 13 forecasts registered; first scoring 2027-01-28, last 2030-01-15; nothing scored yet.
- Integrity: `src/match.py` hash mismatch explained exactly (X1 added); re-run byte-identical.

## Number audit

Abbreviations: NC = `results/null_calibration.json`; N1 = `results/partB_n1.csv`; N2 =
`results/partB_n2.csv`; Q0 = `results/q0_kappa.csv`; QV = `results/q0_verdicts.csv`; PW =
`results/power.csv`; NEG = `results/negative_control.csv`; X1 = `results/exploratory_X1.json`;
REV = `results/review_partB.json`; A7 = `data/penil_tableA7.csv`; T3 =
`data/penil_table3_predictions.csv`; DL = `results/download_log.csv`.

### From Peñil et al. (2026) (arXiv:2606.15676v1 LaTeX source, read 2026-11-25)

| Number in paper | Value | Source |
|---|---|---|
| forecasts, supported, sources | 59, 19 (32%), 30 | their Sec. 8.2; A7 (59 rows, sum of `supported` = 19, 30 names) |
| not supported | 40 | 59 − 19 |
| data length | 17.3 yr | their Sec. 2 |
| window, N_min, tolerance | W = 0.20T, 2, max(60 d, 0.20T) | their Sec. 8.1 (quoted in `notes/penil2026_rules.md`) |
| "some … are consistent with the new observations" | quote | their abstract |
| new forecasts: 8 sources, 13 source–method pairs, 5 with SSA | 8, 13, 5 | their Table 3; T3 (13 rows; 5 `ssa_r`) |
| PG 1553+113: 3 of 3 supported | 3/3 | A7 |

### Data and design

| Number in paper | Value | Source |
|---|---|---|
| cut date | MJD 61000 = 2025-11-21 | `src/config.py` (`PARTB_END_MJD`); date by astropy `Time(61000, format='mjd')` |
| pre-test end | MJD 59065 = 2020-08-04, first 12 yr | `src/config.py`; astropy |
| grid | 211 bins of 30 d | amendment 1 item 3; `src/partb_data.py` `GRID.size` |
| undetected-bin fraction | 0%–46%, median 9% | DL: 1 − n_detected/211 → min 0.000, median 0.092, max 0.464 |
| sources with ≥2 / 1 forecasts | 21 / 9 | QV: forecasts per source = {1: 9, 2: 14, 3: 6, 4: 1} |
| period range | 1.4–5.7 yr | QV `period_d` min 517.7 d, max 2081.9 d |
| N1 draws; N2 simulations | 10,000; 1,000 per source per model | `results/partB_summary.json` |
| power check | 100 samples, 1,000 N1 draws, a = 0.25, 0.5, 1, 2 | `scripts/run_partB.py`; PW |
| N1 tests in robustness grid | 20 | N1: rows with rule ≠ R0 (4 primary + 8 W + 4 N_min + 4 period) |
| threshold for a primary rule | κ ≥ 0.7 | `preregistration/predictions_2026.md` §3 |

### Main results (Table 1, Sec. 5.1–5.3, abstract, conclusions)

| Number in paper | Value | Source |
|---|---|---|
| evaluable forecasts | 56 of 59 | Q0 `evaluable` |
| the 3 non-evaluable are published misses | S4 1030+41 2023-04; TXS 1530−131 2022-08-29 and 2025-06 | REV `C_not_evaluable` |
| R0 hits | 56/56 | Q0 |
| κ for R1–R4 | 0.23, 0.10, 0.34, 0.23 | Q0: 0.2260, 0.1044, 0.3441, 0.2310 |
| R3 agreement | 40 of 59 | Q0 `agreement` 0.6780 × 59 |
| R3: 14 of 19 published hits, 14 of 40 published misses | 14, 14 | REV `A_rule_selection.confusion_R3` |
| hits/evaluable R1–R4 | 41, 47, 28, 27 of 56 | Q0; N1 primary-grid |
| H_obs R1–R4 | 0.73, 0.84, 0.50, 0.48 | N1 primary-grid: 0.7321, 0.8393, 0.5000, 0.4821 |
| N1 mean ± sd R1–R4 | 0.71±0.06, 0.79±0.06, 0.47±0.04, 0.42±0.07 | N1: 0.7090±0.0598, 0.7877±0.0573, 0.4730±0.0450, 0.4180±0.0681 |
| "42%–79%" chance rates | 0.418–0.788 | same |
| excess in points | 2, 5, 3, 6 | H_obs − N1 mean: 0.023, 0.052, 0.027, 0.064 |
| excess in null sd | 0.4–0.9 | 0.39, 0.90, 0.60, 0.94 |
| p_N1 R1–R4 | 0.36, 0.19, 0.32, 0.17 | N1: 0.3579, 0.1921, 0.3151, 0.1664 |
| N2 PL mean (p) R1–R4 | 0.72 (0.46), 0.77 (0.13), 0.54 (0.75), 0.39 (0.12) | N2: 0.7151 (0.4565), 0.7711 (0.1319), 0.5423 (0.7542), 0.3935 (0.1159) |
| N2 BPL mean (p) R1–R4 | 0.71 (0.41), 0.78 (0.18), 0.61 (0.98), 0.41 (0.18) | N2: 0.7110 (0.4126), 0.7783 (0.1828), 0.6143 (0.9750), 0.4141 (0.1798) |
| "p = 0.12–0.98" (abstract), "p ≥ 0.12 against red noise" | min 0.1159, max 0.9750 | N2, R1–R4, both models |
| smallest / largest p of 20 N1 tests | 0.055 (R1, W = 0.10T) / 0.66 | N1: 0.0551 / 0.6628; NC `n1_robustness` |
| power a = 0.25, R1–R4 | 0.61, 0.62, 0.42, 0.90 | PW |
| power a = 0.5, R1–R4 | 0.96, 0.94, 0.89, 1.00 ("89%–100%") | PW |
| power a ≥ 1 | 1.00 for all | PW |
| false-positive rate (a = 0) | 0.07, 0.01, 0.01, 0.05 ("1%–7%") | PW |
| negative control p (shift 1) | 0.93, 0.80, 0.84, 0.76 | NEG: 0.9256, 0.7973, 0.8350, 0.7640 |

### Exploratory (Sec. 5.4 and X1 row of Table 1)

| Number in paper | Value | Source |
|---|---|---|
| X1 κ, hits, H_obs | 0.47, 16/56, 0.29 | X1: 0.4736, 16, 56, 0.2857 |
| X1 N1 mean ± sd, p | 0.29±0.06, 0.53 | X1: 0.2895, 0.0579, 0.5261 |
| X1 N2 PL / BPL mean (p) | 0.28 (0.51) / 0.34 (0.85) | X1: 0.2794 (0.5065) / 0.3412 (0.8482) |
| published 19/59 against X1 nulls | p = 0.27, 0.21, 0.57 | X1 `p_N1_authors`, `p_N2PL_authors`, `p_N2BPL_authors`: 0.2739, 0.2068, 0.5694 |
| X1 is the best pair | pairs: 0.31, 0.44, 0.26, 0.38, 0.23, 0.47 | REV `all_combo_kappas` |
| triple R1&R3&R4 | κ = 0.54 | REV `all_combo_kappas`: 0.5413 |
| triple differs from X1 only for one source (2 forecasts) | TXS 1452+516 | QV (rows where R3 & R4 = 1 and R1 = 0) |
| leave-one-source-out κ, combination family | 0.47 | REV `AND-combinations.kappa_leave_one_source_out` 0.4736 |
| R3 best in every fold | 30 of 30 | REV `R1-R4.loso_rule_counts` |
| bootstrap 95% interval of κ(R3) | 0.09–0.60 | REV `R1-R4.kappa_bootstrap_95`: 0.086, 0.604 |
| permutation: max κ ≥ 0.34 | 0.8% of shuffles | REV `R1-R4.perm_p_value` 0.0082 (4,000 shuffles) |
| negative control, 29 shifts: median p R1–R3 | 0.54, 0.45, 0.46 | REV `B_…`: 0.537, 0.446, 0.461 |
| … shifts with p < 0.05, R1–R3 | 2, 1, 0 ("at most 2") | REV: 0.069, 0.034, 0.000 × 29 |
| … R4 median p; shifts with p < 0.05; mean excess | 0.31; 3 of 29; 4 points | REV: 0.310; 0.103 × 29; 0.0407 |
| fitted forecasts, fixed T, minus random-phase | within 1 point | REV `D….difference_fixed_T_minus_real`: +0.000, −0.010, −0.003, −0.009 |
| fitted forecasts, best T, minus random-phase | 1–3 points | REV `D….difference_best_T_minus_real`: +0.018, +0.021, +0.034, +0.013 |

### Part C (Sec. 6)

| Number in paper | Value | Source |
|---|---|---|
| public registration date | 2026-11-24 | `git log`: commit 6d53da4, 2026-11-24 15:17 +0800 |
| clarifications | 2026-11-25 | `preregistration/2026-11-25_amendment_2.md` §6 (**not yet committed**: the sentence is true only once the researcher commits it) |
| primary set / all | 5 / 13 | `python src/score_preregistered.py --schedule`; predictions_2026.md §5 |
| first and last scoring dates | 2027-01-28 (two forecasts); 2030-01-15 | `--schedule` |
| dry-run numbers | see below | `results/partC_dryrun.json` |

Dry run (`results/partC_dryrun.json`, simulated light curves only, 100 samples per amplitude, 1,000 N1 draws;
values are fractions of samples with p < 0.05 for R1/R2/R3/R4; also in `results/partC_dryrun.log`):

| Amplitude (flux s.d.) | primary 5 | all 13 | one per source (8) |
|---|---|---|---|
| 0 (false-positive rate) | 0.01/0.00/0.00/0.03 | 0.10/0.04/0.02/0.15 | 0.07/0.00/0.00/0.07 |
| 0.5 | 0.00/0.00/0.00/0.06 | 0.24/0.14/0.11/0.46 | 0.16/0.00/0.02/0.32 |
| 1.0 | 0.03/0.00/0.00/0.20 | 0.43/0.32/0.17/0.80 | 0.28/0.15/0.04/0.68 |
| 2.0 | 0.16/0.02/0.00/0.28 | 0.80/0.77/0.53/0.98 | 0.66/0.69/0.12/0.93 |

| Number in paper | Value | Source |
|---|---|---|
| primary set, a = 2: "at most 28%"; R2 and R3 "at most 2%" | 0.16/0.02/0.00/0.28 | table above |
| all 13, a = 2: "53%–98%" | 0.80/0.77/0.53/0.98 | table above |
| all 13 false-positive rate "2%–15%" | 0.10/0.04/0.02/0.15 | table above (100 samples: standard error about 0.02–0.04) |
| one per source false-positive rate "0%–7%" | 0.07/0.00/0.00/0.07 | table above |
| "40%–80%" single-forecast chance | approximate range of N1 means in Table 1 (0.42–0.79) | N1 |


### Limitations (Sec. 7)

| Statement | Source |
|---|---|
| hash mismatch, exact reconstruction, byte-identical re-run | `preregistration/2026-11-25_amendment_2.md` §1; `results/sensitivity_fingerprinted_match/` |
| plan and results in the same public commit | `git log --stat 6d53da4` |
| short low-precision run before the full run (inferred) | file creation times, amendment 2 §1 |
| bending power-law fit on a bound for 4 of 30 sources | `results/psd_fits.csv`, model BPL: log f_b at its lower bound for 3 sources, β = 6 for 1 |
| effect-size and grid deviations | `preregistration/2026-11-22_amendment_1.md` items 3 and 5 |

## References (all checked 2026-11-25)

| Key | Check |
|---|---|
| penil26 | Crossref doi:10.1093/mnras/stag1141: MNRAS 550 (3), stag1141, 2026; 6 authors match. arXiv:2606.15676 (API) matches title and authors. |
| rico25 | Crossref doi:10.1051/0004-6361/202452495: A&A 697, A35, 2025; 7 authors match. arXiv:2412.05812 queried. |
| penil25c | Crossref doi:10.1093/mnras/staf1598: MNRAS 543 (3), 2880–2901, 2025; 6 authors match. |
| abdollahi23 | Crossref doi:10.3847/1538-4365/acbb6a: ApJS 265, 31, 2023; "The Fermi-LAT Lightcurve Repository". arXiv:2301.01607 queried. |
| vaughan16 | Crossref doi:10.1093/mnras/stw1412: MNRAS 461, 3145–3152, 2016; 8 authors match. |
| emmanoulopoulos13 | Crossref doi:10.1093/mnras/stt764: MNRAS 433, 907–927, 2013. |
| vaughan10 | Crossref doi:10.1111/j.1365-2966.2009.15868.x: MNRAS 402, 307–320 (online 2009, volume year 2010). |
| cohen60 | Crossref doi:10.1177/001316446002000104: Educ. Psychol. Meas. 20, 37–46, 1960. |
| timmer95 | No DOI exists. A&A 300, 707 (1995). **Not machine-verified this session** (ADS needs a token); session 1 confirmed it from the Crossref reference lists of emmanoulopoulos13 and vaughan16. Check on ADS (1995A&A...300..707T) before submission. |
| (code only) North, Curtis & Sham 2002 | Crossref doi:10.1086/341527: Am. J. Hum. Genet. 71, 439–441. Cited in `src/nulls.py`, not in the paper. |

Not verified: that each cited paper says what the sentence citing it claims was checked only for
penil26 (read in source) and for the standard methods papers from general knowledge; the
researcher should confirm the claims attributed to rico25 and penil25c (that they contain the
forecasts tested), which rest on Peñil et al.'s own description.

## Open items in the draft

- `[AUTHORS — TBD]`, `[AFFILIATION — TBD]`, `[AI-USE STATEMENT — TBD]`.
- The draft has never been compiled (no LaTeX on this machine).
- Venue: the draft is about 3,000 words; RNAAS allows 1,500.
- UAT keyword numbers and the Zenodo DOI are unchecked/missing.
