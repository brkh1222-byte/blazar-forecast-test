# Research Proposal

## Do Gamma-Ray Blazar Periodicities Keep Time? An Out-of-Sample Test of Published Forecasts with Six Years of New Fermi-LAT Data

**Author:** Berkh (independent student researcher)
**Mentor / prospective co-author:** [mentor name] (cosmology & black holes)
**Field:** High-energy astrophysics / supermassive black hole binaries
**Planned duration:** 3–4 weeks
**Status:** Proposal, Nov 2026

---

## 1. Summary

Some gamma-ray blazars appear to brighten every 1–4 years. A leading explanation is a **supermassive black hole binary (SMBHB)**: two black holes orbiting each other cause the jet to wobble or the accretion rate to change periodically. If this is right, the periodicity must **keep time**: future peaks should arrive when predicted.

Rico et al. (2025, A&A 697, A35; arXiv:2412.05812) found **46 periodicity candidates** in Fermi-LAT data from 2008 to Dec 2020. For **28** of them they **forecast the next four emission cycles**.

This project tests those forecasts against **about 5.8 years of Fermi-LAT data that the forecasts never saw** (Jan 2021 → Oct 2026). Predictions were made first and are tested now, which makes this a clean falsification test. Any outcome is publishable. If the peaks arrive on time, the case for SMBHBs is strengthened. If they don't, most "periodicities" are red-noise artefacts.

## 2. Background

- **Blazars** are active galactic nuclei whose relativistic jets point close to our line of sight. Their gamma-ray emission is highly variable.
- **Periodicity and SMBHBs.** Galaxy mergers should produce SMBH pairs, and close pairs are the source of the nanohertz gravitational-wave background detected by pulsar timing arrays in 2023. Finding individual SMBHBs is a major goal, and quasi-periodic AGN light curves are one of the main ways candidates are selected.
- **The red-noise problem.** AGN light curves are "red noise": random variability with more power on long timescales. Red noise readily produces apparent periods that last 2–3 cycles. With only about 12 years of Fermi data and periods of 1–4 years, many published candidates show only 3–6 cycles. Vaughan et al. (2016, MNRAS 461, 3145) showed how easily such false periodicities appear. **Out-of-sample prediction is the strongest available test.**
- **PG 1553+113** is the best-established case, with a period of about 2.2 years. Its periodicity has persisted for more than 7 cycles. It serves as a positive control.

## 3. Prior work and the gap

| Work | What it did | What is missing |
|---|---|---|
| Rico et al. 2025, A&A 697 A35 (arXiv:2412.05812) | 46 candidates from 2008–2020 Fermi data; forecasts of the next 4 cycles for 28 sources | Forecasts tested only for PG 1553+113 |
| Hashad et al. 2026, ApJ 1009, 28 (arXiv:2602.19214) | 6 blazars, data to early 2025; only PG 1553+113 persistent | Small sample; did not test Rico's forecasts |
| Yang et al. 2026 (arXiv:2608.24522) | 41 TeV blazars, no robust detection | No forecast test |
| Peñil et al. (arXiv:2507.13906) | Transient-periodicity framework | Different question |
| Abdo/Ackermann et al. 2015; PG 1553+113 papers (arXiv:2501.08015, 2603.04527) | PG 1553+113 confirmation | Single source |

**Gap:** No systematic out-of-sample test of the published Fermi blazar periodicity forecasts exists. This was confirmed by literature search in Nov 2026.

## 4. Research questions and hypotheses

1. **Q1, timing:** For each of the 28 forecast sources, did the 2021–2026 gamma-ray peaks occur inside the forecast windows?
   - H0 (red noise): the hit rate equals the hit rate of matched red-noise simulations.
   - H1 (true periodicity): the hit rate is significantly above that.
2. **Q2, persistence:** Is the period measured *only* from 2021–2026 data consistent with the pre-2021 period?
3. **Q3, population:** What fraction of the 46 candidates still behave periodically, and does persistence correlate with the original significance, the number of cycles, or the blazar class (BL Lac vs FSRQ)?

## 5. Data

| Source | Details |
|---|---|
| **Fermi LAT Light Curve Repository** (LCR; Abdollahi et al. 2023, ApJS; arXiv:2301.01607) | Ready-made 3-day, weekly and **monthly** (30-day) light curves for more than 1,500 variable 4FGL sources, updated continuously. Public JSON/CSV API. Tested Nov 2026: monthly light curves download through about mid-Oct 2026. |
| Rico et al. 2025 | Candidate list, periods and forecasts (Appendix C figures; request tables from the authors) |
| 4FGL-DR4 catalog | Source classes (BL Lac / FSRQ), redshifts |

Data volume is a few MB in total. No Fermi Science Tools analysis is required.

## 6. Method

All in Python with numpy, scipy, astropy and emcee.

1. **Download** the monthly LCR light curves for all 46 candidates. Handle upper limits (TS < 4) consistently, e.g. treat them as censored data or drop them, and test both.
2. **Reproduce** the pre-2021 periods by running a Lomb–Scargle periodogram on 2008–2020 data. Validate against Rico et al. values, with PG 1553+113 at about 2.2 years.
3. **Obtain the forecasts:**
   - (a) Request the forecast tables from the authors.
   - (b) Otherwise, digitise Appendix C (e.g. WebPlotDigitizer).
   - (c) Independently, make our own forecasts: fit a sinusoid to the 2008–2020 data only and extrapolate with uncertainties from MCMC.
4. **Measure the observed peaks** in 2021–2026: fit Gaussian or Bayesian-block peaks to the light curves. Compare peak times with the forecast windows.
5. **Persistence test:** Lomb–Scargle on post-2021 data alone. Check period consistency.
6. **Red-noise calibration:**
   - For each source, fit a power-law PSD to the pre-2021 data.
   - Simulate 10,000 light curves with the same PSD and flux distribution (Timmer & König 1995; Emmanoulopoulos et al. 2013).
   - Apply the *same* forecast-and-test procedure to each simulated curve to get the chance hit rate.
7. **Population statistics:** compare the hit rate across the sample with the red-noise expectation using a binomial test or a likelihood ratio.

## 7. Timeline

| Week | Tasks | Deliverable |
|---|---|---|
| 1 | Read the key papers. Email the Rico/Domínguez group for forecast tables. Download the LCR data. Reproduce PG 1553+113. | Data plus positive control |
| 2 | Extract or recompute forecasts. Measure the 2021–2026 peaks. Run the persistence test. | Results table |
| 3 | Red-noise simulations and population statistics. Make figures. | Final figures |
| 4 | Write up; mentor review. Submit to RNAAS. Post to arXiv (mentor endorsement). | Submitted paper |

**Minimum viable result (end of week 2):** a forecast-vs-observed table for the 28 sources. That is enough for a Research Note.

## 8. Expected outputs and venue

- **RNAAS** (Research Notes of the AAS): a short note of 1,500 words and one figure, free, high acceptance likelihood.
- **Expanded paper:** all 46 candidates plus full red-noise statistics for **ApJ** or **MNRAS** with the mentor as co-author.
- **Alternative:** the *Journal of Emerging Investigators* (the project is hypothesis-driven; requires an adult mentor as senior author). Do not publish the same result in two venues.
- Public code and data tables in this repository.

## 9. Where the mentor helps most

- Red-noise statistics and the correct framing of significance and trials factors.
- Physical interpretation (SMBHB vs jet precession vs other quasi-periodic mechanisms).
- Sanity-checking the methodology.
- arXiv endorsement (required for first-time submitters since Jan 2026).

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Forecasts only available as figures | Digitise, contact the authors, and make independent forecasts (step 3c) |
| LCR light curves (fixed photon index, 30-day bins) differ from the authors' own analysis | Compare peak *timing*, not amplitude; note the differences in the paper |
| The original group tests its own forecasts first | Contact them early; offer collaboration; move fast (RNAAS in about 3 weeks) |
| Too few cycles after 2021 for long-period sources | Restrict the strong test to periods under 3 years; report others as limits |

## 11. Key references

- Rico, A. et al. (2025). A&A 697, A35. arXiv:2412.05812
- Abdollahi, S. et al. (2023). The Fermi-LAT Light Curve Repository. ApJS. arXiv:2301.01607
- Hashad, M. et al. (2026). ApJ 1009, 28. arXiv:2602.19214
- Yang et al. (2026). arXiv:2608.24522
- Peñil, P. et al. (2025). arXiv:2507.13906
- Vaughan, S. et al. (2016). False periodicities in quasar time-domain surveys. MNRAS 461, 3145
- Timmer, J. & König, M. (1995). A&A 300, 707
- Emmanoulopoulos, D. et al. (2013). MNRAS 433, 907
- Ackermann, M. et al. (2015). PG 1553+113 periodicity. ApJL 813, L41

> ⚠️ These references were compiled by an AI research assistant. Verify every citation (authors, year, journal, arXiv ID) against the source before using it in the paper.
