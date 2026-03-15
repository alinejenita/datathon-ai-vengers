"""
pipeline/scrapers/amazon_offers.py
────────────────────────────────────
Scrapes the offer listing page for a given ASIN to find third-party sellers
and their prices.
"""

import time
import random
import requests
from bs4 import BeautifulSoup

from pipeline.config import (
    SCRAPER_API_KEY,
    REQUEST_DELAY_MIN,
    REQUEST_DELAY_MAX,
)
from pipeline.apis.normaliser import clean_price, clean_text


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
                print(f"[BLOCKED] CAPTCHA on offers: {url}")
                return None
            return resp.text
        print(f"[WARN] Offers {resp.status_code}: {url}")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] amazon_offers: {e}")
        return None


def scrape_offers(asin: str) -> list[dict]:
    """
    Scrape the offer listing page for an ASIN.

    Returns a list of dicts:
        { asin, seller, price, condition }
    """
    url = f"https://www.amazon.in/gp/offer-listing/{asin}"
    html = _get(url)

    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    offers = []

    for offer in soup.select(".olpOffer"):
        seller_el    = offer.select_one(".olpSellerName")
        price_el     = offer.select_one(".olpOfferPrice")
        condition_el = offer.select_one(".olpCondition")

        price_raw = price_el.get_text(strip=True) if price_el else None

        offers.append({
            "asin":      asin,
            "seller":    clean_text(seller_el.get_text(strip=True)) if seller_el else None,
            "price":     clean_price(price_raw),
            "condition": clean_text(condition_el.get_text(strip=True)) if condition_el else None,
        })

    return offers