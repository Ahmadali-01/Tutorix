from fastapi import APIRouter, Depends
from google import genai
from google.genai import types
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.curriculum_graph import generate_curriculum
from app.agents.tools import TOOL_NAMES, call_tool
from app.api.deps import require_role
from app.config import settings
from app.db.session import get_db
from app.models.user import User

router = APIRouter()

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


class AgentRunRequest(BaseModel):
    agent: str
    input: dict


class CurriculumRequest(BaseModel):
    subject: str
    grade_level: str
    duration_weeks: int = 4


class ToolChatRequest(BaseModel):
    message: str


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


# -------- Function calling tools for Gemini --------

def _tool_declarations():
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="calculator",
                    description="Evaluate a math expression like 2+3*4 or (10/2)+5",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "expression": types.Schema(
                                type=types.Type.STRING,
                                description="The math expression to evaluate",
                            )
                        },
                        required=["expression"],
                    ),
                ),
                types.FunctionDeclaration(
                    name="current_time",
                    description="Get the current UTC date and time",
                    parameters=types.Schema(type=types.Type.OBJECT, properties={}),
                ),
                types.FunctionDeclaration(
                    name="search_questions",
                    description="Search the question bank by keyword to find existing questions",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "keyword": types.Schema(type=types.Type.STRING, description="Search keyword"),
                            "limit": types.Schema(type=types.Type.INTEGER, description="Max results"),
                        },
                        required=["keyword"],
                    ),
                ),
                types.FunctionDeclaration(
                    name="get_student_stats",
                    description="Get performance stats for a student by their UUID",
                    parameters=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "student_id": types.Schema(
                                type=types.Type.STRING,
                                description="The student UUID",
                            )
                        },
                        required=["student_id"],
                    ),
                ),
            ]
        )
    ]


@router.post("/tools/chat")
def tools_chat(
    payload: ToolChatRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("teacher", "admin")),
):
    client = get_client()
    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=payload.message)],
        )
    ]
    config = types.GenerateContentConfig(
        tools=_tool_declarations(),
        temperature=0.2,
    )

    tool_calls_made = []

    for _round in range(4):
        response = client.models.generate_content(
            model=settings.GEMINI_CHAT_MODEL,
            contents=contents,
            config=config,
        )

        # Check for function calls
        calls = []
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "function_call", None):
                    calls.append(part.function_call)

        if not calls:
            return {
                "reply": response.text or "",
                "tools_used": tool_calls_made,
            }

        # Append the model's tool call message
        contents.append(response.candidates[0].content)

        # Execute each tool and append the result
        for fc in calls:
            name = fc.name
            args = dict(fc.args) if fc.args else {}
            result = call_tool(name, args, db)
            tool_calls_made.append({"tool": name, "args": args, "result": result})

            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=name,
                                response={"result": result},
                            )
                        )
                    ],
                )
            )

    return {
        "reply": "Reached max tool-calling rounds without a final answer.",
        "tools_used": tool_calls_made,
    }
