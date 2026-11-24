# STATUS (kept current by the piloting agent)

Last update: 2026-11-25, end of session 2. Branch `research-plan` (pushed). `main` is untouched.

## How to resume
1. `git checkout research-plan`; read this file.
2. Environment: `.venv/` (git-ignored). Recreate with
   `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`;
   tests: `.venv/bin/python -m pytest -q` (27 pass, about 1 minute).
3. Never `git add` anything under `preregistration/` (the researcher commits those).
4. Never download LCR data for a Part C source before its scoring date
   (`python src/score_preregistered.py --schedule`). The cache holds nothing after MJD 60998.

## Waiting for the researcher
1. **Read and commit `preregistration/2026-11-25_amendment_2.md`** (untracked draft). The paper
   and notes refer to it.
2. **Part C power** (amendment 2 §7): the registered primary test of 5 forecasts can almost never
   reject. Decide before 2027-01-28 whether to register an additional, more powerful test.
3. **Email to the authors** (`notes/email_penil_draft.md`): not sent. Their rule would close T2.2.
4. **Venue and authorship**: the draft is about 3,500 words (RNAAS allows 1,500);
   `[AUTHORS — TBD]`, `[AI-USE STATEMENT — TBD]`.
5. Merge `research-plan` into `main` when satisfied.

## What session 2 established
- **The brief was out of date about git.** All of session 1 (including `preregistration/`) had
  been committed by the researcher on 2026-11-24 15:17 +0800 (`6d53da4`) and pushed to `main`.
- **`src/match.py` hash mismatch: solved exactly.** Removing the X1 additions from the current
  file reproduces the fingerprinted SHA-256. Re-running Part B with that file gives byte-identical
  outputs (`results/sensitivity_fingerprinted_match/`). Details and the time line: amendment 2 §1.
- **Things amendment 2 also records:** plan and results share one public commit (§2); MJD 61000
  is 2025-11-21, not 11-24 (§3); the triple R1&R3&R4 has κ = 0.54, above X1 (§4); a probable
  `--quick` run preceded the full run (§1).
- **Gate T1.1 re-done from the arXiv LaTeX source:** no chance baseline in Peñil et al. Tables
  in `data/` match the source exactly.
- **Part B numbers stand:** best κ = 0.34 (R3), no primary rule; N1 p = 0.36, 0.19, 0.32, 0.17;
  N2 p = 0.12–0.98; power 89–100% at half the flux scatter.
- **Review (exploratory, `results/review_partB.json`):** κ of R3 is not inflated by selection
  (bootstrap 0.09–0.60); N1 is lenient for R4 (negative control over 29 shifts: median p 0.31);
  forecasts fitted to red noise gain 0–3 points over random-phase ones; 4 of 30 bending
  power-law fits sit on a bound. No bug was found that changes a Part B number.
- **Part C:** `src/score_preregistered.py` written, tested, dry-run on simulated data only.
  First scoring 2027-01-28 (S5 1044+71 SSA-R, TXS 0518+211 phase folding); last 2030-01-15.
- **References:** 8 of 9 verified on Crossref; Timmer & König (1995) has no DOI and was not
  machine-checked this session.
- **Paper:** `paper/paper.tex` is a full draft; `paper/notes.md` lists each number with its source.

## Known weaknesses / not done
- The paper has never been compiled (no LaTeX here).
- The published MNRAS version of Peñil et al. was not compared with arXiv v1.
- `data/candidates.csv` (T1.2) was never built; not needed for v2.
- The LCR name of PKS 0215+015 is unverified (cannot check before its scoring date).
- No N2 variant re-runs the SSA / phase-folding forecast methods on simulations (only a sinusoid proxy).
- `src/config.py` still carries the wrong date comment for MJD 61000 (left so its hash matches).
- PROPOSAL.md still describes the old plan, timeline and author line; it was not edited.

## Next technical steps (no researcher input needed)
- On or after 2027-01-28: `python src/score_preregistered.py --score` (scores only what is due).
- If the authors state their rule: implement it in `src/match.py` as a new rule, record it in an
  amendment, and re-run `scripts/run_partB.py`.
