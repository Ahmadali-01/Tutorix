import json
import time
from typing import TypedDict

from google import genai
from langgraph.graph import END, StateGraph

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _call_llm(prompt: str, retries: int = 4) -> str:
    client = get_client()
    last_err = None
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_CHAT_MODEL,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception as e:
            last_err = e
            wait = 2 ** attempt
            time.sleep(wait)
    raise last_err


def _parse_json(raw: str, fallback):
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return fallback


class CurriculumState(TypedDict):
    subject: str
    grade_level: str
    duration_weeks: int
    modules: list
    objectives: list
    lessons: list
    assessments: list


PLANNER_PROMPT = """You are a curriculum planner.
Create a {duration_weeks}-week curriculum outline for the subject "{subject}" at grade level "{grade_level}".

Return ONLY valid JSON, no markdown:
{{
  "modules": [
    {{"week": 1, "title": "Module title", "summary": "brief summary"}}
  ]
}}

Rules:
- Exactly {duration_weeks} modules (one per week).
- Titles must be short and clear.
"""


def planner_agent(state: CurriculumState) -> CurriculumState:
    prompt = PLANNER_PROMPT.format(
        duration_weeks=state["duration_weeks"],
        subject=state["subject"],
        grade_level=state["grade_level"],
    )
    raw = _call_llm(prompt)
    data = _parse_json(raw, {"modules": []})
    state["modules"] = data.get("modules", [])
    return state


OBJECTIVES_PROMPT = """You are a learning objectives specialist.
For each module below, write 2-3 clear, measurable learning objectives.

Modules:
{modules}

Return ONLY valid JSON, no markdown:
{{
  "objectives": [
    {{"week": 1, "title": "Module title", "objectives": ["...", "..."]}}
  ]
}}
"""


def objectives_agent(state: CurriculumState) -> CurriculumState:
    prompt = OBJECTIVES_PROMPT.format(modules=json.dumps(state["modules"], indent=2))
    raw = _call_llm(prompt)
    data = _parse_json(raw, {"objectives": []})
    state["objectives"] = data.get("objectives", [])
    return state


LESSONS_PROMPT = """You are a lesson designer.
For each module, propose 2-3 lesson topics and one hands-on activity.

Modules with objectives:
{payload}

Return ONLY valid JSON, no markdown:
{{
  "lessons": [
    {{
      "week": 1,
      "title": "Module title",
      "topics": ["...", "..."],
      "activity": "one hands-on activity"
    }}
  ]
}}
"""


def lessons_agent(state: CurriculumState) -> CurriculumState:
    payload = json.dumps(
        [
            {
                "week": o.get("week"),
                "title": o.get("title"),
                "objectives": o.get("objectives", []),
            }
            for o in state["objectives"]
        ],
        indent=2,
    )
    prompt = LESSONS_PROMPT.format(payload=payload)
    raw = _call_llm(prompt)
    data = _parse_json(raw, {"lessons": []})
    state["lessons"] = data.get("lessons", [])
    return state


ASSESSMENT_PROMPT = """You are an assessment designer.
For each module, suggest one quiz topic and one project idea.

Modules with lessons:
{payload}

Return ONLY valid JSON, no markdown:
{{
  "assessments": [
    {{"week": 1, "title": "Module title", "quiz_topic": "...", "project": "..."}}
  ]
}}
"""


def assessment_agent(state: CurriculumState) -> CurriculumState:
    payload = json.dumps(state["lessons"], indent=2)
    prompt = ASSESSMENT_PROMPT.format(payload=payload)
    raw = _call_llm(prompt)
    data = _parse_json(raw, {"assessments": []})
    state["assessments"] = data.get("assessments", [])
    return state


def build_graph():
    graph = StateGraph(CurriculumState)
    graph.add_node("planner", planner_agent)
    graph.add_node("objectives", objectives_agent)
    graph.add_node("lessons", lessons_agent)
    graph.add_node("assessment", assessment_agent)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "objectives")
    graph.add_edge("objectives", "lessons")
    graph.add_edge("lessons", "assessment")
    graph.add_edge("assessment", END)

    return graph.compile()


_compiled = None


def generate_curriculum(subject: str, grade_level: str, duration_weeks: int) -> dict:
    global _compiled
    if _compiled is None:
        _compiled = build_graph()

    initial: CurriculumState = {
        "subject": subject,
        "grade_level": grade_level,
        "duration_weeks": duration_weeks,
        "modules": [],
        "objectives": [],
        "lessons": [],
        "assessments": [],
    }
    result = _compiled.invoke(initial)
    return {
        "subject": result["subject"],
        "grade_level": result["grade_level"],
        "duration_weeks": result["duration_weeks"],
        "modules": result["modules"],
        "objectives": result["objectives"],
        "lessons": result["lessons"],
        "assessments": result["assessments"],
    }
