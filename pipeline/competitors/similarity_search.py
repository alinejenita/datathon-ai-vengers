"""
pipeline/competitors/similarity_search.py
──────────────────────────────────────────
Uses pgvector cosine similarity to find similar products,
then writes classified competitor relationships to the DB.
"""

from sqlalchemy import text
from pipeline.db.database import SessionLocal, engine
from pipeline.db.models import Product
from pipeline.db.writer import save_competitor
from pipeline.competitors.matcher import classify_competitor, is_direct_competitor
from pipeline.config import SIMILARITY_SIMILAR_PRODUCT, SIMILARITY_TOP_K


# ── CORE VECTOR SEARCH ────────────────────────────────────────────────────

def find_similar_products(
    asin: str,
    platform: str = "amazon",
    top_k: int | None = None,
    min_similarity: float | None = None,
) -> list[dict]:
    """
    Find the most similar products to `asin` using pgvector cosine distance.

    Returns list of dicts:
        { asin, platform, title, brand, similarity, distance }
    sorted by similarity descending.
    """
    k           = top_k or SIMILARITY_TOP_K
    min_sim     = min_similarity if min_similarity is not None else SIMILARITY_SIMILAR_PRODUCT

    with engine.connect() as conn:
        # Get the embedding for the base product
        base_row = conn.execute(
            text("""
                SELECT embedding
                FROM products
                WHERE asin = :asin AND platform = :platform
                LIMIT 1
            """),
            {"asin": asin, "platform": platform},
        ).fetchone()

        if not base_row or base_row[0] is None:
            print(f"[SIMILARITY] No embedding found for {asin}")
            return []

        # cosine distance: 1 - cosine_similarity → lower = more similar
        rows = conn.execute(
            text("""
                SELECT
                    asin,
                    platform,
                    title,
                    brand,
                    1 - (embedding <=> (
                        SELECT embedding
                        FROM products
                        WHERE asin = :asin AND platform = :platform
                        LIMIT 1
                    )) AS similarity
                FROM products
                WHERE
                    asin      != :asin
                    AND embedding IS NOT NULL
                ORDER BY embedding <=> (
                    SELECT embedding
                    FROM products
                    WHERE asin = :asin AND platform = :platform
                    LIMIT 1
                )
                LIMIT :k
            """),
            {"asin": asin, "platform": platform, "k": k},
        ).fetchall()

    results = []
    for row in rows:
        sim = float(row[4]) if row[4] is not None else 0.0
        if sim >= min_sim:
            results.append({
                "asin":       row[0],
                "platform":   row[1],
                "title":      row[2],
                "brand":      row[3],
                "similarity": round(sim, 4),
            })

    return sorted(results, key=lambda x: x["similarity"], reverse=True)


# ── FULL COMPETITOR DETECTION ─────────────────────────────────────────────

def detect_and_save_competitors(
    base_asin: str,
    platform: str = "amazon",
    top_k: int | None = None,
) -> list[dict]:
    """
    Run similarity search for base_asin, classify each result,
    and persist valid competitor relationships.

    Returns the list of saved competitor dicts.
    """
    with SessionLocal() as session:
        base_product = session.query(Product).filter_by(
            asin=base_asin, platform=platform
        ).first()

    if not base_product:
        print(f"[SIMILARITY] Base product not found: {base_asin}")
        return []

    base_dict = {
        "asin":     base_product.asin,
        "platform": base_product.platform,
        "title":    base_product.title,
        "brand":    base_product.brand,
    }

    candidates = find_similar_products(base_asin, platform, top_k=top_k)
    saved = []

    for candidate in candidates:
        competitor_type = classify_competitor(
            base_dict, candidate, candidate["similarity"]
        )

        if not is_direct_competitor(competitor_type):
            continue

        save_competitor(
            base_asin       = base_asin,
            competitor_asin = candidate["asin"],
            similarity      = candidate["similarity"],
            competitor_type = competitor_type,
        )

        saved.append({**candidate, "competitor_type": competitor_type})
        print(
            f"[SIMILARITY] {base_asin} → {candidate['asin']} "
            f"({competitor_type}, sim={candidate['similarity']:.3f})"
        )

    return saved


# ── BATCH: run for ALL own products ──────────────────────────────────────

def detect_all_competitors() -> dict:
    """
    Run competitor detection for every product in the DB that has an embedding.
    Returns summary stats.
    """
    stats = {"processed": 0, "competitors_found": 0}

    with SessionLocal() as session:
        own_products = (
            session.query(Product)
            .filter(
                Product.is_own_product == 1,
                Product.embedding.isnot(None),
            )
            .all()
        )

    for p in own_products:
        found = detect_and_save_competitors(p.asin, p.platform)
        stats["processed"]        += 1
        stats["competitors_found"] += len(found)

    print(f"[SIMILARITY] Batch complete — {stats}")
    return stats