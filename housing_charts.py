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

FONT_IMPORT = (
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600'
    '&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300'
    '&display=swap" rel="stylesheet">\n'
)

def finalize(filepath, source_text):
    """Prepend Google Fonts and append source credit below the chart."""
    with open(filepath, "r") as f:
        content = f.read()
    source_html = (
        f'<p style="margin:6px 0 0 4px; font-size:8.5px; color:#6B6B6B; '
        f'font-family:Inter,sans-serif;">{source_text}</p>\n'
    )
    with open(filepath, "w") as f:
        f.write(FONT_IMPORT + content + source_html)


def finalize_with_legend(filepath, source_text, region_colours):
    """Like finalize() but appends a custom HTML legend with click-to-filter."""
    with open(filepath, "r") as f:
        content = f.read()

    items_html = "".join([
        f'<span class="leg-item" data-idx="{i}" style="display:flex;align-items:center;'
        f'gap:5px;cursor:pointer;user-select:none;padding:2px 4px;border-radius:3px;">'
        f'<span style="width:22px;height:3px;background:{colour};display:inline-block;'
        f'border-radius:2px;flex-shrink:0;"></span>'
        f'<span style="font-size:9px;color:#171717;white-space:nowrap;">{region}</span>'
        f'</span>'
        for i, (region, colour) in enumerate(region_colours.items())
    ])

    legend_html = (
        f'<div style="display:flex;flex-wrap:wrap;gap:6px 14px;padding:8px 8px 4px;'
        f'border-top:1px solid #E0E0E0;font-family:Inter,sans-serif;">'
        f'{items_html}</div>\n'
        f'<script>(function(){{'
        f'var items=document.querySelectorAll(".leg-item");'
        f'var hidden={{}};'
        f'items.forEach(function(el){{'
        f'el.addEventListener("click",function(){{'
        f'var idx=parseInt(this.dataset.idx);'
        f'hidden[idx]=!hidden[idx];'
        f'var vis=[];'
        f'items.forEach(function(_,i){{vis.push(hidden[i]?"legendonly":true);}});'
        f'var div=document.querySelector(".plotly-graph-div");'
        f'Plotly.restyle(div,"visible",vis);'
        f'this.style.opacity=hidden[idx]?"0.35":"1";'
        f'}});}});}})();</script>\n'
    )

    source_html = (
        f'<p style="margin:4px 0 0 4px; font-size:8.5px; color:#6B6B6B; '
        f'font-family:Inter,sans-serif;">{source_text}</p>\n'
    )
    with open(filepath, "w") as f:
        f.write(FONT_IMPORT + content + legend_html + source_html)

# Colour palette
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
    "Northland":     "#9B7BB8",
    "Hawke's Bay":   "#A0856C",
}

conn = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
)
cursor = conn.cursor()

def base_layout(title_text, subtitle_text):
    return dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=DARK),
        title=dict(
            text=(
                f"<b>{title_text}</b><br>"
                f"<span style='font-size:11px;color:{GREY};'><i>{subtitle_text}</i></span>"
            ),
            x=0.02, xanchor="left", y=0.95, yanchor="top",
            font=dict(size=15, color=DARK),
        ),
        shapes=[],
        annotations=[],
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(size=10, color=DARK),
            itemclick=False,
            itemdoubleclick=False,
        ),
        height=360,
        margin=dict(l=60, r=30, t=120, b=50),
        hoverlabel=dict(
            bgcolor=BG, bordercolor=GREEN_MID,
            font_size=12, font_family="Inter, sans-serif",
        ),
    )

# ── Chart 1: OCR Rate Over Time ───────────────────────────────────────────────
cursor.execute("SELECT date, rate FROM ocr_rates ORDER BY date")
ocr_rows  = cursor.fetchall()
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

layout1 = base_layout(
    "New Zealand Official Cash Rate, 2015–2025",
    "Reserve Bank of New Zealand policy rate, percent",
)
layout1.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, ticksuffix="%",
               tickfont=dict(size=10, color=GREY)),
))
fig1.update_layout(**layout1)

fig1.write_html("chart_ocr.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("chart_ocr.html", "Source: Reserve Bank of New Zealand (RBNZ)")
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
    "NZ Median House Prices by Region, 2015–2025",
    "Annual median sale price in NZD, selected regions",
)
layout2.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, tickprefix="$", tickformat=",",
               tickfont=dict(size=10, color=GREY),
               range=[0, 1600000], dtick=250000),
    showlegend=False,
    margin=dict(l=60, r=30, t=120, b=50),
))
fig2.update_layout(**layout2)

fig2.write_html("chart_house_prices.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize_with_legend("chart_house_prices.html", "Source: REINZ / Stats NZ regional estimates",
                     REGION_COLOURS)
print("Saved → chart_house_prices.html")

# ── Chart 3: Rental Prices by Region ─────────────────────────────────────────
cursor.execute("""
    SELECT date, region, median_weekly_rent
    FROM rental_prices
    ORDER BY date, region
""")
rental_rows = cursor.fetchall()

rental_data = {r: {"dates": [], "rents": []} for r in regions}
for date, region, rent in rental_rows:
    if region in rental_data:
        rental_data[region]["dates"].append(date)
        rental_data[region]["rents"].append(rent)

fig3 = go.Figure()
for region, colour in REGION_COLOURS.items():
    d = rental_data[region]
    fig3.add_trace(go.Scatter(
        x=d["dates"], y=d["rents"],
        mode="lines+markers",
        name=region,
        line=dict(color=colour, width=2),
        marker=dict(size=5),
        hovertemplate=f"<b>{region}</b><br>%{{x}}<br>Median rent: $%{{y}}/wk<extra></extra>",
    ))

layout3 = base_layout(
    "NZ Median Weekly Rent by Region, 2015–2025",
    "Median weekly rent in NZD from new tenancy bonds, selected regions",
)
layout3.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, tickprefix="$", ticksuffix="/wk",
               tickfont=dict(size=10, color=GREY),
               range=[200, 800], dtick=50),
    showlegend=False,
    margin=dict(l=60, r=30, t=120, b=50),
))
fig3.update_layout(**layout3)

fig3.write_html("chart_rentals.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize_with_legend("chart_rentals.html", "Source: MBIE Tenancy Services bond data",
                     REGION_COLOURS)
print("Saved → chart_rentals.html")

# ── Chart 4: Deprivation vs House Price (cross-reference) ────────────────────
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

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
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
        "Deprivation rate: %{y}<br>"
        "<extra></extra>"
    ),
))

layout4 = base_layout(
    "House Price vs Housing Deprivation Rate by Region",
    "Bubble size = number of people severely housing deprived (2023). Median price as of 2024.",
)
layout4.update(dict(
    xaxis=dict(
        title=dict(text="Median House Price (NZD)", font=dict(size=10, color=GREY)),
        showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
        tickprefix="$", tickformat=",", tickfont=dict(size=10, color=GREY),
    ),
    yaxis=dict(
        title=dict(text="Deprivation Rate (%)", font=dict(size=10, color=GREY)),
        showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
        ticksuffix="%", tickfont=dict(size=10, color=GREY),
        range=[0.5, 5.5],
    ),
    margin=dict(l=60, r=30, t=120, b=60),
))
layout4.update(dict(dragmode=False))
fig4.update_layout(**layout4)

fig4.write_html("chart_cross_reference.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False, "scrollZoom": False})
finalize("chart_cross_reference.html",
         "Source: REINZ / Stats NZ 2023 Census Severe Housing Deprivation Estimates")
print("Saved → chart_cross_reference.html")

# ── Chart 5: Standalone Deprivation Bar ──────────────────────────────────────
cursor.execute("""
    SELECT region, rate_pct, estimated_people
    FROM housing_deprivation
    ORDER BY rate_pct ASC
""")
dep_rows = cursor.fetchall()

dep_regions = [r[0] for r in dep_rows]
dep_rates   = [float(r[1]) for r in dep_rows]
dep_people  = [r[2] for r in dep_rows]

dep_colours = [GOLD if rate >= 3.0 else GREEN_MID for rate in dep_rates]

fig5 = go.Figure()
fig5.add_trace(go.Bar(
    x=dep_rates,
    y=dep_regions,
    orientation="h",
    marker_color=dep_colours,
    customdata=dep_people,
    text=[f"{r}%" for r in dep_rates],
    textposition="outside",
    textfont=dict(size=10, color=GREY),
    cliponaxis=False,
    hovertemplate=(
        "<b>%{y}</b><br>"
        "Deprivation rate: %{x}%<br>"
        "Est. people: %{customdata:,}<extra></extra>"
    ),
))

layout5 = base_layout(
    "Severe Housing Deprivation by Region",
    "Estimated proportion of population severely housing deprived, 2023 Census",
)
layout5.update(dict(
    xaxis=dict(
        showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
        ticksuffix="%", tickfont=dict(size=10, color=GREY), range=[0, 6],
    ),
    yaxis=dict(
        showgrid=False, zeroline=False, showline=False,
        tickfont=dict(size=10, color=DARK),
    ),
    margin=dict(l=140, r=60, t=120, b=50),
    bargap=0.3,
    height=360,
))
fig5.update_layout(**layout5)

fig5.write_html("chart_deprivation_bar.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("chart_deprivation_bar.html", "Source: Stats NZ 2023 Census Severe Housing Deprivation Estimates")
print("Saved → chart_deprivation_bar.html")

# ── Chart 6: House Prices 2022–2025 (Recovery focus) ─────────────────────────
cursor.execute("""
    SELECT date, region, median_price
    FROM house_prices
    WHERE date >= '2022-01-01'
    ORDER BY date, region
""")
recovery_rows = cursor.fetchall()

recovery_data = {r: {"dates": [], "prices": []} for r in regions}
for date, region, price in recovery_rows:
    if region in recovery_data:
        recovery_data[region]["dates"].append(date)
        recovery_data[region]["prices"].append(price)

fig6 = go.Figure()
for region, colour in REGION_COLOURS.items():
    d = recovery_data[region]
    fig6.add_trace(go.Scatter(
        x=d["dates"], y=d["prices"],
        mode="lines+markers",
        name=region,
        line=dict(color=colour, width=2),
        marker=dict(size=6),
        hovertemplate=f"<b>{region}</b><br>%{{x}}<br>Median: $%{{y:,}}<extra></extra>",
    ))

layout6 = base_layout(
    "NZ House Prices: The Correction, 2022–2025",
    "Median sale price in NZD — from peak to emerging recovery",
)
layout6.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, tickprefix="$", tickformat=",",
               tickfont=dict(size=10, color=GREY),
               range=[400000, 1400000], dtick=250000),
    showlegend=False,
    margin=dict(l=60, r=30, t=120, b=50),
))
fig6.update_layout(**layout6)

fig6.write_html("chart_prices_recovery.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize_with_legend("chart_prices_recovery.html", "Source: REINZ / Stats NZ regional estimates",
                     REGION_COLOURS)
print("Saved → chart_prices_recovery.html")

# ── Chart 7: Rental Prices 2022–2025 (Plateau focus) ─────────────────────────
cursor.execute("""
    SELECT date, region, median_weekly_rent
    FROM rental_prices
    WHERE date >= '2022-01-01'
    ORDER BY date, region
""")
plateau_rows = cursor.fetchall()

plateau_data = {r: {"dates": [], "rents": []} for r in regions}
for date, region, rent in plateau_rows:
    if region in plateau_data:
        plateau_data[region]["dates"].append(date)
        plateau_data[region]["rents"].append(rent)

fig7 = go.Figure()
for region, colour in REGION_COLOURS.items():
    d = plateau_data[region]
    fig7.add_trace(go.Scatter(
        x=d["dates"], y=d["rents"],
        mode="lines+markers",
        name=region,
        line=dict(color=colour, width=2),
        marker=dict(size=6),
        hovertemplate=f"<b>{region}</b><br>%{{x}}<br>Median rent: $%{{y}}/wk<extra></extra>",
    ))

layout7 = base_layout(
    "NZ Weekly Rents: Growth Slowing, 2022–2025",
    "Median weekly rent in NZD — signs of stabilisation after years of rapid growth",
)
layout7.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False,
               showline=False, tickprefix="$", ticksuffix="/wk",
               tickfont=dict(size=10, color=GREY),
               range=[400, 800], dtick=50),
    showlegend=False,
    margin=dict(l=60, r=30, t=120, b=50),
))
fig7.update_layout(**layout7)

fig7.write_html("chart_rentals_plateau.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize_with_legend("chart_rentals_plateau.html", "Source: MBIE Tenancy Services bond data",
                     REGION_COLOURS)
print("Saved → chart_rentals_plateau.html")

# ── Chart 8: Wellington Median House Prices 2023–2026 (bar chart) ────────────
cursor.execute("""
    SELECT YEAR(date), median_price FROM house_prices
    WHERE region = 'Wellington' AND date >= '2022-01-01'
    ORDER BY date
""")
wel_rows = cursor.fetchall()

wel_years  = [str(r[0]) for r in wel_rows]
wel_prices = [r[1] for r in wel_rows]
wel_dates  = [r[0] for r in wel_rows]

fig8 = go.Figure()
fig8.add_trace(go.Scatter(
    x=wel_years,
    y=wel_prices,
    mode="lines+markers+text",
    line=dict(color=GREEN_DARK, width=2.5),
    marker=dict(size=10, color=[GREEN_DARK] * (len(wel_years) - 1) + [GOLD],
                line=dict(color="white", width=2)),
    text=[f"${p:,}" for p in wel_prices],
    textposition="top center",
    textfont=dict(size=10, color=GREY),
    hovertemplate="<b>Wellington %{x}</b><br>Median: $%{y:,}<extra></extra>",
    showlegend=False,
))

layout8 = base_layout(
    "Wellington Median House Price, 2022–2026",
    "Prices correcting from the 2022 peak — a trend playing out nationally",
)
layout8.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=12, color=DARK)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickprefix="$", tickformat=",", tickfont=dict(size=10, color=GREY),
               range=[600000, 1050000], dtick=100000),
    margin=dict(l=70, r=30, t=120, b=50),
))
fig8.update_layout(**layout8)

fig8.write_html("chart_wellington_recovery.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("chart_wellington_recovery.html", "Source: REINZ regional estimates")
print("Saved → chart_wellington_recovery.html")

cursor.close()
conn.close()
print("\nAll charts generated from MySQL.")
