"""
RNZ Headline Analysis
----------------------
23 headlines fetched from RNZ on 18 March 2026.
Each headline was categorised by Claude AI into a topic.
Generates an interactive Plotly chart for the website.
"""

import plotly.graph_objects as go

# ── Data: headlines + AI-assigned categories ──────────────────────────────────
HEADLINES = [
    ("Shadows cast on Auckland's Sunfield development",                       "Housing & Infrastructure"),
    ("Iran confirms death of security chief Ali Larijani",                    "International"),
    ("Syndicate accused of bribing prison guards, bail officials",             "Crime & Justice"),
    ("Government, SPCA putting $1.2 million towards desexing dogs",           "Politics & Government"),
    ("Interest rates rise, so what's the best strategy now?",                 "Economy & Finance"),
    ("Hipkins says he considered his future in politics after ex-wife's claims","Politics & Government"),
    ("Is Nicola Willis's 'worst-case' scenario not bad enough?",              "Economy & Finance"),
    ("Speed limit confusion: NZTA reverses hundreds of fines",                "Politics & Government"),
    ("FENZ postpones decision on cutting 140 jobs",                           "Employment"),
    ("Government extends redress for abuse in state-run facilities up to 2022","Crime & Justice"),
    ("'Iran posed no imminent threat': Senior Trump official quits",          "International"),
    ("If Trump has already won in Iran, why is he now asking for help?",      "International"),
    ("Troubled pilot academy: Mayor backs review after $11m loss revealed",   "Politics & Government"),
    ("Investment property report sparks questions",                           "Economy & Finance"),
    ("Demand for New Zealand cream surges in China",                          "Economy & Finance"),
]

CATEGORY_COLOURS = {
    "Economy & Finance":      "#1E3A2A",
    "Politics & Government":  "#3A5C45",
    "International":          "#5A7D66",
    "Health & Wellbeing":     "#8FAF8A",
    "Crime & Justice":        "#B8883A",
    "Culture & Community":    "#C8A96E",
    "Sport":                  "#9AA398",
    "Housing & Infrastructure":"#6B5B45",
    "Employment":             "#A0856C",
    "Education":              "#7EB8F7",
}

# ── Aggregate ─────────────────────────────────────────────────────────────────
from collections import defaultdict
groups = defaultdict(list)
for headline, category in HEADLINES:
    groups[category].append(headline)

# Sort by count descending
sorted_cats  = sorted(groups.items(), key=lambda x: len(x[1]), reverse=True)
categories   = [c for c, _ in sorted_cats]
counts       = [len(h) for _, h in sorted_cats]
colours      = [CATEGORY_COLOURS.get(c, "#999") for c in categories]
hover_texts  = ["<br>".join(f"· {h}" for h in headlines) for _, headlines in sorted_cats]

# Reverse for horizontal bar (highest at top)
categories  = categories[::-1]
counts      = counts[::-1]
colours     = colours[::-1]
hover_texts = hover_texts[::-1]

# ── Chart ─────────────────────────────────────────────────────────────────────
fig = go.Figure()

fig.add_trace(go.Bar(
    x=counts,
    y=categories,
    orientation="h",
    marker_color=colours,
    customdata=hover_texts,
    hovertemplate="<b>%{y}</b><br>%{x} headlines<br><br>%{customdata}<extra></extra>",
    text=counts,
    textposition="outside",
    textfont=dict(size=12, color="#171717"),
    cliponaxis=False,
))

fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#171717"),
    margin=dict(l=20, r=60, t=110, b=60),
    height=420,

    title=dict(
        text=(
            "<b>What is New Zealand media talking about?</b><br>"
            "<span style='font-size:11px; color:#6B6B6B;'>"
            "<i>23 RNZ headlines categorised by Claude AI · 18 March 2026</i>"
            "</span>"
        ),
        x=0, xanchor="left", xref="paper",
        y=0.97, yanchor="top",
        font=dict(size=15, color="#171717", family="Fraunces, serif"),
    ),

    xaxis=dict(
        showgrid=True, gridcolor="#E0E0E0", gridwidth=1,
        zeroline=False, showline=False,
        tickfont=dict(size=10, color="#6B6B6B"),
        dtick=1,
    ),
    yaxis=dict(
        showgrid=False, zeroline=False, showline=False,
        tickfont=dict(size=12, color="#171717"),
    ),

    annotations=[dict(
        text="Source: Radio New Zealand (rnz.co.nz) · Categorised using Claude AI (Anthropic)",
        xref="paper", yref="paper",
        x=0, y=-0.12,
        showarrow=False,
        font=dict(size=8.5, color="#6B6B6B"),
        align="left",
    )],

    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#3A5C45",
        font_size=12,
        font_family="Inter, sans-serif",
        align="left",
    ),

    bargap=0.35,
)

fig.write_html(
    "rnz_chart.html",
    include_plotlyjs="cdn",
    full_html=False,
    config={"displayModeBar": False},
)

# Prepend Google Fonts so Inter & Fraunces load inside the iframe
FONT_IMPORT = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300&display=swap" rel="stylesheet">\n'
with open("rnz_chart.html", "r") as f:
    content = f.read()
with open("rnz_chart.html", "w") as f:
    f.write(FONT_IMPORT + content)

print("Chart saved → rnz_chart.html")
