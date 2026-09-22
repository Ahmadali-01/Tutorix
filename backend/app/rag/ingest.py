import os
import uuid

from app.rag.chunker import chunk_text, extract_text_from_pdf, extract_text_from_txt
from app.rag.embeddings import embed_batch
from app.rag.vector_store import upsert_chunks


def ingest_document(file_path: str, course_id: str, document_id: str | None = None) -> dict:
    if document_id is None:
        document_id = str(uuid.uuid4())

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in (".txt", ".md"):
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    chunks = chunk_text(text)
    if not chunks:
        return {"document_id": document_id, "chunks": 0, "status": "empty"}

    vectors = embed_batch(chunks)
    count = upsert_chunks(course_id, document_id, chunks, vectors)
    return {"document_id": document_id, "chunks": count, "status": "ingested"}
