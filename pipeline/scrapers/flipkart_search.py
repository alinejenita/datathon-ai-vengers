"""
pipeline/scrapers/flipkart_search.py
──────────────────────────────────────
Discovers product IDs from Flipkart search result pages via ScraperAPI.
"""

import re
import time
import random
import requests
from bs4 import BeautifulSoup

from pipeline.config import (
    SCRAPER_API_KEY,
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
)

DEFAULT_KEYWORDS = [
    "tws earbuds under 2000",
    "wireless earbuds",
    "bluetooth earbuds",
]

# Flipkart product URL pattern: /product-name/p/ITEM_ID
_FK_ID_PATTERN = re.compile(r"/p/([A-Z0-9]+)")


def _get(url: str) -> str | None:
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
    try:
        proxy_url = (
            f"http://api.scraperapi.com"
            f"?api_key={SCRAPER_API_KEY}"
            f"&url={url}"
            f"&country_code=in"
        )
        resp = requests.get(proxy_url, timeout=60)
        if resp.status_code == 200:
            if "captcha" in resp.text.lower():
                print(f"[BLOCKED] CAPTCHA: {url}")
                return None
            return resp.text
        print(f"[WARN] Flipkart search {resp.status_code}: {url}")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] flipkart_search: {e}")
        return None


def scrape_flipkart_search(
    query: str,
    pages: int = 2,
) -> list[dict]:
    """
    Scrape Flipkart search results for `query`.

    Returns list of dicts:
        { product_id, platform, title, url }
    """
    encoded  = requests.utils.quote(query)
    all_products = {}

    for page in range(1, pages + 1):
        url  = f"https://www.flipkart.com/search?q={encoded}&page={page}"
        print(f"[FK SEARCH] {query!r} — page {page}")
        html = _get(url)
        if not html:
            break

        soup  = BeautifulSoup(html, "html.parser")
        found = 0

        # Product cards on search page
        for item in soup.select("._1AtVbE, ._13oc-S, .s1Q9rs"):
            link_el = item.select_one("a._1fQZEK, a.s1Q9rs, a[href*='/p/']")
            if not link_el:
                continue

            href = link_el.get("href", "")
            m    = _FK_ID_PATTERN.search(href)
            if not m:
                continue

            product_id = m.group(1)
            title_el   = item.select_one("._4rR01T, .IRpwTa, a._1fQZEK")
            title      = title_el.get_text(strip=True) if title_el else None

            if product_id not in all_products:
                all_products[product_id] = {
                    "product_id": product_id,
                    "platform":   "flipkart",
                    "title":      title,
                    "url":        f"https://www.flipkart.com{href}",
                }
                found += 1

        print(f"  └─ found {found} products (total: {len(all_products)})")

    return list(all_products.values())


def discover_flipkart_competitors(
    keywords: list[str] | None = None,
    pages_per_keyword: int = 2,
    exclude_ids: set | None = None,
) -> list[dict]:
    """
    Multi-keyword Flipkart discovery — returns deduplicated product list.
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS

    exclude = exclude_ids or set()
    seen    = {}

    for kw in keywords:
        for p in scrape_flipkart_search(kw, pages=pages_per_keyword):
            pid = p["product_id"]
            if pid not in exclude and pid not in seen:
                seen[pid] = p

    print(f"[FK SEARCH] Discovered {len(seen)} Flipkart products")
    return list(seen.values())