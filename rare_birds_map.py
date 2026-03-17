"""
NZ Rare & Endemic Bird Sightings Map
--------------------------------------
Maps 15 rare/endemic NZ species using Māori names.
Data from GBIF via fetch_rare_birds.py
"""

import csv
from collections import defaultdict
import plotly.graph_objects as go

# Colour per species — all within the green/earth palette
SPECIES_COLOURS = {
    "Kea":       "#E3120B",  # red — iconic mountain parrot
    "Kiwi":      "#1E3A2A",  # very dark green
    "Ruru":      "#4A3728",  # dark brown — nocturnal owl
    "Kākāriki":  "#5A9E3A",  # bright green — parakeet
    "Korimako":  "#3A5C45",  # forest green — bellbird
    "Whio":      "#006BA2",  # blue — blue duck
    "Kārearea":  "#B8883A",  # gold — falcon
    "Takahē":    "#7B3FA0",  # purple — very rare
    "Miromiro":  "#5A7D66",  # mid green — tomtit
    "Pōpokotea": "#8FAF8A",  # pale green — whitehead
    "Kuaka":     "#A0856C",  # warm brown — godwit
    "Hoiho":     "#F0A500",  # amber/yellow — yellow-eyed penguin
    "Kororā":    "#4472C4",  # mid blue — little blue penguin
    "Tieke":     "#C0392B",  # dark red — saddleback
    "Kōtuku":    "#BDC3C7",  # white/silver — white heron
}

# Load data, group by Māori name
with open("nz_rare_birds.csv", newline="", encoding="utf-8") as f:
    rows = [r for r in csv.DictReader(f)
            if r["decimalLatitude"] and r["decimalLongitude"]]

groups = defaultdict(lambda: {"lats": [], "lons": [], "regions": []})
for row in rows:
    name = row["maoriName"]
    groups[name]["lats"].append(float(row["decimalLatitude"]))
    groups[name]["lons"].append(float(row["decimalLongitude"]))
    groups[name]["regions"].append(row.get("stateProvince", "") or "Unknown")

# ── Build map ────────────────────────────────────────────────────────────────
fig = go.Figure()

for name, data in sorted(groups.items(), key=lambda x: x[0]):
    colour = SPECIES_COLOURS.get(name, "#999999")
    count  = len(data["lats"])

    fig.add_trace(go.Scattergeo(
        lat=data["lats"],
        lon=data["lons"],
        mode="markers",
        name=f"{name} ({count})",
        marker=dict(
            size=7,
            color=colour,
            opacity=0.8,
            line=dict(color="white", width=0.5),
        ),
        customdata=list(zip(data["regions"])),
        hovertemplate=(
            f"<b>{name}</b><br>"
            "Region: %{customdata[0]}<br>"
            "Lat: %{lat:.3f}, Lon: %{lon:.3f}"
            "<extra></extra>"
        ),
    ))

# ── Layout ───────────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor="white",
    height=580,
    geo=dict(
        resolution=50,
        showland=True,
        landcolor="#F0EDE8",
        showocean=True,
        oceancolor="#EAF2F8",
        showlakes=False,
        showrivers=False,
        showcoastlines=True,
        coastlinecolor="#BBBBBB",
        coastlinewidth=0.8,
        showframe=False,
        bgcolor="white",
        lataxis=dict(range=[-48, -33], showgrid=False),
        lonaxis=dict(range=[165, 180], showgrid=False),
    ),
    margin=dict(l=0, r=0, t=100, b=30),
    title=dict(
        text=(
            "<b>Rare & endemic bird sightings across Aotearoa</b><br>"
            "<span style='font-size:11px;color:#6B6B6B;'>"
            "<i>1,800 sightings of 15 native species by Māori name, via GBIF</i>"
            "</span>"
        ),
        x=0.02, xanchor="left",
        y=0.98, yanchor="top",
        font=dict(size=15, color="#171717", family="Georgia, serif"),
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#E0E0E0",
        borderwidth=1,
        font=dict(size=9.5, color="#171717", family="Georgia, serif"),
        x=0.01, y=0.42,
        xanchor="left",
        tracegroupgap=2,
    ),
    annotations=[dict(
        text="Source: Global Biodiversity Information Facility (GBIF) · iNaturalist",
        xref="paper", yref="paper",
        x=0.02, y=-0.03,
        showarrow=False,
        font=dict(size=8.5, color="#6B6B6B", family="Georgia, serif"),
    )],
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#3A5C45",
        font_size=12,
        font_family="Georgia, serif",
    ),
)

fig.write_html(
    "nz_rare_birds_map.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"displayModeBar": False, "scrollZoom": False},
)
print("Map saved → nz_rare_birds_map.html")
