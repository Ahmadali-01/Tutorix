from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


PROMPT = """You are Tutorix, an AI education assistant.
Answer the user's question using ONLY the context below.
If the answer is not in the context, say you don't know.

Context:
{context}

Question: {question}

Answer:"""


def generate_answer(question: str, contexts: list[dict]) -> str:
    context_text = "\n\n---\n\n".join(c["text"] for c in contexts) if contexts else "(no context)"
    prompt = PROMPT.format(context=context_text, question=question)
    client = get_client()
    response = client.models.generate_content(
        model=settings.GEMINI_CHAT_MODEL,
        contents=prompt,
    )
    return response.text or ""
