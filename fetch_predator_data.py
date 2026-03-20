"""
Fetch Kiwi + Predator Data for Scrollytelling Map
--------------------------------------------------
Outputs predator_data.js — loaded as a script tag in index.html.
Re-run this script to refresh the underlying GBIF data.
"""

import requests, json, time

BASE_URL  = "https://api.gbif.org/v1/occurrence/search"
PAGE_SIZE = 300
MIN_YEAR  = 2000

# (scientific_name, display_name, group, min_lat, max_lat)
SPECIES = [
    ("Apteryx mantelli",      "North Island Brown Kiwi", "kiwi",     -42.0, -34.0),
    ("Apteryx australis",     "Southern Brown Kiwi",     "kiwi",     -48.0, -40.0),
    ("Trichosurus vulpecula", "Possum",                  "predator", -48.0, -34.0),
    ("Rattus rattus",         "Ship rat",                "predator", -48.0, -34.0),
    ("Rattus norvegicus",     "Norway rat",              "predator", -48.0, -34.0),
    ("Mustela erminea",       "Stoat",                   "predator", -48.0, -34.0),
]

def fetch_species(sci_name, min_lat, max_lat):
    records, offset = [], 0
    while True:
        r = requests.get(BASE_URL, params={
            "scientificName": sci_name, "country": "NZ",
            "hasCoordinate": "true", "limit": PAGE_SIZE, "offset": offset,
        }, timeout=20)
        r.raise_for_status()
        data = r.json()
        for row in data.get("results", []):
            lat  = row.get("decimalLatitude")
            lon  = row.get("decimalLongitude")
            year = row.get("year")
            if not lat or not lon:
                continue
            if not (min_lat <= lat <= max_lat):
                continue
            if year and year < MIN_YEAR:
                continue
            records.append([
                round(lat, 4),
                round(lon, 4),
                year or "Unknown",
                row.get("stateProvince") or "Unknown",
            ])
        if data.get("endOfRecords") or not data.get("results"):
            break
        offset += PAGE_SIZE
        time.sleep(0.3)
    return records

output = {}
for sci_name, label, group, min_lat, max_lat in SPECIES:
    print(f"  Fetching {label}...")
    try:
        records = fetch_species(sci_name, min_lat, max_lat)
        output[sci_name] = {"name": label, "group": group, "records": records}
        print(f"    → {len(records)} records kept")
    except Exception as e:
        print(f"    → Error: {e}")
    time.sleep(0.3)

with open("predator_data.js", "w") as f:
    f.write("const PREDATOR_DATA=")
    json.dump(output, f, separators=(',', ':'))
    f.write(";")

print("\nSaved → predator_data.js")
