"""
kiwisaver_forecast.py
─────────────────────────────────────────────────────────────────────────────
Forecasts the impact of two April 1 2026 KiwiSaver policy changes:

  1. Employer minimum contribution: 3% → 3.5% (including 16–17 year olds)
  2. Government member tax credit: max $521.43 → $260.72/year
     (Still 50c per $1 contributed, but cap halved — threshold drops from
      $1,042.86 to $521.44 of contributions to reach maximum)

Generates:
  ks_forecast_personal.html  — per-person net impact by income band
  ks_forecast_total.html     — total employer contributions by month, 2026
  ks_forecast_govt.html      — government savings from halving the credit

Assumptions (adjust constants below if better data is available):
  MEDIAN_SALARY      Stats NZ median annual earnings ($69k)
  MEAN_SALARY        Stats NZ mean annual earnings (~$76k)
  ACTIVE_EMPLOYEES   Employer-matched KiwiSaver members (~1.62m)
  FULL_CREDIT_MEMBERS Members receiving the full government tax credit (~1.5m)
  PARTIAL_CREDIT_MEMBERS Members receiving partial government tax credit (~200k)
  PARTIAL_AVG_OLD    Average govt credit for partial recipients under old rules
"""

import plotly.graph_objects as go
import calendar

# ── Adjustable assumptions ─────────────────────────────────────────────────────
MEDIAN_SALARY          = 69_000
MEAN_SALARY            = 76_000
ACTIVE_EMPLOYEES       = 1_620_000
FULL_CREDIT_MEMBERS    = 1_500_000   # contributed ≥ $1,042.86 — got full $521.43
PARTIAL_CREDIT_MEMBERS =   200_000   # contributed $521.44–$1,042.85 — got partial
PARTIAL_AVG_OLD        =   390.00    # avg govt credit for partial recipients (old)

OLD_EMPLOYER_RATE = 0.030
NEW_EMPLOYER_RATE = 0.035
EMPLOYER_INCREASE = 0.005

OLD_GOVT_MAX = 521.43
NEW_GOVT_MAX = 260.72
GOVT_REDUCTION = OLD_GOVT_MAX - NEW_GOVT_MAX   # $260.71

POLICY_MONTH = 4
YEAR         = 2026

# ── Colour palette ─────────────────────────────────────────────────────────────
GREEN_DARK  = "#1E3A2A"
GREEN_MID   = "#3A5C45"
GREEN_LT    = "#5A7D66"
GOLD        = "#B8883A"
RED_MUTED   = "#B85C45"
DARK        = "#171717"
GREY        = "#6B6B6B"
LINE_COL    = "#E0E0E0"
BG          = "#FFFFFF"

FONT_IMPORT = (
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600'
    '&family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;1,9..144,300'
    '&display=swap" rel="stylesheet">\n'
)


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
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(family="Inter, sans-serif", color=DARK),
        title=dict(
            text=(
                f"<b>{title_text}</b><br>"
                f"<span style='font-size:11px;color:{GREY};'><i>{subtitle_text}</i></span>"
            ),
            x=0.02, xanchor="left", y=0.95, yanchor="top",
            font=dict(size=15, color=DARK),
        ),
        height=360,
        margin=dict(l=60, r=30, t=120, b=50),
        hoverlabel=dict(bgcolor=BG, bordercolor=GREEN_MID, font_size=12,
                        font_family="Inter, sans-serif"),
    )


def esct_rate(salary):
    """NZ Employer Superannuation Contribution Tax rate by income band."""
    if salary <= 16_800:   return 0.105
    elif salary <= 57_600: return 0.175
    elif salary <= 84_000: return 0.300
    else:                  return 0.330


def govt_credit(annual_contribution, max_credit):
    """Government member tax credit: 50c per $1 contributed, up to max_credit."""
    return min(annual_contribution * 0.5, max_credit)


# ── Income bands for per-person analysis ──────────────────────────────────────
BANDS = [
    ("$30k",  30_000),
    ("$45k",  45_000),
    ("$60k",  60_000),
    ("$69k\n(median)", 69_000),
    ("$80k",  80_000),
    ("$100k", 100_000),
    ("$130k", 130_000),
]

EMPLOYEE_RATE = 0.03  # assuming 3% employee contribution rate

results = []
for label, salary in BANDS:
    esct       = esct_rate(salary)
    emp_contrib = salary * EMPLOYEE_RATE

    # Employer gain (net of ESCT)
    employer_gain_net = salary * EMPLOYER_INCREASE * (1 - esct)

    # Government credit: old and new
    old_credit = govt_credit(emp_contrib, OLD_GOVT_MAX)
    new_credit = govt_credit(emp_contrib, NEW_GOVT_MAX)
    govt_loss  = old_credit - new_credit

    net = employer_gain_net - govt_loss

    results.append({
        "label":            label,
        "salary":           salary,
        "employer_gain":    employer_gain_net,
        "govt_loss":        govt_loss,
        "net":              net,
        "old_total":        emp_contrib + salary * OLD_EMPLOYER_RATE * (1 - esct) + old_credit,
        "new_total":        emp_contrib + salary * NEW_EMPLOYER_RATE * (1 - esct) + new_credit,
    })

# Find break-even salary
# employer_gain_net = govt_loss → salary × 0.005 × (1 - esct(salary)) = 260.71
# In the $57,601–$84,000 bracket (ESCT 30%): salary × 0.005 × 0.70 = 260.71 → salary = $74,489
BREAKEVEN_SALARY = GOVT_REDUCTION / (EMPLOYER_INCREASE * (1 - esct_rate(74_489)))


# ── Government savings calculation ────────────────────────────────────────────
# Members receiving full credit under old rules (contributed ≥ $1,042.86)
old_full_spend    = FULL_CREDIT_MEMBERS * OLD_GOVT_MAX
new_full_spend    = FULL_CREDIT_MEMBERS * NEW_GOVT_MAX   # all now capped at new lower max
full_savings      = old_full_spend - new_full_spend

# Members receiving partial credit — those contributing $521.44–$1,042.85
# Under old rules: they got (contribution × 0.5) < $521.43
# Under new rules: they are capped at $260.72 (since their credit > $260.72)
partial_avg_new   = NEW_GOVT_MAX                         # all partial recipients now hit new cap
old_partial_spend = PARTIAL_CREDIT_MEMBERS * PARTIAL_AVG_OLD
new_partial_spend = PARTIAL_CREDIT_MEMBERS * partial_avg_new
partial_savings   = old_partial_spend - new_partial_spend

total_old_spend   = old_full_spend + old_partial_spend
total_new_spend   = new_full_spend + new_partial_spend
total_govt_saving = total_old_spend - total_new_spend

# Employer cost increase (gross, no ESCT — this is the employer's additional outlay)
monthly_increase  = ACTIVE_EMPLOYEES * MEAN_SALARY * EMPLOYER_INCREASE / 12
months_new_policy = 12 - POLICY_MONTH + 1
annual_employer_increase_gross = ACTIVE_EMPLOYEES * MEAN_SALARY * EMPLOYER_INCREASE

# Net into employee accounts (after ESCT, blended 22%)
BLENDED_ESCT = 0.22
annual_employer_increase_net = annual_employer_increase_gross * (1 - BLENDED_ESCT)


# ── Print summary ──────────────────────────────────────────────────────────────
print("=" * 64)
print("  KiwiSaver Policy Change Forecast — April 2026")
print("=" * 64)
print(f"\n  Change 1: Employer minimum 3% → 3.5%  (incl. 16–17 year olds)")
print(f"  Change 2: Govt member tax credit max $521.43 → $260.72/year\n")
print("  ── Per person (3% employee contribution rate) ──────────")
for r in results:
    tag = " ◄ break-even ~$74.5k" if abs(r["net"]) < 30 and r["salary"] in (69_000, 80_000) else ""
    print(f"  {r['label'].replace(chr(10),' '):18s}  "
          f"employer +${r['employer_gain']:5.0f}  "
          f"govt −${r['govt_loss']:5.0f}  "
          f"net {'+' if r['net']>=0 else ''}{r['net']:6.0f}{tag}")
print(f"\n  Break-even salary: ~${BREAKEVEN_SALARY:,.0f} — earners below lose out")
print()
print("  ── Government savings ──────────────────────────────────")
print(f"  Full credit members ({FULL_CREDIT_MEMBERS/1e6:.1f}m):  "
      f"${old_full_spend/1e6:.0f}m → ${new_full_spend/1e6:.0f}m  "
      f"(save ${full_savings/1e6:.0f}m)")
print(f"  Partial credit members ({PARTIAL_CREDIT_MEMBERS/1e3:.0f}k): "
      f"${old_partial_spend/1e6:.0f}m → ${new_partial_spend/1e6:.0f}m  "
      f"(save ${partial_savings/1e6:.0f}m)")
print(f"  Total govt saving:          ${total_govt_saving/1e6:.0f}m/year")
print()
print("  ── Employer cost increase ──────────────────────────────")
print(f"  Additional gross/year:      ${annual_employer_increase_gross/1e6:.0f}m")
print(f"  Additional net (ESCT 22%):  ${annual_employer_increase_net/1e6:.0f}m into accounts")
print()
print(f"  Govt saves:  ${total_govt_saving/1e6:.0f}m")
print(f"  Employers pay extra: ${annual_employer_increase_gross/1e6:.0f}m gross  "
      f"(${annual_employer_increase_net/1e6:.0f}m net to members)")
print(f"  The govt has shifted ~${total_govt_saving/1e6:.0f}m/year of KiwiSaver "
      f"cost onto employers.")
print("=" * 64)


# ── Chart 1: Per-person impact by income band ─────────────────────────────────
labels       = [r["label"] for r in results]
employer_gains = [r["employer_gain"] for r in results]
govt_losses  = [-r["govt_loss"] for r in results]   # negative = loss
nets         = [r["net"] for r in results]

fig1 = go.Figure()

fig1.add_trace(go.Bar(
    name="Employer contribution gain (net ESCT)",
    x=labels, y=employer_gains,
    marker_color=GREEN_MID,
    hovertemplate="<b>%{x}</b><br>Employer gain: +$%{y:.0f}<extra></extra>",
))

fig1.add_trace(go.Bar(
    name="Govt member tax credit reduction",
    x=labels, y=govt_losses,
    marker_color=RED_MUTED,
    hovertemplate="<b>%{x}</b><br>Govt credit lost: −$%{customdata:.0f}<extra></extra>",
    customdata=[r["govt_loss"] for r in results],
))

# Net line
fig1.add_trace(go.Scatter(
    name="Net change",
    x=labels, y=nets,
    mode="lines+markers",
    line=dict(color=GOLD, width=2.5),
    marker=dict(size=7, color=[GREEN_MID if n >= 0 else RED_MUTED for n in nets]),
    hovertemplate="<b>%{x}</b><br>Net: %{y:+.0f}/year<extra></extra>",
))

# Zero reference line
fig1.add_hline(y=0, line_width=1, line_color=LINE_COL)

# Break-even annotation
fig1.add_annotation(
    x="$80k", y=15,
    text=f"Break-even ~$74.5k<br>Below this: net worse off",
    showarrow=False, font=dict(size=9, color=GREY),
    bgcolor="rgba(255,255,255,0.85)", xanchor="center",
)

layout1 = base_layout(
    "Who gains and who loses — combined policy changes",
    "Per-person annual impact (NZD): employer gain vs government credit reduction",
)
layout1.update(dict(
    barmode="relative",
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=DARK)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickprefix="$", tickformat=",", tickfont=dict(size=10, color=GREY)),
    legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top",
                bgcolor="rgba(255,255,255,0.92)", bordercolor=LINE_COL, borderwidth=1,
                font=dict(size=10, color=DARK),
                itemclick=False, itemdoubleclick=False),
    margin=dict(l=60, r=30, t=120, b=50),
))
fig1.update_layout(**layout1)
fig1.write_html("ks_forecast_personal.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_forecast_personal.html",
         "Net of ESCT at marginal rates; 3% employee contribution assumed; break-even ~$74,500 salary")
print("Saved → ks_forecast_personal.html")


# ── Chart 2: Monthly employer contribution totals — 2026 ──────────────────────
months      = list(range(1, 13))
month_names = [calendar.month_abbr[m] for m in months]

old_monthly_net = [ACTIVE_EMPLOYEES * MEAN_SALARY * OLD_EMPLOYER_RATE / 12
                   * (1 - BLENDED_ESCT) / 1e6] * 12
new_monthly_net = []
for m in months:
    rate = NEW_EMPLOYER_RATE if m >= POLICY_MONTH else OLD_EMPLOYER_RATE
    new_monthly_net.append(
        ACTIVE_EMPLOYEES * MEAN_SALARY * rate / 12 * (1 - BLENDED_ESCT) / 1e6
    )

bar_colours = [GREEN_LT if m < POLICY_MONTH else GREEN_DARK for m in months]

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=month_names, y=old_monthly_net,
    name="Previous policy (3%)",
    mode="lines",
    line=dict(color=LINE_COL, width=2, dash="dot"),
    hovertemplate="<b>Previous (3%)</b><br>%{x}: $%{y:.0f}m<extra></extra>",
))
fig2.add_trace(go.Bar(
    x=month_names, y=new_monthly_net,
    name="New policy (3.5% from Apr)",
    marker_color=bar_colours,
    hovertemplate="<b>New policy</b><br>%{x}: $%{y:.0f}m<extra></extra>",
))
fig2.add_vline(x=2.5, line_width=1.5, line_dash="dash", line_color=GOLD)
fig2.add_annotation(
    x=2.5, y=max(new_monthly_net) * 0.62,
    text="3.5% minimum<br>takes effect", showarrow=False,
    font=dict(size=9, color=GOLD), xanchor="left",
    bgcolor="rgba(255,255,255,0.85)",
)

layout2 = base_layout(
    "Total employer contributions into KiwiSaver — 2026",
    f"Estimated monthly totals into accounts (net of ESCT, $m NZD) · {ACTIVE_EMPLOYEES/1e6:.2f}m employer-matched members",
)
layout2.update(dict(
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=10, color=GREY)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickprefix="$", ticksuffix="m", tickformat=",",
               tickfont=dict(size=10, color=GREY)),
    barmode="overlay",
    legend=dict(x=0.02, y=0.98, xanchor="left", yanchor="top",
                bgcolor="rgba(255,255,255,0.92)", bordercolor=LINE_COL, borderwidth=1,
                font=dict(size=10, color=DARK),
                itemclick=False, itemdoubleclick=False),
))
fig2.update_layout(**layout2)
fig2.write_html("ks_forecast_total.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_forecast_total.html",
         f"Assumptions: {ACTIVE_EMPLOYEES/1e6:.2f}m employer-matched members, mean salary ${MEAN_SALARY:,}, blended ESCT {BLENDED_ESCT*100:.0f}%")
print("Saved → ks_forecast_total.html")


# ── Chart 3: Government savings — old vs new member tax credit spend ───────────
categories   = ["Full credit\nmembers (1.5m)", "Partial credit\nmembers (200k)", "Total"]
old_values   = [old_full_spend / 1e6, old_partial_spend / 1e6, total_old_spend / 1e6]
new_values   = [new_full_spend / 1e6, new_partial_spend / 1e6, total_new_spend / 1e6]
savings_vals = [full_savings / 1e6, partial_savings / 1e6, total_govt_saving / 1e6]

fig3 = go.Figure()

fig3.add_trace(go.Bar(
    name="Previous (max $521.43)",
    x=categories, y=old_values,
    marker_color=GREEN_LT,
    hovertemplate="<b>%{x}</b><br>Old spend: $%{y:.0f}m<extra></extra>",
))
fig3.add_trace(go.Bar(
    name="New (max $260.72)",
    x=categories, y=new_values,
    marker_color=GREEN_DARK,
    hovertemplate="<b>%{x}</b><br>New spend: $%{y:.0f}m<extra></extra>",
))

# Savings annotations
for i, (cat, saving) in enumerate(zip(categories, savings_vals)):
    fig3.add_annotation(
        x=cat, y=old_values[i] + 15,
        text=f"−${saving:.0f}m",
        showarrow=False,
        font=dict(size=10, color=RED_MUTED, family="Inter, sans-serif"),
        xanchor="center",
    )

layout3 = base_layout(
    "Government member tax credit spend — before and after",
    "Annual outlay on KiwiSaver government contributions ($m NZD)",
)
layout3.update(dict(
    barmode="group",
    bargap=0.25,
    xaxis=dict(showgrid=False, zeroline=False, showline=False,
               tickfont=dict(size=11, color=DARK)),
    yaxis=dict(showgrid=True, gridcolor=LINE_COL, zeroline=False, showline=False,
               tickprefix="$", ticksuffix="m", tickformat=",",
               tickfont=dict(size=10, color=GREY),
               range=[0, max(old_values) * 1.2]),
    legend=dict(x=0.98, y=0.98, xanchor="right", yanchor="top",
                bgcolor="rgba(255,255,255,0.92)", bordercolor=LINE_COL, borderwidth=1,
                font=dict(size=10, color=DARK),
                itemclick=False, itemdoubleclick=False),
))
fig3.update_layout(**layout3)
fig3.write_html("ks_forecast_govt.html", include_plotlyjs="cdn",
                full_html=False, config={"displayModeBar": False})
finalize("ks_forecast_govt.html",
         f"Estimates: {FULL_CREDIT_MEMBERS/1e6:.1f}m members at full credit, {PARTIAL_CREDIT_MEMBERS/1e3:.0f}k at partial; actual IRD spend may differ")
print("Saved → ks_forecast_govt.html")

print("\nAll forecast charts generated.")
