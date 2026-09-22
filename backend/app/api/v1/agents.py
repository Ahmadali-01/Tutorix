from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import require_role
from app.models.user import User

router = APIRouter()


class AgentRunRequest(BaseModel):
    agent: str
    input: dict


@router.post("/run")
def run_agent(
    payload: AgentRunRequest,
    _: User = Depends(require_role("teacher", "admin")),
):
    # Placeholder — LangGraph agents will be wired in a later step.
    return {
        "agent": payload.agent,
        "status": "not_implemented",
        "output": None,
        "note": "Multi-agent workflow coming soon.",
    }