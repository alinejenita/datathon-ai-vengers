print("INGESTION SCRIPT STARTED")
from datetime import datetime, timedelta
from sqlalchemy import text
from agents.db import SessionLocal


def check_data_freshness():
    """
    Checks whether scraped data is fresh.
    Returns summary of products tracked and last update time.
    """

    session = SessionLocal()

    try:
        # Get latest scrape timestamp
        result = session.execute(
            text("SELECT MAX(scraped_at) FROM price_snapshots")
        )

        last_scraped = result.scalar()

        if last_scraped is None:
            return {
                "status": "no_data",
                "message": "No scraped data found in database",
                "products_tracked": 0
            }

        now = datetime.now()
        age = now - last_scraped

        if age < timedelta(hours=6):
            status = "fresh"
        else:
            status = "stale"

        # Count tracked products
        product_count = session.execute(
            text("SELECT COUNT(DISTINCT asin) FROM products")
        ).scalar()

        return {
            "status": status,
            "last_updated": last_scraped.isoformat(),
            "products_tracked": product_count
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        session.close()


if __name__ == "__main__":
    result = check_data_freshness()
    print(result)