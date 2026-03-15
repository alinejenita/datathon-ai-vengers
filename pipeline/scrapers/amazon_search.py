"""
pipeline/scrapers/amazon_search.py
───────────────────────────────────
Discovers ASINs from Amazon search result pages.
Uses ScraperAPI to bypass bot detection.
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

# Default search keywords for TWS earbud competitors
DEFAULT_KEYWORDS = [
    "tws earbuds under 2000",
    "wireless earbuds india",
    "boat airdopes alternatives",
    "bluetooth earbuds under 1500",
]


def _get(url: str) -> str | None:
    """Fetch via ScraperAPI."""
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
                print(f"[BLOCKED] CAPTCHA on search: {url}")
                return None
            return resp.text
        print(f"[WARN] Search {resp.status_code}: {url}")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] amazon_search: {e}")
        return None


def _extract_asins(soup: BeautifulSoup) -> list[dict]:
    """
    Extract ASINs + titles from a parsed Amazon search results page.
    Uses multiple strategies for robustness.
    """
    found = {}

    # Strategy 1: data-asin attribute on result items
    for item in soup.select("[data-asin]"):
        asin = item.get("data-asin", "").strip()
        if not asin or len(asin) != 10:
            continue

        title_el = (
            item.select_one("h2 a span")
            or item.select_one(".a-size-medium.a-color-base")
            or item.select_one("h2 span")
        )

        price_el = (
            item.select_one(".a-price .a-offscreen")
            or item.select_one("span.a-price-whole")
        )

        rating_el = item.select_one("span.a-icon-alt")

        if asin not in found:
            found[asin] = {
                "asin":     asin,
                "platform": "amazon",
                "title":    title_el.get_text(strip=True) if title_el else None,
                "price":    price_el.get_text(strip=True) if price_el else None,
                "rating":   rating_el.get_text(strip=True) if rating_el else None,
            }

    # Strategy 2: extract from product links as fallback
    asin_pattern = re.compile(r"/dp/([A-Z0-9]{10})")
    for a in soup.select("a[href*='/dp/']"):
        m = asin_pattern.search(a.get("href", ""))
        if m:
            asin = m.group(1)
            if asin not in found:
                found[asin] = {
                    "asin":     asin,
                    "platform": "amazon",
                    "title":    a.get_text(strip=True) or None,
                    "price":    None,
                    "rating":   None,
                }

    return list(found.values())


def scrape_amazon_search(
    query: str,
    pages: int = 2,
    min_asin_length: int = 10,
) -> list[dict]:
    """
    Scrape Amazon search results for `query` across `pages` pages.

    Returns a list of dicts:
        { asin, platform, title, price, rating }
    """
    all_products = {}
    encoded = requests.utils.quote(query)

    for page in range(1, pages + 1):
        url = f"https://www.amazon.in/s?k={encoded}&page={page}"
        print(f"[SEARCH] {query!r} — page {page}")

        html = _get(url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        products = _extract_asins(soup)

        for p in products:
            if p["asin"] not in all_products:
                all_products[p["asin"]] = p

        print(f"  └─ found {len(products)} ASINs (total so far: {len(all_products)})")

    return list(all_products.values())


def discover_competitors(
    keywords: list[str] | None = None,
    pages_per_keyword: int = 2,
    exclude_asins: set | None = None,
) -> list[dict]:
    """
    Run multiple keyword searches and return deduplicated competitor ASINs.

    Args:
        keywords:           Search terms. Defaults to DEFAULT_KEYWORDS.
        pages_per_keyword:  Pages to scrape per keyword.
        exclude_asins:      ASINs to skip (e.g. own products).

    Returns:
        Deduplicated list of { asin, platform, title, price, rating }
    """
    if keywords is None:
        keywords = DEFAULT_KEYWORDS

    exclude = exclude_asins or set()
    seen    = {}

    for kw in keywords:
        results = scrape_amazon_search(kw, pages=pages_per_keyword)
        for p in results:
            asin = p["asin"]
            if asin not in exclude and asin not in seen:
                seen[asin] = p

    print(f"[SEARCH] Discovered {len(seen)} unique competitor ASINs")
    return list(seen.values())