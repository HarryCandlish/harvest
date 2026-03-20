"""
fetch_greens.py
────────────────────────────────────────────────────────────────────────────
Scrapes Green Party 2026 press releases via the sitemap (no Playwright needed).
Filters sitemap for long descriptive slugs updated in 2026, fetches each page,
and appends articles to hansard_2026.csv.

Run:  python3 fetch_greens.py
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

# Patterns that indicate non-article pages
SKIP_PATTERNS = re.compile(
    r'_\d{6}|buttons|_bio_|doorknock|_evn_|_vol_|_dk_|_se_|_vt_|_dp_|'
    r'topline|_candidate|candidates_|contact_|pints_with|donate_|_policy$|'
    r'_of_action|weekend_of|activation|representatives'
)


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

# ── Greens — via sitemap ───────────────────────────────────────────────────
print("\n── Green Party (via sitemap) ──────────────────────────")

sitemap_html = fetch("http://www.greens.org.nz/sitemap.xml")
if not sitemap_html:
    print("  Could not fetch sitemap")
else:
    soup = BeautifulSoup(sitemap_html, "html.parser")

    candidate_urls = []
    for url_el in soup.find_all("url"):
        loc     = url_el.find("loc")
        lastmod = url_el.find("lastmod")
        if not loc or not lastmod:
            continue
        if str(START_YEAR) not in lastmod.text:
            continue
        slug = loc.text.split("/")[-1]
        if SKIP_PATTERNS.search(slug):
            continue
        if len(slug) < 30:
            continue
        candidate_urls.append(loc.text.strip())

    candidate_urls.sort()  # alphabetical (roughly chronological within month)
    print(f"  {len(candidate_urls)} candidate URLs from sitemap")

    for url in candidate_urls:
        if url in scraped_urls:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue

        page_soup = BeautifulSoup(page_html, "html.parser")
        full_text = page_soup.get_text(" ", strip=True)

        # Date
        date_str = ""
        date_m = re.search(
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+(\d{4}))",
            full_text[:3000]
        )
        if date_m:
            date_str = date_m.group(1)
            year = int(date_m.group(2))
            if year < START_YEAR:
                continue

        # Title
        title = ""
        title_tag = page_soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True).split("|")[0].split("-")[0].strip()
        if not title:
            h1 = page_soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)

        # Body: paragraphs with substance
        paras = [p.get_text(" ", strip=True) for p in page_soup.find_all("p")
                 if len(p.get_text(strip=True)) > 40]
        text = " ".join(paras)[:3000]

        if not text or len(text) < 150:
            continue

        words = len(text.split())
        writer.writerow({"date": date_str, "party": "Green", "title": title,
                         "url": url, "text": text, "words": words})
        csvfile.flush()
        scraped_urls.add(url)
        total_new += 1
        print(f"  [{total_new}] {date_str:<22} {title[:50]}")
        time.sleep(DELAY)

csvfile.close()
print(f"\nDone. {total_new} new Green Party articles added to {OUTPUT_CSV}")
