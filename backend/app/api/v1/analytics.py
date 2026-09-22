from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.agents.predictor import predict_student
from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.analytics import AnalyticsEvent, MasteryScore, Prediction
from app.models.assignment import Assignment, Evaluation, Submission
from app.models.user import User
from app.services.analytics_service import log_event

router = APIRouter()


@router.get("/student/{student_id}")
def student_analytics(
    student_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    events = (
        db.query(AnalyticsEvent)
        .filter(AnalyticsEvent.user_id == student_id)
        .order_by(AnalyticsEvent.created_at.desc())
        .limit(50)
        .all()
    )
    event_counts = (
        db.query(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
        .filter(AnalyticsEvent.user_id == student_id)
        .group_by(AnalyticsEvent.event_type)
        .all()
    )
    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    submission_ids = [s.id for s in submissions]
    evaluations = []
    if submission_ids:
        evaluations = db.query(Evaluation).filter(Evaluation.submission_id.in_(submission_ids)).all()
    scores = [float(e.score) for e in evaluations if e.score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None
    mastery = db.query(MasteryScore).filter(MasteryScore.student_id == student_id).all()
    return {
        "student_id": student_id,
        "total_events": sum(c for _, c in event_counts),
        "event_breakdown": {et: c for et, c in event_counts},
        "recent_events": [
            {
                "event_type": e.event_type,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "payload": e.payload,
            }
            for e in events
        ],
        "submissions_count": len(submissions),
        "avg_score": avg_score,
        "mastery": [
            {"topic": m.topic, "score": float(m.score) if m.score is not None else None}
            for m in mastery
        ],
    }


@router.get("/course/{course_id}")
def course_analytics(
    course_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    total_events = (
        db.query(func.count(AnalyticsEvent.id))
        .filter(AnalyticsEvent.course_id == course_id)
        .scalar()
    )
    event_counts = (
        db.query(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id))
        .filter(AnalyticsEvent.course_id == course_id)
        .group_by(AnalyticsEvent.event_type)
        .all()
    )
    total_submissions = (
        db.query(func.count(Submission.id))
        .join(Assignment, Assignment.id == Submission.assignment_id)
        .filter(Assignment.course_id == course_id)
        .scalar()
    )
    return {
        "course_id": course_id,
        "total_events": total_events or 0,
        "event_breakdown": {et: c for et, c in event_counts},
        "total_submissions": total_submissions or 0,
    }


@router.get("/predictions/student/{student_id}")
def student_prediction(
    student_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    preds = (
        db.query(Prediction)
        .filter(Prediction.student_id == student_id)
        .order_by(Prediction.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "student_id": student_id,
        "predictions": [
            {
                "id": str(p.id),
                "type": p.prediction_type,
                "value": float(p.value) if p.value is not None else None,
                "risk_level": p.risk_level,
                "explanation": p.explanation,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in preds
        ],
    }


@router.post("/predict/student/{student_id}")
def run_prediction(
    student_id: str,
    course_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher", "admin", "analyst")),
):
    events = db.query(AnalyticsEvent).filter(AnalyticsEvent.user_id == student_id).all()
    total_events = len(events)

    last_event = (
        db.query(AnalyticsEvent)
        .filter(AnalyticsEvent.user_id == student_id)
        .order_by(AnalyticsEvent.created_at.desc())
        .first()
    )
    days_inactive = 0
    if last_event and last_event.created_at:
        delta = datetime.now(timezone.utc) - last_event.created_at.replace(tzinfo=timezone.utc)
        days_inactive = max(delta.days, 0)

    submissions = db.query(Submission).filter(Submission.student_id == student_id).all()
    submission_ids = [s.id for s in submissions]
    evaluations = []
    if submission_ids:
        evaluations = db.query(Evaluation).filter(Evaluation.submission_id.in_(submission_ids)).all()
    scores = [float(e.score) for e in evaluations if e.score is not None]
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    result = predict_student(
        total_events=total_events,
        submissions=len(submissions),
        avg_score=avg_score,
        days_inactive=days_inactive,
    )

    prediction = Prediction(
        student_id=student_id,
        course_id=course_id,
        prediction_type="risk",
        value=result["predicted_score"],
        risk_level=result["risk_level"],
        explanation=result["explanation"],
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    log_event(db, current_user.id, course_id, "prediction_run", {"student_id": student_id})

    return {
        "prediction_id": str(prediction.id),
        "student_id": student_id,
        "risk_level": result["risk_level"],
        "predicted_score": result["predicted_score"],
        "explanation": result["explanation"],
        "features": result["features"],
    }


class EventLogRequest(BaseModel):
    event_type: str
    course_id: Optional[str] = None
    payload: Optional[dict] = None


@router.post("/events/log")
def log_event_endpoint(
    payload: EventLogRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log_event(db, current_user.id, payload.course_id, payload.event_type, payload.payload)
    return {"status": "logged"}
