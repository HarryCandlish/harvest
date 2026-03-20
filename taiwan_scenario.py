"""
taiwan_scenario.py
------------------
Builds taiwan.html — an interactive scenario modelling page.
Question: What would it mean for New Zealand if China moved on Taiwan?

Structure:
  1. Scrollytelling map — NZ-China economic relationship (6 steps)
  2. Decision point — how does the PM respond? (3 choices)
  3. Consequence branches — economic data for each path

Run:  python3 taiwan_scenario.py
"""

import json

# ── Brand ──────────────────────────────────────────────────────────────────────
GREEN   = "#3A5C45"
GOLD    = "#B8883A"
RED     = "#C0392B"
CHINA_R = "#8B1A1A"
BLUE    = "#2C5F8A"
DARK    = "#1A1E1A"
CREAM   = "#F7F6F2"

# ── Trade data (Stats NZ goods & services, 2023) ──────────────────────────────
# China dependency: % of each sector's exports that go to China
EXPORTS = [
    {"commodity": "Whole milk powder", "value_bn": 4.20, "china_pct": 60, "lat": -37.9, "lon": 175.5, "size": 22},
    {"commodity": "Butter and AMF",    "value_bn": 2.10, "china_pct": 35, "lat": -43.5, "lon": 172.6, "size": 16},
    {"commodity": "Logs and timber",   "value_bn": 2.10, "china_pct": 55, "lat": -38.1, "lon": 176.2, "size": 16},
    {"commodity": "Beef and lamb",     "value_bn": 1.20, "china_pct": 22, "lat": -40.3, "lon": 175.6, "size": 13},
    {"commodity": "Seafood",           "value_bn": 0.80, "china_pct": 28, "lat": -46.5, "lon": 168.4, "size": 11},
    {"commodity": "Wool",              "value_bn": 0.40, "china_pct": 45, "lat": -45.0, "lon": 170.5, "size":  9},
    {"commodity": "Education",         "value_bn": 1.20, "china_pct": 30, "lat": -36.8, "lon": 174.7, "size": 13},
]

PORTS = [
    {"name": "Shanghai",  "lat": 31.23, "lon": 121.47, "size": 14},
    {"name": "Tianjin",   "lat": 39.08, "lon": 117.20, "size": 11},
    {"name": "Guangzhou", "lat": 23.13, "lon": 113.26, "size": 11},
    {"name": "Qingdao",   "lat": 36.07, "lon": 120.38, "size": 11},
]

# Approximate great circle NZ → Shanghai (9 waypoints)
ROUTE = [
    {"lat": -41.0, "lon": 174.0},
    {"lat": -32.0, "lon": 168.5},
    {"lat": -22.0, "lon": 162.0},
    {"lat": -12.0, "lon": 155.5},
    {"lat":  -2.0, "lon": 149.0},
    {"lat":   8.0, "lon": 142.5},
    {"lat":  18.0, "lon": 136.0},
    {"lat":  25.0, "lon": 129.0},
    {"lat":  31.23, "lon": 121.47},
]

FIVE_EYES = [
    {"name": "United States", "lat": 38.9,  "lon": -77.0,  "size": 14},
    {"name": "United Kingdom","lat": 51.5,  "lon": -0.12,  "size": 11},
    {"name": "Australia",     "lat": -35.3, "lon": 149.1,  "size": 13},
    {"name": "Canada",        "lat": 45.4,  "lon": -75.7,  "size": 11},
]

CHINA_NAVAL = [
    {"name": "PLAN carrier group — eastern strait",   "lat": 24.8, "lon": 122.8},
    {"name": "PLAN destroyer screen — northern",      "lat": 25.4, "lon": 120.5},
    {"name": "PLAN amphibious fleet — southern",      "lat": 23.2, "lon": 118.8},
    {"name": "PLAN submarine patrol — Bashi Channel", "lat": 20.5, "lon": 122.0},
]

FTA_PARTNERS = [
    {"name": "United Kingdom", "lat": 51.5,  "lon": -0.12},
    {"name": "European Union", "lat": 50.8,  "lon":  4.4},
    {"name": "Canada",         "lat": 45.4,  "lon": -75.7},
    {"name": "Japan",          "lat": 35.7,  "lon": 139.7},
]

PRECEDENT_COUNTRIES = [
    {"name": "Australia · 2020", "lat": -35.3, "lon": 149.1},
    {"name": "Lithuania · 2021", "lat":  54.7, "lon":  25.3},
    {"name": "Canada · 2018",    "lat":  45.4, "lon": -75.7},
    {"name": "Japan · 2022",     "lat":  35.7, "lon": 139.7},
]

# Serialise for JavaScript
exports_js      = json.dumps(EXPORTS)
ports_js        = json.dumps(PORTS)
route_js        = json.dumps(ROUTE)
five_eyes_js    = json.dumps(FIVE_EYES)
naval_js        = json.dumps(CHINA_NAVAL)
fta_js          = json.dumps(FTA_PARTNERS)
precedent_js    = json.dumps(PRECEDENT_COUNTRIES)

TOTAL_EXPORTS_BN = 20.4
# ── UNGA voting blocs (based on Russia-Ukraine 2022 precedent) ────────────────
UNGA_CONDEMN = [
    {"name": "United States",  "lat": 38.9,  "lon": -77.0},
    {"name": "United Kingdom", "lat": 51.5,  "lon": -0.12},
    {"name": "Germany",        "lat": 52.5,  "lon": 13.4},
    {"name": "France",         "lat": 48.9,  "lon":  2.3},
    {"name": "Japan",          "lat": 35.7,  "lon": 139.7},
    {"name": "South Korea",    "lat": 37.6,  "lon": 126.9},
    {"name": "Australia",      "lat": -35.3, "lon": 149.1},
    {"name": "Canada",         "lat": 45.4,  "lon": -75.7},
    {"name": "Poland",         "lat": 52.2,  "lon": 21.0},
    {"name": "Netherlands",    "lat": 52.1,  "lon":  5.3},
    {"name": "Sweden",         "lat": 59.3,  "lon": 18.1},
    {"name": "Norway",         "lat": 59.9,  "lon": 10.7},
]
UNGA_ABSTAIN = [
    {"name": "India",          "lat": 28.6,  "lon":  77.2},
    {"name": "Saudi Arabia",   "lat": 24.7,  "lon":  46.7},
    {"name": "Indonesia",      "lat": -6.2,  "lon": 106.8},
    {"name": "Brazil",         "lat": -15.8, "lon": -47.9},
    {"name": "South Africa",   "lat": -25.7, "lon":  28.2},
    {"name": "Pakistan",       "lat": 33.7,  "lon":  73.1},
    {"name": "UAE",            "lat": 24.5,  "lon":  54.4},
    {"name": "Thailand",       "lat": 13.7,  "lon": 100.5},
    {"name": "Mexico",         "lat": 19.4,  "lon": -99.1},
    {"name": "Vietnam",        "lat": 21.0,  "lon": 105.8},
    {"name": "Ethiopia",       "lat":  9.0,  "lon":  38.7},
    {"name": "Bangladesh",     "lat": 23.7,  "lon":  90.4},
    {"name": "Malaysia",       "lat":  3.1,  "lon": 101.7},
    {"name": "Cambodia",       "lat": 11.6,  "lon": 104.9},
    {"name": "Laos",           "lat": 17.9,  "lon": 102.6},
    {"name": "Egypt",          "lat": 30.0,  "lon":  31.2},
    {"name": "Nigeria",        "lat":  9.1,  "lon":   7.5},
    {"name": "Kenya",          "lat": -1.3,  "lon":  36.8},
    {"name": "Tanzania",       "lat": -6.8,  "lon":  39.3},
    {"name": "Angola",         "lat": -8.8,  "lon":  13.2},
    {"name": "Zimbabwe",       "lat": -17.8, "lon":  31.1},
    {"name": "Mozambique",     "lat": -25.9, "lon":  32.6},
    {"name": "Algeria",        "lat": 36.7,  "lon":   3.0},
    {"name": "Morocco",        "lat": 33.9,  "lon":  -6.9},
    {"name": "Turkey",         "lat": 39.9,  "lon":  32.9},
    {"name": "Kazakhstan",     "lat": 51.2,  "lon":  71.4},
    {"name": "Nepal",          "lat": 27.7,  "lon":  85.3},
    {"name": "Sri Lanka",      "lat":  7.9,  "lon":  80.7},
    {"name": "Argentina",      "lat": -34.6, "lon": -58.4},
    {"name": "Peru",           "lat": -12.0, "lon": -77.0},
    {"name": "Bolivia",        "lat": -16.5, "lon": -68.1},
    {"name": "Cuba",           "lat": 23.1,  "lon": -82.4},
    {"name": "Serbia",         "lat": 44.8,  "lon":  20.5},
]
UNGA_AGAINST = [
    {"name": "Russia",         "lat": 55.8,  "lon":  37.6},
    {"name": "North Korea",    "lat": 39.0,  "lon": 125.8},
    {"name": "Belarus",        "lat": 53.9,  "lon":  27.6},
    {"name": "Nicaragua",      "lat": 12.1,  "lon": -86.3},
]

unga_condemn_js = json.dumps(UNGA_CONDEMN)
unga_abstain_js = json.dumps(UNGA_ABSTAIN)
unga_against_js = json.dumps(UNGA_AGAINST)

DAIRY_BN         = 6.30   # WMP + butter
LOGS_BN          = 2.10
NZD_SURPLUS_BN   = 4.20   # NZ goods surplus with China

PAGE = "taiwan.html"

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Taiwan Scenario · NZ Economic Exposure · Harvest</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
  <script src="https://unpkg.com/scrollama@3.2.0/build/scrollama.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{ background: {DARK}; color: {CREAM}; font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }}

    .site-nav {{
      background: {DARK}; padding: 0 48px; height: 57px;
      display: flex; align-items: center; justify-content: space-between;
      position: sticky; top: 0; z-index: 100;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }}
    .nav-back {{ font-size: 13px; color: rgba(255,255,255,0.5); text-decoration: none; transition: color 0.2s; }}
    .nav-back:hover {{ color: {CREAM}; }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; }}
    .nav-links a {{ font-size: 13px; color: rgba(255,255,255,0.45); text-decoration: none; transition: color 0.2s; }}
    .nav-links a:hover, .nav-links a.active {{ color: {CREAM}; }}

    .step-card {{
      background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px; padding: 28px;
    }}
    .step-label {{ font-size: 11px; font-weight: 600; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 10px; }}
    .step-title {{ font-family: 'Fraunces', serif; font-size: 22px; font-weight: 300; color: {CREAM}; line-height: 1.3; letter-spacing: -0.2px; margin-bottom: 12px; }}
    .step-body {{ font-size: 14px; color: rgba(255,255,255,0.55); line-height: 1.8; }}
    .step-body strong {{ color: rgba(255,255,255,0.85); font-weight: 500; }}
    .step-stat {{ font-family: 'Fraunces', serif; font-size: 32px; font-weight: 300; line-height: 1; margin-top: 16px; }}
    .step-stat span {{ font-family: 'Inter', sans-serif; font-size: 12px; color: rgba(255,255,255,0.35); margin-left: 8px; }}
    .step-mini-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }}
    .step-mini-num {{ font-family: 'Fraunces', serif; font-size: 22px; font-weight: 300; line-height: 1; }}
    .step-mini-label {{ font-size: 11px; color: rgba(255,255,255,0.35); margin-top: 4px; }}

    .map-legend {{
      position: absolute; bottom: 20px; left: 20px;
      display: flex; flex-direction: column; gap: 6px; pointer-events: none;
    }}
    .legend-row {{ display: flex; align-items: center; gap: 8px; }}
    .legend-dot {{ width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }}
    .legend-label {{ font-size: 10px; color: rgba(255,255,255,0.55); font-family: 'Inter', sans-serif; }}

    /* ── Decision section ─────────────────────────────────── */
    .decision-section {{
      background: #0D1210;
      border-top: 1px solid rgba(255,255,255,0.08);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      padding: 80px 48px;
    }}
    .decision-inner {{ max-width: 960px; margin: 0 auto; }}
    .decision-scenario {{
      background: rgba(139,26,26,0.12); border: 1px solid rgba(192,57,43,0.3);
      border-radius: 12px; padding: 28px; margin-bottom: 48px;
    }}
    .decision-scenario-label {{
      font-size: 10px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase;
      color: {RED}; margin-bottom: 12px;
    }}
    .decision-scenario-title {{
      font-family: 'Fraunces', serif; font-size: 22px; font-weight: 300; color: {CREAM};
      line-height: 1.4; margin-bottom: 12px;
    }}
    .decision-scenario-body {{
      font-size: 14px; color: rgba(255,255,255,0.5); line-height: 1.8;
    }}
    .decision-prompt {{
      font-family: 'Fraunces', serif; font-size: 28px; font-weight: 300; color: {CREAM};
      line-height: 1.3; margin-bottom: 8px; letter-spacing: -0.3px;
    }}
    .decision-sub {{
      font-size: 14px; color: rgba(255,255,255,0.4); margin-bottom: 40px; line-height: 1.7;
    }}
    .choice-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .choice-btn {{
      background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12);
      border-radius: 12px; padding: 28px 24px; cursor: pointer; text-align: left;
      transition: all 0.25s; color: {CREAM}; font-family: 'Inter', sans-serif;
    }}
    .choice-btn:hover {{ background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.25); transform: translateY(-2px); }}
    .choice-btn.chosen {{ border-width: 2px; transform: translateY(-2px); }}
    .choice-btn.faded {{ opacity: 0.3; }}
    .choice-tag {{ font-size: 10px; font-weight: 600; letter-spacing: 1.3px; text-transform: uppercase; margin-bottom: 12px; }}
    .choice-title {{ font-family: 'Fraunces', serif; font-size: 18px; font-weight: 300; line-height: 1.3; margin-bottom: 12px; }}
    .choice-desc {{ font-size: 13px; color: rgba(255,255,255,0.45); line-height: 1.75; }}
    .choice-consequence {{ font-size: 12px; margin-top: 16px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.08); color: rgba(255,255,255,0.3); }}

    /* ── Consequence sections ─────────────────────────────── */
    .consequence {{ display: none; }}
    .consequence-inner {{ max-width: 960px; margin: 0 auto; padding: 80px 48px; }}
    .consequence-header {{ margin-bottom: 40px; }}
    .consequence-choice-label {{ font-size: 10px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 12px; opacity: 0.6; }}
    .consequence-title {{ font-family: 'Fraunces', serif; font-size: 32px; font-weight: 300; color: {CREAM}; line-height: 1.25; letter-spacing: -0.4px; margin-bottom: 16px; }}
    .consequence-body {{ font-size: 15px; color: rgba(255,255,255,0.5); line-height: 1.85; max-width: 720px; }}
    .consequence-body strong {{ color: rgba(255,255,255,0.8); font-weight: 500; }}
    .data-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 40px 0; }}
    .data-card {{
      background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 12px; padding: 24px;
    }}
    .data-card-num {{ font-family: 'Fraunces', serif; font-size: 36px; font-weight: 300; line-height: 1; margin-bottom: 8px; }}
    .data-card-label {{ font-size: 12px; color: rgba(255,255,255,0.4); line-height: 1.6; }}
    .exposure-table {{ width: 100%; border-collapse: collapse; margin-top: 32px; }}
    .exposure-table th {{ font-size: 10px; font-weight: 600; letter-spacing: 1.1px; text-transform: uppercase; color: rgba(255,255,255,0.3); padding: 10px 16px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); }}
    .exposure-table td {{ font-size: 13px; color: rgba(255,255,255,0.6); padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
    .exposure-table td:first-child {{ color: rgba(255,255,255,0.85); }}
    .bar-wrap {{ background: rgba(255,255,255,0.06); border-radius: 4px; height: 6px; margin-top: 6px; }}
    .bar-fill {{ height: 6px; border-radius: 4px; }}

    .policy-row {{
      display: grid; grid-template-columns: 40px 1fr; gap: 20px;
      padding: 24px 28px; background: rgba(255,255,255,0.03);
      border-bottom: 1px solid rgba(255,255,255,0.06); align-items: start;
    }}
    .policy-row:last-child {{ border-bottom: none; }}
    .policy-num {{ font-family: 'Fraunces', serif; font-size: 22px; font-weight: 300; color: {GREEN}; line-height: 1; }}
    .policy-strong {{ font-size: 14px; color: {CREAM}; display: block; margin-bottom: 4px; }}
    .policy-text {{ font-size: 14px; color: rgba(255,255,255,0.5); line-height: 1.75; }}

    @media (max-width: 900px) {{
      .site-nav {{ padding: 0 24px; }}
      #conflict-scrolly {{ flex-direction: column; }}
      #map-panel {{ position: sticky; top: 57px; height: 55vw; min-height: 280px; width: 100% !important; }}
      #steps-col {{ width: 100% !important; padding: 0 24px !important; }}
      .choice-grid {{ grid-template-columns: 1fr; }}
      .data-grid {{ grid-template-columns: 1fr 1fr; }}
      .decision-section {{ padding: 56px 24px; }}
      .consequence-inner {{ padding: 56px 24px; }}
    }}
  </style>
</head>
<body>

  <nav class="site-nav">
    <a href="index.html" class="nav-back">← Portfolio</a>
    <ul class="nav-links">
      <li><a href="projects.html">Stories</a></li>
      <li><a href="fuel_prices.html">Iran War</a></li>
      <li><a href="taiwan.html" class="active">Taiwan</a></li>
    </ul>
  </nav>

  <!-- Hero -->
  <div style="padding:80px 48px 72px; border-bottom:1px solid rgba(255,255,255,0.06);">
    <div style="max-width:1100px; display:flex; align-items:flex-start; justify-content:space-between; gap:48px; flex-wrap:wrap;">
      <div style="flex:1; min-width:0;">
        <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{RED}; margin-bottom:16px;">Scenario model · Hypothetical · 2027</p>
        <h1 style="font-family:'Fraunces',serif; font-size:clamp(32px,4.5vw,52px); font-weight:300; color:{CREAM}; line-height:1.2; margin-bottom:20px; letter-spacing:-0.5px;">If China moved on Taiwan — <em style="color:{GOLD}; font-style:normal;">what would it mean for New Zealand?</em></h1>
        <p style="font-size:16px; color:rgba(255,255,255,0.45); line-height:1.8; max-width:620px; margin-bottom:28px;">This is a scenario model, not a forecast. It uses real trade data — export volumes, commodity flows, and bilateral dependency — to map what a Chinese move on Taiwan would cost New Zealand. Trade is where the numbers are clearest. Currency, inflation, and employment would follow. At each decision point, you choose New Zealand's response. The data shows what the exposure looks like on each path.</p>
        <div style="display:inline-flex; gap:8px; flex-wrap:wrap;">
          <span style="font-size:11px; background:rgba(184,136,58,0.12); border:1px solid rgba(184,136,58,0.3); color:{GOLD}; padding:5px 12px; border-radius:20px; letter-spacing:0.5px;">Scenario model</span>
          <span style="font-size:11px; background:rgba(58,92,69,0.15); border:1px solid rgba(58,92,69,0.4); color:#8FAF8A; padding:5px 12px; border-radius:20px; letter-spacing:0.5px;">Real trade data</span>
          <span style="font-size:11px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.12); color:rgba(255,255,255,0.5); padding:5px 12px; border-radius:20px; letter-spacing:0.5px;">Interactive decisions</span>
        </div>
      </div>
      <div style="flex-shrink:0; width:230px; background:rgba(139,26,26,0.1); border:1px solid rgba(192,57,43,0.25); border-radius:16px; padding:28px;">
        <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:rgba(192,57,43,0.7); margin-bottom:20px;">NZ exposure to China</div>
        <div style="font-family:'Fraunces',serif; font-size:64px; font-weight:300; color:{CREAM}; line-height:1; letter-spacing:-2px; margin-bottom:4px;">${TOTAL_EXPORTS_BN:.0f}B</div>
        <div style="font-size:13px; color:rgba(255,255,255,0.4); margin-bottom:20px;">NZD exports annually</div>
        <div style="padding-top:16px; border-top:1px solid rgba(192,57,43,0.15);">
          <div style="font-size:11px; color:rgba(255,255,255,0.3); margin-bottom:10px;">28% of all NZ exports</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.3); margin-bottom:10px;">~5% of New Zealand's entire GDP</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.3);">China's FTA partner since 2008 — the first with a developed nation</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Scrollytelling: trade map -->
  <div id="conflict-scrolly" style="position:relative; display:flex; align-items:flex-start; background:#0D1210;">

    <div id="map-panel" style="position:sticky; top:57px; height:calc(100vh - 57px); width:58%; flex-shrink:0; display:flex; flex-direction:column;">
      <div style="position:relative; flex:1; padding:16px 8px 8px 16px;">
        <div id="trade-map" style="width:100%; height:100%;"></div>
        <div class="map-legend" id="map-legend" style="display:none;">
          <div class="legend-row" id="leg-nz"><span class="legend-dot" style="background:{GREEN};"></span><span class="legend-label">New Zealand</span></div>
          <div class="legend-row" id="leg-china" style="display:none;"><span class="legend-dot" style="background:{RED};"></span><span class="legend-label">Chinese import ports</span></div>
          <div class="legend-row" id="leg-route" style="display:none;"><span style="width:20px;height:2px;background:{GOLD};display:inline-block;"></span><span class="legend-label" style="margin-left:8px;">Trade route — $20.4B/yr</span></div>
          <div class="legend-row" id="leg-exports" style="display:none;"><span class="legend-dot" style="background:rgba(184,136,58,0.7);"></span><span class="legend-label">NZ export commodities</span></div>
          <div class="legend-row" id="leg-naval" style="display:none;"><span class="legend-dot" style="background:{RED};"></span><span class="legend-label">PLAN naval vessels</span></div>
          <div class="legend-row" id="leg-fta" style="display:none;"><span class="legend-dot" style="background:#4A9B7F;"></span><span class="legend-label">FTA partners — new markets</span></div>
          <div class="legend-row" id="leg-precedents" style="display:none;"><span class="legend-dot" style="background:#E67E22;"></span><span class="legend-label">Countries that spoke up</span></div>
        </div>
      </div>
    </div>

    <div id="steps-col" style="width:42%; padding:0 48px 0 32px;">
      <div style="height:40vh;"></div>

      <!-- Step 0: The Pacific -->
      <div class="conf-step" data-step="0" style="min-height:70vh; display:flex; align-items:center; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:rgba(255,255,255,0.3);">The Pacific — 2026</p>
          <h3 class="step-title">A relationship built over 20 years — now at the centre of the most dangerous scenario in the region</h3>
          <p class="step-body">In 2008, New Zealand became the first developed nation to sign a Free Trade Agreement with China. It was considered a diplomatic triumph. Eighteen years later, that relationship is the single biggest variable in how a Taiwan conflict would land on New Zealand — economically, politically, and strategically. Scroll through to see what is at stake.</p>
        </div>
      </div>

      <!-- Step 1: The relationship -->
      <div class="conf-step" data-step="1" style="min-height:70vh; display:flex; align-items:center; opacity:0.3; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:{RED};">The relationship</p>
          <h3 class="step-title">China is New Zealand's largest trading partner — by a significant margin</h3>
          <p class="step-body">In 2023, New Zealand exported <strong>$20.4 billion</strong> in goods and services to China — 28% of the national total. The next largest partner, Australia, took 14%. China is not replaceable overnight. NZ also runs a <strong>$4.2 billion goods surplus</strong> with China — we need this relationship considerably more than it needs us.</p>
          <div class="step-mini-grid">
            <div><div class="step-mini-num" style="color:{RED};">28%</div><div class="step-mini-label">of all NZ exports go to China</div></div>
            <div><div class="step-mini-num" style="color:{RED};">14%</div><div class="step-mini-label">go to Australia — our second largest</div></div>
          </div>
        </div>
      </div>

      <!-- Step 2: What we send -->
      <div class="conf-step" data-step="2" style="min-height:70vh; display:flex; align-items:center; opacity:0.3; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:{GOLD};">What we send</p>
          <h3 class="step-title">Dairy dominates — and it is the hardest to replace</h3>
          <p class="step-body">Dairy products account for over <strong>$6.3 billion</strong> of what New Zealand exports to China — whole milk powder alone is $4.2 billion. China takes <strong>60% of all NZ whole milk powder exports</strong>. The global market for WMP in the volumes Fonterra produces is extremely thin outside China. Logs, education, beef, and seafood complete the picture.</p>
          <div class="step-mini-grid">
            <div><div class="step-mini-num" style="color:{GOLD};">\$6.3B</div><div class="step-mini-label">dairy exports to China annually</div></div>
            <div><div class="step-mini-num" style="color:{GOLD};">60%</div><div class="step-mini-label">of WMP exports go to China</div></div>
          </div>
        </div>
      </div>

      <!-- Step 3: The route -->
      <div class="conf-step" data-step="3" style="min-height:70vh; display:flex; align-items:center; opacity:0.3; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:{GOLD};">The trade route</p>
          <h3 class="step-title">14,000 km of ocean — and it all passes through the South China Sea</h3>
          <p class="step-body">Every container ship carrying NZ dairy, logs, and meat to China transits the South China Sea — the same body of water at the centre of a Taiwan conflict. A naval blockade or conflict in the strait would not just restrict China's imports — it would make the physical delivery of NZ goods dangerous and potentially impossible regardless of trade policy.</p>
          <div class="step-stat" style="color:rgba(255,255,255,0.5);">14,000 km<span>Auckland → Shanghai, through the South China Sea</span></div>
        </div>
      </div>

      <!-- Step 4: Great Decoupling -->
      <div class="conf-step" data-step="4" style="min-height:70vh; display:flex; align-items:center; opacity:0.3; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:{GOLD};">The great decoupling · 2020–2026</p>
          <h3 class="step-title">New Zealand tried to diversify — the numbers didn't move</h3>
          <p class="step-body">After Australia's 2020 experience, NZ quietly began opening new markets. A <strong>UK FTA</strong> (Feb 2023) reached 67 million consumers — dairy gains phased over 15 years. An <strong>EU FTA</strong> (May 2024) opened 450 million — behind quota restrictions. CPTPP added Canada and Mexico. Fonterra sold its China consumer brands, pivoting to B2B ingredients. Despite it all, China's share of NZ exports in 2026 is <strong>exactly what it was in 2020</strong>. The structural problem is WMP: no market on earth buys it in Fonterra-scale volumes outside China.</p>
          <div class="step-mini-grid">
            <div><div class="step-mini-num" style="color:rgba(255,255,255,0.3);">28%</div><div class="step-mini-label">China share of NZ exports — 2020</div></div>
            <div><div class="step-mini-num" style="color:{GOLD};">28%</div><div class="step-mini-label">China share of NZ exports — 2026</div></div>
          </div>
        </div>
      </div>

      <!-- Step 5: Precedents -->
      <div class="conf-step" data-step="5" style="min-height:80vh; display:flex; align-items:center; opacity:0.3; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:{RED};">The precedents · 2018–2026</p>
          <h3 class="step-title">When countries spoke up — did allies buy what China stopped buying?</h3>
          <p class="step-body">Four countries challenged China in the past eight years. Each time, Beijing responded with precision economic retaliation. Each time, allies offered <strong>words, not markets</strong>.</p>
          <div style="margin-top:16px; display:flex; flex-direction:column; gap:8px;">
            <div style="padding:12px 14px; background:rgba(255,255,255,0.04); border-radius:8px; border-left:3px solid rgba(192,57,43,0.6);">
              <div style="font-size:11px; font-weight:600; color:{RED}; margin-bottom:3px;">Australia · 2020 · COVID inquiry</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.45); line-height:1.65;">~$20B trade disruption. Wine and lobster lost permanently. Five Eyes solidarity. Zero market substitution.</div>
            </div>
            <div style="padding:12px 14px; background:rgba(255,255,255,0.04); border-radius:8px; border-left:3px solid rgba(192,57,43,0.6);">
              <div style="font-size:11px; font-weight:600; color:{RED}; margin-bottom:3px;">Lithuania · 2021 · Taiwan representative office</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.45); line-height:1.65;">Removed from Chinese customs database. Multinationals pressured to cut Lithuanian supply chains. EU filed WTO dispute — unresolved years later. No EU member bought Lithuanian goods to offset losses.</div>
            </div>
            <div style="padding:12px 14px; background:rgba(255,255,255,0.04); border-radius:8px; border-left:3px solid rgba(192,57,43,0.6);">
              <div style="font-size:11px; font-weight:600; color:{RED}; margin-bottom:3px;">Canada · 2018 · Meng Wanzhou arrest</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.45); line-height:1.65;">Arrested Huawei's CFO at the US's request. China took two Canadians hostage, banned $2.7B in canola. The US gave verbal support — and nothing else.</div>
            </div>
            <div style="padding:12px 14px; background:rgba(255,255,255,0.04); border-radius:8px; border-left:3px solid rgba(192,57,43,0.6);">
              <div style="font-size:11px; font-weight:600; color:{RED}; margin-bottom:3px;">Japan · 2022 · Taiwan named as security concern</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.45); line-height:1.65;">Seafood ban 2023. US reaffirmed Article 5 — a defence guarantee, not an economic one. Japan is absorbing its own cost.</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Step 6: The scenario -->
      <div class="conf-step" data-step="6" style="min-height:70vh; display:flex; align-items:center; opacity:0.3; transition:opacity 0.4s;">
        <div class="step-card">
          <p class="step-label" style="color:{RED};">27 November 2027 — The scenario begins</p>
          <h3 class="step-title">Beijing declares a reunification operation — the strait is sealed</h3>
          <p class="step-body">China announces a special military operation to reunify Taiwan with the mainland. PLAN carrier groups are positioned at both ends of the Taiwan Strait. Commercial flights over Taiwan are suspended. The United States activates the 7th Fleet. Japan places its Self-Defence Forces on alert. The world is watching. And in New Zealand, the Prime Minister's office is drafting a statement.</p>
          <div class="step-mini-grid">
            <div><div class="step-mini-num" style="color:{RED};">4</div><div class="step-mini-label">PLAN carrier groups positioned in strait</div></div>
            <div><div class="step-mini-num" style="color:{RED};">US 7th</div><div class="step-mini-label">Fleet activated — 60 vessels mobilising</div></div>
          </div>
        </div>
      </div>

      <div style="height:40vh;"></div>
    </div>
  </div>

  <!-- ── US Posture Variable ──────────────────────────────────────────────── -->
  <div style="background:#0A0F1A; border-top:2px solid {BLUE}; padding:72px 48px;">
    <div style="max-width:960px; margin:0 auto;">
      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{BLUE}; margin-bottom:16px;">Scenario variable · Washington's posture · Set before proceeding</p>
      <h2 style="font-family:'Fraunces',serif; font-size:32px; font-weight:300; color:{CREAM}; line-height:1.25; letter-spacing:-0.4px; margin-bottom:16px;">The single biggest variable isn't what New Zealand does. It's what the United States does.</h2>
      <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:32px;">US posture determines two things: how large the structural economic shock is for New Zealand, and how much capacity China retains to punish NZ's decisions. A full US deployment devastates China's economy — but that same devastation is also what collapses NZ's $20.4B trade relationship, regardless of what New Zealand says. No US involvement means less global disruption, but China faces no external pressure and retains full economic leverage. Choose the scenario you're modelling.</p>

      <!-- Why this decision is hard -->
      <div style="margin-bottom:40px; padding:28px 32px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:14px;">
        <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:20px;">Why Option A may be unavoidable — even for a president who prefers Option B</h4>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
          <div style="display:flex; flex-direction:column; gap:14px;">
            <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid rgba(44,95,138,0.5);">
              <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">Strategic ambiguity as deterrent</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.65;">The US has never confirmed whether it would intervene militarily — because the threat of intervention is worth more than certainty. The moment China concludes the US has settled on Option B, the deterrent collapses. Every US president, regardless of preference, must maintain the credible possibility of full deployment. Strategic ambiguity only functions if Option A remains genuinely on the table.</div>
            </div>
            <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid rgba(44,95,138,0.5);">
              <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">The semiconductor dependency</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.65;">Taiwan produces roughly 92% of the world's most advanced semiconductors. TSMC's sub-5nm chips have no alternative supplier at scale. A Chinese-controlled Taiwan means China controls the hardware layer of the global economy — every advanced military system, every data centre, every modern weapons platform in the West. This is not a trade consideration. It is an existential strategic threat that changes the calculus entirely.</div>
            </div>
          </div>
          <div style="display:flex; flex-direction:column; gap:14px;">
            <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid rgba(44,95,138,0.5);">
              <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">The first island chain</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.65;">Taiwan sits at the centre of the arc of islands — from Japan through Taiwan to the Philippines — that contains Chinese naval power in the Western Pacific. If China takes Taiwan, the PLAN breaks out of that containment. Chinese submarines operate freely in the Pacific. Japan's southern islands are exposed. The entire US forward defence posture, built around that chain since 1945, collapses. Taiwan is strategically different from Ukraine precisely because of geography.</div>
            </div>
            <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid rgba(44,95,138,0.5);">
              <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">Japan and South Korea going nuclear</div>
              <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.65;">Both countries could build nuclear weapons within months — the enriched uranium, delivery systems, and engineering base exist. Both currently shelter under the US nuclear umbrella. If China takes Taiwan without US intervention, both governments face the same conclusion: the umbrella doesn't hold. Two highly capable, historically adversarial states acquiring nuclear weapons in the most militarised region on earth may be a greater threat to US security than the cost of defending Taiwan directly.</div>
            </div>
          </div>
        </div>
        <p style="font-size:13px; color:rgba(255,255,255,0.3); line-height:1.7; margin-top:20px; font-style:italic;">Most analysts consider Option B the likely opening position — with Option A already decided privately and triggered if Taiwan comes within 72 hours of falling. The ambiguity is maintained for diplomatic reasons. The contingency planning assumes full deployment.</p>
      </div>

      <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:36px;">
        <button id="us-choice-full" onclick="makeChoice0('full')" style="background:rgba(44,95,138,0.08); border:1px solid rgba(44,95,138,0.3); border-radius:12px; padding:24px 20px; text-align:left; cursor:pointer; transition:all 0.2s;">
          <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:{BLUE}; margin-bottom:10px;">Option A</div>
          <div style="font-family:'Fraunces',serif; font-size:17px; font-weight:400; color:{CREAM}; line-height:1.3; margin-bottom:8px;">Full military deployment</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.35); line-height:1.65;">7th Fleet in active engagement. Comprehensive Western sanctions on China. US and China in direct military confrontation.</div>
        </button>
        <button id="us-choice-arms" onclick="makeChoice0('arms')" style="background:rgba(44,95,138,0.08); border:1px solid rgba(44,95,138,0.3); border-radius:12px; padding:24px 20px; text-align:left; cursor:pointer; transition:all 0.2s;">
          <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:{BLUE}; margin-bottom:10px;">Option B</div>
          <div style="font-family:'Fraunces',serif; font-size:17px; font-weight:400; color:{CREAM}; line-height:1.3; margin-bottom:8px;">Arms &amp; intelligence only</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.35); line-height:1.65;">The Ukraine model. US supplies Taiwan, imposes financial sanctions, but avoids direct combat. Prolonged conflict likely.</div>
        </button>
        <button id="us-choice-none" onclick="makeChoice0('none')" style="background:rgba(44,95,138,0.08); border:1px solid rgba(44,95,138,0.3); border-radius:12px; padding:24px 20px; text-align:left; cursor:pointer; transition:all 0.2s;">
          <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:{BLUE}; margin-bottom:10px;">Option C</div>
          <div style="font-family:'Fraunces',serif; font-size:17px; font-weight:400; color:{CREAM}; line-height:1.3; margin-bottom:8px;">No US involvement</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.35); line-height:1.65;">US stays out. China faces limited external military pressure. Conflict resolves faster. New Pacific order established.</div>
        </button>
      </div>

      <div id="us-consequence-full" style="display:none; padding:28px 32px; background:rgba(44,95,138,0.07); border:1px solid rgba(44,95,138,0.25); border-radius:14px;">
        <h4 style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; margin-bottom:6px;">Full deployment — what this means for the model</h4>
        <p style="font-size:13px; color:rgba(255,255,255,0.35); margin-bottom:20px;">Structural shock rises. China's punishment capacity falls. NZ decision paths converge.</p>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {BLUE};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">Structural shock</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">~1.5–2%</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">GDP. Comprehensive Western sanctions and China GDP contraction of 8–12% drive NZ export losses well beyond the structural baseline.</div>
          </div>
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {BLUE};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">China's punishment capacity</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">Constrained</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">SWIFT exclusion risk. Military spending absorbs fiscal space. Retaliating against NZ dairy is low priority when fighting for economic survival.</div>
          </div>
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {BLUE};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{BLUE}; text-transform:uppercase; margin-bottom:6px;">NZ decision range</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">1.5–3.5%</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">GDP. Gap between paths narrows. Silent floor rises. Condemn ceiling falls. NZ loses the trade partly regardless — the question is whether the loss comes with a values position attached.</div>
          </div>
        </div>
      </div>

      <div id="us-consequence-arms" style="display:none; padding:28px 32px; background:rgba(44,95,138,0.07); border:1px solid rgba(44,95,138,0.25); border-radius:14px;">
        <h4 style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; margin-bottom:6px;">Arms &amp; intelligence — what this means for the model</h4>
        <p style="font-size:13px; color:rgba(255,255,255,0.35); margin-bottom:20px;">This is the model baseline. NZ's diplomatic choices carry their largest marginal weight in this scenario.</p>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {GOLD};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:6px;">Structural shock</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">~1%</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">GDP. Prolonged conflict, moderate sanctions. China under pressure but retains trade capacity. The economic reality section below uses this as its baseline.</div>
          </div>
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {GOLD};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:6px;">China's punishment capacity</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">Moderate</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">Feels economic pressure but retains selective retaliation capacity. The Australia 2020 barley-and-wine model is available to Beijing. NZ's stance matters.</div>
          </div>
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {GOLD};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:6px;">NZ decision range</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">1–4.5%</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">GDP. Full spread applies. This is the scenario where NZ's diplomatic positioning has the largest marginal economic impact. Proceed to the decisions below.</div>
          </div>
        </div>
      </div>

      <div id="us-consequence-none" style="display:none; padding:28px 32px; background:rgba(44,95,138,0.07); border:1px solid rgba(44,95,138,0.25); border-radius:14px;">
        <h4 style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; margin-bottom:6px;">No involvement — what this means for the model</h4>
        <p style="font-size:13px; color:rgba(255,255,255,0.35); margin-bottom:20px;">Structural shock shrinks. China's punishment capacity is maximised. NZ decision paths diverge most sharply.</p>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px;">
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {RED};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{RED}; text-transform:uppercase; margin-bottom:6px;">Structural shock</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">~0.5–0.7%</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">GDP. Conflict resolves faster with less prolonged global disruption. No comprehensive Western sanctions. Taiwan Strait closure shorter.</div>
          </div>
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {RED};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{RED}; text-transform:uppercase; margin-bottom:6px;">China's punishment capacity</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">Maximised</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">No SWIFT pressure. Economy intact. Establishes Pacific primacy from a position of strength. Full Australia 2020 model available — applied at greater scale and confidence.</div>
          </div>
          <div style="padding:16px; background:rgba(255,255,255,0.03); border-radius:10px; border-left:3px solid {RED};">
            <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{RED}; text-transform:uppercase; margin-bottom:6px;">NZ decision range</div>
            <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:4px;">0.5–5.5%</div>
            <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">GDP. Paths diverge most sharply. The best economic outcome for NZ — silent, short conflict — is also the scenario that most fully establishes Chinese primacy in the Pacific. That tension is highest here.</div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- ── Structural Trade Exposure ────────────────────────────────────────── -->
  <div style="background:#0D1210; border-top:1px solid rgba(255,255,255,0.06); padding:64px 48px;">
    <div style="max-width:960px; margin:0 auto;">
      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{GOLD}; margin-bottom:16px;">Trade exposure · The structural floor</p>
      <h2 style="font-family:'Fraunces',serif; font-size:28px; font-weight:300; color:{CREAM}; line-height:1.25; letter-spacing:-0.4px; margin-bottom:12px;">Before any decision is made, these losses begin regardless.</h2>
      <p style="font-size:14px; color:rgba(255,255,255,0.4); line-height:1.8; max-width:720px; margin-bottom:8px;">The conflict reshapes the economies NZ depends on independent of what the government decides. China diverts GDP to military spending. The US mobilises. Global shipping through the Taiwan Strait — $5 trillion in annual trade — is in disruption. These are the trade channels where the numbers are clearest.</p>
      <p style="font-size:12px; color:rgba(255,255,255,0.25); line-height:1.7; max-width:720px; margin-bottom:28px; font-style:italic;">Note: NZ's food exports — dairy, meat — are strategic commodities in wartime. China's food security needs may moderate deliberate trade punishment, but cannot prevent the structural demand contraction that follows a contracting Chinese economy. Demand contraction figures use a 15–20% fall in Chinese purchasing of NZ commodities as a modelling assumption based on historical wartime demand contractions.</p>
      <div style="display:grid; grid-template-columns:repeat(5,1fr); gap:14px;">
        <div style="padding:18px; background:rgba(255,255,255,0.03); border-radius:12px; border-left:3px solid rgba(184,136,58,0.5);">
          <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:8px;">China demand contraction</div>
          <div style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:6px;">$3–4B</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">15–20% fall in Chinese demand for NZ dairy, meat, and logs — even with the FTA intact.</div>
        </div>
        <div style="padding:18px; background:rgba(255,255,255,0.03); border-radius:12px; border-left:3px solid rgba(184,136,58,0.5);">
          <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:8px;">Chinese tourism</div>
          <div style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:6px;">~$1.5B</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">Stops immediately — not a phased trade risk. Chinese visitor arrivals cease with the conflict itself, regardless of NZ's stance.</div>
        </div>
        <div style="padding:18px; background:rgba(255,255,255,0.03); border-radius:12px; border-left:3px solid rgba(184,136,58,0.5);">
          <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:8px;">US slowdown</div>
          <div style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:6px;">$700M–$1B</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">NZ's third-largest export market. Military mobilisation and conflict uncertainty drag on US growth.</div>
        </div>
        <div style="padding:18px; background:rgba(255,255,255,0.03); border-radius:12px; border-left:3px solid rgba(184,136,58,0.5);">
          <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:8px;">Taiwan Strait disruption</div>
          <div style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{CREAM}; line-height:1; margin-bottom:6px;">$5T</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">In annual global trade through the strait. Freight costs and commodity volatility hit NZ acutely as an isolated export economy.</div>
        </div>
        <div style="padding:18px; background:rgba(184,136,58,0.08); border-radius:12px; border:1px solid rgba(184,136,58,0.25);">
          <div style="font-size:10px; font-weight:600; letter-spacing:1px; color:{GOLD}; text-transform:uppercase; margin-bottom:8px;">Structural floor</div>
          <div style="font-family:'Fraunces',serif; font-size:20px; font-weight:300; color:{GOLD}; line-height:1; margin-bottom:6px;">~$5.5–6.5B</div>
          <div style="font-size:11px; color:rgba(255,255,255,0.35); line-height:1.6;">Lost revenue — ~1.5% of GDP. Applies regardless of what New Zealand decides. Everything after this is a political question.</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Decision Point ──────────────────────────────────────────────────── -->
  <div class="decision-section">
    <div class="decision-inner">

      <div class="decision-scenario">
        <p class="decision-scenario-label">Decision point 1 · 27 November 2027 · 90 minutes to respond</p>
        <h3 class="decision-scenario-title">The joint statement closes in 90 minutes. Every Five Eyes partner has signed. New Zealand has not.</h3>
        <p class="decision-scenario-body">The Foreign Minister is on the phone. The Prime Minister has the draft statement in front of them. The economic data is in the room. So is the ambassador's assessment. New Zealand has signed every previous joint statement with its Five Eyes partners. This one is different — China is not Russia. The trade exposure is not 0.3% of exports. It is 28%.</p>
      </div>

      <h2 class="decision-prompt">What does New Zealand do?</h2>
      <p class="decision-sub">Choose the Prime Minister's response. The economic data shows what follows each path.</p>

      <div class="choice-grid">

        <button class="choice-btn" id="choice-condemn" onclick="makeChoice('condemn')">
          <div class="choice-tag" style="color:{RED};">Option A — Condemn</div>
          <div class="choice-title">Sign the Five Eyes statement. Explicitly name China's action as a violation of international law.</div>
          <div class="choice-desc">NZ joins Australia, the US, UK, and Canada in a unified condemnation. The alliance holds. New Zealand signals it will follow the US lead.</div>
          <div class="choice-consequence">⚠ Economic retaliation risk — modelled on Australia 2020</div>
        </button>

        <button class="choice-btn" id="choice-measured" onclick="makeChoice('measured')">
          <div class="choice-tag" style="color:{GOLD};">Option B — Express concern</div>
          <div class="choice-title">Issue an independent statement expressing deep concern. Do not sign the joint Five Eyes condemnation.</div>
          <div class="choice-desc">NZ maintains its tradition of independent foreign policy. Expresses concern about stability and international law without naming China directly.</div>
          <div class="choice-consequence">↔ Pressure from both sides — NZ historical precedent</div>
        </button>

        <button class="choice-btn" id="choice-silent" onclick="makeChoice('silent')">
          <div class="choice-tag" style="color:rgba(255,255,255,0.4);">Option C — Stay silent</div>
          <div class="choice-title">No public statement. Cite New Zealand's independent foreign policy and the need for diplomacy over escalation.</div>
          <div class="choice-desc">NZ protects its trade relationship and avoids being drawn into a conflict 14,000 km away. But the silence is its own statement.</div>
          <div class="choice-consequence">↓ Five Eyes tension — strategic long-term cost</div>
        </button>

      </div>
    </div>
  </div>

  <!-- ── Consequence A: Condemn ──────────────────────────────────────────── -->
  <div id="consequence-condemn" class="consequence" style="background:#1A1E1A; border-top:2px solid {RED};">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:{RED};">You chose: Condemn — Option A</p>
        <h2 class="consequence-title">New Zealand signs the statement. China responds within 48 hours.</h2>
        <p class="consequence-body">Beijing announces an "indefinite suspension of all trade consultations with New Zealand pending a review of the bilateral relationship." No formal tariffs are announced — yet. But the informal signals are clear. Chinese state media publishes a list of Australian precedents. Fonterra's Shanghai office receives its first calls from buyers asking about "contract review timelines." The NZD falls 2–4% against the USD in overnight trading.</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">\$6.3B</div>
          <div class="data-card-label">Dairy exports at immediate risk — China is the only viable market for WMP at this volume</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">\$2.1B</div>
          <div class="data-card-label">Logs and timber exposed — China takes 55% of NZ log exports, alternatives are thin</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{GOLD};">\$4.2B</div>
          <div class="data-card-label">Goods surplus with China — this reverses immediately if retaliation mirrors the Australian model</div>
        </div>
      </div>

      <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:16px;">Sector-by-sector exposure</h4>
      <table class="exposure-table">
        <thead>
          <tr>
            <th>Commodity</th>
            <th>Annual value to China</th>
            <th>China dependency</th>
            <th>Replaceability</th>
            <th>Risk</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Whole milk powder</td>
            <td>\$4.2B</td>
            <td><div>60%</div><div class="bar-wrap"><div class="bar-fill" style="width:60%;background:{RED};"></div></div></td>
            <td>Very low</td>
            <td style="color:{RED};">Critical</td>
          </tr>
          <tr>
            <td>Logs and timber</td>
            <td>\$2.1B</td>
            <td><div>55%</div><div class="bar-wrap"><div class="bar-fill" style="width:55%;background:{RED};"></div></div></td>
            <td>Low</td>
            <td style="color:{RED};">High</td>
          </tr>
          <tr>
            <td>Butter and AMF</td>
            <td>\$2.1B</td>
            <td><div>35%</div><div class="bar-wrap"><div class="bar-fill" style="width:35%;background:{GOLD};"></div></div></td>
            <td>Moderate</td>
            <td style="color:{GOLD};">Medium</td>
          </tr>
          <tr>
            <td>Beef and lamb</td>
            <td>\$1.2B</td>
            <td><div>22%</div><div class="bar-wrap"><div class="bar-fill" style="width:22%;background:{GREEN};"></div></div></td>
            <td>High</td>
            <td style="color:{GREEN};">Lower</td>
          </tr>
          <tr>
            <td>Education services</td>
            <td>\$1.2B</td>
            <td><div>30%</div><div class="bar-wrap"><div class="bar-fill" style="width:30%;background:{GOLD};"></div></div></td>
            <td>None — immediate</td>
            <td style="color:{GOLD};">Medium · instant</td>
          </tr>
        </tbody>
      </table>

      <div style="margin-top:48px; border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div style="padding:28px 28px 0; border-bottom:2px solid {GREEN};">
          <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{GREEN}; margin-bottom:8px;">What the data also shows</p>
          <h4 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:20px;">Condemning has costs — but staying silent has different ones</h4>
        </div>
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">The Five Eyes relationship has tangible economic value.</strong><span class="policy-text">NZ's access to US, UK, and Australian intelligence networks underpins its defence posture. GCSB signals intelligence sharing has direct implications for cybersecurity, counterterrorism, and trade security. This is not a cost-free relationship — or a cost-free thing to damage.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">Australia found alternative markets — but not at the same scale.</strong><span class="policy-text">Australian barley found new buyers in Southeast Asia. Wine did not — the Chinese market was unique. NZ whole milk powder faces the same structural problem as Australian wine: China was not just the biggest buyer, it was almost the only buyer at this volume and price.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">The NZD is a direct transmission mechanism.</strong><span class="policy-text">NZ's currency is sensitive to commodity export sentiment. A sustained reduction in dairy export volumes would weaken the NZD — making imports more expensive and adding to an already stretched cost-of-living environment for New Zealand families.</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Consequence B: Measured ─────────────────────────────────────────── -->
  <div id="consequence-measured" class="consequence" style="background:#1A1E1A; border-top:2px solid {GOLD};">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:{GOLD};">You chose: Express concern — Option B</p>
        <h2 class="consequence-title">New Zealand walks its own line. Neither side is satisfied.</h2>
        <p class="consequence-body">New Zealand issues a statement calling for "restraint by all parties and respect for the principles of international law" — without naming China. The Five Eyes statement publishes without New Zealand's name, for the second time in a decade. Beijing notes the omission favourably but issues no formal reassurance. Washington signals "disappointment." The Australian Foreign Minister calls her NZ counterpart. This is where New Zealand has been before — and it is not a comfortable place to stand.</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <div class="data-card-num" style="color:{GOLD};">\$20.4B</div>
          <div class="data-card-label">Trade relationship initially protected — China makes no immediate move</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{GOLD};">2020</div>
          <div class="data-card-label">Last time NZ declined to join a Five Eyes statement — on Xinjiang. The trade relationship held, but so did the tension.</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:rgba(255,255,255,0.4);">Ongoing</div>
          <div class="data-card-label">Pressure from both sides does not resolve — it accumulates. The next decision point arrives sooner than expected.</div>
        </div>
      </div>

      <div style="margin-top:32px; padding:24px; background:rgba(184,136,58,0.06); border:1px solid rgba(184,136,58,0.2); border-radius:12px;">
        <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:12px;">The historical pattern</h4>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8; margin-bottom:16px;">New Zealand has used independent foreign policy positioning before — most notably in 2020 on Xinjiang, and in 1985 on nuclear ships. The 1985 decision cost NZ its formal ANZUS obligations with the US. The 2020 Xinjiang decision preserved trade but drew criticism from Five Eyes partners. <strong style="color:rgba(255,255,255,0.8);">The pattern is consistent: NZ independence is real, but it comes with a balance sheet.</strong></p>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8;">What is different in a Taiwan scenario is the scale and speed. The 1985 nuclear dispute played out over months. A Taiwan conflict would force decisions in hours — and the consequences of each choice would compound before the full picture was clear.</p>
      </div>

      <div style="margin-top:48px; border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div style="padding:28px 28px 0; border-bottom:2px solid {GOLD};">
          <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{GOLD}; margin-bottom:8px;">The deeper tension</p>
          <h4 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:20px;">Independent foreign policy is real — but so is the cost of choosing it</h4>
        </div>
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">Five Eyes is not just intelligence — it is infrastructure.</strong><span class="policy-text">GCSB access to the Five Eyes network means NZ receives threat intelligence it could not generate alone. Sustained friction with alliance partners does not immediately cut this off — but it changes the nature of what is shared and on what terms.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">China reads the gap in the statement — and files it.</strong><span class="policy-text">Beijing noted every country that did and did not sign the 2020 Xinjiang statement. Diplomatic memory is long. NZ's omission would be recorded as a point of leverage — not necessarily used immediately, but available.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">The next decision point comes faster.</strong><span class="policy-text">If conflict escalates — US forces engage, Australia commits ships, Taiwan formally requests military support — NZ will face a harder version of the same question within days. The measured response buys time. It does not resolve the underlying tension.</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Consequence C: Silent ───────────────────────────────────────────── -->
  <div id="consequence-silent" class="consequence" style="background:#1A1E1A; border-top:2px solid rgba(255,255,255,0.2);">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:rgba(255,255,255,0.5);">You chose: Stay silent — Option C</p>
        <h2 class="consequence-title">No statement. The trade relationship holds — and the alliance fractures.</h2>
        <p class="consequence-body">New Zealand issues nothing. The Five Eyes statement publishes with four names. Beijing makes no immediate economic move. But within 24 hours, the US National Security Advisor references "partners who have chosen commerce over principle." The Australian Prime Minister's office does not return calls. The GCSB Director receives a message from his NSA counterpart asking for a call at his earliest convenience. The silence was not neutral — it was a statement, and everyone understood it.</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <div class="data-card-num" style="color:rgba(255,255,255,0.5);">\$20.4B</div>
          <div class="data-card-label">Trade protected in the short term — no immediate Chinese retaliation</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">5 Eyes</div>
          <div class="data-card-label">Intelligence relationship under acute strain — access to shared signals may be restricted</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">ANZUS</div>
          <div class="data-card-label">NZ-US relationship — already complicated since 1985 — reaches a new low point</div>
        </div>
      </div>

      <div style="margin-top:32px; padding:24px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
        <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:12px;">What silence actually costs</h4>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8; margin-bottom:16px;">The trade relationship with China is worth $20.4 billion. But quantifying what Five Eyes membership is worth is harder — and that difficulty is itself the problem. The value is in what does not happen: cyberattacks that are detected before they land, threats that are shared before they materialise, intelligence that shapes policy before the crisis arrives.</p>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8;"><strong style="color:rgba(255,255,255,0.8);">There is no line on a spreadsheet for "intelligence not received."</strong> But New Zealand's defence posture — a small country with no ability to project force — depends almost entirely on the alliance network for its strategic awareness. Staying silent in this scenario does not make NZ neutral. It makes it alone.</p>
      </div>

      <div style="margin-top:48px; border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div style="padding:28px 28px 0; border-bottom:2px solid rgba(255,255,255,0.2);">
          <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:rgba(255,255,255,0.4); margin-bottom:8px;">The strategic cost</p>
          <h4 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:20px;">Short-term trade protection, long-term strategic isolation</h4>
        </div>
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">China does not reward silence — it banks it.</strong><span class="policy-text">Beijing's track record shows it does not offer concessions in exchange for diplomatic restraint. NZ's silence would be noted as useful — a precedent to be repeated — not as a basis for a more generous trade relationship. The $20.4B is not more secure because NZ stayed quiet. It is simply not yet in danger.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">The GCSB question becomes acute.</strong><span class="policy-text">New Zealand's signals intelligence capability is largely provided through Five Eyes infrastructure. A decision to stay silent on Taiwan would trigger a serious review of what intelligence NZ receives and on what terms. This has direct implications for domestic security — not just foreign policy optics.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">The trade relationship is not stable — it is suspended.</strong><span class="policy-text">China does not need to retaliate immediately. If it moves on Taiwan and succeeds, the dynamic of the entire region changes. A China that has absorbed Taiwan without Western consequence is a different trading partner than the one NZ signed an FTA with in 2008. Silence today does not guarantee the relationship tomorrow.</span></div>
        </div>
      </div>
    </div>
  </div>


  <!-- ── UNSC / UNGA context ───────────────────────────────────────────────── -->
  <div style="background:#0D1210; border-top:1px solid rgba(255,255,255,0.06); padding:80px 48px;">
    <div style="max-width:960px; margin:0 auto;">
      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{BLUE}; margin-bottom:16px;">The international response</p>
      <h2 style="font-family:'Fraunces',serif; font-size:32px; font-weight:300; color:{CREAM}; line-height:1.25; letter-spacing:-0.4px; margin-bottom:16px;">The Security Council convenes — and China vetoes within the hour</h2>
      <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:12px;">As a permanent member of the UN Security Council, China has an unconditional veto over any resolution directed at its own actions. This is not a technicality — it is the central structural problem with the international rules-based order when a great power is the one breaking the rules. The US tables a resolution condemning the blockade anyway. China vetoes it within the hour. Russia seconds the veto.</p>
      <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:40px;">The matter is referred to the <strong style="color:rgba(255,255,255,0.75);">UN General Assembly</strong> under the Uniting for Peace procedure — the same mechanism used after the Russian invasion of Ukraine in 2022. The UNGA resolution is non-binding. But who votes, who abstains, and who votes against will define the international response and determine what economic consequences follow.</p>

      <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:40px;">
        <div style="background:rgba(44,95,138,0.12); border:1px solid rgba(44,95,138,0.3); border-radius:12px; padding:20px;">
          <div style="font-family:'Fraunces',serif; font-size:36px; font-weight:300; color:{BLUE}; line-height:1; margin-bottom:8px;">141</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.6;">Nations voted to condemn Russia in March 2022 — the precedent this vote will follow</div>
        </div>
        <div style="background:rgba(184,136,58,0.1); border:1px solid rgba(184,136,58,0.25); border-radius:12px; padding:20px;">
          <div style="font-family:'Fraunces',serif; font-size:36px; font-weight:300; color:{GOLD}; line-height:1; margin-bottom:8px;">35</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.6;">Nations abstained on Russia — including India, representing 1.4 billion people. The abstain bloc would be larger for China.</div>
        </div>
        <div style="background:rgba(192,57,43,0.1); border:1px solid rgba(192,57,43,0.25); border-radius:12px; padding:20px;">
          <div style="font-family:'Fraunces',serif; font-size:36px; font-weight:300; color:{RED}; line-height:1; margin-bottom:8px;">5</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.6;">Voted against on Russia — Russia, Belarus, North Korea, Eritrea, Syria. The against bloc for China would include Russia.</div>
        </div>
      </div>

      <p style="font-size:13px; color:rgba(255,255,255,0.3); margin-bottom:24px; font-style:italic;">Projected UNGA alignment — based on Russia-Ukraine 2022 precedent. NZ position is the decision you are about to make.</p>
      <div style="background:#0D1210; border-radius:12px; overflow:hidden; border:1px solid rgba(255,255,255,0.06);">
        <div id="unga-map" style="width:100%; height:420px;"></div>
        <div style="padding:12px 16px; display:flex; gap:24px; border-top:1px solid rgba(255,255,255,0.06);">
          <div style="display:flex; align-items:center; gap:8px;"><span style="width:10px;height:10px;border-radius:50%;background:{BLUE};display:inline-block;"></span><span style="font-size:11px; color:rgba(255,255,255,0.4);">Likely condemn (~130 nations)</span></div>
          <div style="display:flex; align-items:center; gap:8px;"><span style="width:10px;height:10px;border-radius:50%;background:{GOLD};display:inline-block;"></span><span style="font-size:11px; color:rgba(255,255,255,0.4);">Likely abstain (~60+ nations, representative selection shown)</span></div>
          <div style="display:flex; align-items:center; gap:8px;"><span style="width:10px;height:10px;border-radius:50%;background:{RED};display:inline-block;"></span><span style="font-size:11px; color:rgba(255,255,255,0.4);">Likely vote against (~5 nations)</span></div>
          <div style="display:flex; align-items:center; gap:8px;"><span style="width:10px;height:10px;border-radius:50%;background:{GREEN};display:inline-block;"></span><span style="font-size:11px; color:rgba(255,255,255,0.4);">New Zealand — your decision</span></div>
        </div>
      </div>

      <div style="margin-top:32px; padding:28px 32px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
        <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:16px;">Before you decide on sanctions — understand what they would actually do</h4>
        <p style="font-size:14px; color:rgba(255,255,255,0.45); line-height:1.8; margin-bottom:14px;"><strong style="color:rgba(255,255,255,0.75);">The Russia parallel has limits.</strong> When the West sanctioned Russia, China continued trading — buying Russian oil at a discount and filling the gap left by Western firms. There is no equivalent absorber for China. China <em>is</em> the absorber. It is the world's largest manufacturer, the second largest economy, and the central node in the supply chains of most nations that would be imposing the sanctions. A coordinated sanctions package against China would be the most economically disruptive act in the history of the international trading system — and a significant share of that disruption would flow back to the sanctioning nations themselves.</p>
        <p style="font-size:14px; color:rgba(255,255,255,0.45); line-height:1.8; margin-bottom:14px;"><strong style="color:rgba(255,255,255,0.75);">For New Zealand, the sanctions calculus is particularly asymmetric.</strong> NZ represents roughly 0.2% of global GDP. Its participation in a sanctions coalition would contribute almost nothing to the economic pressure on China. But the sanctions themselves — by disrupting global supply chains, weakening NZ's trading partners, and accelerating inflation through a falling NZD and higher import costs — would damage the New Zealand economy through channels entirely separate from China's retaliation. NZ would absorb the consequences of the sanctions whether or not it joined them. Joining adds direct Chinese retaliation on top.</p>
        <p style="font-size:14px; color:rgba(255,255,255,0.45); line-height:1.8;"><strong style="color:rgba(255,255,255,0.75);">Sanctions are a weapon designed for countries that are peripheral to your supply chain.</strong> Russia was peripheral. China is not. The decision below is not simply about values versus trade — it is about whether NZ's symbolic participation in a sanctions regime meaningfully changes its outcome, or whether it primarily determines how much of the economic damage NZ absorbs directly versus indirectly.</p>
      </div>
    </div>
  </div>

  <!-- ── Decision Point 2 ────────────────────────────────────────────────── -->
  <div class="decision-section" style="border-top:1px solid rgba(44,95,138,0.3);">
    <div class="decision-inner">
      <div class="decision-scenario" style="background:rgba(44,95,138,0.1); border-color:rgba(44,95,138,0.3);">
        <p class="decision-scenario-label" style="color:{BLUE};">Decision point 2 · UN General Assembly</p>
        <h3 class="decision-scenario-title">The UNGA resolution is tabled. Every Five Eyes partner has announced they will vote to condemn. New Zealand has spoken with its major trading partners in Asia — several are abstaining. The vote is in four hours.</h3>
        <p class="decision-scenario-body">NZ voted yes to condemn Russia in 2022. But Russia took 0.3% of NZ exports. China takes 28%. The economics are different. So is the precedent. India — a democracy, a Commonwealth member, a Pacific partner — is abstaining. The choice is not simple.</p>
      </div>

      <h2 class="decision-prompt">How does New Zealand vote?</h2>
      <p class="decision-sub">This vote shapes whether international sanctions follow — and what that means for $20.4 billion in annual trade.</p>

      <div class="choice-grid">
        <button class="choice-btn" id="choice2-condemn-sanctions" onclick="makeChoice2('condemn-sanctions')">
          <div class="choice-tag" style="color:{BLUE};">Option A — Vote yes, back sanctions</div>
          <div class="choice-title">Condemn in UNGA and join the coordinated Western sanctions package.</div>
          <div class="choice-desc">NZ aligns fully with Five Eyes partners. Trade relationship with China takes the full impact. Secondary sanctions protection from the Western bloc.</div>
          <div class="choice-consequence">⚠ $20.4B trade exposure crystallises — NZ joins unprecedented sanctions</div>
        </button>
        <button class="choice-btn" id="choice2-condemn-nosanctions" onclick="makeChoice2('condemn-nosanctions')">
          <div class="choice-tag" style="color:{GOLD};">Option B — Vote yes, oppose sanctions</div>
          <div class="choice-title">Condemn China's action in the UNGA vote — but decline to join economic sanctions.</div>
          <div class="choice-desc">NZ separates the political condemnation from economic action. Precedent: Germany on Russia (NordStream). Partial protection of trade, partial satisfaction of alliance obligations.</div>
          <div class="choice-consequence">↔ Pressure from both sides — trade partially protected</div>
        </button>
        <button class="choice-btn" id="choice2-abstain" onclick="makeChoice2('abstain')">
          <div class="choice-tag" style="color:rgba(255,255,255,0.4);">Option C — Abstain</div>
          <div class="choice-title">Follow India's precedent. Abstain from the vote and call for immediate dialogue.</div>
          <div class="choice-desc">NZ joins the world's largest democracy and much of the Global South. The abstaining bloc may represent more of the world population than those who condemn.</div>
          <div class="choice-consequence">↓ Five Eyes relationship under severe strain — trade protected</div>
        </button>
      </div>
    </div>
  </div>

  <!-- ── DP2 Consequence A: Condemn + Sanctions ─────────────────────────── -->
  <div id="consequence2-condemn-sanctions" class="consequence" style="background:#1A1E1A; border-top:2px solid {BLUE};">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:{BLUE};">You chose: Vote yes, back sanctions — Option A</p>
        <h2 class="consequence-title">New Zealand joins the sanctions package. The trade relationship ends — for now.</h2>
        <p class="consequence-body">The Western sanctions coalition announces coordinated measures against China within 72 hours of the UNGA vote: targeted asset freezes, technology export controls, financial system restrictions. New Zealand's participation is symbolic in scale — NZ is not an economic giant — but its membership in the Five Eyes and its Pacific location make its position politically significant. Beijing suspends the FTA immediately. Fonterra's China operations are placed under review. The NZD falls to its lowest level against the USD since 2009.</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <div class="data-card-num" style="color:{BLUE};">\$20.4B</div>
          <div class="data-card-label">Annual exports to China — the full relationship now at risk, not just dairy</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">FTA suspended</div>
          <div class="data-card-label">China suspends the 2008 Free Trade Agreement — the first developed-nation FTA China ever signed</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{GOLD};">Unprecedented</div>
          <div class="data-card-label">No comparable sanctions package exists — China is 15x more economically significant than Russia was in 2022</div>
        </div>
      </div>

      <div style="padding:24px; background:rgba(44,95,138,0.08); border:1px solid rgba(44,95,138,0.2); border-radius:12px; margin-bottom:32px;">
        <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:12px;">The Russia comparison — and why it breaks down</h4>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8;">When the West sanctioned Russia in 2022, Russian GDP fell around 2% — far less than predicted, because India, China, and the Gulf absorbed much of the trade. <strong style="color:rgba(255,255,255,0.75);">There is no equivalent absorber for China.</strong> The global economy does not have a spare manufacturing base at Chinese scale. Sanctions on China would increase inflation across the sanctioning nations — including New Zealand — faster than they would damage China.</p>
      </div>

      <div style="border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div style="padding:28px 28px 0; border-bottom:2px solid {BLUE};">
          <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{BLUE}; margin-bottom:8px;">What NZ gains</p>
          <h4 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:20px;">Alignment has its own value — even at economic cost</h4>
        </div>
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">The Five Eyes relationship is preserved and deepened.</strong><span class="policy-text">Full participation in the sanctions coalition signals NZ as a reliable ally. Intelligence sharing continues at full capacity. US market access preferences and defence cooperation are maintained. The strategic relationship with Australia — NZ's most important security partner — holds.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">Diversification becomes policy, not aspiration.</strong><span class="policy-text">The economic shock forces what trade policy had not delivered: genuine diversification of export markets. Dairy finds lower-volume buyers across Southeast Asia, the Middle East, and Africa at lower prices. The transition is painful but the structural dependency is broken.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">The cost lands on ordinary New Zealanders.</strong><span class="policy-text">Dairy farmer incomes fall. The NZD weakens. Import costs rise. In a country already dealing with a cost-of-living crisis, the economic consequences of full alignment are not abstract — they are felt at the supermarket and at the mortgage payment.</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── DP2 Consequence B: Condemn, no sanctions ───────────────────────── -->
  <div id="consequence2-condemn-nosanctions" class="consequence" style="background:#1A1E1A; border-top:2px solid {GOLD};">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:{GOLD};">You chose: Vote yes, oppose sanctions — Option B</p>
        <h2 class="consequence-title">NZ condemns the action — but draws the line at sanctions. A position with precedent, and with costs.</h2>
        <p class="consequence-body">New Zealand votes yes in the UNGA but announces it will not join the Western sanctions package, citing the disproportionate economic impact on its export-dependent economy and the importance of maintaining dialogue channels. Germany made a similar argument about Russia and NordStream in 2022. It bought Germany some time — but not much goodwill. China notes the vote against it in UNGA. The sanctions question does not go away.</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <div class="data-card-num" style="color:{GOLD};">\$20.4B</div>
          <div class="data-card-label">Trade relationship initially intact — China does not immediately retaliate to a vote it expected</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{GOLD};">Partial</div>
          <div class="data-card-label">Five Eyes partners frustrated but not alienated — NZ condemned, which matters even without sanctions</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:rgba(255,255,255,0.4);">Unstable</div>
          <div class="data-card-label">The position is not sustainable long-term — as the conflict escalates, the gap between condemning and not sanctioning narrows</div>
        </div>
      </div>

      <div style="border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div style="padding:28px 28px 0; border-bottom:2px solid {GOLD};">
          <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{GOLD}; margin-bottom:8px;">The honest tension</p>
          <h4 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:20px;">Condemning without consequence is a position — but not a stable one</h4>
        </div>
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">Germany tried this with Russia — it did not hold.</strong><span class="policy-text">Germany initially resisted full sanctions citing energy dependency. Within weeks, under sustained alliance pressure and public opinion shifts, it moved to full alignment. The economic dependency that made sanctions unthinkable in February 2022 was largely severed by the end of the year. The question is not whether NZ would face the same pressure — it is how long before it does.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">China may retaliate to the vote regardless.</strong><span class="policy-text">Beijing does not distinguish cleanly between condemning and sanctioning. A yes vote in UNGA is itself a hostile act in Chinese diplomatic framing. The informal trade pressure that followed Australia in 2020 followed a far less explicit action than a UN condemnation vote.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">It buys time for diversification.</strong><span class="policy-text">If the conflict is prolonged, this position gives NZ 6-18 months to accelerate market diversification before the sanctions question becomes unavoidable. That window has real value — if it is used.</span></div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── DP2 Consequence C: Abstain ─────────────────────────────────────── -->
  <div id="consequence2-abstain" class="consequence" style="background:#1A1E1A; border-top:2px solid rgba(255,255,255,0.2);">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:rgba(255,255,255,0.5);">You chose: Abstain — Option C</p>
        <h2 class="consequence-title">NZ abstains. The trade relationship holds. The alliances do not.</h2>
        <p class="consequence-body">New Zealand abstains from the UNGA vote, joining India, Saudi Arabia, Indonesia, Brazil, and dozens of other nations in calling for immediate dialogue rather than condemnation. The abstaining bloc represents over half the world population. But the phone calls from Washington, London, Canberra, and Ottawa are not congratulatory. NZ voted yes on Russia in 2022. The gap between those two positions will define NZ's international reputation for a decade.</p>
      </div>

      <div class="data-grid">
        <div class="data-card">
          <div class="data-card-num" style="color:rgba(255,255,255,0.6);">\$20.4B</div>
          <div class="data-card-label">Trade relationship protected — Beijing views the abstention as meaningful and reciprocates with restraint</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">GCSB</div>
          <div class="data-card-label">Signals intelligence sharing reviewed — Five Eyes partners begin restricting what flows to New Zealand</div>
        </div>
        <div class="data-card">
          <div class="data-card-num" style="color:{RED};">Precedent broken</div>
          <div class="data-card-label">NZ voted to condemn Russia in 2022 — abstaining on China is a visible reversal with no principled distinction available</div>
        </div>
      </div>

      <div style="margin-top:28px; padding:24px; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08); border-radius:12px;">
        <h4 style="font-family:'Fraunces',serif; font-size:18px; font-weight:300; color:{CREAM}; margin-bottom:12px;">The 2022 precedent NZ cannot escape</h4>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8; margin-bottom:12px;">When the UNGA voted on Russia in March 2022, New Zealand voted yes to condemn. Russia took <strong style="color:rgba(255,255,255,0.7);">0.3%</strong> of NZ exports. China takes <strong style="color:rgba(255,255,255,0.7);">28%</strong>. The numbers explain the logic of abstaining. But the numbers are also exactly what makes it look like New Zealand's principles have a price tag. Every diplomat in Geneva, New York, and Beijing will do that arithmetic.</p>
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8;">India has been able to sustain its abstention on Russia partly because it is a major power with its own strategic weight. New Zealand does not have that latitude. Its credibility in international forums — the Pacific, climate, trade — rests on being seen as a principled small state. That reputation, once spent, is very difficult to rebuild.</p>
      </div>

      <div style="margin-top:32px; border:1px solid rgba(255,255,255,0.08); border-radius:12px; overflow:hidden;">
        <div style="padding:28px 28px 0; border-bottom:2px solid rgba(255,255,255,0.15);">
          <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:8px;">What abstaining actually costs</p>
          <h4 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:20px;">The trade is protected. Everything else is in question.</h4>
        </div>
        <div class="policy-row">
          <div class="policy-num">01</div>
          <div><strong class="policy-strong">Five Eyes intelligence access is formally reviewed.</strong><span class="policy-text">The NSA, GCHQ, ASD, and CSE each conduct their own review of what intelligence to continue sharing with GCSB. This does not happen in public. But it happens. The signals NZ stops receiving are the ones it does not know it has lost — until something goes wrong.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">02</div>
          <div><strong class="policy-strong">The Pacific relationships become complicated.</strong><span class="policy-text">NZ has invested heavily in Pacific diplomacy — competing with China for influence in Samoa, Tonga, Fiji, and the Solomon Islands. An abstention signals to Pacific island nations that China-adjacent positioning is viable even for a Western aligned state. NZ loses the moral authority it uses as its primary diplomatic tool in the Pacific.</span></div>
        </div>
        <div class="policy-row">
          <div class="policy-num">03</div>
          <div><strong class="policy-strong">The trade relationship is not guaranteed by the abstention.</strong><span class="policy-text">China does not offer formal assurances in exchange for diplomatic restraint. Beijing banks the abstention and moves on. NZ has given up strategic credibility for a trade relationship that remains subject to Chinese discretion — not NZ's choices.</span></div>
        </div>
      </div>
    </div>
  </div>


  <!-- ── AUKUS + Military Contribution Context ─────────────────────────── -->
  <div style="background:#0D1210; border-top:1px solid rgba(255,255,255,0.06); padding:80px 48px;">
    <div style="max-width:960px; margin:0 auto;">
      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:{RED}; margin-bottom:16px;">Decision point 3 · Coalition contribution · Hours 24–48</p>
      <h2 style="font-family:'Fraunces',serif; font-size:32px; font-weight:300; color:{CREAM}; line-height:1.25; letter-spacing:-0.4px; margin-bottom:16px;">The US is not deploying combat forces — not yet. It is assembling an intelligence and logistics coalition. Washington wants to know what New Zealand brings.</h2>
      <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:12px;">The most likely opening US posture is Option B — arms, intelligence, and financial pressure on China, without direct military engagement. That means the coalition being assembled in the first 48 hours is not a combat coalition. It is an intelligence-sharing network, a surveillance operation, and a logistics chain. The question being asked of New Zealand is not "will you send a warship" — it is "what capability can you contribute to supporting Taiwan's defence without crossing into direct combat." That question is harder to deflect. NZ has relevant assets. The P-8A Poseidon maritime surveillance aircraft is exactly the kind of capability this coalition needs — eyes over the Taiwan Strait, feeding targeting data and movement intelligence to allies. HMNZS Aotearoa provides replenishment and medical support that any sustained operation requires. Australia committed before dawn on 28 November. The UK signalled support by midday. Washington is working down its list.</p>
      <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:40px;">NZ has no legal obligation to answer yes. AUKUS — the pact signed in September 2021 between Australia, the United Kingdom, and the United States — explicitly excludes New Zealand. The barrier is the Nuclear Free Zone, Disarmament and Arms Control Act 1987, which prohibits nuclear-powered vessels from NZ waters, making AUKUS Pillar I legally impossible without repealing one of the most defining Acts in NZ's political history. There is no ANZUS obligation either — that ended in 1985. What NZ has is precedent and relationship. On <strong style="color:rgba(255,255,255,0.75);">25 September 2024</strong>, HMNZS Aotearoa transited the Taiwan Strait alongside HMAS Toowoomba and USS Ralph Johnson. It was a replenishment vessel, not a combat ship — but the signal was clear. This decision is the next signal. And it needs to be sent in the next 90 minutes.</p>
      <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:16px;">
        <div style="background:rgba(192,57,43,0.08); border:1px solid rgba(192,57,43,0.2); border-radius:12px; padding:22px;">
          <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:{RED}; margin-bottom:10px;">AUKUS status</div>
          <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1.2; margin-bottom:8px;">Not a member</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.6;">Nuclear Free Act 1987 prevents participation in Pillar I. No treaty obligation to act militarily alongside Australia or the US under AUKUS.</div>
        </div>
        <div style="background:rgba(184,136,58,0.08); border:1px solid rgba(184,136,58,0.2); border-radius:12px; padding:22px;">
          <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:{GOLD}; margin-bottom:10px;">Last gesture</div>
          <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1.2; margin-bottom:8px;">25 Sep 2024</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.6;">HMNZS Aotearoa transited the Taiwan Strait alongside Australia and the US. A replenishment vessel — symbolic and significant, not combat-capable.</div>
        </div>
        <div style="background:rgba(44,95,138,0.08); border:1px solid rgba(44,95,138,0.2); border-radius:12px; padding:22px;">
          <div style="font-size:10px; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; color:{BLUE}; margin-bottom:10px;">Combat assets</div>
          <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; line-height:1.2; margin-bottom:8px;">2 frigates</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.4); line-height:1.6;">HMNZS Te Kaha and Te Mana — aging ANZAC-class frigates. NZ's entire blue-water combat capability. Capable but not designed for peer adversary conflict at this scale.</div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── DP3: Military Contribution ─────────────────────────────────────── -->
  <div class="decision-section" style="border-top:1px solid rgba(192,57,43,0.25);">
    <div class="decision-inner">
      <div class="decision-scenario">
        <p class="decision-scenario-label">Decision point 3 · Coalition contribution · 6am, 28 November 2027</p>
        <h3 class="decision-scenario-title">The US State Department called New Zealand at 3am. The question is not whether to send a warship. It is whether to contribute what New Zealand actually has.</h3>
        <p class="decision-scenario-body">Washington is not asking for a combat commitment. It is asking what NZ will contribute to an intelligence, surveillance, and logistics coalition supporting Taiwan's defence. NZ has a P-8A Poseidon maritime patrol aircraft — one of the most capable surveillance platforms in the region. It has HMNZS Aotearoa, a replenishment vessel already deployed in the Pacific. It has GCSB signals intelligence feeding into Five Eyes. These are real assets in a real coalition. The NZDF Chief is in the room. The Prime Minister is on the phone. Cabinet has 90 minutes.</p>
      </div>
      <h2 class="decision-prompt">What does New Zealand tell Washington?</h2>
      <p class="decision-sub">The commitment is political, not yet operational. But absence from the planning table now is a permanent condition.</p>
      <div class="choice-grid">
        <button class="choice-btn" id="choice3-none" onclick="makeChoice3('none')">
          <div class="choice-tag" style="color:rgba(255,255,255,0.4);">Option A — Existing commitments only</div>
          <div class="choice-title">No additional contribution. NZ continues existing GCSB intelligence sharing and offers diplomatic support. No assets placed on standby.</div>
          <div class="choice-desc">NZ exercises its right as a non-AUKUS, post-ANZUS nation to limit its exposure. The P-8A stays at Whenuapai. Aotearoa continues its scheduled patrol. The position is legally clean. The trade relationship is undisturbed. New Zealand is not in the room when the coalition plans.</div>
          <div class="choice-consequence">↔ Trade protected — NZ excluded from coalition planning</div>
        </button>
        <button class="choice-btn" id="choice3-support" onclick="makeChoice3('support')">
          <div class="choice-tag" style="color:{GOLD};">Option B — Active non-combat contribution</div>
          <div class="choice-title">Place P-8A Poseidon on operational standby. Offer HMNZS Aotearoa for allied logistics. Share enhanced GCSB signals intelligence with the coalition.</div>
          <div class="choice-desc">NZ contributes what it genuinely has — surveillance, logistics, intelligence — without a combat commitment. The P-8A is a significant asset in this scenario. This extends the September 2024 Taiwan Strait precedent into an active coalition role and keeps NZ in every planning meeting.</div>
          <div class="choice-consequence">↑ Meaningful coalition role — no NZ personnel in direct combat</div>
        </button>
        <button class="choice-btn" id="choice3-combat" onclick="makeChoice3('combat')">
          <div class="choice-tag" style="color:{RED};">Option C — Full contribution including combat contingency</div>
          <div class="choice-title">All of Option B, plus: in-principle commitment that HMNZS Te Kaha will deploy if the US escalates to full military engagement.</div>
          <div class="choice-desc">NZ signals it will follow the US escalation path. No deployment today — Te Kaha is still in Devonport. But the commitment is on the record. If the US moves from Option B to Option A, New Zealand has already said it comes too. Beijing has this within hours.</div>
          <div class="choice-consequence">⚠ FTA strain begins immediately — Te Kaha deploys if US escalates</div>
        </button>
      </div>
    </div>
  </div>

  <!-- ── DP3 Consequence A: Diplomatic only ────────────────────────────── -->
  <div id="consequence3-none" class="consequence" style="background:#1A1E1A; border-top:2px solid rgba(255,255,255,0.2);">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:rgba(255,255,255,0.5);">You chose: Diplomatic and humanitarian only — Option A</p>
        <h2 class="consequence-title">NZ is not in the room. The coalition plans without New Zealand. The trade relationship holds.</h2>
        <p class="consequence-body">New Zealand relays its position to Washington before dawn: NZ will provide diplomatic support, humanitarian contributions, and continued GCSB intelligence sharing. It will not pre-commit military assets. The response is received. The planning meeting proceeds without NZ representation. Allies do not publicly criticise the decision — NZ's right to stay outside the military coalition is legally clear. But the briefings become narrower. The intelligence shared becomes more curated. The sense that NZ is a full partner in the alliance — rather than a beneficiary of it — begins to shift. The trade relationship with China is intact. Beijing notes the decision and files it.</p>
      </div>
      <div class="data-grid">
        <div class="data-card"><div class="data-card-num" style="color:rgba(255,255,255,0.5);">\$20.4B</div><div class="data-card-label">Trade relationship with China undisturbed — non-involvement is read by Beijing as the correct response</div></div>
        <div class="data-card"><div class="data-card-num" style="color:{GOLD};">Legal</div><div class="data-card-label">NZ's position is legally clean — no AUKUS obligation, no ANZUS requirement. The argument is correct and defensible.</div></div>
        <div class="data-card"><div class="data-card-num" style="color:{RED};">Excluded</div><div class="data-card-label">NZ is not in the coalition planning room. Decisions that affect NZ's region will be made without NZ input.</div></div>
      </div>
      <div style="margin-top:16px; display:flex; flex-direction:column; gap:8px;">
        <div data-compound-dp1="condemn" style="display:none; padding:14px 18px; background:rgba(192,57,43,0.08); border-left:3px solid rgba(192,57,43,0.4); border-radius:0 8px 8px 0;">
          <p style="font-size:12px; color:rgba(255,255,255,0.5); line-height:1.75;"><strong style="color:{RED};">Your path:</strong> You condemned China's action publicly — then declined to contribute militarily when the coalition was assembled. The gap between strong words and no action is the gap allies will remember. Condemnation without commitment reads as rhetoric.</p>
        </div>
        <div data-compound-dp1="silent" style="display:none; padding:14px 18px; background:rgba(255,255,255,0.04); border-left:3px solid rgba(255,255,255,0.15); border-radius:0 8px 8px 0;">
          <p style="font-size:12px; color:rgba(255,255,255,0.5); line-height:1.75;"><strong style="color:rgba(255,255,255,0.6);">Your path:</strong> Silent statement. No military commitment. The pattern is complete and consistent — NZ has prioritised the trade relationship and independent foreign policy at every point. China reads NZ as a managed partner. Allies are beginning to reach the same conclusion.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- ── DP3 Consequence B: Non-combat standby ──────────────────────────── -->
  <div id="consequence3-support" class="consequence" style="background:#1A1E1A; border-top:2px solid {GOLD};">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:{GOLD};">You chose: Non-combat standby — Option B</p>
        <h2 class="consequence-title">NZ is in the coalition. P-8A on standby. Aotearoa available. No combat commitment made.</h2>
        <p class="consequence-body">New Zealand confirms to Washington that NZ will place its P-8A Poseidon maritime surveillance aircraft on operational standby and make HMNZS Aotearoa available for allied logistics support if required. No combat deployment is committed. NZ is in every coalition planning meeting. The NZDF is coordinating with Australian and US counterparts. Beijing lodges a formal protest at NZ's "participation in hostile coalition preparations." New Zealand responds that it is contributing to the maintenance of international peace and security — not combatant operations. The trade relationship is under strain. The dairy industry is watching. The commitment is real and bounded.</p>
      </div>
      <div class="data-grid">
        <div class="data-card"><div class="data-card-num" style="color:{GOLD};">P-8A</div><div class="data-card-label">Poseidon maritime surveillance on standby from Whenuapai — real intelligence capability without combat exposure</div></div>
        <div class="data-card"><div class="data-card-num" style="color:{GOLD};">Aotearoa</div><div class="data-card-label">Replenishment and medical support vessel available — extending the September 2024 Taiwan Strait precedent into coalition operations</div></div>
        <div class="data-card"><div class="data-card-num" style="color:{RED};">FTA strain</div><div class="data-card-label">China protests formally. Informal signals on dairy contracts begin. The trade relationship is under direct pressure.</div></div>
      </div>
      <div style="margin-top:16px; display:flex; flex-direction:column; gap:8px;">
        <div data-compound-dp1="condemn" style="display:none; padding:14px 18px; background:rgba(58,92,69,0.08); border-left:3px solid rgba(58,92,69,0.5); border-radius:0 8px 8px 0;">
          <p style="font-size:12px; color:rgba(255,255,255,0.5); line-height:1.75;"><strong style="color:#8FAF8A;">Your path:</strong> You condemned China and have now committed to coalition support. The path from condemnation to contribution is internally consistent. NZ is in the Western coalition without combat risk — a position it can defend domestically and to Beijing.</p>
        </div>
        <div data-compound-dp1="silent" style="display:none; padding:14px 18px; background:rgba(192,57,43,0.08); border-left:3px solid rgba(192,57,43,0.4); border-radius:0 8px 8px 0;">
          <p style="font-size:12px; color:rgba(255,255,255,0.5); line-height:1.75;"><strong style="color:{RED};">Your path:</strong> You issued no public statement — then joined the coalition planning. Beijing considers the silence that preceded this a deception rather than prudence. The non-combat framing offers limited protection when China's foreign ministry has already characterised NZ's participation as hostile.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- ── DP3 Consequence C: Full coalition partner ───────────────────────── -->
  <div id="consequence3-combat" class="consequence" style="background:#1A1E1A; border-top:2px solid {RED};">
    <div class="consequence-inner">
      <div class="consequence-header">
        <p class="consequence-choice-label" style="color:{RED};">You chose: Full coalition partner — Option C</p>
        <h2 class="consequence-title">Te Kaha is named. The commitment is logged. China begins its response before a ship has sailed.</h2>
        <p class="consequence-body">New Zealand tells Washington: in principle, yes. HMNZS Te Kaha will be available for deployment if formally requested by the coalition. NZ takes its seat at the planning table. The NZDF Chief begins operational coordination with the US 7th Fleet and the Australian Defence Force. No deployment order is issued — Te Kaha is still in Devonport. But the commitment is on the record, and Beijing has it within hours. China's foreign ministry issues a statement describing NZ's posture as "deliberately provocative and contrary to the spirit of bilateral relations." Fonterra's Shanghai office receives an informal request for a meeting with the Ministry of Commerce. The NZD falls 2.1% on the foreign exchange market. Te Kaha has not yet sailed. The consequences have already begun.</p>
      </div>
      <div class="data-grid">
        <div class="data-card"><div class="data-card-num" style="color:{RED};">−1.5–3%</div><div class="data-card-label">NZD falls on the in-principle commitment alone — markets pricing in the trade risk before any deployment occurs</div></div>
        <div class="data-card"><div class="data-card-num" style="color:{GREEN};">Planning</div><div class="data-card-label">NZ is in every coalition planning meeting. NZDF coordinating with 7th Fleet and ADF. New Zealand has full situational awareness.</div></div>
        <div class="data-card"><div class="data-card-num" style="color:{RED};">FTA risk</div><div class="data-card-label">China signals trade consequences before Te Kaha leaves port. The FTA is under formal review in Beijing.</div></div>
      </div>
      <div style="padding:24px; background:rgba(192,57,43,0.07); border:1px solid rgba(192,57,43,0.2); border-radius:12px; margin-top:32px;">
        <p style="font-size:14px; color:rgba(255,255,255,0.5); line-height:1.8;">The commitment was made in the planning phase, not the deployment phase — which means NZ's leverage is limited when the formal request arrives. New Zealand said yes before the cost was fully known. <strong style="color:rgba(255,255,255,0.75);">That is what it means to be a coalition partner rather than a spectator.</strong></p>
      </div>
      <div style="margin-top:16px; display:flex; flex-direction:column; gap:8px;">
        <div data-compound-dp1="silent" style="display:none; padding:14px 18px; background:rgba(192,57,43,0.08); border-left:3px solid rgba(192,57,43,0.4); border-radius:0 8px 8px 0;">
          <p style="font-size:12px; color:rgba(255,255,255,0.5); line-height:1.75;"><strong style="color:{RED};">Your path:</strong> You issued no public statement on the conflict — then committed a warship in principle within 48 hours. Beijing reads the gap between public silence and private commitment as the most dangerous kind of duplicity. The silence made the commitment worse, not better.</p>
        </div>
        <div data-compound-dp1="condemn" style="display:none; padding:14px 18px; background:rgba(58,92,69,0.08); border-left:3px solid rgba(58,92,69,0.5); border-radius:0 8px 8px 0;">
          <p style="font-size:12px; color:rgba(255,255,255,0.5); line-height:1.75;"><strong style="color:#8FAF8A;">Your path:</strong> You condemned China publicly and have now committed to the coalition. The path is direct and consistent. NZ has made its alignment clear at every decision point. The economic cost is accumulating. The strategic clarity is complete.</p>
        </div>
      </div>
    </div>
  </div>

  <!-- ── Closing: Global Catastrophe + NZ Preparation ───────────────────── -->
  <div style="background:#0A0F0C; border-top:1px solid rgba(255,255,255,0.06); padding:96px 48px;">
    <div style="max-width:960px; margin:0 auto;">

      <p style="font-size:11px; font-weight:600; letter-spacing:1.4px; text-transform:uppercase; color:rgba(255,255,255,0.3); margin-bottom:20px;">Beyond the model</p>
      <h2 style="font-family:'Fraunces',serif; font-size:40px; font-weight:300; color:{CREAM}; line-height:1.2; letter-spacing:-0.5px; margin-bottom:32px; max-width:760px;">A Chinese occupation of Taiwan would be the largest geopolitical disruption since 1945. New Zealand is not prepared for it.</h2>

      <!-- The full economic picture -->
      <div style="margin-bottom:56px;">
        <h3 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:16px;">The numbers in this model are the floor, not the ceiling</h3>
        <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:16px;">The economic figures shown throughout this scenario capture only direct trade exposure — lost export revenue if China retaliates or its economy contracts. They do not include the full macroeconomic cascade. A conflict of this scale would trigger inflation through disrupted supply chains and a falling NZD. Business investment would freeze. KiwiSaver and superannuation funds would take significant hits as global markets reprice risk. Chinese tourism — worth roughly \$1.5B annually — would end immediately. The housing market, already fragile, would face sustained pressure as credit tightened and confidence collapsed.</p>
        <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px;">When all channels are included — trade, inflation, exchange rate, investment, tourism, and financial market exposure — the full economic impact of the worst-case scenario could be <strong style="color:rgba(255,255,255,0.7);">two to three times the trade figures alone</strong>. For New Zealanders, that is not an abstraction. It is mortgages, grocery bills, and jobs.</p>
      </div>

      <!-- Preparation argument -->
      <div style="margin-bottom:56px;">
        <h3 style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{CREAM}; margin-bottom:16px;">The time to think about this is not when the crisis arrives</h3>
        <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px; margin-bottom:16px;">New Zealand has national security frameworks — a National Security Strategy, a Defence Capability Plan, active Five Eyes commitments. What it does not have is anything comparable to Australia's Defence Strategic Review (2023) or National Defence Strategy (2024), both of which explicitly name the Indo-Pacific threat environment, model capability requirements against specific contingencies, and lay out a published framework for the decisions a government would face. New Zealand's equivalent documents are carefully worded. The word "Taiwan" does not appear as a planning scenario in any of them.</p>
        <p style="font-size:15px; color:rgba(255,255,255,0.45); line-height:1.85; max-width:760px;">The decisions explored in this model — public statement, UNGA vote, coalition posture, naval response, defence spending — would all need to be made under acute time pressure, without the benefit of prior public deliberation, in a media environment moving faster than any Cabinet process. Countries that navigate crises well are countries that have thought about them in advance. Not predicted them — thought about them. Explored the trade-offs. Understood the costs of each path before the phone rings at 3am. <strong style="color:rgba(255,255,255,0.65);">This model is an attempt to make those costs visible before the moment they become unavoidable.</strong></p>
      </div>

      <!-- Closing stat row -->
      <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:20px; padding-top:40px; border-top:1px solid rgba(255,255,255,0.07);">
        <div>
          <div style="font-family:'Fraunces',serif; font-size:36px; font-weight:300; color:{RED}; line-height:1; margin-bottom:8px;">5–8%</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.3); line-height:1.6;">Estimated full GDP impact in year one — central case. Includes trade, tourism, inflation, and investment freeze. Rising to ~10% under full US deployment with NZ in the coalition and sanctions joined.</div>
        </div>
        <div>
          <div style="font-family:'Fraunces',serif; font-size:36px; font-weight:300; color:{GOLD}; line-height:1; margin-bottom:8px;">Not named</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.3); line-height:1.6;">Taiwan does not appear as a planning scenario in any of NZ's published national security or defence strategy documents. Australia, the UK, and the US all go further.</div>
        </div>
        <div>
          <div style="font-family:'Fraunces',serif; font-size:36px; font-weight:300; color:{BLUE}; line-height:1; margin-bottom:8px;">90 min</div>
          <div style="font-size:12px; color:rgba(255,255,255,0.3); line-height:1.6;">Time the Prime Minister would have before the joint condemnation statement closes — faster than any prior public debate has prepared New Zealand to respond</div>
        </div>
      </div>

    </div>
  </div>

    <!-- ── Footer ──────────────────────────────────────────────────────────── -->
  <div style="background:{DARK}; padding:40px 48px; border-top:1px solid rgba(255,255,255,0.06); display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;">
    <div>
      <span style="font-size:13px; color:rgba(255,255,255,0.3);">Harvest · Scenario Model · Wellington, NZ</span>
      <p style="font-size:11px; color:rgba(255,255,255,0.2); margin-top:4px;">This is a hypothetical scenario using real trade data. It is not a forecast or policy recommendation. Trade figures: Stats NZ 2023. Five Eyes background: publicly available sources.</p>
    </div>
    <a href="index.html" style="font-size:13px; color:{GOLD}; text-decoration:none; border:1px solid rgba(184,136,58,0.35); border-radius:40px; padding:10px 20px; transition:all 0.2s;" onmouseover="this.style.background='rgba(184,136,58,0.1)'" onmouseout="this.style.background=''">← Back to portfolio</a>
  </div>

  <script>
  (function() {{

    var exportsData  = {exports_js};
    var portsData    = {ports_js};
    var routeData    = {route_js};
    var fiveEyesData  = {five_eyes_js};
    var navalData     = {naval_js};
    var ftaData       = {fta_js};
    var precedentData = {precedent_js};

    var PACIFIC       = {{ lat: [-50, 50],  lon: [110, 180] }};
    var NZ_CHINA      = {{ lat: [-48, 38],  lon: [112, 180] }};
    var NZ_CLOSE      = {{ lat: [-48, -32], lon: [164, 180] }};
    var TAIWAN_VIEW   = {{ lat: [19, 30],   lon: [113, 128] }};
    var AUS_NZ        = {{ lat: [-50, 8],   lon: [110, 180] }};
    var WORLD_VIEW    = {{ lat: [-55, 70],  lon: [-160, 175] }};

    var _currentView = {{ lat: PACIFIC.lat.slice(), lon: PACIFIC.lon.slice() }};
    var _zoomRaf = null;

    function animateZoom(target, duration) {{
      if (_zoomRaf) cancelAnimationFrame(_zoomRaf);
      var start = null;
      var from = {{ lat: _currentView.lat.slice(), lon: _currentView.lon.slice() }};
      function ease(t) {{ return t < 0.5 ? 2*t*t : -1+(4-2*t)*t; }}
      function step(ts) {{
        if (!start) start = ts;
        var t = Math.min((ts - start) / duration, 1);
        var e = ease(t);
        var lat = [from.lat[0]+(target.lat[0]-from.lat[0])*e, from.lat[1]+(target.lat[1]-from.lat[1])*e];
        var lon = [from.lon[0]+(target.lon[0]-from.lon[0])*e, from.lon[1]+(target.lon[1]-from.lon[1])*e];
        Plotly.relayout('trade-map', {{'geo.lataxis.range': lat, 'geo.lonaxis.range': lon}});
        if (t < 1) {{ _zoomRaf = requestAnimationFrame(step); }}
        else {{ _currentView = {{ lat: target.lat.slice(), lon: target.lon.slice() }}; }}
      }};
      _zoomRaf = requestAnimationFrame(step);
    }}

    // Trace 0: NZ marker
    var nzTrace = {{
      type: 'scattergeo', mode: 'markers+text',
      lat: [-41.3], lon: [174.8],
      text: ['New Zealand'],
      textposition: 'bottom center',
      textfont: {{ size: 11, color: '{GREEN}', family: 'Inter, sans-serif' }},
      marker: {{ size: [14], color: ['{GREEN}'], opacity: 0.95, line: {{ color: 'rgba(58,92,69,0.5)', width: 2 }} }},
      hovertemplate: '<b>New Zealand</b><br>$20.4B exports to China (2023)<extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 1: Chinese ports
    var portsTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: portsData.map(function(d){{ return d.lat; }}),
      lon: portsData.map(function(d){{ return d.lon; }}),
      text: portsData.map(function(d){{ return d.name; }}),
      marker: {{
        size: portsData.map(function(d){{ return d.size; }}),
        color: '{RED}', opacity: 0.85,
        line: {{ color: 'rgba(192,57,43,0.4)', width: 1 }},
        sizemode: 'diameter',
      }},
      hovertemplate: '<b>%{{text}}</b><br>Chinese import port<extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 2: Trade route line
    var routeTrace = {{
      type: 'scattergeo', mode: 'lines',
      lat: routeData.map(function(d){{ return d.lat; }}),
      lon: routeData.map(function(d){{ return d.lon; }}),
      line: {{ color: '{GOLD}', width: 2, dash: 'dot' }},
      opacity: 0.7,
      hoverinfo: 'none',
      showlegend: false, visible: false,
    }};

    // Trace 3: NZ export commodity markers
    var exportsTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: exportsData.map(function(d){{ return d.lat; }}),
      lon: exportsData.map(function(d){{ return d.lon; }}),
      text: exportsData.map(function(d){{ return d.commodity + ' $' + d.value_bn.toFixed(1) + 'B'; }}),
      marker: {{
        size: exportsData.map(function(d){{ return d.size; }}),
        color: '{GOLD}', opacity: 0.8,
        line: {{ color: 'rgba(184,136,58,0.4)', width: 1 }},
        sizemode: 'diameter',
      }},
      hovertemplate: '<b>%{{text}}</b><extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 4: Australia marker
    var ausTrace = {{
      type: 'scattergeo', mode: 'markers+text',
      lat: [-35.3], lon: [149.1],
      text: ['Australia'],
      textposition: 'bottom center',
      textfont: {{ size: 11, color: '#E67E22', family: 'Inter, sans-serif' }},
      marker: {{ size: [14], color: ['#E67E22'], opacity: 0.9, line: {{ color: 'rgba(230,126,34,0.4)', width: 2 }} }},
      hovertemplate: '<b>Australia</b><br>2020 China trade retaliation<extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 5: PLAN naval vessels
    var navalTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: navalData.map(function(d){{ return d.lat; }}),
      lon: navalData.map(function(d){{ return d.lon; }}),
      text: navalData.map(function(d){{ return d.name; }}),
      marker: {{
        size: 14, color: '{RED}', opacity: 0.9,
        symbol: 'triangle-up',
        line: {{ color: 'rgba(192,57,43,0.5)', width: 1.5 }},
      }},
      hovertemplate: '<b>%{{text}}</b><extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 6: Five Eyes (shown post-decision if condemn/measured)
    var fiveEyesTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: fiveEyesData.map(function(d){{ return d.lat; }}),
      lon: fiveEyesData.map(function(d){{ return d.lon; }}),
      text: fiveEyesData.map(function(d){{ return d.name; }}),
      marker: {{
        size: fiveEyesData.map(function(d){{ return d.size; }}),
        color: '#2C5F8A', opacity: 0.85,
        line: {{ color: 'rgba(44,95,138,0.4)', width: 1.5 }},
        sizemode: 'diameter',
      }},
      hovertemplate: '<b>%{{text}}</b><br>Five Eyes partner<extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 7: FTA partner markers
    var ftaTrace = {{
      type: 'scattergeo', mode: 'markers+text',
      lat: ftaData.map(function(d){{ return d.lat; }}),
      lon: ftaData.map(function(d){{ return d.lon; }}),
      text: ftaData.map(function(d){{ return d.name; }}),
      textposition: 'bottom center',
      textfont: {{ size: 10, color: '#4A9B7F', family: 'Inter, sans-serif' }},
      marker: {{ size: 12, color: '#4A9B7F', opacity: 0.9,
                 line: {{ color: 'rgba(74,155,127,0.4)', width: 1.5 }} }},
      hovertemplate: '<b>%{{text}}</b><br>FTA partner<extra></extra>',
      showlegend: false, visible: false,
    }};

    // Trace 8: Precedent country markers
    var precedentTrace = {{
      type: 'scattergeo', mode: 'markers+text',
      lat: precedentData.map(function(d){{ return d.lat; }}),
      lon: precedentData.map(function(d){{ return d.lon; }}),
      text: precedentData.map(function(d){{ return d.name; }}),
      textposition: 'top center',
      textfont: {{ size: 10, color: '#E67E22', family: 'Inter, sans-serif' }},
      marker: {{ size: 12, color: '#E67E22', opacity: 0.9, symbol: 'circle-open-dot',
                 line: {{ color: 'rgba(230,126,34,0.7)', width: 2 }} }},
      hovertemplate: '<b>%{{text}}</b><br>Spoke up — bore the cost<extra></extra>',
      showlegend: false, visible: false,
    }};

    var mapLayout = {{
      paper_bgcolor: '#0D1210',
      geo: {{
        scope: 'world',
        showland: true, landcolor: '#1C2B22',
        showocean: true, oceancolor: '#0D1210',
        showframe: false,
        showcoastlines: true, coastlinecolor: '#3A5040', coastlinewidth: 0.8,
        showcountries: true, countrycolor: '#2A3D30', countrywidth: 0.5,
        showlakes: false,
        lataxis: {{ range: PACIFIC.lat }},
        lonaxis: {{ range: PACIFIC.lon }},
        bgcolor: '#0D1210',
        projection: {{ type: 'mercator' }},
        resolution: 50,
      }},
      margin: {{ l:0, r:0, t:0, b:0 }},
      showlegend: false,
      dragmode: false,
    }};

    var cfg = {{ displayModeBar: false, responsive: true, scrollZoom: false }};
    Plotly.newPlot('trade-map', [nzTrace, portsTrace, routeTrace, exportsTrace, ausTrace, navalTrace, fiveEyesTrace, ftaTrace, precedentTrace], mapLayout, cfg);

    function showLegend(ids, show) {{
      ids.forEach(function(id) {{
        var el = document.getElementById(id);
        if (el) el.style.display = show ? 'flex' : 'none';
      }});
    }}

    function showStep(n) {{
      var legend = document.getElementById('map-legend');
      legend.style.display = n >= 1 ? 'flex' : 'none';

      showLegend(['leg-china'], n >= 1 && n <= 4);
      showLegend(['leg-route'], n === 3);
      showLegend(['leg-exports'], n === 2 || n === 3);
      showLegend(['leg-naval'], n === 6);
      showLegend(['leg-fta'], n === 4);
      showLegend(['leg-precedents'], n === 5);

      if (n === 0) {{
        Plotly.restyle('trade-map', {{ visible: [false,false,false,false,false,false,false,false,false] }}, [0,1,2,3,4,5,6,7,8]);
        animateZoom(PACIFIC, 800);

      }} else if (n === 1) {{
        Plotly.restyle('trade-map', {{ visible: true }}, [0, 1]);
        Plotly.restyle('trade-map', {{ visible: false }}, [2, 3, 4, 5, 6, 7, 8]);
        animateZoom(PACIFIC, 800);

      }} else if (n === 2) {{
        Plotly.restyle('trade-map', {{ visible: true }}, [0, 1, 3]);
        Plotly.restyle('trade-map', {{ visible: false }}, [2, 4, 5, 6, 7, 8]);
        animateZoom(NZ_CLOSE, 1000);

      }} else if (n === 3) {{
        Plotly.restyle('trade-map', {{ visible: true }}, [0, 1, 2, 3]);
        Plotly.restyle('trade-map', {{ visible: false }}, [4, 5, 6, 7, 8]);
        animateZoom(NZ_CHINA, 1000);

      }} else if (n === 4) {{
        Plotly.restyle('trade-map', {{ visible: true }}, [0, 1, 7]);
        Plotly.restyle('trade-map', {{ visible: false }}, [2, 3, 4, 5, 6, 8]);
        animateZoom(WORLD_VIEW, 1000);

      }} else if (n === 5) {{
        Plotly.restyle('trade-map', {{ visible: true }}, [0, 8]);
        Plotly.restyle('trade-map', {{ visible: false }}, [1, 2, 3, 4, 5, 6, 7]);
        animateZoom(WORLD_VIEW, 800);

      }} else if (n === 6) {{
        Plotly.restyle('trade-map', {{ visible: true }}, [5]);
        Plotly.restyle('trade-map', {{ visible: false }}, [0, 1, 2, 3, 4, 6, 7, 8]);
        animateZoom(TAIWAN_VIEW, 1200);
      }}
    }}

    scrollama().setup({{ step: '#steps-col .conf-step', offset: 0.5 }})
      .onStepEnter(function(r) {{
        document.querySelectorAll('#steps-col .conf-step').forEach(function(el, i) {{
          el.style.opacity = i === r.index ? '1' : '0.3';
        }});
        showStep(r.index);
      }});

    window.addEventListener('resize', function() {{ Plotly.Plots.resize('trade-map'); }});

  }})();

  // ── US Posture handler ───────────────────────────────────────────────────────
  function makeChoice0(option) {{
    choices.dp0 = option;
    ['full', 'arms', 'none'].forEach(function(c) {{
      var btn = document.getElementById('us-choice-' + c);
      if (!btn) return;
      btn.style.borderColor = (c === option) ? '{BLUE}' : 'rgba(44,95,138,0.3)';
      btn.style.opacity = (c === option) ? '1' : '0.35';
      btn.style.background = (c === option) ? 'rgba(44,95,138,0.18)' : 'rgba(44,95,138,0.08)';
    }});
    ['full', 'arms', 'none'].forEach(function(c) {{
      document.getElementById('us-consequence-' + c).style.display = 'none';
    }});
    var target = document.getElementById('us-consequence-' + option);
    target.style.display = 'block';
    setTimeout(function() {{
      target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}, 200);
  }}

  // ── Decision handler ────────────────────────────────────────────────────────
  var currentChoice = null;

  function makeChoice(option) {{
    currentChoice = option;
    choices.dp1 = option;

    var colors = {{ condemn: '{RED}', measured: '{GOLD}', silent: 'rgba(255,255,255,0.5)' }};
    ['condemn', 'measured', 'silent'].forEach(function(c) {{
      var btn = document.getElementById('choice-' + c);
      btn.classList.remove('chosen', 'faded');
      if (c === option) {{
        btn.classList.add('chosen');
        btn.style.borderColor = colors[c];
        btn.style.opacity = '1';
      }} else {{
        btn.classList.add('faded');
        btn.style.opacity = '0.3';
      }}
    }});

    ['condemn', 'measured', 'silent'].forEach(function(c) {{
      document.getElementById('consequence-' + c).style.display = 'none';
    }});

    var target = document.getElementById('consequence-' + option);
    target.style.display = 'block';
    applyCompound('consequence-' + option);
    setTimeout(function() {{
      target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}, 200);
  }}

  // ── UNGA map ──────────────────────────────────────────────────────────────────
  (function() {{
    var ungaCondemnData = {unga_condemn_js};
    var ungaAbstainData = {unga_abstain_js};
    var ungaAgainstData = {unga_against_js};

    var condemnTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: ungaCondemnData.map(function(d){{ return d.lat; }}),
      lon: ungaCondemnData.map(function(d){{ return d.lon; }}),
      text: ungaCondemnData.map(function(d){{ return d.name; }}),
      marker: {{ size: 10, color: '{BLUE}', opacity: 0.85, line: {{ color: 'rgba(44,95,138,0.4)', width: 1 }} }},
      hovertemplate: '<b>%{{text}}</b><br>Likely condemn<extra></extra>',
      showlegend: false,
    }};

    var abstainTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: ungaAbstainData.map(function(d){{ return d.lat; }}),
      lon: ungaAbstainData.map(function(d){{ return d.lon; }}),
      text: ungaAbstainData.map(function(d){{ return d.name; }}),
      marker: {{ size: 10, color: '{GOLD}', opacity: 0.85, line: {{ color: 'rgba(184,136,58,0.4)', width: 1 }} }},
      hovertemplate: '<b>%{{text}}</b><br>Likely abstain<extra></extra>',
      showlegend: false,
    }};

    var againstTrace = {{
      type: 'scattergeo', mode: 'markers',
      lat: ungaAgainstData.map(function(d){{ return d.lat; }}),
      lon: ungaAgainstData.map(function(d){{ return d.lon; }}),
      text: ungaAgainstData.map(function(d){{ return d.name; }}),
      marker: {{ size: 10, color: '{RED}', opacity: 0.85, line: {{ color: 'rgba(192,57,43,0.4)', width: 1 }} }},
      hovertemplate: '<b>%{{text}}</b><br>Likely vote against<extra></extra>',
      showlegend: false,
    }};

    var nzUngaTrace = {{
      type: 'scattergeo', mode: 'markers+text',
      lat: [-41.3], lon: [174.8],
      text: ['New Zealand'],
      textposition: 'bottom center',
      textfont: {{ size: 10, color: '{GREEN}', family: 'Inter, sans-serif' }},
      marker: {{ size: 13, color: '{GREEN}', opacity: 1, symbol: 'star',
                 line: {{ color: 'rgba(58,92,69,0.6)', width: 2 }} }},
      hovertemplate: '<b>New Zealand</b><br>Your decision<extra></extra>',
      showlegend: false,
    }};

    var ungaLayout = {{
      paper_bgcolor: '#0D1210',
      geo: {{
        scope: 'world',
        showland: true, landcolor: '#1C2B22',
        showocean: true, oceancolor: '#0D1210',
        showframe: false,
        showcoastlines: true, coastlinecolor: '#3A5040', coastlinewidth: 0.8,
        showcountries: true, countrycolor: '#2A3D30', countrywidth: 0.5,
        showlakes: false,
        bgcolor: '#0D1210',
        projection: {{ type: 'natural earth' }},
        resolution: 50,
      }},
      margin: {{ l:0, r:0, t:0, b:0 }},
      showlegend: false,
      dragmode: false,
    }};

    var ungaCfg = {{ displayModeBar: false, responsive: true, scrollZoom: false }};
    Plotly.newPlot('unga-map', [condemnTrace, abstainTrace, againstTrace, nzUngaTrace], ungaLayout, ungaCfg);
    window.addEventListener('resize', function() {{ Plotly.Plots.resize('unga-map'); }});
  }})();

  // ── Decision 2 handler ────────────────────────────────────────────────────────
  var currentChoice2 = null;

  function makeChoice2(option) {{
    currentChoice2 = option;
    choices.dp2 = option;

    var colors = {{
      'condemn-sanctions':   '{BLUE}',
      'condemn-nosanctions': '{GOLD}',
      'abstain':             'rgba(255,255,255,0.5)',
    }};

    ['condemn-sanctions', 'condemn-nosanctions', 'abstain'].forEach(function(c) {{
      var btn = document.getElementById('choice2-' + c);
      btn.classList.remove('chosen', 'faded');
      if (c === option) {{
        btn.classList.add('chosen');
        btn.style.borderColor = colors[c];
        btn.style.opacity = '1';
      }} else {{
        btn.classList.add('faded');
        btn.style.opacity = '0.3';
      }}
    }});

    ['condemn-sanctions', 'condemn-nosanctions', 'abstain'].forEach(function(c) {{
      document.getElementById('consequence2-' + c).style.display = 'none';
    }});

    var target = document.getElementById('consequence2-' + option);
    target.style.display = 'block';
    applyCompound('consequence2-' + option);
    setTimeout(function() {{
      target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}, 200);
  }}

  // ── Compounding system ────────────────────────────────────────────────────────
  var choices = {{}};

  function applyCompound(id) {{
    var el = document.getElementById(id);
    if (!el) return;
    ['dp0','dp1','dp2','dp3'].forEach(function(dp) {{
      el.querySelectorAll('[data-compound-' + dp + ']').forEach(function(note) {{
        note.style.display = (choices[dp] === note.getAttribute('data-compound-' + dp)) ? 'block' : 'none';
      }});
    }});
  }}

  // ── Decision 3 handler ────────────────────────────────────────────────────────
  var currentChoice3 = null;

  function makeChoice3(option) {{
    currentChoice3 = option;
    choices.dp3 = option;
    var colors = {{ none: 'rgba(255,255,255,0.5)', support: '{GOLD}', combat: '{RED}' }};
    ['none', 'support', 'combat'].forEach(function(c) {{
      var btn = document.getElementById('choice3-' + c);
      btn.classList.remove('chosen', 'faded');
      if (c === option) {{
        btn.classList.add('chosen');
        btn.style.borderColor = colors[c];
        btn.style.opacity = '1';
      }} else {{
        btn.classList.add('faded');
        btn.style.opacity = '0.3';
      }}
    }});
    ['none', 'support', 'combat'].forEach(function(c) {{
      document.getElementById('consequence3-' + c).style.display = 'none';
    }});
    var target = document.getElementById('consequence3-' + option);
    target.style.display = 'block';
    applyCompound('consequence3-' + option);
    setTimeout(function() {{
      target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}, 200);
  }}
  </script>

</body>
</html>"""

with open(PAGE, "w") as f:
    f.write(page)

print(f"Built → {PAGE}")
print(f"Trade exposure: NZD ${TOTAL_EXPORTS_BN:.1f}B | Dairy: ${DAIRY_BN:.1f}B | Logs: ${LOGS_BN:.1f}B")
