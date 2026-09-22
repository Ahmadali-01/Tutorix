from sqlalchemy.orm import Session

from app.models.analytics import AnalyticsEvent


def log_event(db: Session, user_id, course_id, event_type: str, payload: dict | None = None):
    try:
        event = AnalyticsEvent(
            user_id=user_id,
            course_id=course_id,
            event_type=event_type,
            payload=payload or {},
        )
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()
