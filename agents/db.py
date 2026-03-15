import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from pipeline.db.queries import (
    get_product_full,
    get_all_competitors,
    get_price_comparison,
    get_recent_reviews,
    get_seller_summary,
    list_all_products,
)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

OWN_ASIN = "B0F8BVSK21"

def get_own_product():
    return get_product_full(OWN_ASIN)

def get_competitors():
    return get_all_competitors(OWN_ASIN)

def get_pricing():
    return get_price_comparison(OWN_ASIN)

def get_reviews(limit=50):
    return get_recent_reviews(OWN_ASIN, limit=limit)

def get_seller_stats():
    return get_seller_summary(OWN_ASIN, days=30)
