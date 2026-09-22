import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalyticsEventRead(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    course_id: Optional[uuid.UUID] = None
    event_type: str
    payload: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionRead(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    course_id: Optional[uuid.UUID] = None
    prediction_type: Optional[str] = None
    value: Optional[float] = None
    risk_level: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True