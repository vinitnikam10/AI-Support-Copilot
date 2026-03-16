from app.rag.chroma_client import collection
from app.rag.embedder import embed_text


def add_ticket_to_vector_store(ticket_id, text):
    """
    Store ticket embedding in Chroma Cloud
    """

    embedding = embed_text(text)

    collection.add(
        ids=[str(ticket_id)],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"ticket_id": ticket_id}]
    )