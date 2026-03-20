"""
NZ Kiwi Sightings Map
----------------------
Maps North Island Brown Kiwi and Southern Brown Kiwi sightings
separately using GBIF data.
"""

import csv
import plotly.graph_objects as go

SPECIES_CONFIG = {
    "Apteryx mantelli":            ("North Island Brown Kiwi", "#1E3A2A"),  # dark green
    "Apteryx australis":           ("Southern Brown Kiwi",     "#8B6914"),  # dark yellow
}

# Filters to remove bad data (captive/museum records with wrong coordinates)
# Applied per-species: Southern Brown Kiwi shouldn't appear north of -40 (except Zealandia);
# North Island Brown Kiwi shouldn't appear south of -42 (South Island).
MIN_YEAR = 2000
MAX_LAT = {
    "Apteryx australis": -40.0,  # South Island species — keep Zealandia (~-40.84) but drop Auckland/Northland
    "Apteryx mantelli":  -34.0,  # North Island species — no northern cutoff needed
}
MIN_LAT = {
    "Apteryx australis": -48.0,  # no southern cutoff
    "Apteryx mantelli":  -42.0,  # exclude any stray South Island records
}

# Load kiwi sightings only, keyed by scientific name
groups = {name: {"lats": [], "lons": [], "regions": [], "years": []} for name in SPECIES_CONFIG}

with open("nz_rare_birds.csv", newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if not row["decimalLatitude"] or not row["decimalLongitude"]:
            continue
        if row["species"] not in groups:
            continue
        lat  = float(row["decimalLatitude"])
        year = int(row["year"]) if row["year"] else 0
        if year < MIN_YEAR:
            continue
        if lat > MAX_LAT[row["species"]] or lat < MIN_LAT[row["species"]]:
            continue
        groups[row["species"]]["lats"].append(lat)
        groups[row["species"]]["lons"].append(float(row["decimalLongitude"]))
        groups[row["species"]]["regions"].append(row.get("stateProvince", "") or "Unknown")
        groups[row["species"]]["years"].append(str(year) if year else "Unknown")

# ── Build map ────────────────────────────────────────────────────────────────
fig = go.Figure()

for species_name, (label, colour) in SPECIES_CONFIG.items():
    data  = groups[species_name]
    total = len(data["lats"])

    fig.add_trace(go.Scattergeo(
        lat=data["lats"],
        lon=data["lons"],
        mode="markers",
        name=f"{label} ({total:,} sightings)",
        marker=dict(
            size=7,
            color=colour,
            opacity=0.8,
            line=dict(color="white", width=0.5),
        ),
        customdata=list(zip(data["regions"], data["years"])),
        hovertemplate=(
            f"<b>{label}</b><br>"
            "Region: %{customdata[0]}<br>"
            "Year: %{customdata[1]}"
            "<extra></extra>"
        ),
    ))

# ── Layout ───────────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor="white",
    height=500,
    dragmode=False,
    geo=dict(
        resolution=50,
        showland=True,
        landcolor="#F0EDE8",
        showocean=True,
        oceancolor="white",
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
    margin=dict(l=0, r=0, t=80, b=0),
    title=dict(
        text=(
            "<b>Where are New Zealand's Kiwi found?</b><br>"
            "<span style='font-size:11px;color:#6B6B6B;'>"
            "<i>Sightings of the North Island Brown Kiwi and Southern Brown Kiwi, "
            "mapped by GPS coordinates via GBIF</i>"
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
        x=0.01, y=0.30,
        xanchor="left",
    ),
    annotations=[dict(
        text="Source: Global Biodiversity Information Facility (GBIF) · iNaturalist",
        xref="paper", yref="paper",
        x=0.02, y=0.01,
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
