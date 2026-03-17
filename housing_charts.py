"""
NZ Housing Story Charts
-----------------------
Queries MySQL and generates three Plotly charts for the website:
  1. OCR interest rate over time
  2. House prices by region over time
  3. Housing deprivation vs house price by region
"""

import mysql.connector
import plotly.graph_objects as go
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

# Colour palette matching New Harvest website
GREEN_DARK  = "#1E3A2A"
GREEN_MID   = "#3A5C45"
GREEN_LT    = "#5A7D66"
GREEN_PALE  = "#8FAF8A"
GREEN_GHOST = "#C8E6C9"
GOLD        = "#B8883A"
DARK        = "#171717"
GREY        = "#6B6B6B"
LINE_COL    = "#E0E0E0"
BG          = "#FFFFFF"

REGION_COLOURS = {
    "Auckland":      GREEN_DARK,
    "Wellington":    GREEN_MID,
    "Canterbury":    GREEN_LT,
    "Waikato":       GREEN_PALE,
    "Bay of Plenty": GOLD,
    "Otago":         "#7EB8F7",
    "Northland":     "#B8883A",
    "Hawke's Bay":   "#A0856C",
}

conn = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor()

def base_layout(title_text, subtitle_text, source_text):
    return dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Georgia, serif", color=DARK),
        title=dict(
            text=(
                f"<b>{title_text}</b><br>"
                f"<span style='font-size:11px;color:{GREY};'><i>{subtitle_text}</i></span>"
            ),
            x=0.02, xanchor="left", y=0.97, yanchor="top",
            font=dict(size=15, color=DARK),
        ),
        shapes=[],
        annotations=[dict(
            text=source_text,
            xref="paper", yref="paper",
            x=0.02, y=-0.08,
            showarrow=False,
            font=dict(size=8.5, color=GREY, family="Georgia, serif"),
        )],
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=10, color=DARK),
        ),
        margin=dict(l=60, r=30, t=100, b=60),
        hoverlabel=dict(
            bgcolor=BG, bordercolor=GREEN_MID,
            font_size=12, font_family="Georgia, serif",
        ),
    )

# ── Chart 1: OCR Rate Over Time ───────────────────────────────────────────────
cursor.execute("SELECT date, rate FROM ocr_rates ORDER BY date")
ocr_rows = cursor.fetchall()
ocr_dates = [r[0] for r in ocr_rows]
ocr_rates = [float(r[1]) for r in ocr_rows]

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=ocr_dates, y=ocr_rates,
    mode="lines",
    line=dict(color=GREEN_MID, width=2.5),
    fill="tozeroy",
    fillcolor="rgba(58, 92, 69, 0.12)",
    name="OCR %",
    hovertemplate="<b>%{x}</b><br>OCR: %{y}%<extra></extra>",
))

# Annotate key events
annotations = [
    dict(x="2020-03-16", y=0.25, text="COVID cut<br>to 0.25%", ax=40, ay=-40),
    dict(x="2021-10-06", y=0.50, text="Rate hikes<br>begin", ax=50, ay=-50),
    dict(x="2023-05-24", y=5.25, text="Peak:<br>5.5%", ax=40, ay=-30),
]
for a in annotations:
    a.update(dict(
        xref="x", yref="y", showarrow=True,
        arrowhead=2, arrowcolor=GREY, arrowwidth=1,
        font=dict(size=8.5, color=GREY, family="Georgia, serif"),
        bgcolor="white", borderpad=3,
    ))

layout1 = base_layout(
    "New Zealand Official Cash Rate, 2015–2025",
    "Reserve Bank of New Zealand policy rate, percent",
    "Source: Reserve Bank of New Zealand (RBNZ)"
)
layout1.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, ticksuffix="%",
               tickfont=dict(size=10, color=GREY)),
    annotations=layout1.get("annotations", []) + annotations,
))
fig1.update_layout(**layout1)

fig1.write_html("chart_ocr.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
print("Saved → chart_ocr.html")

# ── Chart 2: House Prices by Region ──────────────────────────────────────────
cursor.execute("""
    SELECT date, region, median_price
    FROM house_prices
    ORDER BY date, region
""")
price_rows = cursor.fetchall()

regions = list(REGION_COLOURS.keys())
region_data = {r: {"dates": [], "prices": []} for r in regions}
for date, region, price in price_rows:
    if region in region_data:
        region_data[region]["dates"].append(date)
        region_data[region]["prices"].append(price)

fig2 = go.Figure()
for region, colour in REGION_COLOURS.items():
    d = region_data[region]
    fig2.add_trace(go.Scatter(
        x=d["dates"], y=d["prices"],
        mode="lines+markers",
        name=region,
        line=dict(color=colour, width=2),
        marker=dict(size=5),
        hovertemplate=f"<b>{region}</b><br>%{{x}}<br>Median: $%{{y:,}}<extra></extra>",
    ))

layout2 = base_layout(
    "NZ Median House Prices by Region, 2015–2024",
    "Annual median sale price in NZD, selected regions",
    "Source: REINZ / Stats NZ regional estimates"
)
layout2.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, tickprefix="$", tickformat=",",
               tickfont=dict(size=10, color=GREY)),
))
fig2.update_layout(**layout2)

fig2.write_html("chart_house_prices.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
print("Saved → chart_house_prices.html")

# ── Chart 3: Deprivation vs House Price (cross-reference) ────────────────────
cursor.execute("""
    SELECT hd.region, hd.estimated_people, hd.rate_pct,
           hp.median_price
    FROM housing_deprivation hd
    JOIN house_prices hp
      ON hd.region = hp.region
     AND hp.date = '2024-01-01'
    ORDER BY hp.median_price DESC
""")
cross_rows = cursor.fetchall()

cr_regions  = [r[0] for r in cross_rows]
cr_deprived = [r[1] for r in cross_rows]
cr_rates    = [float(r[2]) for r in cross_rows]
cr_prices   = [r[3] for r in cross_rows]

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=cr_prices,
    y=cr_rates,
    mode="markers+text",
    marker=dict(
        size=[d / 800 for d in cr_deprived],
        color=cr_prices,
        colorscale=[
            [0.0, GREEN_GHOST],
            [0.5, GREEN_LT],
            [1.0, GREEN_DARK],
        ],
        line=dict(color="white", width=1),
        opacity=0.85,
    ),
    text=cr_regions,
    textposition="top center",
    textfont=dict(size=8.5, color=DARK),
    hovertemplate=(
        "<b>%{text}</b><br>"
        "Median price: $%{x:,}<br>"
        "Deprivation rate: %{y}%<br>"
        "<extra></extra>"
    ),
))

layout3 = base_layout(
    "House Price vs Housing Deprivation Rate by Region",
    "Bubble size = number of people severely housing deprived (2023). Median price as of 2024.",
    "Source: REINZ / Stats NZ 2023 Census Severe Housing Deprivation Estimates"
)
layout3.update(dict(
    xaxis=dict(
        title=dict(text="Median House Price (NZD)", font=dict(size=10, color=GREY)),
        showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
        tickprefix="$", tickformat=",", tickfont=dict(size=10, color=GREY),
    ),
    yaxis=dict(
        title=dict(text="Deprivation Rate (%)", font=dict(size=10, color=GREY)),
        showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
        ticksuffix="%", tickfont=dict(size=10, color=GREY),
    ),
    margin=dict(l=60, r=30, t=100, b=80),
))
fig3.update_layout(**layout3)

fig3.write_html("chart_cross_reference.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
print("Saved → chart_cross_reference.html")

cursor.close()
conn.close()
print("\nAll charts generated from MySQL.")
