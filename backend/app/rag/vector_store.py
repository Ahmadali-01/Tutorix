import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings

COLLECTION = "course_materials"
VECTOR_SIZE = 3072

_client = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.QDRANT_URL)
    return _client


def ensure_collection() -> None:
    client = get_qdrant()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def upsert_chunks(course_id, document_id, chunks, vectors):
    client = get_qdrant()
    ensure_collection()
    points = []
    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "course_id": course_id,
                "document_id": document_id,
                "chunk_index": i,
                "text": chunk,
            },
        ))
    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)


def search(query_vector, course_id=None, top_k=5):
    client = get_qdrant()
    ensure_collection()
    query_filter = None
    if course_id:
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        query_filter = Filter(must=[FieldCondition(key="course_id", match=MatchValue(value=course_id))])
    result = client.query_points(
        collection_name=COLLECTION,
        query=query_vector,
        limit=top_k,
        query_filter=query_filter,
    )
    return [
        {
            "score": h.score,
            "text": h.payload.get("text", ""),
            "course_id": h.payload.get("course_id"),
            "document_id": h.payload.get("document_id"),
            "chunk_index": h.payload.get("chunk_index"),
        }
        for h in result.points
    ]