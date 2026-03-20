"""
conservation_chart.py
Visualises the relationship between citizen predator sightings,
DOC operations, and Trap.NZ community projects by NZ region.
Outputs: conservation_correlation.html
"""

import csv
import json

# ── Load region summary ───────────────────────────────────────────────────────

regions, kiwi, predators, doc_ops, trapnz = [], [], [], [], []

with open("region_summary.csv") as f:
    for row in csv.DictReader(f):
        regions.append(row["region"])
        kiwi.append(int(row["kiwi_sightings"]))
        predators.append(int(row["predator_sightings"]))
        doc_ops.append(int(row["doc_operations"]))
        trapnz.append(int(row["trapnz_projects"]))

total_ops = [d + t for d, t in zip(doc_ops, trapnz)]

# ── Colour each region by kiwi health (kiwi vs predator ratio) ───────────────
# High kiwi / low predator = green (healthy), low kiwi / high predator = red (at risk)

def health_colour(k, p):
    if p == 0:
        return "#3A5C45"
    ratio = k / (p + 1)
    if ratio > 2:
        return "#3A5C45"   # green — kiwi thriving
    elif ratio > 0.5:
        return "#B8883A"   # gold — moderate pressure
    else:
        return "#B85C45"   # red — high predator pressure

colours = [health_colour(k, p) for k, p in zip(kiwi, predators)]

# ── Annotations ──────────────────────────────────────────────────────────────

notable = {
    "Southland":          "Most kiwi, least predator pressure",
    "Wellington":         "Most predators — highest community response",
    "Canterbury":         "High predators, few operations",
    "West Coast":         "High DOC ops despite moderate predators",
    "Northland":          "High kiwi, strong community trapping",
}

# ── Build Plotly chart as HTML fragment ──────────────────────────────────────

BG     = "#F7F6F2"
FONT   = "Georgia, serif"
DARK   = "#1A1E1A"
MID    = "#4A5248"
GRID   = "rgba(0,0,0,0.07)"

# Escape for JS string
def js_str(s):
    return s.replace("'", "\\'")

# Build traces — one bubble per region
bubble_x   = predators
bubble_y   = total_ops
bubble_size = [max(8, k // 20 + 8) for k in kiwi]  # size by kiwi count
hover_texts = []
for i, r in enumerate(regions):
    note = notable.get(r, "")
    ht = (
        f"<b>{r}</b><br>"
        f"Predator sightings: {predators[i]:,}<br>"
        f"DOC operations: {doc_ops[i]}<br>"
        f"Trap.NZ projects: {trapnz[i]}<br>"
        f"Kiwi sightings: {kiwi[i]:,}"
        + (f"<br><i>{note}</i>" if note else "")
        + "<extra></extra>"
    )
    hover_texts.append(ht)

# Build annotation labels for notable regions
annotations_js = []
for i, r in enumerate(regions):
    if r in notable:
        annotations_js.append(f"""{{
            x: {predators[i]}, y: {total_ops[i]},
            xref: 'x', yref: 'y',
            text: '{js_str(r)}',
            showarrow: false,
            font: {{ size: 11, color: '{DARK}', family: 'Inter, sans-serif' }},
            xanchor: 'left',
            xshift: 10,
            yshift: 4,
        }}""")

# Legend items (manual)
legend_items = [
    {"colour": "#3A5C45", "label": "Kiwi thriving (high ratio)"},
    {"colour": "#B8883A", "label": "Moderate predator pressure"},
    {"colour": "#B85C45", "label": "High predator pressure"},
]

html = f"""<div id="conservation-chart" style="font-family:'Inter',sans-serif; background:{BG}; border-radius:12px; padding:32px;">
  <div style="margin-bottom:6px; font-size:11px; letter-spacing:1.2px; text-transform:uppercase; color:#9AA398; font-weight:500;">Citizen science vs conservation operations</div>
  <div style="font-family:'Fraunces',serif; font-size:22px; font-weight:300; color:{DARK}; margin-bottom:4px; letter-spacing:-0.3px;">Do operations follow the data?</div>
  <div style="font-size:13px; color:{MID}; margin-bottom:8px;">Each bubble is a NZ region. X axis: predator sightings from GBIF. Y axis: total conservation operations (DOC + community Trap.NZ). Bubble size reflects kiwi sightings.</div>
  <div style="display:flex; gap:16px; margin-bottom:16px; flex-wrap:wrap;">
    {''.join(f'<span style="display:flex; align-items:center; gap:6px; font-size:12px; color:{MID};"><span style="width:10px; height:10px; border-radius:50%; background:{l["colour"]}; display:inline-block;"></span>{l["label"]}</span>' for l in legend_items)}
  </div>
  <div id="cons-bubble" style="width:100%; height:480px;"></div>
  <div style="margin-top:20px; display:grid; grid-template-columns:1fr 1fr; gap:12px;">
    <div style="background:white; border-radius:8px; padding:16px 20px; border:1px solid rgba(0,0,0,0.07);">
      <div style="font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#3A5C45; margin-bottom:6px;">Where kiwi thrive</div>
      <div style="font-size:13px; color:{MID}; line-height:1.6;"><strong style="color:{DARK};">Southland</strong> has the most kiwi sightings (2,417) and the fewest predator records — suggesting that where human-introduced pressure remains low, kiwi populations hold. Few formal operations are needed because the threat hasn't arrived.</div>
    </div>
    <div style="background:white; border-radius:8px; padding:16px 20px; border:1px solid rgba(0,0,0,0.07);">
      <div style="font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em; color:#B85C45; margin-bottom:6px;">Where the community is filling the gap</div>
      <div style="font-size:13px; color:{MID}; line-height:1.6;"><strong style="color:{DARK};">Wellington</strong> has the highest predator density of any region, and the highest number of community Trap.NZ projects (323). The community is responding to what it observes — and the data shows it. <strong style="color:{DARK};">Canterbury</strong>, with similarly high predator counts but far fewer operations, stands out as a potential gap.</div>
    </div>
  </div>
  <div style="margin-top:12px; font-size:12px; color:#9AA398; line-height:1.6; padding-top:12px; border-top:1px solid rgba(0,0,0,0.07);">
    Sources: GBIF occurrence data via iNaturalist NZ · DOC Pesticide Summary (completed operations 2015–2025) · Trap.NZ public community projects · Regions assigned by approximate geographic bounding box.
  </div>
</div>

<script>
(function() {{
  var x     = {json.dumps(bubble_x)};
  var y     = {json.dumps(bubble_y)};
  var sizes = {json.dumps(bubble_size)};
  var cols  = {json.dumps(colours)};
  var regs  = {json.dumps(regions)};
  var htexts = {json.dumps(hover_texts)};

  Plotly.newPlot('cons-bubble', [{{
    type: 'scatter',
    mode: 'markers',
    x: x, y: y,
    text: regs,
    hovertemplate: htexts,
    marker: {{
      size: sizes,
      color: cols,
      opacity: 0.85,
      line: {{ color: 'white', width: 1.5 }},
    }},
    showlegend: false,
  }}], {{
    paper_bgcolor: '{BG}',
    plot_bgcolor: '{BG}',
    font: {{ family: 'Georgia, serif', color: '{DARK}', size: 12 }},
    margin: {{ l: 60, r: 20, t: 20, b: 60 }},
    xaxis: {{
      title: {{ text: 'Predator sightings (citizen science / GBIF)', font: {{ size: 11, color: '#9AA398' }} }},
      showgrid: true, gridcolor: '{GRID}', zeroline: false, tickfont: {{ size: 11 }},
    }},
    yaxis: {{
      title: {{ text: 'Total conservation operations (DOC + Trap.NZ)', font: {{ size: 11, color: '#9AA398' }} }},
      showgrid: true, gridcolor: '{GRID}', zeroline: false, tickfont: {{ size: 11 }},
    }},
    annotations: [{','.join(annotations_js)}],
    hoverlabel: {{
      bgcolor: 'white',
      bordercolor: '#DEDBD3',
      font: {{ size: 12, family: 'Inter, sans-serif', color: '{DARK}' }},
    }},
  }}, {{ displayModeBar: false, responsive: true }});
}})();
</script>"""

with open("conservation_correlation.html", "w") as f:
    f.write(html)

print("Saved → conservation_correlation.html")

# ── Print correlation observation ────────────────────────────────────────────

print("\n── Correlation check ──────────────────────────────────────────────────")
print(f"{'Region':<25} {'Predators':>10} {'Total ops':>10} {'Ratio':>8}")
print("-" * 58)
for i, r in enumerate(regions):
    ratio = total_ops[i] / (predators[i] + 1)
    print(f"{r:<25} {predators[i]:>10} {total_ops[i]:>10} {ratio:>8.2f}")
