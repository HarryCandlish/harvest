"""
KiwiSaver Analytics Charts
----------------------------
Generates four Plotly charts for the KiwiSaver page.
Data source: IRD Annual KiwiSaver Statistics (ird.govt.nz), as at 30 June 2025.
"""

import plotly.graph_objects as go

FONT_IMPORT = (
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600'
    '&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300'
    '&display=swap" rel="stylesheet">\n'
)

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


def finalize(filepath, source_text):
    with open(filepath, "r") as f:
        content = f.read()
    source_html = (
        f'<p style="margin:6px 0 0 4px; font-size:8.5px; color:#6B6B6B; '
        f'font-family:Inter,sans-serif;">{source_text}</p>\n'
    )
    with open(filepath, "w") as f:
        f.write(FONT_IMPORT + content + source_html)


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
        height=340,
        margin=dict(l=60, r=30, t=120, b=50),
        hoverlabel=dict(
            bgcolor=BG, bordercolor=GREEN_MID,
            font_size=12, font_family="Inter, sans-serif",
        ),
    )


# ── Data ──────────────────────────────────────────────────────────────────────

YEARS = list(range(2012, 2026))

FIRST_HOME_COUNT = [5890, 10720, 12720, 16180, 26570, 32680, 31920,
                    40150, 41370, 54520, 38740, 30200, 36960, 43600]
HARDSHIP_COUNT   = [6240,  6010,  7660,  8250, 10670, 14910, 15710,
                    16720, 18220, 19940, 14470, 20600, 32480, 45870]

FIRST_HOME_AMT = [62.7, 123.4, 159.0, 257.8, 495.0, 601.5, 712.5,
                  986.9, 1114.6, 1625.0, 1249.8, 974.7, 1372.7, 1860.7]
HARDSHIP_AMT   = [22.9, 23.1, 30.4, 41.1, 59.4, 69.9, 95.3,
                  104.5, 125.3, 147.9, 104.4, 173.0, 300.5, 471.2]

AGE_GROUPS      = ["0–17", "18–24", "25–34", "35–44", "45–54", "55–64", "65+"]
AGE_COUNTS_2025 = [169409, 393064, 739929, 736662, 590728, 537501, 237634]
AGE_COLOURS     = [GREEN_GHOST, GREEN_PALE, GREEN_MID, GREEN_DARK,
                   GREEN_LT, GOLD, "#A0856C"]

RATE_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
RATE_3PCT  = [948925,  1012660, 1069820, 1160363, 1169537, 1164017]
RATE_4PCT  = [348577,   342661,  337206,  329993,  315833,  304488]
RATE_6PCT  = [ 42738,    71184,   93165,  107086,  116521,  123925]
RATE_8PCT  = [144771,   140841,  130569,  117485,  107929,  101016]
RATE_10PCT = [ 48784,    74315,   87762,   92053,   98378,  105208]


# ── Chart 1: Withdrawal Counts ────────────────────────────────────────────────
fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=YEARS, y=FIRST_HOME_COUNT,
    name="First home purchase",
    mode="lines+markers",
    line=dict(color=GREEN_DARK, width=2.5),
    marker=dict(size=5),
    hovertemplate="<b>First home</b><br>%{x}: %{y:,} members<extra></extra>",
))
fig1.add_trace(go.Scatter(
    x=YEARS, y=HARDSHIP_COUNT,
    name="Financial hardship",
    mode="lines+markers",
    line=dict(color=GOLD, width=2.5),
    marker=dict(size=5),
    hovertemplate="<b>Financial hardship</b><br>%{x}: %{y:,} members<extra></extra>",
))

layout1 = base_layout(
    "First Home vs Hardship Withdrawals, 2012–2025",
    "Annual number of members making KiwiSaver withdrawals",
)
layout1.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY), dtick=2),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickformat=",", tickfont=dict(size=10, color=GREY)),
    legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top",
                bgcolor="rgba(255,255,255,0.92)", bordercolor=LINE_COL, borderwidth=1,
                font=dict(size=10, color=DARK),
                itemclick=False, itemdoubleclick=False),
))
fig1.update_layout(**layout1)
fig1.write_html("ks_withdrawals_count.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_withdrawals_count.html", "Source: IRD Annual KiwiSaver Statistics (ird.govt.nz)")
print("Saved → ks_withdrawals_count.html")


# ── Chart 2: Withdrawal Amounts ───────────────────────────────────────────────
fig2 = go.Figure()

fig2.add_trace(go.Bar(
    x=YEARS, y=FIRST_HOME_AMT,
    name="First home purchase",
    marker_color=GREEN_MID,
    hovertemplate="<b>First home</b><br>%{x}: $%{y:.0f}m<extra></extra>",
))
fig2.add_trace(go.Bar(
    x=YEARS, y=HARDSHIP_AMT,
    name="Financial hardship",
    marker_color=GOLD,
    hovertemplate="<b>Financial hardship</b><br>%{x}: $%{y:.0f}m<extra></extra>",
))

layout2 = base_layout(
    "KiwiSaver Withdrawal Amounts, 2012–2025",
    "Annual value withdrawn ($m NZD) by withdrawal type",
)
layout2.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY), dtick=2),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickprefix="$", ticksuffix="m", tickformat=",",
               tickfont=dict(size=10, color=GREY)),
    barmode="group",
    bargap=0.2,
    legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top",
                bgcolor="rgba(255,255,255,0.92)", bordercolor=LINE_COL, borderwidth=1,
                font=dict(size=10, color=DARK),
                itemclick=False, itemdoubleclick=False),
))
fig2.update_layout(**layout2)
fig2.write_html("ks_withdrawals_amount.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_withdrawals_amount.html", "Source: IRD Annual KiwiSaver Statistics (ird.govt.nz)")
print("Saved → ks_withdrawals_amount.html")


# ── Chart 3: Members by Age Group (2025) ─────────────────────────────────────
fig3 = go.Figure()

fig3.add_trace(go.Bar(
    x=AGE_COUNTS_2025,
    y=AGE_GROUPS,
    orientation="h",
    marker_color=AGE_COLOURS,
    text=[f"{c:,}" for c in AGE_COUNTS_2025],
    textposition="outside",
    textfont=dict(size=10, color=GREY),
    cliponaxis=False,
    hovertemplate="<b>%{y}</b><br>%{x:,} members<extra></extra>",
    showlegend=False,
))

layout3 = base_layout(
    "KiwiSaver Members by Age Group, 2025",
    "Total enrolled members as at 30 June 2025 — 3.4 million New Zealanders",
)
layout3.update(dict(
    xaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickformat=",", tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=11, color=DARK)),
    bargap=0.3,
    margin=dict(l=60, r=110, t=120, b=50),
))
fig3.update_layout(**layout3)
fig3.write_html("ks_age_groups.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_age_groups.html", "Source: IRD Annual KiwiSaver Statistics (ird.govt.nz)")
print("Saved → ks_age_groups.html")


# ── Chart 4: Contribution Rates (2020–2025) ───────────────────────────────────
rate_traces = [
    ("3%",  RATE_3PCT,  GREEN_DARK),
    ("4%",  RATE_4PCT,  GREEN_MID),
    ("6%",  RATE_6PCT,  GREEN_LT),
    ("8%",  RATE_8PCT,  GOLD),
    ("10%", RATE_10PCT, "#A0856C"),
]

fig4 = go.Figure()
for label, values, colour in rate_traces:
    fig4.add_trace(go.Scatter(
        x=RATE_YEARS, y=values,
        name=label,
        mode="lines+markers",
        line=dict(color=colour, width=2),
        marker=dict(size=6),
        hovertemplate=f"<b>{label}</b> %{{x}}: %{{y:,}} members<extra></extra>",
    ))

layout4 = base_layout(
    "Members by Contribution Rate, 2020–2025",
    "Active contributing members by elected employee contribution rate",
)
layout4.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY), dtick=1),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickformat=",", tickfont=dict(size=10, color=GREY)),
    legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top",
                bgcolor="rgba(255,255,255,0.92)", bordercolor=LINE_COL, borderwidth=1,
                font=dict(size=10, color=DARK),
                itemclick=False, itemdoubleclick=False),
))
fig4.update_layout(**layout4)
fig4.write_html("ks_contribution_rates.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_contribution_rates.html", "Source: IRD Annual KiwiSaver Statistics (ird.govt.nz)")
print("Saved → ks_contribution_rates.html")

print("\nAll KiwiSaver charts generated.")
