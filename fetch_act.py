"""
fetch_act.py
────────────────────────────────────────────────────────────────────────────
Scrapes ACT press releases from act.org.nz and appends to hansard_2026.csv.
Uses the sitemap (2,997 URLs) since the listing page is JS-rendered.
Stops when it hits pre-2026 content. Already-scraped URLs are skipped.

Run:  python3 fetch_act.py
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


def extract_text(soup, max_chars=3000):
    for selector in ["article", ".content", ".entry-content", ".post-content",
                     "main", ".page-content", ".release-content"]:
        el = soup.select_one(selector)
        if el:
            for tag in el.find_all(["nav", "aside", "script", "style", "footer"]):
                tag.decompose()
            text = el.get_text(" ", strip=True)
            if len(text) > 100:
                return text[:max_chars]
    paras = soup.find_all("p")
    text = " ".join(p.get_text(" ", strip=True) for p in paras if len(p.get_text(strip=True)) > 40)
    return text[:max_chars]


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

# ── ACT — via sitemap ──────────────────────────────────────────────────────
print("\n── ACT (via sitemap) ─────────────────────────────────")

sitemap_html = fetch("https://www.act.org.nz/sitemap_en-NZ.xml")
if not sitemap_html:
    print("  Could not fetch sitemap")
else:
    sitemap_soup = BeautifulSoup(sitemap_html, "html.parser")
    all_urls = [loc.text.strip() for loc in sitemap_soup.find_all("loc")
                if "/news/" in loc.text]
    print(f"  {len(all_urls)} news URLs in sitemap")

    consecutive_old = 0  # stop after several pre-2026 articles in a row

    for url in all_urls:
        if url in scraped_urls:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue

        page_soup = BeautifulSoup(page_html, "html.parser")

        # Extract date
        date_str = ""
        year = None
        date_el = page_soup.find(class_=re.compile(r"date|time|publish", re.I))
        if not date_el:
            date_el = page_soup.find("time")
        if date_el:
            dt_text = date_el.get("datetime", "") or date_el.get_text(strip=True)
            m = re.search(r"(\d{4})", dt_text)
            if m:
                year = int(m.group(1))
                date_str = dt_text[:20]

        if year is not None and year < START_YEAR:
            consecutive_old += 1
            if consecutive_old >= 5:
                print(f"  Stopping — 5 consecutive pre-{START_YEAR} articles")
                break
            time.sleep(DELAY)
            continue
        consecutive_old = 0

        # Extract title
        title = ""
        h1 = page_soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        if not title:
            title_tag = page_soup.find("title")
            if title_tag:
                title = title_tag.get_text(strip=True).split("|")[0].strip()

        text = extract_text(page_soup)
        if text and len(text) > 150:
            words = len(text.split())
            writer.writerow({"date": date_str, "party": "ACT", "title": title,
                             "url": url, "text": text, "words": words})
            csvfile.flush()
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {title[:70]}")
        time.sleep(DELAY)

csvfile.close()
print(f"\nDone. {total_new} new ACT articles added to {OUTPUT_CSV}")
