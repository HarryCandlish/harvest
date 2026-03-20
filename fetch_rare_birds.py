"""
Fetch Rare NZ Native Bird Sightings
-------------------------------------
Targets specific rare/endemic species by their GBIF taxon keys
and saves to nz_rare_birds.csv.
Set fetch_all=True to paginate and retrieve every available record.
"""

import requests
import csv
import time

BASE_URL = "https://api.gbif.org/v1/occurrence/search"
PAGE_SIZE = 300  # GBIF max per request

# (maori_name, fetch_all)
TARGET_SPECIES = {
    "Ardea modesta":               ("Kōtuku",  False),  # ~1,131 total — rarest
    "Hymenolaimus malacorhynchos": ("Whio",    False),  # ~4,637 total
    "Apteryx mantelli":            ("Kiwi",    True),   # ~2,999 total — fetch all
    "Apteryx australis":           ("Kiwi",    True),   # ~2,882 total — fetch all
    "Megadyptes antipodes":        ("Hoiho",   False),  # ~6,012 total
    "Porphyrio hochstetteri":      ("Takahē",  False),  # ~6,479 total
}

all_records = []

for species_name, (maori_name, fetch_all) in TARGET_SPECIES.items():
    print(f"  Fetching {maori_name} ({species_name})...")
    results = []
    offset  = 0

    while True:
        params = {
            "scientificName": species_name,
            "country":        "NZ",
            "hasCoordinate":  "true",
            "limit":          PAGE_SIZE,
            "offset":         offset,
        }
        try:
            r = requests.get(BASE_URL, params=params, timeout=20)
            r.raise_for_status()
            data   = r.json()
            page   = data.get("results", [])
            total  = data.get("count", 0)
            results.extend(page)

            if not fetch_all or data.get("endOfRecords") or not page:
                break

            offset += PAGE_SIZE
            time.sleep(0.3)

        except Exception as e:
            print(f"    → Error: {e}")
            break

    for row in results:
        all_records.append({
            "maoriName":        maori_name,
            "totalRecords":     total,
            "species":          row.get("species", species_name),
            "decimalLatitude":  row.get("decimalLatitude", ""),
            "decimalLongitude": row.get("decimalLongitude", ""),
            "stateProvince":    row.get("stateProvince", ""),
            "year":             row.get("year", ""),
            "month":            row.get("month", ""),
            "day":              row.get("day", ""),
        })
    print(f"    → {len(results)} fetched of {total:,} total records")
    time.sleep(0.3)

with open("nz_rare_birds.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "maoriName", "totalRecords", "species", "decimalLatitude", "decimalLongitude",
        "stateProvince", "year", "month", "day"
    ])
    writer.writeheader()
    writer.writerows(all_records)

print(f"\nTotal: {len(all_records)} sightings saved → nz_rare_birds.csv")
