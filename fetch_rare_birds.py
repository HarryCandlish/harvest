"""
Fetch Rare NZ Native Bird Sightings
-------------------------------------
Targets specific rare/endemic species by their GBIF taxon keys
and saves to nz_rare_birds.csv
"""

import requests
import csv
import time

BASE_URL = "https://api.gbif.org/v1/occurrence/search"

# GBIF species keys for target species + Maori name mapping
TARGET_SPECIES = {
    "Nestor notabilis":              ("Kea",       300),
    "Apteryx mantelli":              ("Kiwi",      300),
    "Apteryx australis":             ("Kiwi",      300),
    "Ninox novaeseelandiae":         ("Ruru",      300),
    "Cyanoramphus novaezelandiae":   ("Kākāriki",  300),
    "Anthornis melanura":            ("Korimako",  300),
    "Hymenolaimus malacorhynchos":   ("Whio",      300),
    "Falco novaeseelandiae":         ("Kārearea",  300),
    "Porphyrio hochstetteri":        ("Takahē",    300),
    "Petroica macrocephala":         ("Miromiro",  300),
    "Mohoua albicilla":              ("Pōpokotea", 300),
    "Limosa lapponica":              ("Kuaka",     300),
    "Megadyptes antipodes":          ("Hoiho",     300),
    "Eudyptula minor":               ("Kororā",    300),
    "Philesturnus carunculatus":     ("Tieke",     300),
    "Ardea modesta":                 ("Kōtuku",    100),  # only ~1,100 exist
}

FIELDS = [
    "species", "decimalLatitude", "decimalLongitude",
    "stateProvince", "year", "month", "day",
]

all_records = []

for species_name, (maori_name, limit) in TARGET_SPECIES.items():
    params = {
        "scientificName": species_name,
        "country":        "NZ",
        "hasCoordinate":  "true",
        "limit":          limit,
    }
    print(f"  Fetching {maori_name} ({species_name})...")
    try:
        r = requests.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        total   = data.get("count", len(results))
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
        print(f"    → {len(results)} plotted of {total:,} total records")
    except Exception as e:
        print(f"    → Error: {e}")
    time.sleep(0.3)

with open("nz_rare_birds.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "maoriName", "totalRecords", "species", "decimalLatitude", "decimalLongitude",
        "stateProvince", "year", "month", "day"
    ])
    writer.writeheader()
    writer.writerows(all_records)

print(f"\nTotal: {len(all_records)} sightings saved → nz_rare_birds.csv")
