# Sensitivity check: Part B with the fingerprinted `src/match.py`

`match_fingerprinted_reconstruction.py.txt` is the current `src/match.py` with the exploratory
rule X1 additions removed. Its SHA-256 is
`10341e0fc5e4f5589dc77d369b7c7bd92765009d7659fc9f2a5700118624fea4`, the value recorded in
`results/prereg_fingerprint.txt` (check: `shasum -a 256` on the file).

On 2026-11-25 `scripts/run_partB.py` was run in an isolated copy of the repository with this file
in place of `src/match.py` (same seed, same cached light curves, Python 3.14.8 and the pinned
`requirements.txt`). Every output (`q0_kappa.csv`, `q0_verdicts.csv`, `partB_n1.csv`,
`partB_n2.csv`, `power.csv`, `negative_control.csv`, `partB_summary.json`, `psd_fits.csv`, and
all arrays in `null_draws.npz`) is byte-identical to the files in `results/`. `run_partB.log`
here is the log of that run; it differs from `results/run_partB.log` only in elapsed times.

See `preregistration/2026-11-25_amendment_2.md`.
