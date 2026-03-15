"""
seed_mock_data.py
──────────────────
Seeds the database with 30 days of mock historical data for:
  - Own product (boAt Airdopes 141 Gen 2)
  - 4 real competitor products

Run once to bootstrap the DB before live scraping starts:
    python seed_mock_data.py
"""

import random
from datetime import datetime, timedelta, timezone

from pipeline.db.models import ensure_schema
from pipeline.db.database import engine
from pipeline.db.writer import (
    save_product, save_price_snapshot,
    save_rating_snapshot, save_reviews, save_seller_metric,
)

# ── Products ──────────────────────────────────────────────────────────────
OWN_PRODUCTS = [
    {
        "asin":           "B0F8BVSK21",
        "title":          "boAt Airdopes 141 Gen 2 True Wireless Earbuds",
        "brand":          "boAt",
        "is_own_product": 1,
        "platform":       "amazon",
        "price_range":    (899, 1299),
        "rating_range":   (4.0, 4.5),
        "review_range":   (10000, 18000),
        "units_range":    (20, 80),
        "revenue_factor": 1099,
    },
]

COMPETITOR_PRODUCTS = [
    {
        "asin":         "B0D9R4GYTN",
        "title":        "Sony WF-C510 True Wireless Earbuds",
        "brand":        "Sony",
        "price_range":  (2499, 3499),
        "rating_range": (4.1, 4.6),
        "review_range": (2000, 5000),
    },
    {
        "asin":         "B0DHL8XLX5",
        "title":        "JBL Wave Flex 2 True Wireless Earbuds",
        "brand":        "JBL",
        "price_range":  (1999, 2999),
        "rating_range": (3.9, 4.4),
        "review_range": (1500, 4000),
    },
    {
        "asin":         "B09Y5MK1KB",
        "title":        "Noise Buds VS104 True Wireless Earbuds",
        "brand":        "Noise",
        "price_range":  (699, 999),
        "rating_range": (3.8, 4.3),
        "review_range": (8000, 15000),
    },
    {
        "asin":         "B0DZCRYG7R",
        "title":        "Competitor TWS Earbuds",
        "brand":        "Unknown",
        "price_range":  (599, 1199),
        "rating_range": (3.5, 4.2),
        "review_range": (500, 3000),
    },
]

REVIEW_BODIES = [
    "Really happy with this purchase. Sound quality is excellent for the price.",
    "Decent product. Battery life could be better but overall good value.",
    "Comfortable to wear for long hours. Noise isolation works well.",
    "Great sound, easy pairing. Mic quality is average.",
    "Value for money. Build quality feels premium.",
    "Bass is punchy, good for gym use. Recommended!",
    "Had connectivity issues initially but resolved after firmware update.",
    "Impressive ANC for this price range. Highly recommend.",
]

REVIEW_TITLES = [
    "Great product!", "Value for money", "Good but could be better",
    "Highly recommended", "Decent earbuds", "Best in this price range",
]


def seed_product_history(product: dict, is_own: bool = False):
    """Seed 30 days of price, rating history + some reviews for a product."""
    asin  = product["asin"]
    today = datetime.now(timezone.utc)

    # Save product row
    save_product({
        "asin":           asin,
        "title":          product["title"],
        "brand":          product["brand"],
        "is_own_product": 1 if is_own else 0,
        "platform":       "amazon",
    })

    lo_p, hi_p = product["price_range"]
    lo_r, hi_r = product["rating_range"]
    lo_rc, hi_rc = product["review_range"]

    # 30 days of snapshots
    for days_ago in range(30, 0, -1):
        date = today - timedelta(days=days_ago)
        save_price_snapshot(asin,
                            round(random.uniform(lo_p, hi_p), 2))
        save_rating_snapshot(asin,
                             round(random.uniform(lo_r, hi_r), 1),
                             random.randint(lo_rc, hi_rc))

    # 10 mock reviews
    save_reviews([
        {
            "asin":      asin,
            "review_id": f"{asin}_seed_{i}",
            "rating":    round(random.uniform(3.0, 5.0), 1),
            "title":     random.choice(REVIEW_TITLES),
            "body":      random.choice(REVIEW_BODIES),
            "verified":  1,
        }
        for i in range(10)
    ])

    print(f"  ✓ Seeded {asin} ({product['title'][:40]})")


def seed_seller_metrics():
    """Seed 30 days of seller metrics for own products."""
    today = datetime.now(timezone.utc)

    for p in OWN_PRODUCTS:
        asin = p["asin"]
        for days_ago in range(30, 0, -1):
            date   = today - timedelta(days=days_ago)
            units  = random.randint(*p["units_range"])
            revenue = round(units * random.uniform(
                p["revenue_factor"] * 0.85,
                p["revenue_factor"] * 1.15,
            ), 2)
            save_seller_metric({
                "asin":            asin,
                "units_sold":      units,
                "revenue":         revenue,
                "sessions":        random.randint(80, 500),
                "conversion_rate": round(random.uniform(0.04, 0.18), 3),
                "period_start":    date.replace(hour=0,  minute=0,  second=0,  microsecond=0),
                "period_end":      date.replace(hour=23, minute=59, second=59, microsecond=0),
            })

        print(f"  ✓ Seeded 30 days seller metrics for {asin}")


if __name__ == "__main__":
    print("Syncing DB schema...")
    ensure_schema(engine)

    print("\nSeeding own products...")
    for p in OWN_PRODUCTS:
        seed_product_history(p, is_own=True)

    print("\nSeeding competitor products...")
    for p in COMPETITOR_PRODUCTS:
        seed_product_history(p, is_own=False)

    print("\nSeeding seller metrics...")
    seed_seller_metrics()

    print("\n✓ Seed complete!")