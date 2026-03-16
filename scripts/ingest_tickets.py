import os
import sys
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
sys.path.append(BACKEND_DIR)

from app.rag.vector_store import add_ticket_to_vector_store

data_path = os.path.join(BASE_DIR, "data", "sample_tickets.json")

with open(data_path) as f:
    tickets = json.load(f)

for t in tickets:
    add_ticket_to_vector_store(ticket_id=t["id"], text=t["text"])

print("Tickets indexed successfully")
