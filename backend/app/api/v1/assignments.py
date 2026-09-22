from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.assignment import Assignment, Evaluation, Submission
from app.models.user import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentRead,
    EvaluationRead,
    SubmissionCreate,
)

router = APIRouter()


@router.post("", response_model=AssignmentRead, status_code=201)
def create_assignment(
    payload: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher", "admin")),
):
    assignment = Assignment(
        course_id=payload.course_id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        created_by=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("", response_model=List[AssignmentRead])
def list_assignments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Assignment).all()


@router.post("/submissions", status_code=201)
def submit_assignment(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    assignment = db.query(Assignment).filter(Assignment.id == payload.assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    submission = Submission(
        assignment_id=payload.assignment_id,
        student_id=current_user.id,
        content=payload.content,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return {"submission_id": str(submission.id)}


@router.post("/submissions/{submission_id}/evaluate", response_model=EvaluationRead)
def evaluate_submission(
    submission_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("teacher", "admin")),
):
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Placeholder — LLM rubric-based grading will be wired later.
    evaluation = Evaluation(
        submission_id=submission.id,
        score=85,
        feedback="Placeholder AI feedback. LLM evaluation coming soon.",
        rubric_scores={"criteria_1": 85},
        evaluated_by="ai",
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    return evaluation
