from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import require_role
from app.eval.runner import (
    evaluate_evaluation,
    evaluate_prediction,
    evaluate_questions,
    evaluate_rag,
)
from app.models.user import User

router = APIRouter()


class RagEvalRequest(BaseModel):
    query: str
    course_id: Optional[str] = None
    top_k: int = 3


class QuestionsEvalRequest(BaseModel):
    questions: List[dict]


class ScoreEvalRequest(BaseModel):
    score: float


class PredictionEvalRequest(BaseModel):
    prediction: dict


@router.post("/rag")
def eval_rag(
    payload: RagEvalRequest,
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    return evaluate_rag(payload.query, course_id=payload.course_id, top_k=payload.top_k)


@router.post("/questions")
def eval_questions(
    payload: QuestionsEvalRequest,
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    return evaluate_questions(payload.questions)


@router.post("/evaluation")
def eval_evaluation(
    payload: ScoreEvalRequest,
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    return evaluate_evaluation(payload.score)


@router.post("/prediction")
def eval_prediction(
    payload: PredictionEvalRequest,
    _: User = Depends(require_role("teacher", "admin", "analyst")),
):
    return evaluate_prediction(payload.prediction)
