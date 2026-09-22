import json

from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


PROMPT = """You are an academic advisor analyzing a student's performance.

Student features:
- Total events: {total_events}
- Submissions: {submissions}
- Average score: {avg_score}
- Days since last activity: {days_inactive}

Give a short, supportive assessment.
Return ONLY valid JSON, no markdown:
{{
  "risk_level": "low" or "medium" or "high",
  "explanation": "2-3 sentence explanation with a concrete suggestion"
}}
"""


def _rule_based_risk(submissions: int, avg_score: float | None, days_inactive: int) -> str:
    if submissions == 0:
        return "high"
    if avg_score is None:
        return "medium"
    if avg_score < 60 or days_inactive > 14:
        return "high"
    if avg_score < 75 or days_inactive > 7:
        return "medium"
    return "low"


def _llm_explanation(features: dict) -> dict:
    client = get_client()
    prompt = PROMPT.format(**features)
    response = client.models.generate_content(
        model=settings.GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    raw = (response.text or "").strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.replace("json", "", 1).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "risk_level": features.get("rule_risk", "medium"),
            "explanation": "Prediction based on rule-based score only.",
        }


def predict_student(
    total_events: int,
    submissions: int,
    avg_score: float | None,
    days_inactive: int,
) -> dict:
    rule_risk = _rule_based_risk(submissions, avg_score, days_inactive)

    # predicted score = weighted blend of avg score and engagement
    engagement = min(total_events / 20.0, 1.0)  # 20+ events = full engagement
    if avg_score is None:
        predicted_score = round(engagement * 70, 2)
    else:
        predicted_score = round(avg_score * 0.75 + engagement * 100 * 0.25, 2)

    try:
        llm = _llm_explanation({
            "total_events": total_events,
            "submissions": submissions,
            "avg_score": avg_score if avg_score is not None else "no data",
            "days_inactive": days_inactive,
            "rule_risk": rule_risk,
        })
        risk_level = llm.get("risk_level", rule_risk)
        explanation = llm.get("explanation", "No explanation available.")
    except Exception:
        risk_level = rule_risk
        explanation = "Prediction based on rule-based score only (LLM unavailable)."

    return {
        "risk_level": risk_level,
        "predicted_score": predicted_score,
        "explanation": explanation,
        "features": {
            "total_events": total_events,
            "submissions": submissions,
            "avg_score": avg_score,
            "days_inactive": days_inactive,
        },
    }
