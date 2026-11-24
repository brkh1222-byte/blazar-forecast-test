# STATUS (kept current by the piloting agent; newest state at the top)

Last update: 2026-11-25, session 2 (branch `research-plan`).

## How to resume
1. `git checkout research-plan`; read this file, then the "Next" list below.
2. Environment: `.venv/` (git-ignored). Recreate with
   `uv venv .venv && uv pip install --python .venv/bin/python -r requirements.txt`.
3. Never `git add` anything under `preregistration/` (the researcher commits those).
4. Never download LCR data past MJD 61000 for Part B, or past MJD 61205 for Part C sources.

## Facts established this session
- **Repo state differed from the brief.** Everything from session 1 (incl. `preregistration/`)
  was already committed by the researcher on 2026-11-24 15:17 +0800 as `6d53da4 "progress"`
  and pushed to `origin/main`. Only `CLAUDE.md` had an uncommitted edit.
- **match.py integrity question: solved exactly.** Removing the X1 exploratory-rule additions
  (the `EXPLORATORY_RULES` constant with its 3-line comment, the 6-line `if rule in
  EXPLORATORY_RULES:` branch, and `+ EXPLORATORY_RULES` in one error message) from the current
  `src/match.py` gives a file whose SHA-256 equals the fingerprinted
  `10341e0f…fea4`. So the 07:44:59 edit only added exploratory rule X1 (amendment 1, item 4);
  the code paths of R0–R4 are byte-identical. File timestamps also show Q0 and N1 outputs
  (`q0_kappa.csv` 07:44:40, `partB_n1.csv` 07:44:46) were written BEFORE the edit (07:44:59).
  Re-run with the reconstructed file: see below (pending).
- **Gate T1.1 re-done from the arXiv LaTeX source** (v1, fetched 2026-11-25): no chance
  baseline for the forecast hit rate anywhere in Peñil et al. Gate passed.
  Table A7 (59 rows, 19 supported), Table 3 and the Table 1 "previous" periods in `data/*.csv`
  were compared programmatically with the LaTeX tables: all identical.
- **References:** all 8 DOIs in `paper/refs.bib` (+ North et al. 2002 cited in code) resolve on
  Crossref with matching title/volume/page/authors.
- **Date-label erratum:** MJD 61000 is 2025-11-21, not 2025-11-24 as written in
  `predictions_2026.md` §4, `src/config.py` and the paper draft. The code uses the MJD number,
  so no result changes. To be recorded in amendment 2 and fixed in config comment and paper.

## Next (in order)
- [ ] venv install finishing; run tests
- [ ] re-run Part B with reconstructed fingerprinted match.py; compare outputs
- [ ] write preregistration/2026-11-25_amendment_2.md (untracked; researcher commits)
- [ ] critical review of Part B (selection-honest kappa, negative control over all shifts, nulls)
- [ ] Part C scoring code + simulated dry run
- [ ] paper/notes.md number audit; complete paper/paper.tex
- [ ] tick TASKS.md; improve email draft (do not send)
