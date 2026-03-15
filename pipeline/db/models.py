from sqlalchemy import (
    Column, String, Float, Integer,
    DateTime, Text, UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector

Base = declarative_base()


# ── PRODUCTS ──────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("asin", "platform", name="uq_asin_platform"),
    )

    id          = Column(Integer, primary_key=True, autoincrement=True)
    asin        = Column(String, nullable=False)
    platform    = Column(String, default="amazon")   # amazon | flipkart

    title       = Column(String)
    brand       = Column(String)
    category    = Column(String)

    is_own_product = Column(Integer, default=0)      # 1 = seller's own product
    seller_id      = Column(String)                  # future multi-seller support

    amazon_rank         = Column(String)
    bullet_points       = Column(Text)
    product_description = Column(Text)

    # pgvector embedding (all-MiniLM-L6-v2 → 384 dims)
    embedding = Column(Vector(384))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── PRICE HISTORY ─────────────────────────────────────────────────────────
class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    asin       = Column(String, nullable=False)
    price      = Column(Float)
    currency   = Column(String, default="INR")
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── RATING HISTORY ────────────────────────────────────────────────────────
class RatingSnapshot(Base):
    __tablename__ = "rating_snapshots"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    asin         = Column(String, nullable=False)
    rating       = Column(Float)
    review_count = Column(Integer)
    scraped_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── REVIEWS ───────────────────────────────────────────────────────────────
class Review(Base):
    __tablename__ = "reviews"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    asin      = Column(String, nullable=False)
    review_id = Column(String, unique=True)          # dedup key

    rating   = Column(Float)
    title    = Column(String)
    body     = Column(Text)
    verified = Column(Integer, default=0)

    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── SELLER METRICS ────────────────────────────────────────────────────────
class SellerMetric(Base):
    __tablename__ = "seller_metrics"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    asin            = Column(String, nullable=False)
    units_sold      = Column(Integer)
    revenue         = Column(Float)
    sessions        = Column(Integer)
    conversion_rate = Column(Float)
    period_start    = Column(DateTime)
    period_end      = Column(DateTime)
    fetched_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── COMPETITOR RELATIONSHIPS ──────────────────────────────────────────────
class Competitor(Base):
    __tablename__ = "competitors"
    __table_args__ = (
        UniqueConstraint("base_asin", "competitor_asin", name="uq_competitor_pair"),
    )

    id              = Column(Integer, primary_key=True, autoincrement=True)
    base_asin       = Column(String, nullable=False)
    competitor_asin = Column(String, nullable=False)
    similarity      = Column(Float)
    competitor_type = Column(String)    # same_product | similar_product
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ── SCHEMA INIT ───────────────────────────────────────────────────────────
def ensure_schema(engine):
    """
    Create all tables if they don't exist. Never drops or modifies existing
    columns — safe to call on every scheduler start.
    """
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(engine)
    print("[DB] Schema synced.")