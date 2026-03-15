from sentence_transformers import SentenceTransformer
from pipeline.db.database import SessionLocal
from pipeline.db.models import Product
from pipeline.db.writer import save_embedding

_model = None

def _get_model():
    global _model
    if _model is None:
        print("[EMBED] Loading model (first run ~30s)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[EMBED] Model loaded.")
    return _model

def build_embedding_text(product) -> str:
    def _get(obj, key):
        if isinstance(obj, dict):
            return obj.get(key) or ""
        return getattr(obj, key, "") or ""
    parts = [_get(product, "title"), _get(product, "brand"), _get(product, "bullet_points")]
    return " ".join(p.strip() for p in parts if p.strip())

def create_embedding(text: str) -> list:
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")
    return _get_model().encode(text, normalize_embeddings=True).tolist()

def embed_product(asin: str, platform: str = "amazon") -> bool:
    with SessionLocal() as session:
        product = session.query(Product).filter_by(asin=asin, platform=platform).first()
        if not product:
            return False
        text = build_embedding_text(product)
        if not text:
            return False
        try:
            product.embedding = create_embedding(text)
            session.commit()
            return True
        except Exception as e:
            print(f"[EMBED] ✗ {asin} — {e}")
            return False

def embed_all_missing(platform: str = "amazon", delay: float = 0.0) -> dict:
    stats = {"success": 0, "failed": 0, "skipped": 0}
    with SessionLocal() as session:
        products = session.query(Product).filter(
            Product.platform == platform,
            Product.embedding.is_(None),
        ).all()
    print(f"[EMBED] {len(products)} products need embeddings")
    _get_model()
    for product in products:
        text = build_embedding_text(product)
        if not text:
            stats["skipped"] += 1
            continue
        try:
            save_embedding(product.asin, product.platform, create_embedding(text))
            print(f"[EMBED] ✓ {product.asin} ({(product.title or '')[:40]})")
            stats["success"] += 1
        except Exception as e:
            print(f"[EMBED] ✗ {product.asin} — {e}")
            stats["failed"] += 1
    print(f"[EMBED] Done — {stats}")
    return stats
