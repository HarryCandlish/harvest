"""
fetch_nzfirst.py
────────────────────────────────────────────────────────────────────────────
Scrapes NZ First press releases from nzfirst.nz and appends to hansard_2026.csv.
Already-scraped URLs are skipped.

Run:  python3 fetch_nzfirst.py
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os

OUTPUT_CSV = "hansard_2026.csv"
DELAY      = 1.5
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

SKIP_WORDS = {"about", "policy", "team", "principle", "contact", "join",
              "donate", "people", "achieve", "recruit", "petition",
              "newsletter", "calendar", "bill", "caucus", "spread",
              "home", "latest", "news"}


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
        reader = csv.DictReader(f)
        for row in reader:
            scraped_urls.add(row.get("url", ""))
    print(f"Loaded {len(scraped_urls)} already-scraped URLs")

write_header = not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0
csvfile = open(OUTPUT_CSV, "a", newline="", encoding="utf-8")
writer  = csv.DictWriter(csvfile, fieldnames=["date", "party", "title", "url", "text", "words"])
if write_header:
    writer.writeheader()

total_new = 0

# ── NZ First ───────────────────────────────────────────────────────────────
print("\n── NZ First ──────────────────────────────────────────")

html = fetch("https://www.nzfirst.nz/news")
if html:
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)

    # Each article appears 3x (bare link, titled link, "Read more") — keep titled ones only
    NAV_SLUGS = {"about", "policy", "team", "principle", "contact", "join",
                 "donate", "people", "achieve", "recruit", "petition",
                 "newsletter", "calendar", "bill", "caucus", "spread",
                 "home", "latest", "news", "our", "login", "privacy",
                 "tos", "video", "recruit", "latest_news"}

    seen = set()
    unique = []
    for l in links:
        href = l["href"]
        title = l.get_text(strip=True)
        if (href.startswith("/")
                and len(href) > 5
                and href.strip("/").split("/")[0].lower() not in NAV_SLUGS
                and not href.startswith("/our")
                and title
                and title.lower() != "read more"
                and href not in seen):
            seen.add(href)
            unique.append(l)

    print(f"  Found {len(unique)} candidate links")

    for link in unique[:50]:
        href  = link["href"]
        url   = "https://www.nzfirst.nz" + href
        title = link.get_text(strip=True) or href.replace("-", " ").replace("/", "")

        if url in scraped_urls or not title:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue

        page_soup = BeautifulSoup(page_html, "html.parser")

        # Date
        date_str = ""
        date_el = page_soup.find(class_=re.compile(r"date|time|publish", re.I))
        if not date_el:
            date_el = page_soup.find("time")
        if date_el:
            dt_text = date_el.get("datetime", "") or date_el.get_text(strip=True)
            m = re.search(r"(\d{4})", dt_text)
            if m and int(m.group(1)) < START_YEAR:
                print(f"  Stopping — hit pre-{START_YEAR} content")
                break
            date_str = dt_text[:20]

        text = extract_text(page_soup)
        if text and len(text) > 150:
            words = len(text.split())
            writer.writerow({"date": date_str, "party": "NZ First", "title": title,
                             "url": url, "text": text, "words": words})
            csvfile.flush()
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {title[:70]}")
        time.sleep(DELAY)
else:
    print("  Could not fetch nzfirst.nz/latest_news")

csvfile.close()
print(f"\nDone. {total_new} new NZ First articles added to {OUTPUT_CSV}")
