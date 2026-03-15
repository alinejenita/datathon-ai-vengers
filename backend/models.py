from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from backend.db.postgres import Base


# -----------------------------
# SQLAlchemy ORM Models
# -----------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    seller_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    asin = Column(String(20))
    alert_type = Column(String(50))
    severity = Column(String(20))
    message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    is_read = Column(Boolean, default=False)


class StrategyCard(Base):
    __tablename__ = "strategy_cards"

    id = Column(Integer, primary_key=True)
    seller_id = Column(String(50))
    card_rank = Column(Integer)
    action = Column(Text)
    impact = Column(Text)
    tradeoff = Column(Text)
    confidence = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


class SentimentTag(Base):
    __tablename__ = "sentiment_tags"

    id = Column(Integer, primary_key=True)
    asin = Column(String(20))
    category = Column(String(50))
    count = Column(Integer)
    period_start = Column(DateTime)
    period_end = Column(DateTime)


class GapOpportunity(Base):
    __tablename__ = "gap_opportunities"

    id = Column(Integer, primary_key=True)
    asin = Column(String(20))
    description = Column(Text)
    frequency = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


# -----------------------------
# Pydantic Schemas
# -----------------------------

class SuccessResponse(BaseModel):
    message: str
    status: int = 200

class ErrorResponse(BaseModel):
    error: str
    status: int

class UserCreate(BaseModel):
    email: str
    password: str
    seller_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    seller_name: str
    created_at: datetime

class AlertResponse(BaseModel):
    id: int
    asin: Optional[str]
    alert_type: Optional[str]
    severity: Optional[str]
    message: Optional[str]
    created_at: datetime
    is_read: bool

class ListingRewriteRequest(BaseModel):
    title: str
    bullets: List[str]
    gaps: List[str]

class ChatRequest(BaseModel):
    question: str

class StrategyRequest(BaseModel):
    seller_id: Optional[str] = "default_seller"