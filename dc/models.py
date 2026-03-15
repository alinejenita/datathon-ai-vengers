from sqlalchemy import Column, String, Float, Integer, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone
from pipeline.config import DATABASE_URL

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("asin", "platform", name="uq_asin_platform"),)
    id                  = Column(Integer, primary_key=True, autoincrement=True)
    asin                = Column(String, nullable=False)
    platform            = Column(String, default="amazon")
    title               = Column(String)
    brand               = Column(String)
    category            = Column(String)
    is_own_product      = Column(Integer, default=0)
    seller_id           = Column(String)
    amazon_rank         = Column(Text)
    bullet_points       = Column(Text)
    product_description = Column(Text)
    embedding           = Column(Text)
    created_at          = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    asin       = Column(String)
    price      = Column(Float)
    currency   = Column(String, default="INR")
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class RatingSnapshot(Base):
    __tablename__ = "rating_snapshots"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    asin         = Column(String)
    rating       = Column(Float)
    review_count = Column(Integer)
    scraped_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Review(Base):
    __tablename__ = "reviews"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    asin        = Column(String)
    review_id   = Column(String, unique=True)
    rating      = Column(Float)
    title       = Column(String)
    body        = Column(Text)
    review_text = Column(Text)
    verified    = Column(Integer, default=0)
    scraped_at  = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class SellerMetric(Base):
    __tablename__ = "seller_metrics"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    asin            = Column(String)
    units_sold      = Column(Integer)
    revenue         = Column(Float)
    sessions        = Column(Integer)
    conversion_rate = Column(Float)
    period_start    = Column(DateTime)
    period_end      = Column(DateTime)
    fetched_at      = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class CompetitorRelationship(Base):
    __tablename__ = "competitor_relationships"
    __table_args__ = (UniqueConstraint("own_asin", "competitor_asin", name="uq_competitor_pair"),)
    id                = Column(Integer, primary_key=True, autoincrement=True)
    own_asin          = Column(String, nullable=False)
    competitor_asin   = Column(String, nullable=False)
    relationship_type = Column(String)
    similarity_score  = Column(Float)
    created_at        = Column(DateTime, default=lambda: datetime.now(timezone.utc))

def init_db():
    from sqlalchemy import create_engine
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine

def ensure_schema(engine=None):
    if engine is None:
        from sqlalchemy import create_engine
        engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine

# Alias so old imports still work
Competitor = CompetitorRelationship
