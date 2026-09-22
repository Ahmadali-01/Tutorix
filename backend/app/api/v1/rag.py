import os
import shutil
import tempfile

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.course import Course
from app.models.user import User
from app.rag.generator import generate_answer
from app.rag.ingest import ingest_document
from app.rag.retriever import hybrid_search
from app.services.analytics_service import log_event

router = APIRouter()


class RagQuery(BaseModel):
    query: str
    course_id: str | None = None
    top_k: int = 5


@router.post("/query")
def rag_query(
    payload: RagQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contexts = hybrid_search(payload.query, course_id=payload.course_id, top_k=payload.top_k)
    answer = generate_answer(payload.query, contexts)
    log_event(db, current_user.id, payload.course_id, "rag_query", {"query": payload.query})
    return {
        "query": payload.query,
        "answer": answer,
        "sources": [
            {
                "score": round(c["score"], 4),
                "document_id": c.get("document_id"),
                "chunk_index": c.get("chunk_index"),
                "preview": c["text"][:200],
            }
            for c in contexts
        ],
    }


@router.post("/upload")
async def upload_material(
    course_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher", "admin")),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    allowed = (".pdf", ".txt", ".md")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Only {allowed} allowed")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = ingest_document(tmp_path, course_id=course_id)
    finally:
        os.unlink(tmp_path)

    log_event(db, current_user.id, course_id, "material_uploaded", {"filename": file.filename})
    return {"filename": file.filename, **result}
