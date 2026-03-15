print("LISTING WRITER STARTED")
import json
from agents.gap_finder import run_gap_finder_agent
from agents.claude_client import call_claude

def rewrite_listing(title, bullets, gaps, max_bullets=5):
    if not title:
        title = "High-performing product listing"

    gap_descriptions = [g.get("gap", "") for g in gaps[:5] if g.get("gap")]

    system_prompt = (
        "You are an expert Amazon listing copywriter. "
        "Given a product title, existing bullet points, and customer-requested gaps, "
        "rewrite the listing to address those gaps and improve conversion. "
        "Return ONLY valid JSON — no markdown — in this exact structure:\n"
        "{\"title\": \"<improved title>\", \"bullets\": [\"<bullet 1>\", ..., \"<bullet 5>\"]}\n"
        f"Always return exactly {max_bullets} bullet points."
    )

    user_prompt = (
        f"Original title: {title}\n"
        f"Original bullets: {json.dumps(bullets)}\n"
        f"Customer-requested gaps to address: {json.dumps(gap_descriptions)}\n\n"
        "Rewrite the listing. Make bullets specific and benefit-driven."
    )

    response = call_claude(system_prompt, user_prompt, max_tokens=500)

    if "error" not in response:
        try:
            text = response["message"].strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            parsed = json.loads(text.strip())
            if "title" in parsed and "bullets" in parsed:
                parsed["bullets"] = parsed["bullets"][:max_bullets]
                return parsed
        except Exception:
            pass

    # Fallback
    gap_lines = gap_descriptions[:3]
    return {
        "title": f"{title} - improved for durability, value, and customer requests",
        "bullets": ([
            "Premium durability engineered for everyday use",
            "Fast and reliable shipping-ready packaging",
            "Built to deliver top quality and value without compromise",
        ] + [f"Customer request addressed: {g}" for g in gap_lines])[:max_bullets]
    }

if __name__ == "__main__":
    gap_data = run_gap_finder_agent().get("gaps", [])
    print(rewrite_listing("Boat Airdopes 141 Gen 2", [], gap_data))