# Research Proposal (v2, revised 22 Nov 2026)

## How Often Would Chance Alone "Confirm" a Blazar Periodicity Forecast? A Null Calibration of Gamma-Ray Forecast Tests, and a Pre-Registered Test of the 2026 Predictions

**Author:** Berkh (independent student researcher)
**Mentor / prospective co-author:** [mentor name] (cosmology & black holes)
**Field:** High-energy astrophysics / supermassive black hole binaries
**Planned duration:** 2–3 weeks for Part A–B, plus a short follow-up for Part C in early 2027
**Status:** Proposal

> **Why v2?** Version 1 proposed the first out-of-sample test of the Rico et al. (2025) forecasts. On 14 June 2026 the original authors posted that test themselves: **Peñil, Rico, Domínguez, Ajello, Buson & Adhikari, arXiv:2606.15676**. This version is reframed as an **independent statistical check** of their forecast test, plus a **pre-registered blind test** of their *new* predictions.

---

## 1. Summary

Some gamma-ray blazars appear to brighten every 1–4 years. One explanation is a **supermassive black hole binary (SMBHB)**. Peñil et al. (2026) re-examined 49 periodicity candidates with more than 17 years of Fermi-LAT data. In their Section 8.1, they checked earlier forecasts against the new data. They report that **19 of 59 predicted high states (≈32%) across 30 objects are supported**, and that only 8 sources keep more than 2σ local significance. Their abstract says "some [predictions] are consistent with the new observations."

**The open question:** how many forecast "hits" would we expect **by chance alone**? Suppose a match counts when an observed high state falls within ±0.2 of a period from the prediction. Then a randomly placed peak can land in that window a large fraction of the time; a rough estimate is about 40%, to be computed properly here. If the chance rate is close to 32%, the forecast "successes" carry no evidence for periodicity. If it is well below, they do.

This project will:
- **(A)** reproduce their forecast-matching result;
- **(B)** calibrate it against red-noise simulations and randomised forecasts, giving a proper p-value;
- **(C)** **pre-register** (timestamped in this public git repo) a blind test of their new 2026–2027 predictions, to be scored as the Fermi data arrive.

## 2. Background

- **Blazars** are active galaxies whose jets point near our line of sight. Their gamma-ray brightness varies strongly and randomly ("red noise").
- **SMBHBs** are expected from galaxy mergers and are the likely source of the nanohertz gravitational-wave background seen by pulsar timing arrays (2023). Periodic AGN light curves are a main route to finding individual binaries.
- **The red-noise trap:** red noise readily mimics 2–3 cycles of a period (Vaughan et al. 2016, MNRAS 461, 3145). Out-of-sample prediction is the strongest test, *but only if the chance rate of a "hit" is known.*

## 3. Prior work and the gap

| Work | What it did | What is missing |
|---|---|---|
| Rico et al. 2025, A&A 697, A35 (arXiv:2412.05812) | 46 candidates (2008–2020); forecasts of the next 4 cycles for 28 sources (Table 4, Appendix C) | — |
| **Peñil et al. 2026 (arXiv:2606.15676)** | Re-examined 49 candidates with 17.3 years of data; forecast check: 19/59 hits; 8 sources keep >2σ local significance; PG 1553+113 and S5 1044+71 >3σ local, ~0σ global | **No null calibration of the forecast hit rate** (to be confirmed by reading §8.1 closely — Task T1.1); new predictions not yet testable |
| Hashad et al. 2026, ApJ 1009, 28 (arXiv:2602.19214) | 6 blazars; only PG 1553+113 persistent | — |
| Yang et al. 2026 (arXiv:2608.24522) | 41 TeV blazars; no robust detection | — |

**Gap:** (i) the forecast-test hit rate has no chance baseline; (ii) the 2026 predictions have not yet been tested by anyone.

> ⚠️ **Gate:** If T1.1 finds that Peñil et al. already calibrated the forecast hit rate against simulations, Part B is dropped and the project becomes Part C only (plus PG 1553+113), or switches to the backup topic.

## 4. Research questions and hypotheses

- **Q1:** Can we reproduce the 19/59 forecast-hit result from public Light Curve Repository data with their matching rule?
- **Q2 (main):** Under red-noise light curves with each source's own power spectrum, and under randomised forecasts, what is the distribution of hit counts?
  - **H0:** 19/59 is consistent with chance (p > 0.05).
  - **H1:** 19/59 exceeds chance.
- **Q3 (pre-registered):** Do the next predicted high states arrive in their windows?
  - S5 1044+71: 2026-03/04
  - TXS 0518+211: 2026-03 (phase folding) or 2028-08 (SSA)
  - S3 0458−02: 2026-10
  - 87GB 164812.2+524023: 2026-10
  - PG 1553+113: 2027-03 to 06

  Predicted dates must be confirmed from Peñil et al. Table 3.

## 5. Data

| Source | Details |
|---|---|
| **Fermi LAT Light Curve Repository** (Abdollahi et al. 2023, arXiv:2301.01607) | Monthly (30-day) light curves; public API; verified to run to a bin starting 2026-10-15 for J1048.4+7143, J0521.7+2112, J0501.2−0158 and J1649.4+5235 |
| Peñil et al. 2026 | Matching rule (§8.1), predicted vs observed peaks (Table A7), new predictions (Table 3) |
| Rico et al. 2025 | 46 candidates and periods (Table 2, list in `data/` once created), forecasts (Table 4) |

The data total a few MB. No Fermi Science Tools are needed.

## 6. Method (Python: numpy, scipy, astropy, emcee)

1. **Read and encode the rule.** Read Peñil §8.1 and Table A7. Implement their definitions of "high state" and "match window" exactly.
2. **Reproduce** the 19/59 hit rate on the Light Curve Repository data.
3. **Red-noise null:**
   - For each of the 30 sources, fit the PSD (power law and bending power law) to the pre-forecast data.
   - Simulate 10,000 light curves (Emmanoulopoulos et al. 2013), with real cadence, gaps and upper limits.
   - Apply *the same* forecast procedure and matching rule to each, and record the hit counts.
4. **Randomised-forecast null:** keep the real light curves, but shift the predicted phases randomly or scramble periods between sources. This gives the chance hit rate for this rule on these data.
5. **Inference:** p-value of 19/59 under each null; a hit-rate excess with confidence interval; sensitivity to the window width (±0.1, ±0.2, ±0.3 period).
6. **Pre-registration (Part C):**
   - Before scoring, commit `preregistration/predictions_2026.md`: sources, predicted windows, scoring rule and analysis code hash.
   - The git commit timestamp on GitHub is the public record.
   - OSF preregistration requires users to be 18+, so the mentor could co-register it there.
   - Score each prediction once data through 3 months past the window are available.

## 7. Timeline

| Week | Tasks |
|---|---|
| 1 | Read Peñil §8.1 / Table A7 / Table 3 (gate check). Email the Peñil/Domínguez group. Download the data. Encode the rule. Reproduce 19/59. **Commit the pre-registration.** |
| 2 | Red-noise and randomised-forecast simulations. p-values. Window-width sensitivity. Figures. |
| 3 | Write up; mentor review. Submit to RNAAS. arXiv (mentor endorsement). |
| Early–mid 2027 | Score the pre-registered predictions → a second RNAAS note, or merge into a longer paper. |

## 8. Venue

- **RNAAS** for Parts A+B (1,500 words, one figure).
- A follow-up RNAAS note for Part C.
- With the mentor, an ApJ/MNRAS paper combining everything.
- Contacting Peñil et al. early is encouraged: they may welcome an independent check or offer collaboration.

## 9. Where the mentor helps most

- Red-noise simulation choices and the framing of significance and trials factors.
- Interpretation (SMBHB vs jet precession vs stochastic variability).
- arXiv endorsement.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Peñil et al. already calibrated the hit rate (gate) | Drop Part B and switch to Part C plus the backup topic |
| Their light curves differ from the Light Curve Repository's | Use their matching rule on Light Curve Repository data and report any differences in reproduction |
| Predicted dates misread from a garbled table | Confirm from the published PDF; ask the authors |
| Part C needs data through about Jan 2027 | Parts A+B stand alone |

## 11. Key references

- Peñil, P. et al. (2026). Gamma-Ray Periodicity in Jetted AGN: Revisiting Periodicity Candidates with >17 years of Fermi-LAT Data. arXiv:2606.15676
- Rico, A. et al. (2025). A&A 697, A35. arXiv:2412.05812
- Abdollahi, S. et al. (2023). Fermi-LAT Light Curve Repository. ApJS. arXiv:2301.01607
- Hashad, M. et al. (2026). ApJ 1009, 28. arXiv:2602.19214
- Vaughan, S. et al. (2016). MNRAS 461, 3145
- Emmanoulopoulos, D. et al. (2013). MNRAS 433, 907
- Timmer, J. & König, M. (1995). A&A 300, 707

> ⚠️ These references were compiled by an AI research assistant. Verify every citation before using it. arXiv:2606.15676 and 2412.05812 were checked against the arXiv API on 22 Nov 2026.
