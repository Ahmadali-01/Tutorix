from google import genai
import time

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


PROMPT = """You are Tutorix, an expert AI tutor — helpful, accurate, and thorough like ChatGPT, Claude, and Gemini.

Answer the user's question completely and helpfully. Use the course context below when it's relevant.

If the context is relevant: cite specifics from it naturally.
If the context is not relevant or empty: answer from your own full knowledge as a helpful tutor.
Never say "I don't know" or "not in the context" just because the context is thin — use your general knowledge.

Course context (may or may not be relevant):
{context}

User question: {question}

Give a clear, well-structured, accurate answer:"""


def generate_answer(question: str, contexts: list[dict]) -> str:
    context_text = (
        "\n\n---\n\n".join(c["text"] for c in contexts)
        if contexts
        else "(no course context available — answer from general knowledge)"
    )
    prompt = PROMPT.format(context=context_text, question=question)
    client = get_client()
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_CHAT_MODEL,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception:
            time.sleep(2 ** attempt)
    return "The AI service is temporarily unavailable. Please try again in a moment."
