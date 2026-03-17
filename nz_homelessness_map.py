"""
NZ Housing Deprivation Map
---------------------------
Bubble map showing severe housing deprivation (homelessness) estimates
by NZ region, based on Stats NZ 2023 Census data.

Total: 112,496 people severely housing deprived (2.3% of population)
Source: Stats NZ — 2023 Census Severe Housing Deprivation Estimates
"""

import plotly.graph_objects as go

# ── Regional data ─────────────────────────────────────────────────────────────
# Estimates based on Stats NZ 2023 Census regional distributions
# Coordinates: (latitude, longitude, region name, estimate, rate %)
regions = [
    (-35.74, 174.32, "Northland",             6100,  4.1),
    (-36.87, 174.77, "Auckland",             42800,  2.6),
    (-37.78, 175.28, "Waikato",               9200,  2.1),
    (-37.93, 176.73, "Bay of Plenty",         7100,  2.4),
    (-38.66, 178.02, "Gisborne",              1800,  3.8),
    (-39.49, 176.62, "Hawke's Bay",           4500,  2.7),
    (-39.07, 174.08, "Taranaki",              2000,  1.7),
    (-40.35, 175.61, "Manawatū-Whanganui",   5500,  2.3),
    (-41.29, 174.78, "Wellington",           10200,  1.9),
    (-41.27, 172.82, "Tasman",                 800,  1.5),
    (-41.27, 173.28, "Nelson",                 700,  1.4),
    (-41.51, 173.96, "Marlborough",           1200,  2.0),
    (-42.45, 171.21, "West Coast",            1200,  3.6),
    (-43.53, 172.63, "Canterbury",           12000,  1.8),
    (-45.88, 170.50, "Otago",                4000,  1.7),
    (-46.41, 168.36, "Southland",            2400,  2.1),
]

lats    = [r[0] for r in regions]
lons    = [r[1] for r in regions]
names   = [r[2] for r in regions]
counts  = [r[3] for r in regions]
rates   = [r[4] for r in regions]

# Scale bubble size
import math
sizes = [math.sqrt(c) * 1.4 for c in counts]

# Colour scale — light to dark red
colours = counts

# ── Build map ────────────────────────────────────────────────────────────────
fig = go.Figure()

fig.add_trace(go.Scattergeo(
    lat=lats,
    lon=lons,
    mode="markers+text",
    marker=dict(
        size=sizes,
        color=colours,
        colorscale=[
            [0.0, "#FDE8E8"],
            [0.3, "#F4A09A"],
            [0.6, "#E3120B"],
            [1.0, "#8B0000"],
        ],
        cmin=min(counts),
        cmax=max(counts),
        colorbar=dict(
            title=dict(
                text="Estimated people",
                font=dict(size=11, color="#6B6B6B", family="Georgia, serif"),
            ),
            tickfont=dict(size=10, color="#6B6B6B"),
            thickness=12,
            len=0.5,
            x=1.01,
        ),
        line=dict(color="white", width=1),
        opacity=0.85,
        sizemode="diameter",
    ),
    text=names,
    textposition="top center",
    textfont=dict(size=9.5, color="#171717", family="Georgia, serif"),
    customdata=list(zip(counts, rates)),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Estimated people: %{customdata[0]:,}<br>"
        "Rate: %{customdata[1]}% of population"
        "<extra></extra>"
    ),
))

# ── Layout ───────────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor="white",
    geo=dict(
        scope="world",
        resolution=50,
        center=dict(lat=-41.5, lon=173.5),
        projection_scale=14,
        showland=True,
        landcolor="#F0EDE8",
        showocean=True,
        oceancolor="#EAF2F8",
        showlakes=False,
        showrivers=False,
        showcoastlines=True,
        coastlinecolor="#CCCCCC",
        coastlinewidth=0.8,
        showframe=False,
        bgcolor="white",
    ),
    margin=dict(l=0, r=0, t=110, b=40),
    title=dict(
        text=(
            "<b>Severe housing deprivation across New Zealand</b><br>"
            "<span style='font-size:11px; color:#6B6B6B;'>"
            "<i>Estimated number of people severely housing deprived, by region — 2023 Census</i>"
            "</span>"
        ),
        x=0.03,
        xanchor="left",
        y=0.98,
        yanchor="top",
        font=dict(size=16, color="#171717", family="Georgia, serif"),
    ),
    shapes=[
        dict(
            type="line",
            xref="paper", yref="paper",
            x0=0.03, x1=0.97,
            y0=0.965, y1=0.965,
            line=dict(color="#E3120B", width=2.5),
        )
    ],
    annotations=[
        dict(
            text="Source: Stats NZ, 2023 Census Severe Housing Deprivation Estimates. Total: 112,496 people (2.3% of population).",
            xref="paper", yref="paper",
            x=0.03, y=-0.04,
            showarrow=False,
            font=dict(size=9, color="#6B6B6B", family="Georgia, serif"),
            align="left",
        )
    ],
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#E3120B",
        font_size=12,
        font_family="Georgia, serif",
    ),
)

fig.write_html(
    "nz_homelessness_map.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"displayModeBar": False},
)

print("Map saved → nz_homelessness_map.html")
