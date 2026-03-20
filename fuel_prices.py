"""
NZ Fuel Prices — Iran War Impact
---------------------------------
Reads MBIE weekly-table.csv and generates an annotated dual-axis chart:
  - Left axis:  Regular 91 adjusted retail price (NZD c/L)
  - Right axis: Dubai crude price (USD/bbl)
Annotated with war start (28 Feb 2026) and Hormuz closure (20 Mar 2026).
Output: chart_fuel_prices.html (HTML fragment for embedding)
"""

import io
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Brand colours ─────────────────────────────────────────────────────────────
GREEN_DARK = "#1E3A2A"
GREEN_MID  = "#3A5C45"
GOLD       = "#B8883A"
RED        = "#C0392B"
DARK       = "#171717"
GREY       = "#6B6B6B"
BG         = "#FFFFFF"
LINE_COL   = "#E0E0E0"

FONT_IMPORT = (
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600'
    '&display=swap" rel="stylesheet">\n'
)

# ── Key event dates ────────────────────────────────────────────────────────────
WAR_START     = "2026-02-28"
HORMUZ_CLOSED = "2026-03-01"

# ── Load data ──────────────────────────────────────────────────────────────────
MBIE_URL = "https://www.mbie.govt.nz/assets/Data-Files/Energy/Weekly-fuel-price-monitoring/weekly-table.csv"
print("Fetching latest MBIE fuel price data...")
response = requests.get(MBIE_URL, timeout=30)
response.raise_for_status()
df = pd.read_csv(io.StringIO(response.text))
df["Date"] = pd.to_datetime(df["Date"])

# Show last ~20 weeks for context (from ~Nov 2025)
cutoff = pd.Timestamp("2025-11-01")
df = df[df["Date"] >= cutoff].copy()

# Regular Petrol adjusted retail price (NZD c/L → NZD $/L)
petrol = (
    df[(df["Fuel"] == "Regular Petrol") & (df["Variable"] == "Adjusted retail price")]
    .groupby("Date")["Value"].first()
    .div(100)  # convert cents to dollars
    .reset_index()
    .rename(columns={"Value": "price_nzd"})
    .sort_values("Date")
)

# Dubai crude price in USD/bbl
crude = (
    df[(df["Fuel"].isna() | (df["Fuel"] == "NA")) & (df["Variable"] == "Dubai crude price") & (df["Unit"] == "USD/bbl")]
    .groupby("Date")["Value"].first()
    .reset_index()
    .rename(columns={"Value": "crude_usd"})
    .sort_values("Date")
)

# ── Build chart ────────────────────────────────────────────────────────────────
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Petrol price line (left axis)
fig.add_trace(
    go.Scatter(
        x=petrol["Date"], y=petrol["price_nzd"],
        name="Regular 91 (NZD $/L)",
        line=dict(color=GREEN_MID, width=2.5),
        mode="lines+markers",
        marker=dict(size=5, color=GREEN_MID),
        hovertemplate="%{x|%d %b %Y}<br>$%{y:.2f}/L<extra></extra>",
    ),
    secondary_y=False,
)

# Dubai crude line (right axis)
fig.add_trace(
    go.Scatter(
        x=crude["Date"], y=crude["crude_usd"],
        name="Dubai crude (USD/bbl)",
        line=dict(color=GOLD, width=2, dash="dot"),
        mode="lines+markers",
        marker=dict(size=5, color=GOLD),
        hovertemplate="%{x|%d %b %Y}<br>$%{y:.0f}/bbl<extra></extra>",
    ),
    secondary_y=True,
)

# ── Shaded region: war start → Hormuz closure ──────────────────────────────────
fig.add_vrect(
    x0=WAR_START, x1=HORMUZ_CLOSED,
    fillcolor="#FFF3E0", opacity=0.5,
    layer="below", line_width=0,
)

# ── Vertical lines for key events ──────────────────────────────────────────────
for xval, label, ypos in [
    (WAR_START,     "Iran War begins<br>28 Feb", 0.82),
    (HORMUZ_CLOSED, "Hormuz strait closed<br>20 Mar", 0.82),
]:
    fig.add_vline(
        x=xval, line_width=1.5,
        line_dash="dash", line_color=RED,
    )
    fig.add_annotation(
        x=xval, y=ypos, yref="paper",
        text=label,
        showarrow=False,
        font=dict(size=9, color=RED, family="Inter, sans-serif"),
        xanchor="left",
        xshift=6,
        bgcolor="rgba(255,255,255,0.85)",
        borderpad=3,
    )

# ── Price callout annotation (latest week) ─────────────────────────────────────
latest_petrol = petrol.iloc[-1]
latest_crude  = crude.iloc[-1]
fig.add_annotation(
    x=latest_petrol["Date"], y=latest_petrol["price_nzd"],
    text=f"<b>${latest_petrol['price_nzd']:.2f}/L</b>",
    showarrow=True, arrowhead=2,
    arrowcolor=GREEN_DARK, arrowwidth=1.5,
    ax=30, ay=-30,
    font=dict(size=10, color=GREEN_DARK, family="Inter, sans-serif"),
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor=GREEN_MID, borderwidth=1, borderpad=4,
)

# Crude callout
fig.add_annotation(
    x=latest_crude["Date"], y=latest_crude["crude_usd"],
    yref="y2",
    text=f"<b>${latest_crude['crude_usd']:.0f}/bbl</b>",
    showarrow=True, arrowhead=2,
    arrowcolor="#8B6914", arrowwidth=1.5,
    ax=-40, ay=-30,
    font=dict(size=10, color="#8B6914", family="Inter, sans-serif"),
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor=GOLD, borderwidth=1, borderpad=4,
)

# ── Explanation annotation (pump price lag) ────────────────────────────────────
fig.add_annotation(
    x=0.98, y=0.06, xref="paper", yref="paper",
    text=(
        "<b>Crude oil up 62%</b> since war began.<br>"
        "Pump price up 12% — fixed taxes slow<br>"
        "the pass-through. More rises likely."
    ),
    showarrow=False,
    font=dict(size=9, color=GREY, family="Inter, sans-serif"),
    align="right",
    xanchor="right",
    bgcolor="rgba(247,246,242,0.95)",
    bordercolor=LINE_COL, borderwidth=1, borderpad=6,
)

# ── Layout ─────────────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    font=dict(family="Inter, sans-serif", color=DARK),
    title=dict(
        text=(
            "<b>NZ fuel prices surge as Iran war disrupts global oil supply</b><br>"
            f"<span style='font-size:11px;color:{GREY};'>"
            "<i>Regular 91 adjusted retail price (national benchmark, NZD $/L) "
            "vs Dubai crude (USD/bbl)</i></span>"
        ),
        x=0.02, xanchor="left", y=0.97, yanchor="top",
        font=dict(size=15, color=DARK),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        font=dict(size=10, color=DARK),
        orientation="h",
        x=0.02, y=-0.12,
    ),
    margin=dict(t=90, b=60, l=60, r=70),
    hovermode="x unified",
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        tickfont=dict(size=10, color=GREY),
        tickformat="%b %Y",
        linecolor=LINE_COL,
        showline=True,
    ),
    yaxis=dict(
        title=dict(text="NZD $/L", font=dict(size=10, color=GREEN_MID)),
        tickfont=dict(size=10, color=GREEN_MID),
        showgrid=True,
        gridcolor=LINE_COL,
        zeroline=False,
        tickformat="$,.2f",
    ),
    yaxis2=dict(
        title=dict(text="USD/bbl", font=dict(size=10, color=GOLD)),
        tickfont=dict(size=10, color=GOLD),
        showgrid=False,
        zeroline=False,
        tickprefix="$",
    ),
)

# ── Compute key stats for hero ─────────────────────────────────────────────────
pre_war_petrol = petrol[petrol["Date"] < pd.Timestamp(WAR_START)].iloc[-1]["price_nzd"]
pre_war_crude  = crude[crude["Date"] < pd.Timestamp(WAR_START)].iloc[-1]["crude_usd"]
pct_crude      = (latest_crude["crude_usd"] - pre_war_crude) / pre_war_crude * 100
pct_petrol     = (latest_petrol["price_nzd"] - pre_war_petrol) / pre_war_petrol * 100

# ── Export chart div (no plotlyjs — we'll load it in the page head) ────────────
chart_div = fig.to_html(
    full_html=False,
    include_plotlyjs=False,
    config={"displayModeBar": False},
)

# ── chart_fuel_prices.html — embeddable fragment for index.html ────────────────
FRAGMENT = "chart_fuel_prices.html"
source_credit = (
    '<p style="margin:6px 0 0 4px; font-size:8.5px; color:#6B6B6B; '
    'font-family:Inter,sans-serif;">'
    'Source: MBIE Weekly fuel price monitoring. '
    'Adjusted retail price is a national benchmark calculated from importer costs, '
    'taxes, and standard margins. Hormuz closure: 1 March 2026.</p>\n'
)
with open(FRAGMENT, "w") as f:
    f.write(
        FONT_IMPORT
        + '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>\n'
        + chart_div
        + source_credit
    )

# ── fuel_prices.html — full narrative page ─────────────────────────────────────
PAGE = "fuel_prices.html"
page_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NZ Fuel Prices · Iran War · Harvest</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: #1A1E1A; color: #F7F6F2; font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }}

    .site-nav {{
      background: #1A1E1A;
      padding: 0 48px;
      height: 57px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky;
      top: 0;
      z-index: 100;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }}
    .nav-back {{ font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.2s; }}
    .nav-back:hover {{ color: #F7F6F2; }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; }}
    .nav-links a {{ font-size: 13px; color: rgba(255,255,255,0.45); text-decoration: none; transition: color 0.2s; }}
    .nav-links a:hover {{ color: #F7F6F2; }}
    .nav-links a.active {{ color: #F7F6F2; }}

    .stat-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1px;
      background: rgba(255,255,255,0.06);
      border-radius: 12px;
      overflow: hidden;
    }}
    .stat-box {{
      background: rgba(255,255,255,0.03);
      padding: 28px 20px;
    }}
    .stat-num {{
      font-family: 'Fraunces', serif;
      font-size: 36px;
      font-weight: 300;
      line-height: 1;
      margin-bottom: 8px;
      letter-spacing: -0.5px;
    }}
    .stat-label {{
      font-size: 12px;
      color: rgba(255,255,255,0.3);
      line-height: 1.5;
    }}

    .context-card {{
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px;
      padding: 28px;
    }}
    .context-card h3 {{
      font-family: 'Fraunces', serif;
      font-size: 20px;
      font-weight: 300;
      color: #F7F6F2;
      line-height: 1.3;
      margin-bottom: 12px;
    }}
    .context-card p {{
      font-size: 14px;
      color: rgba(255,255,255,0.55);
      line-height: 1.8;
    }}
    .context-card p strong {{ color: rgba(255,255,255,0.85); font-weight: 500; }}

    .policy-row {{
      display: grid;
      grid-template-columns: 40px 1fr;
      gap: 20px;
      padding: 24px 28px;
      background: rgba(255,255,255,0.03);
      border-bottom: 1px solid rgba(255,255,255,0.06);
      align-items: start;
    }}
    .policy-row:last-child {{ border-bottom: none; }}
    .policy-num {{
      font-family: 'Fraunces', serif;
      font-size: 22px;
      font-weight: 300;
      color: #3A5C45;
      line-height: 1;
    }}
    .policy-strong {{ font-size: 14px; color: #F7F6F2; display: block; margin-bottom: 4px; }}
    .policy-text {{ font-size: 14px; color: rgba(255,255,255,0.5); line-height: 1.75; }}

    @media (max-width: 900px) {{
      .site-nav {{ padding: 0 24px; }}
      .stat-grid {{ grid-template-columns: 1fr 1fr; }}
      .context-grid {{ grid-template-columns: 1fr !important; }}
    }}
  </style>
</head>
<body>

  <nav class="site-nav">
    <a href="index.html" class="nav-back">← Portfolio</a>
    <ul class="nav-links">
      <li><a href="projects.html">Stories</a></li>
      <li><a href="housing.html">Housing</a></li>
      <li><a href="fuel_prices.html" class="active">Fuel</a></li>
    </ul>
  </nav>

  <!-- Hero -->
  <div style="padding:80px 48px; border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="max-width:960px;">
      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:#B85C45; margin-bottom:16px;">Iran War · Fuel Prices · 2026</p>
      <h2 style="font-family:'Fraunces',serif; font-size:clamp(32px,4.5vw,52px); font-weight:300; color:#F7F6F2; line-height:1.2; margin-bottom:20px; letter-spacing:-0.5px;">The war that hit <em style="color:#B8883A; font-style:normal;">every petrol station</em> in New Zealand</h2>
      <p style="font-size:16px; color:rgba(255,255,255,0.45); line-height:1.8; max-width:700px; margin-bottom:48px;">The Iran conflict began on 28 February 2026. Within three weeks, Dubai crude had surged 62%. NZ pump prices are already up — but the full impact hasn't fed through yet. The Strait of Hormuz closed on 1 March. What comes next.</p>
      <div class="stat-grid">
        <div class="stat-box">
          <div class="stat-num" style="color:#B85C45;">+{pct_crude:.0f}%</div>
          <div class="stat-label">Dubai crude since<br>war began</div>
        </div>
        <div class="stat-box">
          <div class="stat-num" style="color:#B8883A;">${latest_petrol['price_nzd']:.2f}</div>
          <div class="stat-label">Regular 91 per litre<br>as of {latest_petrol['Date'].strftime('%-d %b %Y')}</div>
        </div>
        <div class="stat-box">
          <div class="stat-num" style="color:#F7F6F2;">+{pct_petrol:.0f}%</div>
          <div class="stat-label">Pump price rise<br>so far — lag effect</div>
        </div>
        <div class="stat-box">
          <div class="stat-num" style="color:#B85C45;">20 Mar</div>
          <div class="stat-label">Hormuz strait closed —<br>first attack 1 March</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Chart -->
  <div style="background:#0D1210; padding:48px 48px 32px; border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="max-width:960px; background:#FFFFFF; border-radius:12px; overflow:hidden; padding:8px;">
      {chart_div}
      <p style="margin:4px 0 6px 6px; font-size:8.5px; color:#6B6B6B; font-family:Inter,sans-serif;">Source: MBIE Weekly fuel price monitoring. Adjusted retail price is a national benchmark. Data updated weekly each Wednesday. Hormuz closure: 1 March 2026.</p>
    </div>
  </div>

  <!-- Context -->
  <div style="background:#0D1210; padding:64px 48px; border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="max-width:960px;">
      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:#3A5C45; margin-bottom:16px;">Understanding the numbers</p>
      <h3 style="font-family:'Fraunces',serif; font-size:28px; font-weight:300; color:#F7F6F2; line-height:1.3; letter-spacing:-0.3px; margin-bottom:32px;">Why pump prices haven't fully caught up — yet</h3>
      <div class="context-grid" style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
        <div class="context-card">
          <h3>The lag effect</h3>
          <p>Crude is priced in USD and bought weeks in advance. The cost of oil imported today reflects crude prices from roughly 2–4 weeks ago. That means the <strong>March 13 pump price of $2.82/L</strong> is still catching up to the crude spike that began in early March. Expect further rises in the weeks ahead.</p>
        </div>
        <div class="context-card">
          <h3>Fixed taxes cushion the blow — partially</h3>
          <p>Around <strong>77c per litre</strong> of the pump price is fixed taxes — fuel excise, ETS levies, ACC — that don't move with the oil price. This acts as a buffer: when crude doubles, the pump price doesn't. But it also means the base price is already high before the oil cost is added.</p>
        </div>
        <div class="context-card">
          <h3>The NZD amplifies the shock</h3>
          <p>Dubai crude is priced in USD. A weaker kiwi dollar means NZ pays more for the same barrel. The NZD/USD exchange rate has fallen from <strong>0.633 to 0.589</strong> since the war began — adding extra cost on top of the crude price rise itself.</p>
        </div>
        <div class="context-card">
          <h3>Hormuz closure — what comes next</h3>
          <p>The Strait of Hormuz carries roughly <strong>20% of global oil supply</strong>. Its closure on 1 March is not yet reflected in MBIE data — that will appear in coming weeks. If the closure persists, analysts expect crude to test <strong>$130–150/bbl</strong>, which would push NZ pump prices above <strong>$3.20/L</strong>.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- What this means -->
  <div style="background:#1A1E1A; padding:80px 48px; border-top:1px solid rgba(255,255,255,0.06);">
    <div style="border-top:2px solid #3A5C45; padding-top:40px; max-width:960px;">
      <p style="font-size:11px; font-weight:500; letter-spacing:1.5px; text-transform:uppercase; color:#3A5C45; margin-bottom:12px;">What this means</p>
      <h3 style="font-family:'Fraunces',serif; font-size:28px; font-weight:300; color:#F7F6F2; line-height:1.3; letter-spacing:-0.3px; margin-bottom:32px;">Four things the data tells us about the road ahead</h3>
      <div style="border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">Pump prices will keep rising for at least 2–3 more weeks.</strong><span class="policy-text">The crude shock is real and already locked in. Importers price fuel on a 2–4 week lag. The March 13 reading of $2.82/L reflects crude bought before the sharpest price moves. The full cost of the spike will show in pump prices through late March and April.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">The Hormuz closure is the bigger unknown.</strong><span class="policy-text">Crude at $115/bbl was already a significant shock. If Hormuz closure persists and supply from the Gulf is rerouted or reduced, the price ceiling moves substantially higher. Rerouting tankers around the Cape of Good Hope adds 10–15 days to shipping time and significant cost — none of which is yet in the data.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">NZ's renewable electricity grid provides partial insulation.</strong><span class="policy-text">Around 80–85% of NZ's electricity comes from hydro, wind, and geothermal. Unlike most countries, a fuel price shock doesn't automatically translate into an electricity price shock. The economy is exposed through transport and freight — not through the power grid.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">04</div>
          <div><strong class="policy-strong">The RBNZ faces a difficult trade-off.</strong><span class="policy-text">Higher fuel prices feed into headline inflation. The Reserve Bank was on a path of gradual rate cuts through 2026. A sustained oil price shock complicates that — it creates inflationary pressure the Bank cannot directly address with rate cuts, but cutting into an inflationary environment risks embedding expectations. Fuel prices are now a material input to the monetary policy outlook.</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div style="background:#1A1E1A; padding:40px 48px; border-top:1px solid rgba(255,255,255,0.06); display:flex; align-items:center; justify-content:space-between;">
    <span style="font-size:13px; color:rgba(255,255,255,0.3);">Harry Candlish · Data Analyst · Wellington, NZ</span>
    <a href="index.html" style="font-size:13px; color:#B8883A; text-decoration:none; border:1px solid rgba(184,136,58,0.35); border-radius:40px; padding:10px 20px; transition:all 0.2s;" onmouseover="this.style.background='rgba(184,136,58,0.1)'" onmouseout="this.style.background=''">← Back to portfolio</a>
  </div>

</body>
</html>"""

with open(PAGE, "w") as f:
    f.write(page_html)

print(f"Fragment written to {FRAGMENT}")
print(f"Full page written to {PAGE}")
print(f"Latest petrol price: ${latest_petrol['price_nzd']:.2f}/L ({latest_petrol['Date'].date()})")
print(f"Latest crude price:  ${latest_crude['crude_usd']:.2f}/bbl ({latest_crude['Date'].date()})")
print(f"Pre-war petrol: ${pre_war_petrol:.2f}/L → crude up {pct_crude:.0f}%, pump up {pct_petrol:.0f}%")
