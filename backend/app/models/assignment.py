import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    question_type = Column(String(50), nullable=False)
    difficulty = Column(String(20))
    prompt = Column(Text, nullable=False)
    options = Column(JSONB)
    answer = Column(Text)
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"))
    criteria = Column(JSONB, nullable=False)
    max_score = Column(Numeric(5, 2), default=100)

    assignment = relationship("Assignment", back_populates="rubrics")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_at = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    rubrics = relationship("Rubric", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"))
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    content = Column(Text)
    file_path = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    assignment = relationship("Assignment", back_populates="submissions")
    evaluations = relationship("Evaluation", back_populates="submission", cascade="all, delete-orphan")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id", ondelete="CASCADE"))
    score = Column(Numeric(5, 2))
    feedback = Column(Text)
    rubric_scores = Column(JSONB)
    evaluated_by = Column(String(50), default="ai")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("Submission", back_populates="evaluations")