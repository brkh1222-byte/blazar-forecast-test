"""Figure 1 of the research note. Regenerate with:  python scripts/make_figure.py
Inputs: results/null_draws.npz, results/null_draws_X1.npz, results/partB_n1.csv,
        results/exploratory_X1.json, results/power.csv
Output: paper/fig1.pdf and paper/fig1.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
INK, INK2, GREY, GRID = "#1f1f1e", "#5b5a55", "#a9a8a2", "#e6e5e0"
ACCENT = "#2a78d6"
CATS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]          # validated (dataviz validator)
MARKERS = ["o", "s", "^", "D"]
LABEL = {"R1_interior_max": "R1 interior max", "R2_local_max": "R2 local max",
         "R3_high_state": "R3 high state", "R4_cycle_max": "R4 cycle max",
         "X1_high_and_cycle": "X1 = R3 & R4\n(exploratory)"}

plt.rcParams.update({"font.size": 8.5, "axes.edgecolor": GREY, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "font.family": "DejaVu Sans"})

draws = dict(np.load(R / "null_draws.npz"))
draws["N1_X1_high_and_cycle"] = np.load(R / "null_draws_X1.npz")["N1"]
n1 = pd.read_csv(R / "partB_n1.csv")
n1 = n1[n1.cell == "primary-grid"].set_index("rule")
x1 = json.loads((R / "exploratory_X1.json").read_text())
obs = {r: n1.loc[r, "H_obs"] for r in LABEL if r in n1.index}
obs["X1_high_and_cycle"] = x1["H_obs"]
pval = {r: n1.loc[r, "p_N1"] for r in LABEL if r in n1.index}
pval["X1_high_and_cycle"] = x1["p_N1"]

fig, (a, b) = plt.subplots(1, 2, figsize=(7.1, 3.3), gridspec_kw=dict(width_ratios=[1.45, 1]))

# (a) chance hit rate per rule (N1) vs observed
rules = list(LABEL)
for i, r in enumerate(rules):
    d = draws[f"N1_{r}"]
    lo, q16, med, q84, hi = np.percentile(d, [2.5, 16, 50, 84, 97.5])
    a.plot([lo, hi], [i, i], color=GREY, lw=1.2, solid_capstyle="round", zorder=1)
    a.plot([q16, q84], [i, i], color=GREY, lw=5, solid_capstyle="round", zorder=1)
    a.plot(med, i, "|", color=INK2, ms=9, mew=1.5, zorder=2)
    a.plot(obs[r], i, "o", color=ACCENT, ms=6.5, mec="white", mew=1.2, zorder=3)
    a.text(1.02, i, f"p = {pval[r]:.2f}", va="center", fontsize=7.5, color=INK2,
           transform=a.get_yaxis_transform())
a.axvline(19 / 59, color=INK, lw=1, ls=(0, (4, 3)), zorder=0)
a.text(19 / 59 - 0.01, -0.62, "Peñil et al. 2026: 19/59", fontsize=7.5, color=INK, ha="right", va="center")
a.set_yticks(range(len(rules)), [LABEL[r] for r in rules])
a.invert_yaxis()
a.set_ylim(len(rules) - 0.4, -0.9)
a.set_xlim(0, 1)
a.set_xlabel("Hit rate (supported / evaluable)")
a.set_title("(a) Chance hit rate depends on the rule", loc="left", fontsize=9, color=INK)
a.grid(axis="x", color=GRID, lw=0.6)
a.set_axisbelow(True)
for s in ("top", "right", "left"):
    a.spines[s].set_visible(False)
a.tick_params(axis="y", length=0)
a.plot([], [], "o", color=ACCENT, ms=6, label="observed (this work)")
a.plot([], [], color=GREY, lw=5, label="N1 null: 68% / 95% range")
a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=7, frameon=False)

# (b) power of the N1 test vs injected amplitude
pw = pd.read_csv(R / "power.csv")
for k, (r, g) in enumerate(pw.groupby("rule", sort=False)):
    g = g.sort_values("amplitude_sd")
    b.plot(g.amplitude_sd, g.power, color=CATS[k], lw=2, marker=MARKERS[k], ms=5, mec="white",
           mew=0.8, label=LABEL[r].split("\n")[0])
b.axhline(0.05, color=INK2, lw=0.8, ls=(0, (2, 2)))
b.text(2.05, 0.085, "α = 0.05", ha="right", fontsize=7.5, color=INK2)
b.set_xlabel("Injected amplitude (× flux s.d.)")
b.set_ylabel("Fraction with p < 0.05")
b.set_ylim(-0.02, 1.04)
b.set_xlim(-0.05, 2.1)
b.set_title("(b) Power of the N1 test", loc="left", fontsize=9, color=INK)
b.grid(color=GRID, lw=0.6)
b.set_axisbelow(True)
for s in ("top", "right"):
    b.spines[s].set_visible(False)
b.legend(fontsize=7, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.45))

fig.tight_layout(w_pad=2.5)
(ROOT / "paper").mkdir(exist_ok=True)
fig.savefig(ROOT / "paper/fig1.pdf")
fig.savefig(ROOT / "paper/fig1.png", dpi=200)
print("wrote paper/fig1.pdf, paper/fig1.png")
