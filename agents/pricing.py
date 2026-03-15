print("PRICING AGENT STARTED")
from datetime import datetime, timedelta
from sqlalchemy import text
from agents.db import SessionLocal


def calculate_price_velocity(asins_prices):
    events = []
    for asin, snapshots in asins_prices.items():
        snapshots.sort(key=lambda x: x[0])
        latest_date, latest_price = snapshots[-1]
        for days in [7, 14, 30]:
            cutoff = latest_date - timedelta(days=days)
            past_prices = [price for d, price in snapshots if d <= cutoff]
            if not past_prices:
                continue
            old_price = past_prices[-1]
            if old_price <= 0:
                continue
            change_pct = ((latest_price - old_price) / old_price) * 100
            drop_pct = -change_pct if change_pct < 0 else 0
            if drop_pct < 3:
                continue
            severity = "HIGH" if drop_pct >= 8 else "MEDIUM"
            events.append({
                "asin": asin,
                "window_days": days,
                "price_drop_pct": round(drop_pct, 2),
                "severity": severity,
                "latest_timestamp": latest_date.isoformat()
            })
    return events


def run_pricing_agent():
    session = SessionLocal()
    try:
        rows = session.execute(
            text("SELECT asin, scraped_at, price FROM price_snapshots ORDER BY asin, scraped_at")
        ).fetchall()
        if not rows:
            return {
                "events": [],
                "message": "No price snapshot data available"
            }

        asins = {}
        for asin, scraped_at, price in rows:
            if asin is None or scraped_at is None or price is None:
                continue
            asins.setdefault(asin, []).append((scraped_at, float(price)))

        events = calculate_price_velocity(asins)
        return {
            "events": events,
            "event_count": len(events)
        }
    except Exception as e:
        return {
            "events": [],
            "error": str(e)
        }
    finally:
        session.close()


if __name__ == "__main__":
    result = run_pricing_agent()
    print(result)
