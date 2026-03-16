import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.rag.vector_store import add_ticket_to_vector_store
from app.rag.retriever import retrieve_similar_ticket_ids

add_ticket_to_vector_store(1, "ERA allowed amount mismatch")

results = retrieve_similar_ticket_ids("ERA amount incorrect")

print(results)
