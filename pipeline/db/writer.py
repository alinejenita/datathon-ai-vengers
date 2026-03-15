from sqlalchemy.dialects.postgresql import insert as pg_insert
from pipeline.db.database import SessionLocal
from pipeline.db.models import (
    Product, PriceSnapshot, RatingSnapshot,
    Review, SellerMetric, Competitor,
)


def save_product(data: dict) -> None:
    """Upsert a product row. Updates metadata fields on conflict."""
    with SessionLocal() as session:
        existing = session.query(Product).filter_by(
            asin=data["asin"],
            platform=data.get("platform", "amazon"),
        ).first()

        if existing:
            for field in ("title", "brand", "amazon_rank",
                          "bullet_points", "product_description", "category"):
                val = data.get(field)
                if val:
                    setattr(existing, field, val)
            session.commit()
            return

        session.add(Product(
            asin                = data["asin"],
            platform            = data.get("platform", "amazon"),
            title               = data.get("title"),
            brand               = data.get("brand"),
            category            = data.get("category"),
            is_own_product      = data.get("is_own_product", 0),
            seller_id           = data.get("seller_id"),
            amazon_rank         = data.get("amazon_rank"),
            bullet_points       = data.get("bullet_points"),
            product_description = data.get("product_description"),
        ))
        session.commit()


def save_embedding(asin: str, platform: str, embedding: list[float]) -> None:
    """Store the 1536-dim embedding vector on an existing product row."""
    with SessionLocal() as session:
        product = session.query(Product).filter_by(
            asin=asin, platform=platform
        ).first()
        if product:
            product.embedding = embedding
            session.commit()
        else:
            print(f"[WARN] save_embedding: product {asin} not found")


def save_price_snapshot(asin: str, price: float, currency: str = "INR") -> None:
    with SessionLocal() as session:
        session.add(PriceSnapshot(asin=asin, price=price, currency=currency))
        session.commit()


def save_rating_snapshot(asin: str, rating: float, review_count: int) -> None:
    with SessionLocal() as session:
        session.add(RatingSnapshot(asin=asin, rating=rating, review_count=review_count))
        session.commit()


def save_reviews(reviews: list[dict]) -> None:
    if not reviews:
        return
    with SessionLocal() as session:
        stmt = pg_insert(Review).values(reviews).on_conflict_do_nothing(
            index_elements=["review_id"]
        )
        session.execute(stmt)
        session.commit()


def save_seller_metric(data: dict) -> None:
    with SessionLocal() as session:
        session.add(SellerMetric(**data))
        session.commit()


def save_competitor(base_asin: str, competitor_asin: str,
                    similarity: float, competitor_type: str) -> None:
    """Upsert a competitor relationship."""
    with SessionLocal() as session:
        existing = session.query(Competitor).filter_by(
            base_asin=base_asin,
            competitor_asin=competitor_asin,
        ).first()

        if existing:
            existing.similarity      = similarity
            existing.competitor_type = competitor_type
            session.commit()
            return

        session.add(Competitor(
            base_asin       = base_asin,
            competitor_asin = competitor_asin,
            similarity      = similarity,
            competitor_type = competitor_type,
        ))
        session.commit()