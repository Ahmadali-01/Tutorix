from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_role
from app.models.user import User

router = APIRouter()


@router.get("/student/{student_id}")
def student_analytics(
    student_id: str,
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    return {
        "student_id": student_id,
        "mastery": [],
        "events": [],
        "note": "Analytics pipeline coming soon.",
    }


@router.get("/predictions/student/{student_id}")
def student_prediction(
    student_id: str,
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    return {
        "student_id": student_id,
        "risk_level": "unknown",
        "value": None,
        "note": "Prediction model coming soon.",
    }