from app.rag.chroma_client import collection
from app.rag.embedder import embed_text


def add_ticket_to_vector_store(
    ticket_id: int,
    text: str,
    embedding: list[float] | None = None,
) -> None:
    """
    Store a ticket's embedding in Chroma.

    Pass `embedding` if you've already computed it elsewhere in the pipeline,
    to avoid a redundant OpenAI embedding call.
    """
    if embedding is None:
        embedding = embed_text(text)

    collection.add(
        ids=[str(ticket_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"ticket_id": ticket_id}],
    )
