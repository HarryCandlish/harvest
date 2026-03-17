"""
NZ Bird Chart Generator
-----------------------
Reads the top 10 most-sighted species from nz_bird_species.csv
and exports a clean bar chart as nz_bird_chart.png
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Load top 10 species ──────────────────────────────────────────────────────
species, counts = [], []

with open("nz_bird_species.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = sorted(reader, key=lambda r: int(r["sightingCount"]), reverse=True)[:10]

for row in rows:
    name = row["species"].split()[-1]  # just the species epithet, keeps labels short
    full = row["species"]
    species.append(full)
    counts.append(int(row["sightingCount"]))

# Reverse so highest is at the top
species = species[::-1]
counts  = counts[::-1]

# ── Economist-inspired style ─────────────────────────────────────────────────
BG      = "#F7F6F2"
GREEN   = "#3A5C45"
RED     = "#B8883A"   # accent / rule line (using Harvest gold)
TEXT    = "#1A1E1A"
SUBTLE  = "#9AA398"

fig, ax = plt.subplots(figsize=(9, 5.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# Horizontal bars
bars = ax.barh(species, counts, color=GREEN, height=0.55, zorder=3)

# Highlight the top bar in gold
bars[-1].set_color(RED)

# Value labels on each bar
for bar, count in zip(bars, counts):
    ax.text(
        bar.get_width() + 0.15,
        bar.get_y() + bar.get_height() / 2,
        str(count),
        va="center", ha="left",
        fontsize=9, color=TEXT,
        fontfamily="DejaVu Sans"
    )

# Gridlines (subtle, behind bars)
ax.xaxis.grid(True, color="white", linewidth=1.2, zorder=2)
ax.set_axisbelow(True)

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

ax.tick_params(axis="both", length=0)
ax.set_xlabel("Number of sightings", fontsize=9, color=SUBTLE, labelpad=8)
ax.tick_params(axis="y", labelsize=9.5)
ax.tick_params(axis="x", labelsize=8.5, colors=SUBTLE)
plt.setp(ax.get_yticklabels(), color=TEXT, style="italic")

# ── Economist-style title block ──────────────────────────────────────────────
fig.text(
    0.13, 0.97,
    "New Zealand bird sightings",
    fontsize=14, fontweight="bold", color=TEXT,
    va="top", ha="left"
)
fig.text(
    0.13, 0.91,
    "Top 10 most recorded species, iNaturalist observations via GBIF, 2026",
    fontsize=8.5, color=SUBTLE,
    va="top", ha="left"
)

# Red rule line under title (Economist signature)
fig.add_artist(plt.Line2D(
    [0.13, 0.92], [0.895, 0.895],
    transform=fig.transFigure,
    color=RED, linewidth=1.5
))

# Source line at bottom
fig.text(
    0.13, 0.02,
    "Source: GBIF (gbif.org) · Harvest Data Solutions",
    fontsize=7.5, color=SUBTLE, va="bottom"
)

plt.tight_layout(rect=[0, 0.04, 1, 0.88])
plt.savefig("nz_bird_chart.png", dpi=150, bbox_inches="tight", facecolor=BG)
print("Chart saved → nz_bird_chart.png")
