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
    "Nestor notabilis":              "Kea",
    "Apteryx mantelli":              "Kiwi",
    "Apteryx australis":             "Kiwi",
    "Ninox novaeseelandiae":         "Ruru",
    "Cyanoramphus novaezelandiae":   "Kākāriki",
    "Cyanoramphus malherbi":         "Kākāriki",
    "Anthornis melanura":            "Korimako",
    "Hymenolaimus malacorhynchos":   "Whio",
    "Falco novaeseelandiae":         "Kārearea",
    "Porphyrio hochstetteri":        "Takahē",
    "Petroica macrocephala":         "Miromiro",
    "Mohoua albicilla":              "Pōpokotea",
    "Limosa lapponica":              "Kuaka",
    "Megadyptes antipodes":          "Hoiho",
    "Eudyptula minor":               "Kororā",
    "Philesturnus carunculatus":     "Tieke",
    "Ardea modesta":                 "Kōtuku",
    "Egretta alba":                  "Kōtuku",
}

FIELDS = [
    "species", "decimalLatitude", "decimalLongitude",
    "stateProvince", "year", "month", "day",
]

all_records = []

for species_name, maori_name in TARGET_SPECIES.items():
    params = {
        "scientificName": species_name,
        "country":        "NZ",
        "hasCoordinate":  "true",
        "limit":          100,
    }
    print(f"  Fetching {maori_name} ({species_name})...")
    try:
        r = requests.get(BASE_URL, params=params, timeout=20)
        r.raise_for_status()
        results = r.json().get("results", [])
        for row in results:
            all_records.append({
                "maoriName":        maori_name,
                "species":          row.get("species", species_name),
                "decimalLatitude":  row.get("decimalLatitude", ""),
                "decimalLongitude": row.get("decimalLongitude", ""),
                "stateProvince":    row.get("stateProvince", ""),
                "year":             row.get("year", ""),
                "month":            row.get("month", ""),
                "day":              row.get("day", ""),
            })
        print(f"    → {len(results)} sightings")
    except Exception as e:
        print(f"    → Error: {e}")
    time.sleep(0.3)

with open("nz_rare_birds.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "maoriName", "species", "decimalLatitude", "decimalLongitude",
        "stateProvince", "year", "month", "day"
    ])
    writer.writeheader()
    writer.writerows(all_records)

print(f"\nTotal: {len(all_records)} sightings saved → nz_rare_birds.csv")
