"""
fetch_maori_party.py
────────────────────────────────────────────────────────────────────────────
Scrapes Te Pāti Māori press releases from maoriparty.org.nz/panui and
appends 2026 articles to hansard_2026.csv. Already-scraped URLs are skipped.

Run:  python3 fetch_maori_party.py
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os

OUTPUT_CSV = "hansard_2026.csv"
DELAY      = 1.2
START_YEAR = 2026

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "text/html,application/xhtml+xml",
    "Accept-Language": "en-NZ,en;q=0.9",
}

NAV_SLUGS = {
    "get-involved", "volunteer", "donate", "our-people", "about-us",
    "our-constitution", "panui", "policy", "campaigns", "store", "logo",
    "search", "join", "tax_calculator", "permanently_ban_seabed_mining",
}


def fetch(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
        print(f"  HTTP {resp.status_code}: {url}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


# ── Load already-scraped URLs ──────────────────────────────────────────────
scraped_urls = set()
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            scraped_urls.add(row.get("url", ""))
    print(f"Loaded {len(scraped_urls)} already-scraped URLs")

write_header = not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0
csvfile = open(OUTPUT_CSV, "a", newline="", encoding="utf-8")
writer  = csv.DictWriter(csvfile, fieldnames=["date", "party", "title", "url", "text", "words"])
if write_header:
    writer.writeheader()

total_new = 0

# ── Te Pāti Māori ─────────────────────────────────────────────────────────
print("\n── Te Pāti Māori ─────────────────────────────────────")

listing_html = fetch("https://www.maoriparty.org.nz/panui")
if not listing_html:
    print("  Could not fetch listing page")
else:
    soup = BeautifulSoup(listing_html, "html.parser")

    seen = set()
    slugs = []
    for a in soup.find_all("a", href=True):
        href = a["href"].lstrip("/")
        if (len(href) > 15
                and "http" not in href
                and "_" in href
                and href not in seen
                and not any(href.startswith(s) for s in NAV_SLUGS)):
            seen.add(href)
            slugs.append(href)

    print(f"  Found {len(slugs)} article slugs")

    for slug in slugs:
        url = f"https://www.maoriparty.org.nz/{slug}"

        if url in scraped_urls:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue

        page_soup = BeautifulSoup(page_html, "html.parser")
        full_text = page_soup.get_text(" ", strip=True)

        # Date: "Published by Te Pāti Māori Month DD, YYYY"
        date_str = ""
        year = None
        date_m = re.search(
            r"Published by Te P[aā]ti M[aā]ori\s+(\w+ \d{1,2},?\s+(\d{4}))",
            full_text
        )
        if date_m:
            date_str = date_m.group(1).strip()
            year = int(date_m.group(2))
        else:
            # fallback: any Month DD, YYYY near start
            fallback = re.search(
                r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+(\d{4}))",
                full_text[:2000]
            )
            if fallback:
                date_str = fallback.group(1)
                year = int(fallback.group(2))

        if year is not None and year < START_YEAR:
            continue  # skip pre-2026

        # Title: appears just before "Published by" in page text
        title = ""
        title_tag = page_soup.find("title")
        if title_tag:
            raw = title_tag.get_text(strip=True)
            title = raw.split(" - ")[0].strip()
        if not title:
            title = slug.replace("_", " ").title()

        # Body text: paragraphs only
        paras = [p.get_text(" ", strip=True) for p in page_soup.find_all("p")
                 if len(p.get_text(strip=True)) > 40]
        text = " ".join(paras)[:3000]

        if text and len(text) > 150:
            words = len(text.split())
            writer.writerow({"date": date_str, "party": "Te Pāti Māori",
                             "title": title, "url": url, "text": text, "words": words})
            csvfile.flush()
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {date_str:<20} {title[:55]}")
        time.sleep(DELAY)

csvfile.close()
print(f"\nDone. {total_new} new Te Pāti Māori articles added to {OUTPUT_CSV}")
