"""
pipeline/scheduler.py
──────────────────────
Main entry point for the Datathon data pipeline.

Stages per run:
  1. ensure_schema()            — sync DB tables from models
  2. run_seller_pipeline()      — scrape own product + save metrics
  3. run_competitor_pipeline()  — scrape hardcoded + auto-discovered competitors
  4. run_embedding_pipeline()   — generate embeddings for products missing them
  5. run_similarity_pipeline()  — detect & save competitor relationships

Run manually:  python -m pipeline.scheduler
Scheduled:     every SCRAPE_INTERVAL_HOURS hours via APScheduler
"""

import random
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler

from pipeline.db.database import engine
from pipeline.db.models import ensure_schema
from pipeline.config import SCRAPE_INTERVAL_HOURS

from pipeline.scrapers.amazon import scrape_product, scrape_reviews
from pipeline.scrapers.amazon_search import discover_competitors

from pipeline.db.writer import (
    save_product, save_price_snapshot,
    save_rating_snapshot, save_reviews, save_seller_metric,
)

from pipeline.competitors.embedding_service import embed_all_missing
from pipeline.competitors.similarity_search import detect_all_competitors

# ── Static ASINs ──────────────────────────────────────────────────────────
OWN_ASINS = [
    {"asin": "B0F8BVSK21", "label": "boAt Airdopes 141 Gen 2 (Own)"},
]

COMPETITOR_ASINS = [
    {"asin": "B0D9R4GYTN", "label": "Sony WF-C510"},
    {"asin": "B0DHL8XLX5", "label": "JBL Wave Flex 2"},
    {"asin": "B09Y5MK1KB", "label": "Noise Buds VS104"},
    {"asin": "B0DZCRYG7R", "label": "Competitor 4"},
]

# Keywords for auto-discovery
DISCOVERY_KEYWORDS = [
    "tws earbuds under 2000",
    "wireless earbuds india",
    "boat airdopes alternative",
]

# Cap on auto-discovered competitors — keeps each run under ~10 minutes
MAX_AUTO_DISCOVERED = 20


# ── Stage 1: Own product ──────────────────────────────────────────────────
def run_seller_pipeline():
    print(f"\n[SELLER] Starting seller pipeline...")
    today = datetime.now(timezone.utc)

    for item in OWN_ASINS:
        asin    = item["asin"]
        product = scrape_product(asin)

        if product:
            save_product({
                "asin":                asin,
                "title":               product["title"],
                "brand":               product["brand"],
                "is_own_product":      1,
                "platform":            "amazon",
                "amazon_rank":         product.get("amazon_rank"),
                "bullet_points":       product.get("bullet_points"),
                "product_description": product.get("product_description"),
            })

            if product.get("price"):
                save_price_snapshot(asin, product["price"])

            if product.get("rating"):
                save_rating_snapshot(asin, product["rating"],
                                     product.get("review_count", 0))

            print(f"  ✓ {item['label']} | price={product['price']} | rating={product['rating']}")
        else:
            print(f"  ✗ {item['label']} — scrape failed")

        # Simulated seller metrics (SP-API not available)
        save_seller_metric({
            "asin":            asin,
            "units_sold":      random.randint(10, 60),
            "revenue":         round(random.uniform(5000, 40000), 2),
            "sessions":        random.randint(100, 600),
            "conversion_rate": round(random.uniform(0.04, 0.18), 3),
            "period_start":    today.replace(hour=0,  minute=0,  second=0,  microsecond=0),
            "period_end":      today.replace(hour=23, minute=59, second=59, microsecond=0),
        })
        print(f"    └─ seller metrics saved")


# ── Stage 2: Competitors ──────────────────────────────────────────────────
def run_competitor_pipeline():
    print(f"\n[COMPETITOR] Starting competitor pipeline...")

    # Auto-discover new competitors from search pages
    own_asins = {item["asin"] for item in OWN_ASINS}
    known     = {item["asin"] for item in COMPETITOR_ASINS}

    try:
        discovered = discover_competitors(
            keywords      = DISCOVERY_KEYWORDS,
            exclude_asins = own_asins,
        )
        discovered = discovered[:MAX_AUTO_DISCOVERED]   # cap to keep runs fast
        new_count = 0
        for p in discovered:
            if p["asin"] not in known:
                COMPETITOR_ASINS.append({"asin": p["asin"], "label": p.get("title", "Auto-discovered")})
                known.add(p["asin"])
                new_count += 1
        print(f"  └─ Auto-discovered {new_count} new competitor ASINs (capped at {MAX_AUTO_DISCOVERED})")
    except Exception as e:
        print(f"  [WARN] Auto-discovery failed: {e}")

    # Scrape all competitors
    for item in COMPETITOR_ASINS:
        asin    = item["asin"]
        product = scrape_product(asin)

        if product:
            save_product({
                "asin":                asin,
                "title":               product["title"],
                "brand":               product["brand"],
                "is_own_product":      0,
                "platform":            "amazon",
                "amazon_rank":         product.get("amazon_rank"),
                "bullet_points":       product.get("bullet_points"),
                "product_description": product.get("product_description"),
            })

            if product.get("price"):
                save_price_snapshot(asin, product["price"])

            if product.get("rating"):
                save_rating_snapshot(asin, product["rating"],
                                     product.get("review_count", 0))

            print(f"  ✓ {item['label']} | price={product['price']} | rating={product['rating']}")
        else:
            print(f"  ✗ {item['label']} ({asin}) — scrape failed")

        reviews = scrape_reviews(asin)
        if reviews:
            save_reviews(reviews)
            print(f"    └─ {len(reviews)} reviews saved")


# ── Stage 3: Embeddings ───────────────────────────────────────────────────
def run_embedding_pipeline():
    print(f"\n[EMBED] Generating missing embeddings...")
    try:
        stats = embed_all_missing(platform="amazon")
        print(f"  └─ {stats}")
    except Exception as e:
        print(f"  [WARN] Embedding pipeline failed: {e}")


# ── Stage 4: Similarity / competitor detection ────────────────────────────
def run_similarity_pipeline():
    print(f"\n[SIMILARITY] Detecting competitor relationships...")
    try:
        stats = detect_all_competitors()
        print(f"  └─ {stats}")
    except Exception as e:
        print(f"  [WARN] Similarity pipeline failed: {e}")


# ── Full run ──────────────────────────────────────────────────────────────
def run_full_pipeline():
    print(f"\n{'='*60}")
    print(f"Pipeline started at {datetime.now()}")
    print(f"{'='*60}")

    run_seller_pipeline()
    run_competitor_pipeline()
    run_embedding_pipeline()
    run_similarity_pipeline()

    print(f"\nPipeline complete at {datetime.now()}")
    print(f"{'='*60}\n")


# ── Entry point ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Datathon pipeline starting...")

    # Always sync schema first
    ensure_schema(engine)

    # Run immediately on start
    run_full_pipeline()

    # Then schedule recurring runs
    scheduler = BlockingScheduler()
    scheduler.add_job(
        run_full_pipeline,
        "interval",
        hours=SCRAPE_INTERVAL_HOURS,
    )

    print(f"Scheduler running — every {SCRAPE_INTERVAL_HOURS}h. Ctrl+C to stop.\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\nScheduler stopped.")