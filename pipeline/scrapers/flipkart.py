import requests
import random
import time
import hashlib
from bs4 import BeautifulSoup

from pipeline.config import (
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX, SCRAPER_API_KEY,
)
from pipeline.apis.normaliser import normalise_product, normalise_review

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
]


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
        print(f"[WARN] {resp.status_code}: {url}")
        return None
    except requests.RequestException as e:
        print(f"[ERROR] flipkart._get: {e}")
        return None


def scrape_product(product_id: str, url: str) -> dict | None:
    """
    product_id : Flipkart internal product ID (used as 'asin' field)
    url        : full product page URL
    """
    html = _get(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    price_el  = soup.select_one("div._30jeq3._16Jk6d") or soup.select_one("div._30jeq3")
    rating_el = soup.select_one("div._3LWZlK")
    count_el  = soup.select_one("span._2_R_DZ")
    title_el  = soup.select_one("span.B_NuCI")

    bullets = [
        b.get_text(strip=True)
        for b in soup.select("div._1mXcCf ul li")
        if len(b.get_text(strip=True)) > 5
    ]

    desc_el = soup.select_one("div._1AN87F") or soup.select_one("div._1mXcCf")

    raw = {
        "asin":                product_id,
        "platform":            "flipkart",
        "title":               title_el.get_text(strip=True) if title_el else None,
        "brand":               None,
        "price":               price_el.get_text(strip=True) if price_el else None,
        "rating":              rating_el.get_text(strip=True) if rating_el else None,
        "review_count":        count_el.get_text(strip=True) if count_el else None,
        "amazon_rank":         None,
        "bullet_points":       " | ".join(bullets) if bullets else None,
        "product_description": desc_el.get_text(strip=True)[:1000] if desc_el else None,
    }

    return normalise_product(raw)


def scrape_reviews(product_id: str, base_url: str, pages: int = 5) -> list[dict]:
    reviews = []

    for page in range(1, pages + 1):
        html = _get(f"{base_url}&page={page}")
        if not html:
            break

        soup   = BeautifulSoup(html, "html.parser")
        blocks = soup.select("div._16PBlm")
        if not blocks:
            break

        for block in blocks:
            body_el   = block.select_one("div.t-ZTKy")
            rating_el = block.select_one("div._3LWZlK")
            title_el  = block.select_one("p._2-N8zT")

            body_text = body_el.get_text(strip=True) if body_el else None
            if not body_text:
                continue

            review_id = hashlib.md5(f"{product_id}{body_text}".encode()).hexdigest()

            reviews.append(normalise_review({
                "asin":      product_id,
                "review_id": review_id,
                "rating":    rating_el.get_text(strip=True) if rating_el else None,
                "title":     title_el.get_text(strip=True) if title_el else None,
                "body":      body_text,
                "verified":  False,
            }))

    return reviews