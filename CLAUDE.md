# CLAUDE.md

This is a research project by a 17-year-old astrophysics student. It calibrates the forecast-hit rate reported by Peñil et al. 2026 (arXiv:2606.15676) against red-noise and randomised-forecast nulls, and pre-registers a test of their new predictions. Never edit `preregistration/` after it is committed; add amendments as new dated files. Read PROPOSAL.md first. The student's mentor works on cosmology and black holes and may co-author.

- **Stack:** Python with numpy, scipy, astropy (LombScargle), emcee and matplotlib. Data comes from the Fermi LAT Light Curve Repository API. Keep it simple; no Fermi Science Tools.
- **Statistics matter most:** every periodicity claim must be calibrated against red-noise simulations (Timmer & König / Emmanoulopoulos). Never report a significance without them.
- **Reproducibility:** pin versions in `requirements.txt`. Every figure and table must be regenerable from a script.
- **Integrity:** the student must understand and write the paper themselves, because arXiv bans AI-written or unread submissions. Explain methods when implementing them. Verify every citation.
