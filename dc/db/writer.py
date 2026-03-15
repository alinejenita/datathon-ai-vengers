from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert as pg_insert
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
            return  # already registered, skip
        product = Product(**data)
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

def save_reviews(reviews: list[dict]):
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