from app.core.openai_client import get_openai_client
from app.core.config import MODEL_EMBEDDING


def embed_text(text: str) -> list[float]:
    """Convert text into a vector embedding via OpenAI."""
    client = get_openai_client()

    response = client.embeddings.create(
        model=MODEL_EMBEDDING,
        input=text,
    )

    return response.data[0].embedding
