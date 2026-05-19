from app.rag.chroma_client import collection
from app.rag.embedder import embed_text


def retrieve_similar_ticket_ids(text: str, k: int = 2, embedding: list[float] | None = None) -> list[str]:
    """
    Find the top-k most similar past ticket IDs in Chroma.

    Pass `embedding` if you've already computed it elsewhere in the pipeline,
    to avoid a redundant OpenAI embedding call.
    """
    if embedding is None:
        embedding = embed_text(text)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k,
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    return results["ids"][0]
