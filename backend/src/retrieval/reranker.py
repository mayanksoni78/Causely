from sentence_transformers import CrossEncoder
from src.connectors.base import EvidenceChunk

# Lazy singleton — loaded only when reranking is first called
_model = None

# Keep 'model' name for backward compat with main.py lifespan
model = None

def _get_model():
    global _model
    if _model is None:
        try:
            _model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        except Exception:
            _model = False  # Mark as failed so we don't retry on every call
    return _model if _model is not False else None

def rerank(query: str, chunks: list[EvidenceChunk], top_k: int = 10) -> list[EvidenceChunk]:
    if not chunks:
        return []

    m = _get_model()
    if not m:
        # Fallback: return by relevance score if model unavailable
        return sorted(chunks, key=lambda c: c.relevance_score, reverse=True)[:top_k]

    pairs = [[query, chunk.content] for chunk in chunks]
    scores = m.predict(pairs)

    for chunk, score in zip(chunks, scores):
        chunk.relevance_score = float(score)

    chunks.sort(key=lambda c: c.relevance_score, reverse=True)
    return chunks[:top_k]
