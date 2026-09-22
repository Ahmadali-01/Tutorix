import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QuestionGenerateRequest(BaseModel):
    course_id: uuid.UUID
    topic: str
    difficulty: str = "medium"
    count: int = 5
    question_type: str = "mcq"


class AssignmentCreate(BaseModel):
    course_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None


class AssignmentRead(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionCreate(BaseModel):
    assignment_id: uuid.UUID
    content: str


class EvaluationRead(BaseModel):
    id: uuid.UUID
    submission_id: uuid.UUID
    score: Optional[float] = None
    feedback: Optional[str] = None
    rubric_scores: Optional[dict] = None
    evaluated_by: str
    created_at: datetime

    class Config:
        from_attributes = True