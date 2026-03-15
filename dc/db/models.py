from sqlalchemy import (
    Column, String, Float, Integer,
    DateTime, Text, create_engine, UniqueConstraint
)
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
from pipeline.config import DATABASE_URL

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("asin", "platform", name="uq_asin_platform"),)

    id              = Column(Integer, primary_key=True, autoincrement=True)  # surrogate PK
    asin            = Column(String, nullable=False)
    platform        = Column(String, default="amazon")   # amazon | flipkart
    title           = Column(String)
    brand           = Column(String)
    category        = Column(String)
    is_own_product  = Column(Integer, default=0)         # 1 = seller's own, 0 = competitor
    seller_id       = Column(String)                     # links to the logged-in seller
    created_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    asin        = Column(String)
    price       = Column(Float)
    currency    = Column(String, default="INR")
    scraped_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RatingSnapshot(Base):
    __tablename__ = "rating_snapshots"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    asin            = Column(String)
    rating          = Column(Float)
    review_count    = Column(Integer)
    scraped_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Review(Base):
    __tablename__ = "reviews"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    asin            = Column(String)
    review_id       = Column(String, unique=True)        # dedup key
    rating          = Column(Float)
    title           = Column(String)
    body            = Column(Text)
    verified        = Column(Integer, default=0)
    scraped_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SellerMetric(Base):
    __tablename__ = "seller_metrics"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    asin            = Column(String)
    units_sold      = Column(Integer)
    revenue         = Column(Float)
    sessions        = Column(Integer)                    # listing visits
    conversion_rate = Column(Float)                      # sessions → sales %
    period_start    = Column(DateTime)
    period_end      = Column(DateTime)
    fetched_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return engine