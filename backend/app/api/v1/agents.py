from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.agents.curriculum_graph import generate_curriculum
from app.api.deps import require_role
from app.models.user import User

router = APIRouter()


class AgentRunRequest(BaseModel):
    agent: str
    input: dict


class CurriculumRequest(BaseModel):
    subject: str
    grade_level: str
    duration_weeks: int = 4


@router.post("/run")
def run_agent(
    payload: AgentRunRequest,
    _: User = Depends(require_role("teacher", "admin")),
):
    return {
        "agent": payload.agent,
        "status": "not_implemented",
        "output": None,
        "note": "Only curriculum agent is available at /curriculum/generate",
    }


@router.post("/curriculum/generate")
def curriculum_generate(
    payload: CurriculumRequest,
    _: User = Depends(require_role("teacher", "admin")),
):
    result = generate_curriculum(
        subject=payload.subject,
        grade_level=payload.grade_level,
        duration_weeks=payload.duration_weeks,
    )
    return result
