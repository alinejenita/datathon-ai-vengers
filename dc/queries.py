from datetime import datetime, timezone, timedelta
from pipeline.db.database import SessionLocal
from pipeline.db.models import (
    Product, PriceSnapshot, RatingSnapshot,
    Review, SellerMetric, CompetitorRelationship,
)

def get_product_full(asin: str, platform: str = "amazon") -> dict | None:
    with SessionLocal() as session:
        product = session.query(Product).filter_by(asin=asin, platform=platform).first()
        if not product:
            return None
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        prices = session.query(PriceSnapshot).filter(
            PriceSnapshot.asin == asin, PriceSnapshot.scraped_at >= cutoff
        ).order_by(PriceSnapshot.scraped_at.desc()).limit(30).all()
        ratings = session.query(RatingSnapshot).filter(
            RatingSnapshot.asin == asin, RatingSnapshot.scraped_at >= cutoff
        ).order_by(RatingSnapshot.scraped_at.desc()).limit(30).all()
        reviews = session.query(Review).filter(
            Review.asin == asin
        ).order_by(Review.scraped_at.desc()).limit(20).all()
        metrics = session.query(SellerMetric).filter(
            SellerMetric.asin == asin, SellerMetric.period_start >= cutoff
        ).order_by(SellerMetric.period_start.desc()).limit(30).all()
        return {
            "product": _product_to_dict(product),
            "price_history": [{"price": p.price, "currency": p.currency, "scraped_at": p.scraped_at.isoformat()} for p in prices],
            "rating_history": [{"rating": r.rating, "review_count": r.review_count, "scraped_at": r.scraped_at.isoformat()} for r in ratings],
            "reviews": [{"rating": r.rating, "title": r.title, "body": r.body, "verified": r.verified, "scraped_at": r.scraped_at.isoformat()} for r in reviews],
            "seller_metrics": [{"units_sold": m.units_sold, "revenue": m.revenue, "sessions": m.sessions, "conversion_rate": m.conversion_rate, "period_start": m.period_start.isoformat(), "period_end": m.period_end.isoformat()} for m in metrics],
        }

def get_all_competitors(asin: str) -> list[dict]:
    with SessionLocal() as session:
        rows = session.query(CompetitorRelationship).filter(
            CompetitorRelationship.own_asin == asin
        ).order_by(CompetitorRelationship.similarity_score.desc()).all()
        result = []
        for row in rows:
            comp_product = session.query(Product).filter_by(asin=row.competitor_asin).first()
            latest_price = session.query(PriceSnapshot).filter(
                PriceSnapshot.asin == row.competitor_asin
            ).order_by(PriceSnapshot.scraped_at.desc()).first()
            latest_rating = session.query(RatingSnapshot).filter(
                RatingSnapshot.asin == row.competitor_asin
            ).order_by(RatingSnapshot.scraped_at.desc()).first()
            result.append({
                "competitor_asin": row.competitor_asin,
                "similarity": row.similarity_score,
                "competitor_type": row.relationship_type,
                "product": _product_to_dict(comp_product) if comp_product else None,
                "latest_price": latest_price.price if latest_price else None,
                "latest_rating": latest_rating.rating if latest_rating else None,
                "latest_review_count": latest_rating.review_count if latest_rating else None,
            })
        return result

def get_price_comparison(base_asin: str) -> dict:
    with SessionLocal() as session:
        def latest_price(asin):
            snap = session.query(PriceSnapshot).filter(
                PriceSnapshot.asin == asin
            ).order_by(PriceSnapshot.scraped_at.desc()).first()
            return snap.price if snap else None
        competitors = session.query(CompetitorRelationship).filter(
            CompetitorRelationship.own_asin == base_asin
        ).all()
        return {
            "own_asin": base_asin,
            "own_price": latest_price(base_asin),
            "competitors": [{"asin": c.competitor_asin, "competitor_type": c.relationship_type, "price": latest_price(c.competitor_asin)} for c in competitors],
        }

def get_recent_reviews(asin: str, limit: int = 50) -> list[dict]:
    with SessionLocal() as session:
        reviews = session.query(Review).filter(
            Review.asin == asin
        ).order_by(Review.scraped_at.desc()).limit(limit).all()
        return [{"rating": r.rating, "title": r.title, "body": r.body, "verified": r.verified, "scraped_at": r.scraped_at.isoformat()} for r in reviews]

def list_all_products(platform: str = "amazon") -> list[dict]:
    with SessionLocal() as session:
        products = session.query(Product).filter(
            Product.platform == platform
        ).order_by(Product.is_own_product.desc(), Product.created_at).all()
        return [_product_to_dict(p) for p in products]

def get_seller_summary(asin: str, days: int = 30) -> dict:
    with SessionLocal() as session:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        metrics = session.query(SellerMetric).filter(
            SellerMetric.asin == asin, SellerMetric.period_start >= cutoff
        ).all()
        if not metrics:
            return {"asin": asin, "days": days, "data": None}
        total_units = sum(m.units_sold or 0 for m in metrics)
        total_revenue = sum(m.revenue or 0 for m in metrics)
        avg_sessions = sum(m.sessions or 0 for m in metrics) / len(metrics)
        avg_conv = sum(m.conversion_rate or 0 for m in metrics) / len(metrics)
        return {
            "asin": asin,
            "days": days,
            "total_units_sold": total_units,
            "total_revenue": round(total_revenue, 2),
            "avg_sessions": round(avg_sessions, 1),
            "avg_conversion": round(avg_conv, 4),
        }

def _product_to_dict(p) -> dict:
    return {
        "id": p.id,
        "asin": p.asin,
        "platform": p.platform,
        "title": p.title,
        "brand": p.brand,
        "category": p.category,
        "is_own_product": p.is_own_product,
        "amazon_rank": p.amazon_rank,
        "bullet_points": p.bullet_points,
        "product_description": p.product_description,
        "has_embedding": p.embedding is not None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
