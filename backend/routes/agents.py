from fastapi import APIRouter, HTTPException
from backend.models import ListingRewriteRequest, ChatRequest, StrategyRequest
from backend.db_writer import (
    save_strategy_cards,
    save_sentiment_tags,
    save_gap_opportunities,
    save_pricing_alerts,
)

from agents.ingestion import check_data_freshness
from agents.pricing import run_pricing_agent
from agents.sentiment import run_sentiment_agent
from agents.gap_finder import run_gap_finder_agent
from agents.orchestrator import generate_strategy_cards
from agents.listing_writer import rewrite_listing
from agents.chat_agent import answer_question
from agents.db import get_competitors, get_own_product

router = APIRouter(tags=["agents"])


@router.get("/health")
def health():
    """Data freshness check."""
    try:
        return check_data_freshness()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pricing")
def pricing():
    """Run pricing agent — detects competitor price drops."""
    try:
        result = run_pricing_agent()
        # Persist HIGH/MEDIUM alerts to DB
        if result.get("events"):
            save_pricing_alerts(result["events"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment")
def sentiment():
    """Run sentiment agent — complaint categories per ASIN."""
    try:
        result = run_sentiment_agent()
        if result.get("sentiment"):
            save_sentiment_tags(result["sentiment"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/gaps")
def gaps():
    """Run gap finder agent — unmet customer needs."""
    try:
        result = run_gap_finder_agent()
        if result.get("gaps"):
            save_gap_opportunities(result["gaps"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategy")
def strategy(body: StrategyRequest):
    """
    Runs all three agents internally, generates 3 strategy cards,
    saves them to DB, and returns the full response.
    """
    try:
        pricing_result = run_pricing_agent()
        sentiment_result = run_sentiment_agent()
        gaps_result = run_gap_finder_agent()

        result = generate_strategy_cards(
            pricing_result.get("events", []),
            sentiment_result.get("sentiment", []),
            gaps_result.get("gaps", []),
        )

        if result.get("strategies"):
            save_strategy_cards(result["strategies"], seller_id=body.seller_id)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/listing/rewrite")
def listing_rewrite(body: ListingRewriteRequest):
    """Rewrite a product listing title and bullets using gap data."""
    try:
        return rewrite_listing(body.title, body.bullets, body.gaps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
def chat(body: ChatRequest):
    """Ask a question to the chat agent."""
    try:
        answer = answer_question(body.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competitors")
def competitors():
    """Get all competitor products from DB."""
    try:
        return get_competitors()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/product")
def own_product():
    """Get own product details from DB."""
    try:
        return get_own_product()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))