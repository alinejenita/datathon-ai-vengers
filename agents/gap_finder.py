print("GAP FINDER AGENT STARTED")
import re
from collections import Counter, defaultdict
from sqlalchemy import text
from agents.db import SessionLocal

def extract_gaps_from_review(text):
    lower = text.lower()
    wants = []
    if "wish" in lower:
        m = re.search(r"wish (it|this|they|there|the product)? (.*)", lower)
        if m:
            wants.append(m.group(2).strip(".?!"))
    if "would be better" in lower or "would have" in lower:
        wants.append("better features")
    if "if only" in lower:
        m = re.search(r"if only (.*)", lower)
        if m:
            wants.append(m.group(1).strip(".?!"))
    for phrase in ["carrying case", "battery life", "more colors", "faster shipping", "easier setup"]:
        if phrase in lower:
            wants.append(phrase)
    return wants

def run_gap_finder_agent(max_reviews=500):
    session = SessionLocal()
    try:
        rows = session.execute(
            text("SELECT asin, body FROM reviews ORDER BY scraped_at DESC LIMIT :limit"),
            {"limit": max_reviews}
        ).fetchall()

        if not rows:
            return {"gaps": [], "message": "No review data to analyze"}

        gap_counts = Counter()
        asin_gaps = defaultdict(Counter)
        for asin, body in rows:
            if not body:
                continue
            extracted = extract_gaps_from_review(body)
            for gap in extracted:
                normalized = gap.strip().rstrip(".?!")
                if len(normalized) < 4:
                    continue
                gap_counts[normalized] += 1
                asin_gaps[asin][normalized] += 1

        top_gaps = [
            {"gap": gap, "mentions": count}
            for gap, count in gap_counts.most_common(10)
        ]

        return {
            "gaps": top_gaps,
            "asin_gaps": {
                asin: [
                    {"gap": gap, "mentions": count}
                    for gap, count in c.most_common(5)
                ]
                for asin, c in asin_gaps.items()
            }
        }
    except Exception as e:
        return {"gaps": [], "error": str(e)}
    finally:
        session.close()

if __name__ == "__main__":
    print(run_gap_finder_agent())
