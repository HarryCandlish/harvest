"""
NZ Bird Chart — Economist Style
--------------------------------
Recreates the visual language of The Economist's charts:
  - Bold title / italic subtitle / red rule line
  - Muted steel-blue bars, red highlight on leader
  - White background, minimal spines, light horizontal gridlines
  - Source credit bottom-left
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── Economist colour palette ─────────────────────────────────────────────────
ECON_RED    = "#E3120B"   # rule line & highlight bar
ECON_BLUE   = "#006BA2"   # primary bar colour
ECON_DARK   = "#171717"   # title / label text
ECON_GREY   = "#6B6B6B"   # subtitle / source text
ECON_LINE   = "#CCCCCC"   # gridlines
BG          = "#FFFFFF"   # white background

# ── Load top 10 species ──────────────────────────────────────────────────────
species, counts = [], []

with open("nz_bird_species.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = sorted(reader, key=lambda r: int(r["sightingCount"]), reverse=True)[:10]

for row in rows:
    common = row.get("vernacularName", "").strip()
    label  = common if common else row["species"]
    species.append(label)
    counts.append(int(row["sightingCount"]))

# Reverse so highest is at top
species = species[::-1]
counts  = counts[::-1]

# ── Figure setup ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)

# ── Bars ─────────────────────────────────────────────────────────────────────
colours = [ECON_RED if i == len(species) - 1 else ECON_BLUE for i in range(len(species))]
bars = ax.barh(species, counts, color=colours, height=0.6, zorder=3)

# Value labels — right of each bar
for bar, count in zip(bars, counts):
    ax.text(
        bar.get_width() + 0.2,
        bar.get_y() + bar.get_height() / 2,
        str(count),
        va="center", ha="left",
        fontsize=9.5, color=ECON_DARK,
    )

# ── Gridlines ────────────────────────────────────────────────────────────────
ax.xaxis.grid(True, color=ECON_LINE, linewidth=0.8, zorder=0)
ax.set_axisbelow(True)

# ── Spines — only keep the bottom ────────────────────────────────────────────
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color(ECON_LINE)
ax.spines["bottom"].set_linewidth(0.8)

# ── Axis ticks ───────────────────────────────────────────────────────────────
ax.tick_params(axis="y", length=0, labelsize=10, colors=ECON_DARK)
ax.tick_params(axis="x", length=3, labelsize=8.5, colors=ECON_GREY)
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))

# ── Y-axis labels — left aligned, regular weight ─────────────────────────────
plt.setp(ax.get_yticklabels(), ha="right", color=ECON_DARK)

# Extend x-axis slightly for the value labels
ax.set_xlim(0, max(counts) + 3)

# ── Title block (drawn on the figure, above the axes) ────────────────────────
# Title
fig.text(
    0.13, 0.97,
    "Most-spotted birds in New Zealand",
    fontsize=15, fontweight="bold", color=ECON_DARK,
    va="top", ha="left", fontfamily="serif"
)

# Subtitle / deck
fig.text(
    0.13, 0.905,
    "Number of recorded sightings by species, iNaturalist observations, 2026",
    fontsize=9, color=ECON_GREY,
    va="top", ha="left", style="italic"
)

# Red rule line — The Economist's signature separator
fig.add_artist(plt.Line2D(
    [0.13, 0.93], [0.893, 0.893],
    transform=fig.transFigure,
    color=ECON_RED, linewidth=2.5, solid_capstyle="butt"
))

# ── Source line ───────────────────────────────────────────────────────────────
fig.text(
    0.13, 0.015,
    "Source: Global Biodiversity Information Facility (GBIF)",
    fontsize=8, color=ECON_GREY, va="bottom"
)

# ── Layout & export ───────────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0.03, 1, 0.875])
plt.savefig("nz_bird_chart_economist.png", dpi=180, bbox_inches="tight", facecolor=BG)
print("Chart saved → nz_bird_chart_economist.png")
