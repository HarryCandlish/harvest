"""
update_fuel_prices.py
Fetches the latest weekly NZ retail fuel prices from MBIE via data.govt.nz
and updates the hardcoded values in fuel_prices.html.

Run each Wednesday after MBIE publishes:
    python update_fuel_prices.py

Note: MBIE suspended publication from 13 March 2026 onwards due to market
volatility. The script will abort rather than overwrite the HTML with older
data if MBIE's CSV hasn't been updated past the date already in the file.
"""

import csv
import re
import urllib.request
from datetime import datetime

CSV_URL = (
    "https://catalogue.data.govt.nz/dataset/"
    "f4ac4dad-6e52-4100-bbb6-00e132935cfa/resource/"
    "9b8bba4c-0ac4-4116-97ab-2a75415da233/download/weekly-table.csv"
)
HTML_FILE = "fuel_prices.html"


def fetch_latest_prices():
    """Download CSV and return (date_str, petrol_dollars, diesel_dollars)."""
    print("Fetching MBIE weekly fuel price CSV...")
    req = urllib.request.Request(CSV_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        lines = response.read().decode("utf-8").splitlines()

    reader = csv.DictReader(lines)

    petrol_rows = {}
    diesel_rows = {}

    for row in reader:
        if row["Variable"].strip() != "Adjusted retail price":
            continue
        fuel = row["Fuel"].strip()
        date = row["Date"].strip()
        try:
            value = float(row["Value"])
        except ValueError:
            continue

        if fuel == "Regular Petrol":
            petrol_rows[date] = value
        elif fuel == "Diesel":
            diesel_rows[date] = value

    if not petrol_rows or not diesel_rows:
        raise ValueError("Could not find 'Adjusted retail price' rows in CSV.")

    # Use the latest date present in both fuels
    latest_date = max(set(petrol_rows) & set(diesel_rows))
    petrol_cents = petrol_rows[latest_date]
    diesel_cents = diesel_rows[latest_date]

    # Format date as "13 Mar 2026"
    dt = datetime.strptime(latest_date, "%Y-%m-%d")
    date_str = dt.strftime("%-d %b %Y")

    return date_str, petrol_cents / 100, diesel_cents / 100


def current_html_date(html):
    """Extract the 'as of DD Mon YYYY' date currently in the HTML."""
    m = re.search(r'as of (\d{1,2} \w+ \d{4})', html)
    if m:
        return datetime.strptime(m.group(1), "%d %b %Y")
    return None


def update_html(date_str, petrol, diesel):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Safety guard: don't overwrite with older data
    new_date = datetime.strptime(date_str, "%d %b %Y")
    existing_date = current_html_date(html)
    if existing_date and new_date <= existing_date:
        print(f"Skipping update: MBIE data ({date_str}) is not newer than what's already in the HTML ({existing_date.strftime('%-d %b %Y')}).")
        print("Update the HTML manually when fresher data is available.")
        return

    petrol_str = f"${petrol:.2f}"
    diesel_str = f"${diesel:.2f}"

    # Replace Regular 91 price (large Fraunces number in the callout box)
    html, n1 = re.subn(
        r'(font-size:72px[^>]+>)\$[\d.]+(<)',
        rf'\g<1>{petrol_str}\2',
        html
    )

    # Replace Diesel price
    html, n2 = re.subn(
        r'(font-size:36px[^>]+>)\$[\d.]+(<)',
        rf'\g<1>{diesel_str}\2',
        html
    )

    # Replace "as of DD Mon YYYY" date stamp
    html, n3 = re.subn(
        r'as of \d{1,2} \w+ \d{4}',
        f'as of {date_str}',
        html
    )

    if n1 == 0 or n2 == 0 or n3 == 0:
        print(f"WARNING: some replacements did not match (petrol={n1}, diesel={n2}, date={n3})")
        print("Check that the HTML structure hasn't changed.")
    else:
        print(f"Updated: Regular 91 = {petrol_str}, Diesel = {diesel_str}, as of {date_str}")

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    date_str, petrol, diesel = fetch_latest_prices()
    update_html(date_str, petrol, diesel)
    print("Done.")
