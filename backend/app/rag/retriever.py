from app.rag.embeddings import embed_text
from app.rag.vector_store import search


def semantic_search(query: str, course_id: str | None = None, top_k: int = 5):
    vec = embed_text(query)
    return search(vec, course_id=course_id, top_k=top_k)


def keyword_search(query: str, candidates: list[dict], top_k: int = 5):
    query_words = set(query.lower().split())
    scored = []
    for c in candidates:
        text_words = set(c["text"].lower().split())
        overlap = len(query_words & text_words)
        scored.append((overlap, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:top_k]]


def hybrid_search(query: str, course_id: str | None = None, top_k: int = 5):
    semantic = semantic_search(query, course_id=course_id, top_k=top_k * 2)
    return keyword_search(query, semantic, top_k=top_k)
