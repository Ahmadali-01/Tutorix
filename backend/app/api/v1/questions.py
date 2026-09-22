from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.question_generator import generate_questions as llm_generate
from app.api.deps import require_role
from app.db.session import get_db
from app.models.assignment import Question
from app.models.course import Course
from app.models.user import User
from app.rag.retriever import hybrid_search
from app.schemas.assignment import QuestionGenerateRequest

router = APIRouter()


@router.post("/generate")
def generate_questions_endpoint(
    payload: QuestionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher", "admin")),
):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    context = ""
    try:
        chunks = hybrid_search(payload.topic, course_id=str(payload.course_id), top_k=3)
        context = "\n\n".join(c["text"] for c in chunks)
    except Exception:
        context = ""

    generated = llm_generate(
        topic=payload.topic,
        count=payload.count,
        difficulty=payload.difficulty,
        question_type=payload.question_type,
        context=context,
    )

    if not generated:
        raise HTTPException(status_code=502, detail="LLM returned no valid questions")

    saved = []
    for q in generated:
        row = Question(
            course_id=payload.course_id,
            created_by=current_user.id,
            question_type=payload.question_type,
            difficulty=payload.difficulty,
            prompt=q.get("prompt", ""),
            options=q.get("options"),
            answer=q.get("answer"),
            explanation=q.get("explanation"),
        )
        db.add(row)
        saved.append(row)

    db.commit()
    for row in saved:
        db.refresh(row)

    return {
        "status": "generated",
        "count": len(saved),
        "questions": [
            {
                "id": str(r.id),
                "prompt": r.prompt,
                "options": r.options,
                "answer": r.answer,
                "explanation": r.explanation,
                "difficulty": r.difficulty,
                "type": r.question_type,
            }
            for r in saved
        ],
    }