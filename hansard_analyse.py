"""
hansard_analyse.py
─────────────────────────────────────────────────────────────────────────────
Reads hansard_2026.csv and generates keyword frequency charts for the
"Finding signal in the noise" page (hansard.html).

Run:  python3 hansard_analyse.py
Output: chart_keywords_bar.html, chart_keywords_share.html
"""

import csv
import re
import json
import plotly.graph_objects as go
from plotly.io import to_html

# ── Config ──────────────────────────────────────────────────────────────────
INPUT_CSV = "hansard_2026.csv"
BG        = "#1C1F1C"
PAPER     = "#1C1F1C"
FONT      = "Georgia, serif"
NAT_COL   = "#4A8FD4"   # National blue (lightened for dark bg)
LAB_COL   = "#E05A52"   # Labour red   (lightened for dark bg)
TEXT_COL  = "#D8D4C8"
GRID_COL  = "rgba(255,255,255,0.06)"

# ── Keyword categories ───────────────────────────────────────────────────────
CATEGORIES = {
    "Housing":       ["housing", "rent", "landlord", "tenancy", "first home", "homeless"],
    "Economy":       ["economy", "economic", "gdp", "growth", "jobs", "unemployment", "tax"],
    "Cost of Living": ["inflation", "cost of living", "grocery", "groceries", "fuel", "power", "afford"],
    "Healthcare":    ["health", "hospital", "healthcare", "medical", "mental health"],
    "Crime":         ["crime", "police", "gang", "prison", "sentencing", "violence"],
    "Environment":   ["climate", "emissions", "environment", "biodiversity", "water"],
    "Immigration":   ["immigration", "migrant", "visa", "border", "refugee", "deportation"],
    "Education":     ["education", "school", "teacher", "university", "student", "curriculum"],
}

NZF_COL    = "#C8B060"   # NZ First gold/amber
ACT_COL    = "#F5C400"   # ACT yellow
TPM_COL    = "#1A8C7C"   # Te Pāti Māori teal
GRN_COL    = "#098137"   # Green Party green

PARTIES = ["National", "Labour", "NZ First", "ACT", "Te Pāti Māori", "Green"]
PARTY_COLS = {"National": NAT_COL, "Labour": LAB_COL, "NZ First": NZF_COL, "ACT": ACT_COL, "Te Pāti Māori": TPM_COL, "Green": GRN_COL}

# ── Read data ────────────────────────────────────────────────────────────────
total_words    = {p: 0 for p in PARTIES}
total_articles = {p: 0 for p in PARTIES}
hits           = {p: {cat: 0 for cat in CATEGORIES} for p in PARTIES}

with open(INPUT_CSV, "r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        p = row.get("party", "")
        if p not in PARTIES:
            continue
        word_count = int(row.get("words", 0))
        total_words[p]    += word_count
        total_articles[p] += 1
        text = (row.get("text", "") + " " + row.get("title", "")).lower()
        for cat, kws in CATEGORIES.items():
            for kw in kws:
                hits[p][cat] += len(re.findall(r"\b" + re.escape(kw) + r"\b", text))

# ── Normalise: mentions per 1,000 words ─────────────────────────────────────
rates = {
    p: {cat: round(hits[p][cat] / total_words[p] * 1000, 2) for cat in CATEGORIES}
    for p in PARTIES
}

# Sort categories by combined total (most-discussed topics first)
sorted_cats = sorted(
    CATEGORIES.keys(),
    key=lambda c: sum(rates[p][c] for p in PARTIES),
    reverse=True
)

print("Keyword frequencies (per 1,000 words):")
print(f"  {'Category':<16}  {'National':>10}  {'Labour':>10}  {'Gap':>8}")
for cat in sorted_cats:
    gap = rates["Labour"][cat] - rates["National"][cat]
    sign = "+" if gap > 0 else ""
    print(f"  {cat:<16}  {rates['National'][cat]:>10.2f}  {rates['Labour'][cat]:>10.2f}  {sign}{gap:.2f}")

print(f"\n  Articles:  National {total_articles['National']}, Labour {total_articles['Labour']}")
print(f"  Words:     National {total_words['National']:,}, Labour {total_words['Labour']:,}")


# ── Base layout helper ───────────────────────────────────────────────────────
def base_layout(**kwargs):
    layout = dict(
        paper_bgcolor=PAPER,
        plot_bgcolor=BG,
        font=dict(family=FONT, color=TEXT_COL, size=13),
        margin=dict(l=20, r=20, t=60, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="left",   x=0,
            font=dict(size=13),
            bgcolor="rgba(0,0,0,0)",
        ),
    )
    layout.update(kwargs)
    return go.Layout(**layout)


# ══════════════════════════════════════════════════════════════════════════════
# Chart 1: Horizontal grouped bar — keyword frequency by topic
# ══════════════════════════════════════════════════════════════════════════════
fig1 = go.Figure()

for party in PARTIES:
    fig1.add_trace(go.Bar(
        name=party,
        y=sorted_cats,
        x=[rates[party][cat] for cat in sorted_cats],
        orientation="h",
        marker_color=PARTY_COLS[party],
        marker_line_width=0,
        opacity=0.92,
        hovertemplate="<b>%{y}</b><br>" + party + ": %{x:.2f} per 1,000 words<extra></extra>",
    ))

fig1.update_layout(base_layout(
    barmode="group",
    xaxis=dict(
        title="mentions per 1,000 words",
        title_font=dict(size=11, color="rgba(216,212,200,0.5)"),
        showgrid=True, gridcolor=GRID_COL, gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        showgrid=False,
        tickfont=dict(size=13),
        automargin=True,
    ),
    bargap=0.25,
    bargroupgap=0.06,
    margin=dict(l=20, r=30, t=60, b=40),
))

chart1_html = to_html(fig1, full_html=False, include_plotlyjs=False,
                      config={"displayModeBar": False, "responsive": True})

with open("chart_keywords_bar.html", "w", encoding="utf-8") as f:
    f.write(chart1_html)
print("\nWrote chart_keywords_bar.html")


# ══════════════════════════════════════════════════════════════════════════════
# Chart 2: Dot / diverging chart — Labour emphasis vs National (gap)
# ══════════════════════════════════════════════════════════════════════════════
gaps = {cat: rates["Labour"][cat] - rates["National"][cat] for cat in sorted_cats}
gap_sorted = sorted(sorted_cats, key=lambda c: gaps[c])

gap_values = [gaps[c] for c in gap_sorted]
gap_colors = [LAB_COL if g > 0 else NAT_COL for g in gap_values]
gap_labels = [
    f"Labour +{g:.2f}" if g > 0 else f"National +{abs(g):.2f}"
    for g in gap_values
]

fig2 = go.Figure()

# Zero line
fig2.add_vline(x=0, line_color="rgba(255,255,255,0.15)", line_width=1)

fig2.add_trace(go.Bar(
    y=gap_sorted,
    x=gap_values,
    orientation="h",
    marker_color=gap_colors,
    marker_line_width=0,
    opacity=0.88,
    customdata=gap_labels,
    hovertemplate="<b>%{y}</b><br>%{customdata}<extra></extra>",
    showlegend=False,
))

fig2.update_layout(base_layout(
    xaxis=dict(
        title="gap in mentions per 1,000 words (Labour vs National)",
        title_font=dict(size=11, color="rgba(216,212,200,0.5)"),
        showgrid=True, gridcolor=GRID_COL, gridwidth=1,
        zeroline=False,
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        showgrid=False,
        tickfont=dict(size=13),
        automargin=True,
    ),
    margin=dict(l=20, r=30, t=60, b=40),
))

# Annotations: party labels on each side
fig2.add_annotation(
    x=min(gap_values) * 0.5, y=1.06, xref="x", yref="paper",
    text="← National leads", showarrow=False,
    font=dict(size=11, color=NAT_COL), xanchor="center",
)
fig2.add_annotation(
    x=max(gap_values) * 0.5, y=1.06, xref="x", yref="paper",
    text="Labour leads →", showarrow=False,
    font=dict(size=11, color=LAB_COL), xanchor="center",
)

chart2_html = to_html(fig2, full_html=False, include_plotlyjs=False,
                      config={"displayModeBar": False, "responsive": True})

with open("chart_keywords_gap.html", "w", encoding="utf-8") as f:
    f.write(chart2_html)
print("Wrote chart_keywords_gap.html")

# ── Write stats JSON for embedding in hansard.html ───────────────────────────
stats = {
    "total_articles": total_articles,
    "total_words":    total_words,
    "rates":          rates,
    "gaps":           {cat: round(gaps[cat], 2) for cat in CATEGORIES},
    "sorted_cats":    sorted_cats,
}
with open("hansard_stats.json", "w") as f:
    json.dump(stats, f, indent=2)
print("Wrote hansard_stats.json")
