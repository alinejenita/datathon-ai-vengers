"""
pipeline/competitors/matcher.py
────────────────────────────────
Classifies a candidate product as same_product, similar_product, or None
based on cosine similarity score and optional metadata heuristics.
"""

from pipeline.config import (
    SIMILARITY_SAME_PRODUCT,
    SIMILARITY_SIMILAR_PRODUCT,
)


def classify_competitor(
    base: dict,
    candidate: dict,
    similarity: float,
) -> str | None:
    """
    Classify the relationship between base and candidate products.

    Args:
        base:       Dict with keys: asin, title, brand, platform
        candidate:  Dict with keys: asin, title, brand, platform
        similarity: Cosine similarity score (0.0 – 1.0)

    Returns:
        "same_product"    — likely the exact same SKU listed by another seller
        "similar_product" — competing product in the same category
        None              — not a meaningful competitor
    """
    # Skip self-comparison
    if base.get("asin") == candidate.get("asin"):
        return None

    # Exact match on ASIN across platforms → same product
    if (
        base.get("asin") == candidate.get("asin")
        and base.get("platform") != candidate.get("platform")
    ):
        return "same_product"

    # Similarity-based classification
    if similarity >= SIMILARITY_SAME_PRODUCT:
        return "same_product"

    if similarity >= SIMILARITY_SIMILAR_PRODUCT:
        return "similar_product"

    return None


def is_direct_competitor(competitor_type: str | None) -> bool:
    """Returns True if the competitor type is meaningful."""
    return competitor_type in ("same_product", "similar_product")


def rank_competitors(competitors: list[dict]) -> list[dict]:
    """
    Sort competitors list by similarity descending,
    with same_product ranked above similar_product at equal similarity.
    """
    type_priority = {"same_product": 0, "similar_product": 1}

    return sorted(
        competitors,
        key=lambda c: (
            type_priority.get(c.get("competitor_type"), 2),
            -(c.get("similarity") or 0),
        ),
    )