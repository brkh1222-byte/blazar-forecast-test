# blazar-forecast-test

How often would chance alone "confirm" a blazar periodicity forecast? This repo does a null calibration of the Fermi-LAT gamma-ray forecast test (Peñil et al. 2026) for supermassive black hole binary candidates, plus a pre-registered blind test of the 2026–27 predictions.

📄 **Read the research proposal:** [PROPOSAL.md](PROPOSAL.md)

## Plan

Read Peñil+2026 matching rule → reproduce 19/59 hits → red-noise and randomised-forecast nulls → p-value → pre-registered scoring of the new predictions (2027)

## Layout

```
data/             transcribed tables from Peñil et al. (2026); downloaded light curves (data/lcr, not committed)
src/              analysis code (matching rules, nulls, simulations, Part C scoring)
scripts/          run_partB.py, review_partB.py, make_figure.py, make_null_calibration.py
tests/            pytest suite
results/          tables, logs and figures
preregistration/  analysis plan and dated amendments (never edited after commit)
notes/            STATUS.md (current state), gate notes, email draft
paper/            manuscript draft and paper/notes.md (source of every number)
```

## Status (25 Nov 2026)

- **Part B (retrospective calibration): run.** The published matching rule could not be reproduced
  (best Cohen's κ = 0.34 among four rules fixed in advance). Under each of those rules the forecasts
  hit about as often as chance (N1 p = 0.17–0.36). See `results/reproduction.md`,
  `results/null_calibration.json` and `paper/paper.tex` (draft, not yet reviewed by the researcher).
- **Part C (test of the 2026 forecasts): registered, pending.** First scoring date 2027-01-28, last 2030-01-15.
- Current state and open questions: `notes/STATUS.md`.

## Data credit

Fermi LAT Light Curve Repository (Abdollahi et al. 2023), NASA Fermi Science Support Center.
