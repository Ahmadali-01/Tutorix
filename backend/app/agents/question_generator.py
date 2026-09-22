import json

from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


PROMPT = """You are an expert teacher creating exam questions.

Generate {count} {question_type} questions on the topic: "{topic}"
Difficulty: {difficulty}
Course context (if any):
{context}

Return ONLY valid JSON as a list, no explanation, no markdown. Format:
[
  {{
    "prompt": "question text",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A",
    "explanation": "why this is correct"
  }}
]

Rules:
- For "short_answer" or "true_false", options can be null.
- Every question must be clear and unambiguous.
- Answers must match one of the options for MCQ.
"""


def generate_questions(
    topic: str,
    count: int = 5,
    difficulty: str = "medium",
    question_type: str = "mcq",
    context: str = "",
) -> list[dict]:
    prompt = PROMPT.format(
        count=count,
        topic=topic,
        difficulty=difficulty,
        question_type=question_type,
        context=context or "(none)",
    )
    client = get_client()
    response = client.models.generate_content(
        model=settings.GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    raw = (response.text or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return data