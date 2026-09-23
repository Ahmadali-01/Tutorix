import json
import time

from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _ask(prompt: str, retries: int = 4) -> dict:
    client = get_client()
    last_err = None
    for attempt in range(retries):
        try:
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
                return {"score": 0.0, "reason": "unparseable response"}
        except Exception as e:
            last_err = e
            time.sleep(2 ** attempt)
    return {"score": 0.0, "reason": f"LLM unavailable: {last_err}"}


FAITHFULNESS_PROMPT = """You are evaluating a RAG answer.

Context:
{context}

Answer:
{answer}

Question: Is every claim in the answer supported by the context?

Return ONLY JSON:
{{"score": 0.0, "reason": "short reason"}}

Score rules:
- 1.0 = fully grounded in context
- 0.5 = partially grounded
- 0.0 = hallucinated / not supported
"""

RELEVANCY_PROMPT = """You are evaluating a RAG answer.

Question:
{question}

Answer:
{answer}

Question: Does the answer directly address the question?

Return ONLY JSON:
{{"score": 0.0, "reason": "short reason"}}

Score rules:
- 1.0 = fully answers the question
- 0.5 = partially answers
- 0.0 = off-topic or evasive
"""

CONTEXT_PRECISION_PROMPT = """You are evaluating retrieved context for a RAG system.

Question:
{question}

Retrieved chunks:
{chunks}

Question: How many chunks are relevant to the question?

Return ONLY JSON:
{{"score": 0.0, "relevant_count": 0, "reason": "short reason"}}

Score rules:
- score = relevant_count / total_chunks (0.0 to 1.0)
"""


def faithfulness(context: str, answer: str) -> dict:
    return _ask(FAITHFULNESS_PROMPT.format(context=context, answer=answer))


def answer_relevancy(question: str, answer: str) -> dict:
    return _ask(RELEVANCY_PROMPT.format(question=question, answer=answer))


def context_precision(question: str, chunks: list[str]) -> dict:
    numbered = "\n".join(f"{i+1}. {c[:300]}" for i, c in enumerate(chunks))
    return _ask(CONTEXT_PRECISION_PROMPT.format(question=question, chunks=numbered))
