import json

from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


PROMPT = """You are an expert teacher evaluating a student's assignment.

Assignment title: {title}
Assignment description: {description}

Rubric criteria:
{rubric}

Student submission:
{submission}

Evaluate the submission strictly against the rubric.
Return ONLY valid JSON, no explanation, no markdown. Format:
{{
  "score": 85,
  "rubric_scores": {{"criterion_1": 8, "criterion_2": 7}},
  "feedback": "Constructive, specific feedback for the student. Mention strengths and areas to improve.",
  "strengths": ["...", "..."],
  "improvements": ["...", "..."]
}}

Rules:
- Score must be between 0 and 100.
- Be fair, specific, and encouraging.
- Feedback should be 3–6 sentences.
"""


def evaluate_submission(
    title: str,
    description: str,
    submission: str,
    rubric: dict | None = None,
) -> dict:
    rubric_text = json.dumps(rubric, indent=2) if rubric else "(no rubric provided)"
    prompt = PROMPT.format(
        title=title,
        description=description or "(no description)",
        rubric=rubric_text,
        submission=submission or "(empty submission)",
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
        return {
            "score": 0,
            "rubric_scores": {},
            "feedback": "Evaluation failed: could not parse LLM response.",
            "strengths": [],
            "improvements": [],
        }
    return data