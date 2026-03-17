"""
Common Name Fetcher
-------------------
For each species in nz_bird_species.csv, looks up the English common name
from the GBIF species API and patches both CSVs.
"""

import csv
import time
import requests

SPECIES_FILE    = "nz_bird_species.csv"
OCCURRENCE_FILE = "nz_bird_occurrences.csv"
MATCH_URL       = "https://api.gbif.org/v1/species/match"
VERNACULAR_URL  = "https://api.gbif.org/v1/species/{key}/vernacularNames"

def get_common_name(species_name):
    """Look up English common name from GBIF for a given species."""
    try:
        # Step 1: match the species name to get its GBIF key
        r = requests.get(MATCH_URL, params={"name": species_name, "kingdom": "Animalia"}, timeout=10)
        r.raise_for_status()
        data = r.json()
        key = data.get("usageKey") or data.get("speciesKey")
        if not key:
            return ""

        # Step 2: fetch vernacular names for that key
        r2 = requests.get(VERNACULAR_URL.format(key=key), timeout=10)
        r2.raise_for_status()
        names = r2.json().get("results", [])

        # Prefer English names
        english = [n["vernacularName"] for n in names if n.get("language") == "eng"]
        if english:
            return english[0]

        # Fall back to any language
        if names:
            return names[0].get("vernacularName", "")

        return ""

    except Exception:
        return ""


def patch_csv(filepath, name_map, key_field):
    """Read a CSV, fill in vernacularName, write it back."""
    with open(filepath, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        fieldnames = rows[0].keys() if rows else []

    for row in rows:
        species = row.get(key_field, "")
        if not row.get("vernacularName") and species in name_map:
            row["vernacularName"] = name_map[species]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    # Get unique species from species file
    with open(SPECIES_FILE, newline="", encoding="utf-8") as f:
        species_list = [row["species"] for row in csv.DictReader(f) if row["species"]]

    print(f"Looking up common names for {len(species_list)} species...\n")

    name_map = {}
    for i, species in enumerate(species_list, 1):
        common = get_common_name(species)
        name_map[species] = common
        label = common if common else "(not found)"
        print(f"  [{i}/{len(species_list)}] {species} → {label}")
        time.sleep(0.3)  # polite rate limiting

    # Patch both CSVs
    print("\nUpdating CSVs...")
    patch_csv(SPECIES_FILE, name_map, "species")
    patch_csv(OCCURRENCE_FILE, name_map, "species")
    print("Done — both CSVs updated with common names.")


if __name__ == "__main__":
    main()
