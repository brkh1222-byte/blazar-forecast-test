# data/

| File | Content | Source |
|---|---|---|
| `penil_tableA7.csv` | 59 earlier forecasts (30 sources) and whether Peñil et al. marked each as supported (1) or not (0). Month precision only. | Peñil et al. 2026, MNRAS 550, stag1141 (arXiv:2606.15676 v1), Table A7, transcribed from the PDF on 2026-11-22. Totals check: 59 forecasts, 19 supported, 7/15/8 sources full/none/mixed. |
| `penil_table3_predictions.csv` | New forecasts for the 8 Table 3 candidates (next two peaks, phase folding and SSA-R). PKS 0215+015, S3 0458-02 and 87GB 164812.2+524023 have no SSA-R forecast (too many gaps). | Same paper, Table 3. Note: the caption says "≥3σ" but six rows are 2.0–2.5σ. |

Light curves will go in `data/lcr/` (not committed; regenerate with `src/download_lcr.py`).
