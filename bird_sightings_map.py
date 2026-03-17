"""
NZ Bird Sightings Map
----------------------
Plots every individual bird sighting as a dot on a NZ map,
coloured by bird order (type of bird).
Data sourced from nz_bird_occurrences.csv (GBIF API).
"""

import csv
import plotly.graph_objects as go

# ── Colour map by bird order ──────────────────────────────────────────────────
ORDER_COLOURS = {
    "Passeriformes":    "#3A5C45",  # songbirds — dark green
    "Charadriiformes":  "#5A7D66",  # waders/gulls — mid green
    "Anseriformes":     "#8FAF8A",  # ducks/geese — pale green
    "Gruiformes":       "#B8883A",  # rails (Pukeko) — gold
    "Sphenisciformes":  "#006BA2",  # penguins — blue
    "Procellariiformes":"#7EB8F7",  # seabirds/albatross — light blue
    "Psittaciformes":   "#E3120B",  # parrots/kea — red
    "Apterygiformes":   "#1E3A2A",  # kiwi — very dark green
    "Accipitriformes":  "#C4A35A",  # hawks/eagles — tan
    "Pelecaniformes":   "#A0856C",  # herons/spoonbills — brown
    "Falconiformes":    "#D4845A",  # falcons — orange
    "Podicipediformes": "#9BB8A0",  # grebes — sage
}
DEFAULT_COLOUR = "#CCCCCC"

# ── Load occurrence data ──────────────────────────────────────────────────────
with open("nz_bird_occurrences.csv", newline="", encoding="utf-8") as f:
    rows = [r for r in csv.DictReader(f)
            if r["decimalLatitude"] and r["decimalLongitude"]]

# Group by order
from collections import defaultdict
order_groups = defaultdict(lambda: {"lats": [], "lons": [], "names": [], "species": []})

for row in rows:
    order = row["order"] or "Unknown"
    common = row.get("vernacularName", "").strip() or row["species"]
    order_groups[order]["lats"].append(float(row["decimalLatitude"]))
    order_groups[order]["lons"].append(float(row["decimalLongitude"]))
    order_groups[order]["names"].append(common)
    order_groups[order]["species"].append(row["species"])

# Friendly order names for legend
ORDER_LABELS = {
    "Passeriformes":    "Songbirds",
    "Charadriiformes":  "Waders & Gulls",
    "Anseriformes":     "Ducks & Geese",
    "Gruiformes":       "Rails (Pūkeko etc.)",
    "Sphenisciformes":  "Penguins",
    "Procellariiformes":"Seabirds & Albatross",
    "Psittaciformes":   "Parrots & Kea",
    "Apterygiformes":   "Kiwi",
    "Accipitriformes":  "Hawks & Eagles",
    "Pelecaniformes":   "Herons & Spoonbills",
    "Falconiformes":    "Falcons",
    "Podicipediformes": "Grebes",
}

# ── Build map ────────────────────────────────────────────────────────────────
fig = go.Figure()

for order, data in sorted(order_groups.items(), key=lambda x: -len(x[1]["lats"])):
    colour = ORDER_COLOURS.get(order, DEFAULT_COLOUR)
    label  = ORDER_LABELS.get(order, order)
    count  = len(data["lats"])

    fig.add_trace(go.Scattergeo(
        lat=data["lats"],
        lon=data["lons"],
        mode="markers",
        name=f"{label} ({count})",
        marker=dict(
            size=7,
            color=colour,
            opacity=0.75,
            line=dict(color="white", width=0.5),
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Order: " + label + "<br>"
            "Lat: %{lat:.3f}, Lon: %{lon:.3f}"
            "<extra></extra>"
        ),
        customdata=list(zip(data["names"])),
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
            "<b>Bird sightings across New Zealand</b><br>"
            "<span style='font-size:11px;color:#6B6B6B;'>"
            "<i>500 individual sightings plotted by location and bird type, via GBIF, 2026</i>"
            "</span>"
        ),
        x=0.02, xanchor="left",
        y=0.98, yanchor="top",
        font=dict(size=15, color="#171717", family="Georgia, serif"),
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#E0E0E0",
        borderwidth=1,
        font=dict(size=9.5, color="#171717", family="Georgia, serif"),
        x=0.01, y=0.35,
        xanchor="left",
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
    "nz_bird_sightings_map.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"displayModeBar": False, "scrollZoom": False},
)
print("Map saved → nz_bird_sightings_map.html")
