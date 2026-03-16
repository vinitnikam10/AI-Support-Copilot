from app.rag.chroma_client import collection
from app.rag.embedder import embed_text


def retrieve_similar_ticket_ids(text, k=3):
    embedding = embed_text(text)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    return results["ids"][0]
