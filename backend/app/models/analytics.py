import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.db.base import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"))
    event_type = Column(String(100), nullable=False)
    payload = Column(JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MasteryScore(Base):
    __tablename__ = "mastery_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    topic = Column(String(255), nullable=False)
    score = Column(Numeric(5, 2))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"))
    prediction_type = Column(String(50))
    value = Column(Numeric(5, 2))
    risk_level = Column(String(20))
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    action = Column(String(255), nullable=False)
    resource = Column(String(255))
    metadata_ = Column("metadata", JSONB, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())