import json
import re
import time

from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


PROMPT = """You are an expert teacher creating exam questions.

Generate exactly {count} {question_type} questions on the topic: "{topic}"
Difficulty level: {difficulty}
Course context (optional):
{context}

Output MUST be a JSON array. No text before or after. No markdown. No code fences.

Format:
[
  {{
    "prompt": "the question text",
    "options": {{"A": "first option", "B": "second option", "C": "third option", "D": "fourth option"}},
    "answer": "A",
    "explanation": "why this answer is correct"
  }}
]

Rules:
- For {question_type} = mcq: include options A-D and answer is one of A/B/C/D.
- For {question_type} = short_answer: set options to null, answer is a model answer string.
- For {question_type} = true_false: options should be {{"A": "True", "B": "False"}}, answer is "A" or "B".
- Base questions on the latest accurate knowledge in this field.
- Output ONLY the JSON array, starting with [ and ending with ].
"""


def _extract_json(raw: str):
    """Try hard to extract a JSON array from the LLM response."""
    if not raw:
        return None

    # Strip code fences
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    # Try direct parse
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get("questions"), list):
            return data["questions"]
    except Exception:
        pass

    # Find the first [ ... ] block
    start = raw.find("[")
    end = raw.rfind("]")
    if start != -1 and end != -1 and end > start:
        chunk = raw[start : end + 1]
        try:
            data = json.loads(chunk)
            if isinstance(data, list):
                return data
        except Exception:
            # Try fixing trailing commas
            fixed = re.sub(r",\s*([\]}])", r"\1", chunk)
            try:
                data = json.loads(fixed)
                if isinstance(data, list):
                    return data
            except Exception:
                return None
    return None


def _normalize(questions: list[dict], qtype: str) -> list[dict]:
    """Ensure every question has required fields."""
    out = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        prompt = q.get("prompt") or q.get("question") or q.get("text")
        if not prompt:
            continue
        options = q.get("options")
        answer = q.get("answer")
        explanation = q.get("explanation") or q.get("reason") or ""

        if qtype == "true_false" and not options:
            options = {"A": "True", "B": "False"}

        out.append({
            "prompt": str(prompt).strip(),
            "options": options,
            "answer": str(answer).strip() if answer is not None else None,
            "explanation": str(explanation).strip(),
        })
    return out


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

    for attempt in range(4):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_CHAT_MODEL,
                contents=prompt,
            )
            raw = response.text or ""
            data = _extract_json(raw)
            if data:
                normalized = _normalize(data, question_type)
                if normalized:
                    return normalized
        except Exception as e:
            print(f"[question_generator] attempt {attempt + 1} failed: {e}")
            time.sleep(2 ** attempt)
    return []
