from google import genai

from app.config import settings

_client = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def embed_text(text: str) -> list[float]:
    client = get_client()
    result = client.models.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        contents=text,
    )
    return list(result.embeddings[0].values)


def embed_batch(texts: list[str]) -> list[list[float]]:
    return [embed_text(t) for t in texts]
