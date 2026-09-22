import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CourseCreate(BaseModel):
    title: str
    description: Optional[str] = None


class CourseRead(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    teacher_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    course_id: uuid.UUID
    student_id: uuid.UUID