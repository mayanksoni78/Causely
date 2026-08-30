from sentence_transformers import SentenceTransformer

# Lazy singleton — model loaded only on first call, not at import time
_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

# Keep 'model' name for backward compat with main.py lifespan
model = None

def embed_texts(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(texts).tolist()

def embed_query(text: str) -> list[float]:
    return _get_model().encode([text])[0].tolist()
