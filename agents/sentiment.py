print("SENTIMENT AGENT STARTED")
import json
from collections import Counter, defaultdict
from sqlalchemy import text
from agents.db import SessionLocal
from agents.claude_client import call_claude

VALID_CATEGORIES = {"durability", "shipping", "quality", "packaging", "value", "size", "other"}

def classify_review_with_rules(text):
    lower = text.lower()
    if any(k in lower for k in ["broken", "broke", "durable", "durability"]):
        return "durability"
    if any(k in lower for k in ["slow shipping", "late", "arrived", "delayed"]):
        return "shipping"
    if any(k in lower for k in ["cheap", "poor quality", "quality", "defect"]):
        return "quality"
    if any(k in lower for k in ["package", "packaging", "box"]):
        return "packaging"
    if any(k in lower for k in ["expensive", "value", "worth"]):
        return "value"
    if any(k in lower for k in ["small", "large", "size", "fit"]):
        return "size"
    return "other"

def classify_review(review_text):
    system_prompt = (
        "You are an e-commerce review analyst. "
        "Classify the review into exactly one category: "
        "durability, shipping, quality, packaging, value, size, or other. "
        "Respond with ONLY valid JSON: {\"category\": \"<one of the above>\"}. "
        "No explanation, no markdown, no extra text."
    )
    user_prompt = f"Review: {review_text}"
    response = call_claude(system_prompt, user_prompt, max_tokens=60)

    if "error" in response:
        return classify_review_with_rules(review_text)

    try:
        parsed = json.loads(response["message"])
        cat = parsed.get("category", "").strip().lower()
        if cat in VALID_CATEGORIES:
            return cat
    except Exception:
        pass

    return classify_review_with_rules(review_text)

def run_sentiment_agent(batch_limit=300):
    session = SessionLocal()
    try:
        rows = session.execute(
            text("SELECT asin, body, scraped_at FROM reviews ORDER BY scraped_at DESC LIMIT :limit"),
            {"limit": batch_limit}
        ).fetchall()

        if not rows:
            return {"sentiment": [], "message": "No reviews found"}

        asins = defaultdict(list)
        for asin, body, scraped_at in rows:
            if not asin or not body:
                continue
            category = classify_review(body)
            asins[asin].append({"text": body, "category": category, "scraped_at": scraped_at})

        summary = []
        for asin, reviews in asins.items():
            counts = Counter(r["category"] for r in reviews)
            top_categories = [c for c, _ in counts.most_common(3)]
            sentiment_drift = "stable"
            if len(reviews) >= 4:
                midpoint = len(reviews) // 2
                old = Counter(r["category"] for r in reviews[midpoint:])
                recent = Counter(r["category"] for r in reviews[:midpoint])
                if recent.get("quality", 0) > old.get("quality", 0) + 2:
                    sentiment_drift = "worsening"
                elif recent.get("quality", 0) < old.get("quality", 0) - 2:
                    sentiment_drift = "improving"

            summary.append({
                "asin": asin,
                "review_count": len(reviews),
                "top_complaint_categories": top_categories,
                "sentiment_drift": sentiment_drift
            })

        return {"sentiment": summary, "asin_count": len(summary)}

    except Exception as e:
        return {"sentiment": [], "error": str(e)}
    finally:
        session.close()

if __name__ == "__main__":
    print(run_sentiment_agent())
