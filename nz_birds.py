"""
NZ Bird Data Fetcher
--------------------
Pulls New Zealand bird occurrence data from the GBIF API and saves
two CSVs ready for Power BI:

  nz_bird_occurrences.csv  — individual sighting records
  nz_bird_species.csv      — unique species summary

GBIF API docs: https://techdocs.gbif.org/en/openapi/
No API key required for read-only requests.
"""

import requests
import csv
import time

# ── CONFIG ──────────────────────────────────────────────────────────────────
COUNTRY = "NZ"          # ISO country code for New Zealand
CLASS_KEY = 212         # GBIF taxon key for Aves (birds)
RECORDS_TO_FETCH = 500  # increase this for more data (max 300 per page)
OUTPUT_OCCURRENCES = "nz_bird_occurrences.csv"
OUTPUT_SPECIES     = "nz_bird_species.csv"
# ────────────────────────────────────────────────────────────────────────────

BASE_URL = "https://api.gbif.org/v1/occurrence/search"

FIELDS = [
    "key",
    "species",
    "genus",
    "family",
    "order",
    "vernacularName",
    "decimalLatitude",
    "decimalLongitude",
    "stateProvince",
    "locality",
    "year",
    "month",
    "day",
    "individualCount",
    "occurrenceStatus",
    "datasetName",
    "recordedBy",
    "basisOfRecord",
]

def fetch_occurrences(total=500):
    records = []
    page_size = 300
    offset = 0
    pages = (total + page_size - 1) // page_size

    for page in range(pages):
        limit = min(page_size, total - offset)
        params = {
            "country":    COUNTRY,
            "classKey":   CLASS_KEY,
            "hasCoordinate": "true",
            "limit":      limit,
            "offset":     offset,
        }
        print(f"  Fetching records {offset + 1}–{offset + limit}...")
        resp = requests.get(BASE_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        results = data.get("results", [])
        if not results:
            print("  No more records available.")
            break

        records.extend(results)
        offset += limit

        if data.get("endOfRecords"):
            break

        time.sleep(0.5)  # be polite to the API

    return records


def flatten(record):
    """Pull only the fields we want from a raw GBIF occurrence record."""
    return {field: record.get(field, "") for field in FIELDS}


def build_species_summary(records):
    """Aggregate occurrence records into a per-species summary."""
    species_map = {}
    for r in records:
        name = r.get("species") or r.get("genus") or "Unknown"
        if name not in species_map:
            species_map[name] = {
                "species":        name,
                "vernacularName": r.get("vernacularName", ""),
                "genus":          r.get("genus", ""),
                "family":         r.get("family", ""),
                "order":          r.get("order", ""),
                "sightingCount":  0,
                "earliestYear":   None,
                "latestYear":     None,
                "regions":        set(),
            }
        entry = species_map[name]
        entry["sightingCount"] += 1

        year = r.get("year")
        if year:
            year = int(year)
            if entry["earliestYear"] is None or year < entry["earliestYear"]:
                entry["earliestYear"] = year
            if entry["latestYear"] is None or year > entry["latestYear"]:
                entry["latestYear"] = year

        region = r.get("stateProvince")
        if region:
            entry["regions"].add(region)

    # Convert sets to strings for CSV
    for entry in species_map.values():
        entry["regions"] = " | ".join(sorted(entry["regions"]))

    return list(species_map.values())


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {len(rows)} rows → {path}")


def main():
    print(f"\nFetching {RECORDS_TO_FETCH} NZ bird occurrence records from GBIF...\n")
    raw = fetch_occurrences(RECORDS_TO_FETCH)
    print(f"\n  Total fetched: {len(raw)} records")

    # Occurrences CSV
    flat = [flatten(r) for r in raw]
    write_csv(OUTPUT_OCCURRENCES, flat, FIELDS)

    # Species summary CSV
    species_fields = [
        "species", "vernacularName", "genus", "family", "order",
        "sightingCount", "earliestYear", "latestYear", "regions"
    ]
    species = build_species_summary(raw)
    species.sort(key=lambda x: x["sightingCount"], reverse=True)
    write_csv(OUTPUT_SPECIES, species, species_fields)

    print("\nDone! Open Power BI and import the two CSV files.")
    print(f"  • {OUTPUT_OCCURRENCES}  — use for map visuals and time-series charts")
    print(f"  • {OUTPUT_SPECIES}      — use for species rankings and family breakdowns")


if __name__ == "__main__":
    main()
