print("STRATEGY ORCHESTRATOR STARTED")
import json
from agents.claude_client import call_claude

def compute_competitor_health(pricing_events, sentiment_summary, gaps):
    score = 70
    for ev in pricing_events:
        drop = float(ev.get("price_drop_pct", 0))
        if ev.get("severity") == "HIGH":
            score -= min(25, drop * 1.5)
        elif ev.get("severity") == "MEDIUM":
            score -= min(15, drop)
    for s in sentiment_summary:
        drift = s.get("sentiment_drift", "stable")
        if drift == "worsening":
            score -= 12
        elif drift == "improving":
            score += 8
    if gaps:
        score -= min(10, len(gaps) * 1.2)
    return max(0, min(100, int(score)))

def generate_strategy_cards(pricing_events, sentiment_summary, gaps, seller_metrics=None):
    health_score = compute_competitor_health(pricing_events, sentiment_summary, gaps)

    system_prompt = (
        "You are a strategic advisor for an e-commerce seller on Amazon India. "
        "You will receive market signals (competitor pricing events, sentiment drift, product gaps, seller metrics). "
        "You must return ONLY valid JSON — no markdown, no explanation — in exactly this structure:\n"
        "{\n"
        "  \"strategies\": [\n"
        "    {\n"
        "      \"action\": \"<specific recommended action>\",\n"
        "      \"impact\": \"<estimated business impact>\",\n"
        "      \"tradeoff\": \"<risk or downside>\",\n"
        "      \"confidence\": \"<integer 0-100>\"\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Always return exactly 3 strategies. Be specific and data-driven."
    )

    payload = {
        "pricing_events": pricing_events,
        "sentiment_summary": sentiment_summary,
        "gaps": gaps,
        "seller_metrics": seller_metrics or {},
        "competitor_health_score": health_score
    }

    user_prompt = (
        f"Market signals for analysis:\n{json.dumps(payload, default=str, indent=2)}\n\n"
        "Generate exactly 3 ranked strategy cards based on these signals."
    )

    response = call_claude(system_prompt, user_prompt, max_tokens=800)

    if "error" not in response:
        try:
            text = response["message"].strip()
            # Strip markdown fences if Claude adds them despite instructions
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            parsed = json.loads(text.strip())
            if "strategies" in parsed and len(parsed["strategies"]) == 3:
                parsed["competitor_health_score"] = health_score
                return parsed
        except Exception:
            pass

    # Fallback — always returns 3 cards
    return {
        "competitor_health_score": health_score,
        "strategies": [
            {
                "action": "Raise price for low-velocity SKUs and increase marketing on high-quality products.",
                "impact": "Estimated 4-6% revenue uplift in 2 weeks.",
                "tradeoff": "May reduce conversion if price-sensitive customers leave.",
                "confidence": "75"
            },
            {
                "action": "Update listing copy to address top gaps (e.g., include carrying case, durability features).",
                "impact": "Expected to reduce returns and improve conversion by 3-5%.",
                "tradeoff": "Requires listing optimization time.",
                "confidence": "80"
            },
            {
                "action": "Run a limited discount on at-risk SKUs with poor sentiment to regain buy-box share.",
                "impact": "Temporary volume growth with lower margin.",
                "tradeoff": "Margin impact may be 1-2%.",
                "confidence": "70"
            }
        ]
    }

if __name__ == "__main__":
    print(generate_strategy_cards([], [], []))