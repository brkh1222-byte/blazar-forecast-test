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

---

## Re-check of the gate on 2026-11-25 (from the arXiv LaTeX source, v1)

The gate was re-done independently of the notes above, from the LaTeX source of
arXiv:2606.15676v1 (`main.tex`, fetched from arxiv.org/e-print on 2026-11-25; the source says
"Accepted 2026 June 10"). Crossref lists the published version as MNRAS 550, issue 3, stag1141
(doi:10.1093/mnras/stag1141). Only v1 exists on arXiv. The published MNRAS text was not compared
with v1.

**(b) Did Peñil et al. calibrate the forecast hit rate against a null? No.**

- Section 8 ("Predictions", `\label{sec:predictions_results}`) has two subsections, "Sample
  Validation of Predicted Maxima" and "Results". They define the window and tolerance, then
  report "59 predicted high states across 30 objects; 19/59 (≃32%) are supported", 7/30 full
  agreement, 15/30 none, 8/30 mixed. There is no expected-by-chance number, no simulation, no
  shuffling and no binomial comparison in either subsection.
- A search of the whole source for "chance", "coincidence", "binomial", "shuffl", "random
  phase/shift/forecast", "false positive", "baseline" and "expected number of" finds matches only
  in the periodogram-significance sections (Sections 4–7: the global-significance trials factor
  and the SSA window tests). None refers to the forecast test.
- The artificial light curves (PL, BPL, ARIMA, ARFIMA) are used to calibrate periodogram test
  statistics only.
- The one other forecast check is for SSA-R (Section 9, Figure 9 and A-figure): the last one or
  two cycles are removed, the forecast is repeated and "an overlap greater than 80% considering
  flux uncertainties" is reported. This is a hindcast on the same sources, again without a null.
- How the result is used: the abstract says "some are consistent with the new observations";
  Section 9 uses forecast agreement as support when describing the final candidates and as the
  reason to keep PKS 0454−234 and PKS 2155−304 "under continued monitoring".

**Gate passed (confirmed): Part B is not redundant with the paper.**

**(a) Rule text.** The quotes in section (a) above match the source word for word. Two more
phrases bear on the unstated step: the test checks "whether high states occur near those times",
and t_pred are the "predicted maxima epochs ... that fall within the test interval". The first
supports a high-state condition (our R3); neither states it as a rule.

**(c), (d) Tables.** `data/penil_tableA7.csv` (59 rows, 19 supported),
`data/penil_table3_predictions.csv` and the first "previous" period of each source in
`data/penil_sources.csv` were compared by script with `table_4_predictions_comparation.tex`,
`table_5_final_candidates.tex` and `table_1_list_objects.tex`: all identical. The only name
differences are the two LCR names recorded in amendment 1 (J0811.3→J0811.4, J1649.4+5238→+5235).

**Other details noticed**
- The sample is 52 candidates, 49 after removing three with > 50% upper limits.
- Table 1 lists TXS 0518+211 as 4FGL J0521.7+2113; PROPOSAL.md §5 found it in the LCR as
  J0521.7+2112. To be confirmed at Part C scoring time (no Part C source is downloaded before).
- The data end date is not given (only "17.3 years"), so MJD 61000 remains our assumption.
