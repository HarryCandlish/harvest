"""
hansard_scrape.py
─────────────────────────────────────────────────────────────────────────────
Scrapes NZ political party press releases and media statements for 2026
keyword frequency analysis ("Finding signal in the noise").

Note: parliament.nz is behind Radware DDoS protection and cannot be scraped.
This scraper uses party websites directly instead, which is actually better
for pre-election analysis as press releases represent intentional messaging.

Sources:
  - National:     national.org.nz/news          (requests, static HTML)
  - ACT:          act.org.nz/news               (requests, static HTML)
  - Labour:       labour.org.nz/news            (Playwright, JS-rendered)
  - Green:        greens.org.nz/media           (Playwright, JS-rendered)
  - NZ First:     nzfirst.nz/latest_news        (requests, limited)
  - Te Pāti Māori: maoriparty.org.nz/news       (requests)

Run:  python3 hansard_scrape.py
Output: hansard_2026.csv  (columns: date, party, title, url, text, words)

Re-run at any time — already-saved URLs are skipped.

Requires: pip3 install requests beautifulsoup4 playwright playwright-stealth
          python3 -m playwright install chromium
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# ── Config ─────────────────────────────────────────────────────────────────────
OUTPUT_CSV = "hansard_2026.csv"
DELAY      = 1.5   # seconds between requests
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

PARTY_COLOURS = {
    "National":      "#00529F",
    "Labour":        "#D82A20",
    "Green":         "#098137",
    "ACT":           "#FFD100",
    "NZ First":      "#212121",
    "Te Pāti Māori": "#B22222",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def fetch(url):
    """Simple HTTP GET with headers."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            return resp.text
        print(f"  HTTP {resp.status_code}: {url}")
        return None
    except Exception as e:
        print(f"  Error: {e}")
        return None


def is_2026(date_str):
    """Return True if the date string looks like it's from 2026."""
    return "2026" in date_str


def extract_text(soup, max_chars=3000):
    """Extract body text from an article page."""
    # Try common article content containers
    for selector in ["article", ".content", ".entry-content", ".post-content",
                     "main", ".page-content", ".release-content"]:
        el = soup.select_one(selector)
        if el:
            # Remove nav, aside, scripts
            for tag in el.find_all(["nav", "aside", "script", "style", "footer"]):
                tag.decompose()
            text = el.get_text(" ", strip=True)
            if len(text) > 100:
                return text[:max_chars]

    # Fallback: all <p> tags
    paras = soup.find_all("p")
    text = " ".join(p.get_text(" ", strip=True) for p in paras if len(p.get_text(strip=True)) > 40)
    return text[:max_chars]


def save_article(writer, csvfile, party, title, url, date_str, text):
    """Write one article row to CSV."""
    words = len(text.split())
    writer.writerow({
        "date":  date_str,
        "party": party,
        "title": title,
        "url":   url,
        "text":  text,
        "words": words,
    })
    csvfile.flush()


# ── Load already-scraped URLs ──────────────────────────────────────────────────
scraped_urls = set()
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            scraped_urls.add(row.get("url", ""))
    print(f"Loaded {len(scraped_urls)} already-scraped articles")

write_header = not os.path.exists(OUTPUT_CSV) or os.path.getsize(OUTPUT_CSV) == 0
csvfile = open(OUTPUT_CSV, "a", newline="", encoding="utf-8")
writer  = csv.DictWriter(
    csvfile,
    fieldnames=["date", "party", "title", "url", "text", "words"]
)
if write_header:
    writer.writeheader()

total_new = 0


# ══════════════════════════════════════════════════════════════════════════════
# NATIONAL  (national.org.nz/news — static HTML, paginated)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── National ──────────────────────────────────────────")
nat_page = 1
nat_done = False

while not nat_done:
    html = fetch(f"https://www.national.org.nz/news?page={nat_page}")
    if not html:
        break
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    articles = [l for l in links if "/news/" in l.get("href", "") and
                re.search(r"/news/\d{8}", l.get("href", ""))]

    if not articles:
        break

    found_old = False
    for link in articles:
        href  = link["href"]
        url   = "https://www.national.org.nz" + href if href.startswith("/") else href
        title = link.get_text(strip=True)
        # Extract date from URL: /news/20260318-...
        m = re.search(r"/news/(\d{8})", href)
        date_str = ""
        if m:
            d = m.group(1)
            date_str = f"{d[:4]}-{d[4:6]}-{d[6:8]}"
            if int(d[:4]) < START_YEAR:
                found_old = True
                nat_done = True
                continue
        if url in scraped_urls:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue
        page_soup = BeautifulSoup(page_html, "html.parser")
        text = extract_text(page_soup)
        if text:
            save_article(writer, csvfile, "National", title, url, date_str, text)
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {title[:70]}")
        time.sleep(DELAY)

    if found_old:
        break
    nat_page += 1
    time.sleep(DELAY)


# ══════════════════════════════════════════════════════════════════════════════
# ACT  (act.org.nz/news — static HTML, paginated)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── ACT ───────────────────────────────────────────────")
act_page = 1
act_done = False
act_prev_urls = set()  # detect when pagination repeats itself

while not act_done and act_page <= 20:
    html = fetch(f"https://www.act.org.nz/news?page={act_page}")
    if not html:
        break
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    articles = [l for l in links if "/news/" in l.get("href", "") and
                len(l.get("href", "")) > 10]
    # De-duplicate within this page
    seen = set()
    unique_articles = []
    for l in articles:
        if l["href"] not in seen:
            seen.add(l["href"])
            unique_articles.append(l)

    if not unique_articles:
        break

    # Stop if this page returns the same URLs as the previous page (pagination loop)
    page_urls = {l["href"] for l in unique_articles}
    if page_urls == act_prev_urls:
        print(f"  ACT: pagination repeated on page {act_page} — stopping")
        break
    act_prev_urls = page_urls

    for link in unique_articles:
        href  = link["href"]
        url   = "https://www.act.org.nz" + href if href.startswith(".") or href.startswith("/") else href
        url   = url.replace("//www.act.org.nz/./", "//www.act.org.nz/")
        title = link.get_text(strip=True)

        if url in scraped_urls:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue
        page_soup = BeautifulSoup(page_html, "html.parser")

        # Extract date from page
        date_str = ""
        date_el = page_soup.find(class_=re.compile(r"date|time|publish", re.I))
        if date_el:
            date_text = date_el.get_text(strip=True)
            m = re.search(r"(\d{4})", date_text)
            if m and int(m.group(1)) < START_YEAR:
                act_done = True
                break
            date_str = date_text[:20]

        text = extract_text(page_soup)
        if text:
            save_article(writer, csvfile, "ACT", title, url, date_str, text)
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {title[:70]}")
        time.sleep(DELAY)

    if not act_done:
        act_page += 1
        time.sleep(DELAY)


# ══════════════════════════════════════════════════════════════════════════════
# LABOUR  (labour.org.nz/news — Playwright required, JS-rendered)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── Labour (Playwright) ───────────────────────────────")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=HEADERS["User-Agent"],
        locale="en-NZ",
        viewport={"width": 1280, "height": 800},
    )
    page = context.new_page()
    Stealth().apply_stealth_sync(page)

    lab_page_num = 1
    lab_done     = False
    lab_prev_urls = set()

    while not lab_done and lab_page_num <= 30:
        url_listing = f"https://www.labour.org.nz/news?page={lab_page_num}"
        try:
            page.goto(url_listing, wait_until="load", timeout=20000)
        except Exception as e:
            print(f"  Error loading listing page {lab_page_num}: {e}")
            break
        time.sleep(2)

        soup = BeautifulSoup(page.content(), "html.parser")
        links = soup.find_all("a", href=True)
        articles = [l for l in links if "/news/" in l.get("href", "")
                    and l.get("href", "") != "/news/"
                    and len(l.get("href", "")) > 8]
        seen = set()
        unique = []
        for l in articles:
            if l["href"] not in seen:
                seen.add(l["href"])
                unique.append(l)

        if not unique:
            print(f"  No more articles on page {lab_page_num}")
            break

        # Stop if pagination is looping
        page_urls = {l["href"] for l in unique}
        if page_urls == lab_prev_urls:
            print(f"  Labour: pagination repeated on page {lab_page_num} — stopping")
            break
        lab_prev_urls = page_urls

        for link in unique:
            href = link["href"]
            art_url = "https://www.labour.org.nz" + href if href.startswith("/") else href
            title   = link.get_text(strip=True)

            if art_url in scraped_urls:
                continue

            try:
                page.goto(art_url, wait_until="load", timeout=20000)
            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(DELAY)
                continue
            time.sleep(1.5)

            art_soup = BeautifulSoup(page.content(), "html.parser")

            # Date
            date_str = ""
            date_el = art_soup.find(class_=re.compile(r"date|time|publish", re.I))
            if not date_el:
                date_el = art_soup.find("time")
            if date_el:
                dt_text = date_el.get("datetime", "") or date_el.get_text(strip=True)
                m = re.search(r"(\d{4})", dt_text)
                if m and int(m.group(1)) < START_YEAR:
                    lab_done = True
                    break
                date_str = dt_text[:20]

            text = extract_text(art_soup)
            if text:
                save_article(writer, csvfile, "Labour", title, art_url, date_str, text)
                scraped_urls.add(art_url)
                total_new += 1
                print(f"  [{total_new}] {title[:70]}")
            time.sleep(DELAY)

        if not lab_done:
            lab_page_num += 1
            time.sleep(DELAY)

    browser.close()


# ══════════════════════════════════════════════════════════════════════════════
# NZ FIRST  (nzfirst.nz — static HTML)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── NZ First ──────────────────────────────────────────")

html = fetch("https://www.nzfirst.nz/latest_news")
if html:
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    skip_words = {"about", "policy", "team", "principle", "contact", "join",
                  "donate", "people", "achieve", "recruit", "petition",
                  "newsletter", "calendar", "bill", "caucus", "spread",
                  "home", "latest", "news"}
    articles = [l for l in links if l["href"].startswith("/")
                and len(l["href"]) > 5
                and l["href"].strip("/").split("/")[0].lower() not in skip_words]
    # Unique
    seen = set()
    unique = []
    for l in articles:
        if l["href"] not in seen:
            seen.add(l["href"])
            unique.append(l)

    for link in unique[:30]:
        href = link["href"]
        url  = "https://www.nzfirst.nz" + href
        title = link.get_text(strip=True) or href.replace("-", " ").replace("/", "")

        if url in scraped_urls or not title:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue
        page_soup = BeautifulSoup(page_html, "html.parser")
        text = extract_text(page_soup)
        if text and len(text) > 150:
            date_str = ""
            date_el = page_soup.find(class_=re.compile(r"date|time|publish", re.I))
            if date_el:
                date_str = date_el.get_text(strip=True)[:20]
            save_article(writer, csvfile, "NZ First", title, url, date_str, text)
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {title[:70]}")
        time.sleep(DELAY)


# ══════════════════════════════════════════════════════════════════════════════
# TE PĀTI MĀORI  (maoriparty.org.nz)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── Te Pāti Māori ─────────────────────────────────────")

html = fetch("https://www.maoriparty.org.nz/news")
if html:
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)
    articles = [l for l in links if len(l["href"]) > 15
                and not l["href"].startswith("http")
                and not any(x in l["href"] for x in
                            ["get-involved", "volunteer", "donate", "people",
                             "about", "/news", "policy", "our-", "constitution",
                             "petition"])]
    for link in articles[:20]:
        href = link["href"]
        url  = "https://www.maoriparty.org.nz" + href if href.startswith("/") else \
               "https://www.maoriparty.org.nz/" + href.lstrip("/")
        title = link.get_text(strip=True)

        if url in scraped_urls or not title:
            continue

        page_html = fetch(url)
        if not page_html:
            time.sleep(DELAY)
            continue
        page_soup = BeautifulSoup(page_html, "html.parser")
        text = extract_text(page_soup)
        if text and len(text) > 150:
            date_str = ""
            date_el = page_soup.find(class_=re.compile(r"date|time|publish", re.I))
            if date_el:
                date_str = date_el.get_text(strip=True)[:20]
            save_article(writer, csvfile, "Te Pāti Māori", title, url, date_str, text)
            scraped_urls.add(url)
            total_new += 1
            print(f"  [{total_new}] {title[:70]}")
        time.sleep(DELAY)


# ══════════════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════════════
csvfile.close()
print(f"\n{'─'*60}")
print(f"Done. {total_new} new articles written to {OUTPUT_CSV}")
if os.path.exists(OUTPUT_CSV):
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        total_rows = sum(1 for _ in f) - 1
    print(f"Total rows in file: {total_rows}")

    # Party breakdown
    counts = {}
    with open(OUTPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = row.get("party", "Unknown")
            counts[p] = counts.get(p, 0) + 1
    print("\nBy party:")
    for party, count in sorted(counts.items()):
        print(f"  {party:20s}: {count}")
