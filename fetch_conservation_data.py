"""
fetch_conservation_data.py
Fetches DOC pesticide operations and Trap.NZ community trapping projects,
then cross-references spatially with existing GBIF predator/kiwi sightings.
Outputs: conservation_operations.csv, trapnz_projects.csv, region_summary.csv
"""

import requests
import json
import csv
import re
import math
from collections import defaultdict

# ── NZ bounding box ──────────────────────────────────────────────────────────
NZ_BBOX = {"minLat": -47.5, "maxLat": -34.0, "minLon": 166.0, "maxLon": 178.5}

# ── 1. Load existing predator/kiwi sightings from predator_data.js ──────────

def load_predator_data(filepath="predator_data.js"):
    print("Loading existing GBIF sighting data...")
    with open(filepath, "r") as f:
        raw = f.read()
    # Strip the JS variable assignment to get pure JSON
    raw = re.sub(r"^const PREDATOR_DATA\s*=\s*", "", raw.strip()).rstrip(";")
    data = json.loads(raw)

    sightings = []
    for sci_name, species in data.items():
        group = species.get("group", "unknown")
        for rec in species["records"]:
            lat, lon = rec[0], rec[1]
            year = rec[2] if len(rec) > 2 else None
            region = rec[3] if len(rec) > 3 else None
            sightings.append({
                "species": sci_name,
                "name": species["name"],
                "group": group,
                "lat": lat,
                "lon": lon,
                "year": year,
                "gbif_region": region,
            })
    print(f"  Loaded {len(sightings)} sightings across {len(data)} species")
    return sightings


# ── 2. Fetch DOC Operations Regions (11 polygons) ───────────────────────────

def fetch_doc_regions():
    print("Fetching DOC operations regions...")
    url = (
        "https://services1.arcgis.com/3JjYDyG3oajxU6HO/arcgis/rest/services/"
        "DOC_Operations_Regions/FeatureServer/0/query"
        "?where=1%3D1&outFields=RegionName,RegionCode&f=geojson&returnGeometry=true"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    features = r.json()["features"]
    print(f"  Got {len(features)} DOC regions")
    return features


# ── 3. Fetch DOC Pesticide Summary — completed operations ───────────────────

def fetch_doc_pesticide_ops(max_records=2000):
    print("Fetching DOC pesticide/predator control operations (completed)...")
    base = (
        "https://mapserver.doc.govt.nz/arcgis/rest/services/AnimalPests/"
        "PesticideSummary/MapServer/1/query"
    )
    all_features = []
    offset = 0
    batch = 500

    while True:
        params = {
            "where": "FinishDate >= DATE '2015-01-01'",
            "outFields": "BlockName,AreaName,StartDate,FinishDate,ActivityName,MethodName,Pesticide,LeadAgency,ControlMethodStatus",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "json",
            "resultOffset": offset,
            "resultRecordCount": batch,
        }
        r = requests.get(base, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        print(f"  Fetched {len(all_features)} operations so far...")
        if not data.get("exceededTransferLimit", False):
            break
        offset += batch
        if len(all_features) >= max_records:
            print(f"  Reached max_records limit ({max_records})")
            break

    print(f"  Total DOC operations fetched: {len(all_features)}")
    return all_features


# ── 4. Fetch Trap.NZ public project centroids ────────────────────────────────

def fetch_trapnz_projects(max_features=2000):
    print("Fetching Trap.NZ community project centroids...")
    all_features = []
    start_index = 0
    batch = 500

    while True:
        url = (
            "https://io.trap.nz/geo/tnzmaps/ows"
            "?service=WFS&version=1.0.0&request=GetFeature"
            "&typeName=tnzmaps%3Apublic_projects_centroid"
            "&outputFormat=application%2Fjson"
            f"&maxFeatures={batch}&startIndex={start_index}"
        )
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
        features = data.get("features", [])
        if not features:
            break
        all_features.extend(features)
        print(f"  Fetched {len(all_features)} Trap.NZ projects so far...")
        if len(features) < batch:
            break
        start_index += batch
        if len(all_features) >= max_features:
            print(f"  Reached max_features limit ({max_features})")
            break

    # Filter to NZ bounding box
    nz = [
        f for f in all_features
        if f.get("geometry") and
        NZ_BBOX["minLon"] <= f["geometry"]["coordinates"][0] <= NZ_BBOX["maxLon"] and
        NZ_BBOX["minLat"] <= f["geometry"]["coordinates"][1] <= NZ_BBOX["maxLat"]
    ]
    print(f"  Trap.NZ projects within NZ bbox: {len(nz)}")
    return nz


# ── 5. Simple point-in-bounding-box region assignment ───────────────────────
# We use approximate region bounding boxes since full polygon PIP is complex.
# Regions mapped to rough lat/lon ranges covering NZ.

REGION_BOXES = {
    "Northland":            {"minLat": -36.5, "maxLat": -34.5, "minLon": 172.5, "maxLon": 174.8},
    "Auckland":             {"minLat": -37.5, "maxLat": -36.5, "minLon": 174.0, "maxLon": 175.6},
    "Waikato":              {"minLat": -38.7, "maxLat": -37.0, "minLon": 174.5, "maxLon": 176.5},
    "Bay of Plenty":        {"minLat": -38.5, "maxLat": -37.5, "minLon": 175.5, "maxLon": 178.0},
    "East Coast":           {"minLat": -39.5, "maxLat": -37.8, "minLon": 176.5, "maxLon": 178.5},
    "Wellington":           {"minLat": -41.8, "maxLat": -39.5, "minLon": 174.5, "maxLon": 176.5},
    "Nelson Marlborough":   {"minLat": -42.5, "maxLat": -40.5, "minLon": 172.5, "maxLon": 174.5},
    "West Coast":           {"minLat": -44.5, "maxLat": -41.5, "minLon": 168.0, "maxLon": 172.0},
    "Canterbury":           {"minLat": -44.5, "maxLat": -42.0, "minLon": 170.5, "maxLon": 173.0},
    "Otago":                {"minLat": -46.5, "maxLat": -44.0, "minLon": 167.5, "maxLon": 171.5},
    "Southland":            {"minLat": -47.5, "maxLat": -45.5, "minLon": 166.5, "maxLon": 169.5},
}

def assign_region(lat, lon):
    for region, box in REGION_BOXES.items():
        if box["minLat"] <= lat <= box["maxLat"] and box["minLon"] <= lon <= box["maxLon"]:
            return region
    return "Unknown"


def polygon_centroid(rings):
    """Rough centroid from first ring of an Esri polygon geometry."""
    ring = rings[0]
    lons = [c[0] for c in ring]
    lats = [c[1] for c in ring]
    return sum(lats) / len(lats), sum(lons) / len(lons)


# ── 6. Build regional summary ────────────────────────────────────────────────

def build_summary(sightings, doc_ops, trapnz_projects):
    print("\nBuilding regional summary...")
    summary = defaultdict(lambda: {
        "kiwi_sightings": 0,
        "predator_sightings": 0,
        "doc_operations": 0,
        "trapnz_projects": 0,
    })

    # Count sightings
    for s in sightings:
        region = assign_region(s["lat"], s["lon"])
        if s["group"] == "kiwi":
            summary[region]["kiwi_sightings"] += 1
        else:
            summary[region]["predator_sightings"] += 1

    # Count DOC operations
    for op in doc_ops:
        geom = op.get("geometry", {})
        rings = geom.get("rings", [])
        if rings:
            lat, lon = polygon_centroid(rings)
        else:
            continue
        region = assign_region(lat, lon)
        summary[region]["doc_operations"] += 1

    # Count Trap.NZ projects
    for proj in trapnz_projects:
        geom = proj.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) >= 2:
            lon, lat = coords[0], coords[1]
            region = assign_region(lat, lon)
            summary[region]["trapnz_projects"] += 1

    return summary


# ── 7. Save outputs ──────────────────────────────────────────────────────────

def save_region_summary(summary, filepath="region_summary.csv"):
    rows = []
    for region, counts in summary.items():
        if region == "Unknown":
            continue
        rows.append({"region": region, **counts})
    rows.sort(key=lambda x: x["predator_sightings"], reverse=True)

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["region", "kiwi_sightings", "predator_sightings", "doc_operations", "trapnz_projects"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved region summary → {filepath}")
    print(f"\n{'Region':<25} {'Kiwi':>6} {'Predators':>10} {'DOC ops':>8} {'Trap.NZ':>8}")
    print("-" * 65)
    for row in rows:
        print(f"{row['region']:<25} {row['kiwi_sightings']:>6} {row['predator_sightings']:>10} {row['doc_operations']:>8} {row['trapnz_projects']:>8}")


def save_doc_ops(doc_ops, filepath="conservation_operations.csv"):
    rows = []
    for op in doc_ops:
        attrs = op.get("attributes", {})
        geom = op.get("geometry", {})
        rings = geom.get("rings", [])
        lat, lon = polygon_centroid(rings) if rings else (None, None)
        rows.append({
            "block_name": attrs.get("BlockName"),
            "area_name": attrs.get("AreaName"),
            "activity": attrs.get("ActivityName"),
            "method": attrs.get("MethodName"),
            "pesticide": attrs.get("Pesticide"),
            "lead_agency": attrs.get("LeadAgency"),
            "start_date": attrs.get("StartDate"),
            "finish_date": attrs.get("FinishDate"),
            "lat": lat,
            "lon": lon,
            "region": assign_region(lat, lon) if lat else "Unknown",
        })
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved DOC operations → {filepath} ({len(rows)} records)")


def save_trapnz(projects, filepath="trapnz_projects.csv"):
    rows = []
    for p in projects:
        props = p.get("properties", {})
        coords = p.get("geometry", {}).get("coordinates", [None, None])
        lon, lat = coords[0], coords[1]
        rows.append({
            "title": props.get("node_title"),
            "organisation": props.get("organisation"),
            "lat": lat,
            "lon": lon,
            "region": assign_region(lat, lon) if lat else "Unknown",
        })
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved Trap.NZ projects → {filepath} ({len(rows)} records)")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sightings  = load_predator_data("predator_data.js")
    doc_ops    = fetch_doc_pesticide_ops(max_records=3000)
    trapnz     = fetch_trapnz_projects(max_features=2000)

    if doc_ops:
        save_doc_ops(doc_ops)
    if trapnz:
        save_trapnz(trapnz)

    summary = build_summary(sightings, doc_ops, trapnz)
    save_region_summary(summary)

    print("\nDone. Run conservation_chart.py next to visualise the correlation.")
