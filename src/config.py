"""Fixed dates and settings for the analysis (see preregistration/).

All times are MJD (days). Fermi mission elapsed time (MET) is seconds since
2001-01-01 00:00:00 UTC = MJD 51910; leap seconds (< 10 s) are ignored, which
is negligible for 30-day bins.
"""
MET_ZERO_MJD = 51910.0
LCR_START_MJD = 54682.0          # 2008-08-04, first LCR bin edge

# Peñil et al. (2026) Section 2: "17.3 years Fermi-LAT observations".
# 17.3 yr after the LCR start = MJD 61000.8 (2025-11-25). We keep bins whose
# centre is <= PARTB_END_MJD. This is our default; the authors were asked for
# their exact end date.
PARTB_END_MJD = 61000.0          # 2025-11-24

# "the original ~12 yr dataset" (Peñil et al. 2026, Sec. 8.1). Data before this
# date are "pre-test": used only to fit the noise model (N2) and the R3
# reference level, never to score.
PRETEST_END_MJD = LCR_START_MJD + 12.0 * 365.25   # MJD 59065, 2020-08-04

# Part C blind start: arXiv date of Peñil et al. (2026). No flux after this
# date is saved or inspected before each forecast's scoring date.
PARTC_BLIND_START_MJD = 61205.0  # 2026-06-14

DAYS_PER_YEAR = 365.25
