import requests
import random
import time
import hashlib
from bs4 import BeautifulSoup

from pipeline.config import (
    REQUEST_DELAY_MIN, REQUEST_DELAY_MAX,
    MAX_REVIEW_PAGES, SCRAPER_API_KEY,
)
from pipeline.apis.normaliser import normalise_product, normalise_review

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def _get(url: str) -> str | None:
    """Fetch a URL via ScraperAPI with random delay."""
    time.sleep(random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX))
    try:
        proxy_url = (
            f"http://api.scraperapi.com"
            f"?api_key={SCRAPER_API_KEY}"
            f"&url={url}"
            f"&country_code=in"
        )
        response = requests.get(proxy_url, timeout=60)

        if response.status_code == 200:
            if "captcha" in response.text.lower():
                print(f"[BLOCKED] CAPTCHA detected: {url}")
                return None
            return response.text

        print(f"[WARN] {response.status_code} for {url}")
        return None

    except requests.RequestException as e:
        print(f"[ERROR] {e}")
        return None


def scrape_product(asin: str) -> dict | None:
    """Scrape product page and return normalised dict."""
    url = f"https://www.amazon.in/dp/{asin}"
    html = _get(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Price — try multiple selectors in order of reliability
    price_el = (
        soup.select_one("span.a-price-whole")
        or soup.select_one(".a-price .a-offscreen")
        or soup.select_one("#priceblock_ourprice")
        or soup.select_one("#priceblock_dealprice")
        or soup.select_one("#apex_offerDisplay_desktop .a-price .a-offscreen")
    )

    rating_el       = soup.select_one("span.a-icon-alt")
    review_count_el = soup.select_one("#acrCustomerReviewText")
    title_el        = soup.select_one("#productTitle")
    brand_el        = soup.select_one("#bylineInfo")

    # Best Sellers Rank
    rank_text = None
    rank_table = soup.select_one("#productDetails_detailBullets_sections1")
    if rank_table:
        for row in rank_table.select("tr"):
            if "Best Sellers Rank" in row.get_text():
                rank_text = row.get_text(strip=True, separator=" ")[:200]
                break

    # Fallback rank in sidebar
    if not rank_text:
        for li in soup.select("#detailBulletsWrapper_feature_div li"):
            if "Best Sellers Rank" in li.get_text():
                rank_text = li.get_text(strip=True, separator=" ")[:200]
                break

    # Bullet points
    bullets = [
        b.get_text(strip=True)
        for b in soup.select("#feature-bullets ul li span.a-list-item")
        if len(b.get_text(strip=True)) > 5
    ]

    # Product description
    desc_el = (
        soup.select_one("#productDescription_feature_div")
        or soup.select_one("#aplus_feature_div")
        or soup.select_one("#aplus")
        or soup.select_one("#productDescription")
    )

    raw = {
        "asin":                asin,
        "platform":            "amazon",
        "title":               title_el.get_text(strip=True) if title_el else None,
        "brand":               brand_el.get_text(strip=True) if brand_el else None,
        "price":               price_el.get_text(strip=True) if price_el else None,
        "rating":              rating_el.get_text(strip=True) if rating_el else None,
        "review_count":        review_count_el.get_text(strip=True) if review_count_el else None,
        "amazon_rank":         rank_text,
        "bullet_points":       " | ".join(bullets) if bullets else None,
        "product_description": desc_el.get_text(strip=True)[:1000] if desc_el else None,
    }

    return normalise_product(raw)


def scrape_reviews(asin: str) -> list[dict]:
    """Scrape up to MAX_REVIEW_PAGES pages of reviews."""
    reviews = []

    for page in range(1, MAX_REVIEW_PAGES + 1):
        url = (
            f"https://www.amazon.in/product-reviews/{asin}"
            f"?pageNumber={page}&sortBy=recent"
        )
        html = _get(url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")
        blocks = soup.select("[data-hook='review']")
        if not blocks:
            break

        for block in blocks:
            body_el     = block.select_one("[data-hook='review-body']")
            stars_el    = block.select_one("[data-hook='review-star-rating']")
            title_el    = block.select_one("[data-hook='review-title']")
            verified_el = block.select_one("[data-hook='avp-badge']")

            body_text = body_el.get_text(strip=True) if body_el else None
            if not body_text:
                continue

            review_id = hashlib.md5(f"{asin}{body_text}".encode()).hexdigest()

            reviews.append(normalise_review({
                "asin":      asin,
                "review_id": review_id,
                "rating":    stars_el.get_text(strip=True) if stars_el else None,
                "title":     title_el.get_text(strip=True) if title_el else None,
                "body":      body_text,
                "verified":  verified_el is not None,
            }))

    return reviews