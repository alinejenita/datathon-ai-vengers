import re


def clean_price(raw: str | None) -> float | None:
    if not raw:
        return None
    # Take only the FIRST price if a range is returned
    first  = raw.split("-")[0].split("–")[0]
    digits = re.sub(r"[^\d.]", "", first)
    try:
        return float(digits) if digits else None
    except ValueError:
        return None


def clean_rating(raw: str | None) -> float | None:
    if not raw:
        return None
    match = re.search(r"(\d+\.?\d*)", raw)
    return float(match.group(1)) if match else None


def clean_review_count(raw: str | None) -> int | None:
    if not raw:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def clean_text(raw: str | None) -> str | None:
    if not raw:
        return None
    return raw.strip().replace("\n", " ").replace("\r", "")


def normalise_product(raw: dict) -> dict:
    return {
        "asin":                raw.get("asin"),
        "title":               clean_text(raw.get("title")),
        "brand":               clean_text(raw.get("brand")),
        "price":               clean_price(raw.get("price")),
        "rating":              clean_rating(raw.get("rating")),
        "review_count":        clean_review_count(raw.get("review_count")),
        "platform":            raw.get("platform", "amazon"),
        "amazon_rank":         clean_text(raw.get("amazon_rank")),
        "bullet_points":       clean_text(raw.get("bullet_points")),
        "product_description": clean_text(raw.get("product_description")),
    }


def normalise_review(raw: dict) -> dict:
    return {
        "asin":      raw.get("asin"),
        "review_id": raw.get("review_id"),
        "rating":    clean_rating(raw.get("rating")),
        "title":     clean_text(raw.get("title")),
        "body":      clean_text(raw.get("body")),
        "verified":  1 if raw.get("verified") else 0,
    }