import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import text
from pipeline.db.models import (
    Product, PriceSnapshot, RatingSnapshot,
    Review, SellerMetric, init_db
)
from pipeline.config import DATABASE_URL

engine = init_db()
Session = sessionmaker(bind=engine)

def save_product(data: dict):
    with Session() as session:
        existing = session.query(Product).filter_by(
            asin=data["asin"], platform=data.get("platform", "amazon")
        ).first()
        if existing:
            return
        product = Product(**{k: v for k, v in data.items() if hasattr(Product, k)})
        session.add(product)
        session.commit()

def save_price_snapshot(asin: str, price: float, currency: str = "INR"):
    with Session() as session:
        snap = PriceSnapshot(asin=asin, price=price, currency=currency)
        session.add(snap)
        session.commit()

def save_rating_snapshot(asin: str, rating: float, review_count: int):
    with Session() as session:
        snap = RatingSnapshot(asin=asin, rating=rating, review_count=review_count)
        session.add(snap)
        session.commit()

def save_reviews(reviews: list):
    if not reviews:
        return
    with Session() as session:
        stmt = pg_insert(Review).values(reviews).on_conflict_do_nothing(
            index_elements=["review_id"]
        )
        session.execute(stmt)
        session.commit()

def save_seller_metric(data: dict):
    with Session() as session:
        metric = SellerMetric(**data)
        session.add(metric)
        session.commit()

def save_embedding(asin: str, platform: str = "amazon", embedding: list = None):
    with Session() as session:
        session.execute(
            text("""
                UPDATE products
                SET embedding = :embedding
                WHERE asin = :asin AND platform = :platform
            """),
            {"asin": asin, "platform": platform, "embedding": json.dumps(embedding)}
        )
        session.commit()

def save_competitor(base_asin: str, competitor_asin: str, similarity: float, competitor_type: str):
    with Session() as session:
        session.execute(
            text("""
                INSERT INTO competitor_relationships (own_asin, competitor_asin, relationship_type, similarity_score)
                VALUES (:own_asin, :competitor_asin, :relationship_type, :similarity_score)
                ON CONFLICT (own_asin, competitor_asin) DO UPDATE SET
                    similarity_score = :similarity_score,
                    relationship_type = :relationship_type
            """),
            {
                "own_asin": base_asin,
                "competitor_asin": competitor_asin,
                "relationship_type": competitor_type,
                "similarity_score": similarity
            }
        )
        session.commit()
