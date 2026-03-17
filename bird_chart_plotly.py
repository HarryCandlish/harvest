"""
NZ Bird Chart — Plotly Interactive
------------------------------------
Generates an interactive Economist-style bar chart and exports it as
a self-contained HTML file that can be embedded directly in the website.

Features: hover tooltips, smooth animations, Economist colour palette.
"""

import csv
import plotly.graph_objects as go

# ── Economist colours ────────────────────────────────────────────────────────
ECON_RED  = "#E3120B"
ECON_BLUE = "#006BA2"
ECON_DARK = "#171717"
ECON_GREY = "#6B6B6B"
ECON_LINE = "#E0E0E0"

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

# Colour each bar — red for the leader, blue for the rest
colours = [ECON_RED if i == len(species) - 1 else ECON_BLUE for i in range(len(species))]

# ── Build chart ──────────────────────────────────────────────────────────────
fig = go.Figure()

fig.add_trace(go.Bar(
    x=counts,
    y=species,
    orientation="h",
    marker_color=colours,
    text=counts,
    textposition="outside",
    textfont=dict(size=12, color=ECON_DARK),
    hovertemplate="<b>%{y}</b><br>Sightings: %{x}<extra></extra>",
    cliponaxis=False,
))

# ── Layout ───────────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Georgia, serif", color=ECON_DARK),
    margin=dict(l=180, r=60, t=110, b=60),

    title=dict(
        text=(
            "<b>Most-spotted birds in New Zealand</b><br>"
            "<span style='font-size:12px; color:#6B6B6B;'>"
            "<i>Number of recorded sightings by species, iNaturalist observations, 2026</i>"
            "</span>"
        ),
        x=0,
        xanchor="left",
        xref="paper",
        y=0.98,
        yanchor="top",
        font=dict(size=18, color=ECON_DARK),
    ),

    xaxis=dict(
        showgrid=True,
        gridcolor=ECON_LINE,
        gridwidth=1,
        zeroline=False,
        showline=True,
        linecolor=ECON_LINE,
        tickfont=dict(size=11, color=ECON_GREY),
        range=[0, max(counts) + 3],
    ),

    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        tickfont=dict(size=12, color=ECON_DARK),
    ),

    shapes=[
        # Red rule line under title — Economist signature
        dict(
            type="line",
            xref="paper", yref="paper",
            x0=0, x1=1,
            y0=1.04, y1=1.04,
            line=dict(color=ECON_RED, width=3),
        )
    ],

    annotations=[
        dict(
            text="Source: Global Biodiversity Information Facility (GBIF)",
            xref="paper", yref="paper",
            x=0, y=-0.12,
            showarrow=False,
            font=dict(size=10, color=ECON_GREY),
            align="left",
        )
    ],

    hoverlabel=dict(
        bgcolor="white",
        bordercolor=ECON_BLUE,
        font_size=13,
        font_family="Georgia, serif",
    ),

    bargap=0.35,
)

# ── Export ───────────────────────────────────────────────────────────────────
fig.write_html(
    "nz_bird_chart_interactive.html",
    include_plotlyjs="cdn",   # loads Plotly from CDN — keeps file size small
    full_html=False,          # just the <div> — easy to embed in index.html
    config={"displayModeBar": False},  # hide the plotly toolbar
)

print("Chart saved → nz_bird_chart_interactive.html")
print("Open it directly in your browser or embed it in index.html")
