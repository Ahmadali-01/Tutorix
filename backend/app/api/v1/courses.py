from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.course import Course, Enrollment
from app.models.user import User
from app.schemas.course import CourseCreate, CourseRead, EnrollmentCreate

router = APIRouter()


@router.post("", response_model=CourseRead, status_code=201)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("teacher", "admin")),
):
    course = Course(
        title=payload.title,
        description=payload.description,
        teacher_id=current_user.id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=List[CourseRead])
def list_courses(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(Course).all()


@router.post("/enroll", status_code=201)
def enroll(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    course = db.query(Course).filter(Course.id == payload.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id == payload.course_id,
            Enrollment.student_id == payload.student_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled")

    enrollment = Enrollment(course_id=payload.course_id, student_id=payload.student_id)
    db.add(enrollment)
    db.commit()
    return {"status": "enrolled"}