from app.core.openai_client import get_openai_client


def embed_text(text: str):
    """Convert text into vector embedding using OpenAI"""
    client = get_openai_client()

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding
