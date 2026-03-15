from datetime import datetime
from backend.db.postgres import SessionLocal
from backend.models import StrategyCard, SentimentTag, GapOpportunity, Alert


def save_strategy_cards(cards: list, seller_id: str = "default_seller"):
    """Save strategy cards returned by generate_strategy_cards() to DB."""
    db = SessionLocal()
    try:
        # Delete old cards for this seller before inserting fresh ones
        db.query(StrategyCard).filter(StrategyCard.seller_id == seller_id).delete()

        for rank, card in enumerate(cards, start=1):
            db.add(StrategyCard(
                seller_id=seller_id,
                card_rank=rank,
                action=card.get("action", ""),
                impact=card.get("impact", ""),
                tradeoff=card.get("tradeoff", ""),
                confidence=int(card.get("confidence", 0)),
            ))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def save_sentiment_tags(sentiment_list: list):
    """Save sentiment data from run_sentiment_agent() to sentiment_tags table."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        for item in sentiment_list:
            asin = item.get("asin")
            for category in item.get("top_complaint_categories", []):
                db.add(SentimentTag(
                    asin=asin,
                    category=category,
                    count=item.get("review_count", 0),
                    period_start=now,
                    period_end=now,
                ))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def save_gap_opportunities(gaps: list):
    """Save gaps from run_gap_finder_agent() to gap_opportunities table."""
    db = SessionLocal()
    try:
        for gap in gaps:
            db.add(GapOpportunity(
                asin=None,  # top-level gaps have no specific asin
                description=gap.get("gap", ""),
                frequency=gap.get("mentions", 0),
            ))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def save_pricing_alerts(events: list):
    """Save HIGH/MEDIUM pricing events as alerts."""
    db = SessionLocal()
    try:
        for event in events:
            db.add(Alert(
                asin=event.get("asin"),
                alert_type="price_drop",
                severity=event.get("severity", "MEDIUM"),
                message=(
                    f"Price dropped {event.get('price_drop_pct')}% "
                    f"over {event.get('window_days')} days"
                ),
            ))
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()