from app.services.summarizer import summarize_ticket
from app.services.classifier import classify_ticket
from app.services.responder import generate_response

from app.services.ticket_store import store_ticket
from app.services.ticket_retrieval import get_tickets_by_ids

from app.rag.vector_store import add_ticket_to_vector_store
from app.rag.retriever import retrieve_similar_ticket_ids


def analyze_ticket(ticket_text: str):
    """
    Main AI pipeline for analyzing support tickets.
    """

    # -----------------------------
    # 1️⃣ Summarize the ticket
    # -----------------------------
    summary = summarize_ticket(ticket_text)

    # -----------------------------
    # 2️⃣ Classify the ticket
    # -----------------------------
    classification = classify_ticket(ticket_text)

    major_category = classification["major_category"]
    sub_category = classification["sub_category"]

    # -----------------------------
    # 3️⃣ Retrieve similar tickets
    # -----------------------------
    similar_ids = retrieve_similar_ticket_ids(ticket_text)

    similar_tickets = get_tickets_by_ids(similar_ids)

    # Convert to simple text list for LLM
    similar_ticket_texts = [
        t.ticket_text for t in similar_tickets
    ]

    # -----------------------------
    # 4️⃣ Generate AI response
    # -----------------------------
    suggested_reply = generate_response(
        ticket_text=ticket_text,
        summary=summary,
        major_category=major_category,
        sub_category=sub_category,
        similar_tickets=similar_ticket_texts
    )

    # -----------------------------
    # 5️⃣ Store ticket in MySQL
    # -----------------------------
    ticket_id = store_ticket(
        ticket_text=ticket_text,
        summary=summary,
        major_category=major_category,
        sub_category=sub_category,
        response=suggested_reply
    )

    # -----------------------------
    # 6️⃣ Store embedding in Chroma
    # -----------------------------
    add_ticket_to_vector_store(
        ticket_id=ticket_id,
        text=ticket_text
    )

    # -----------------------------
    # 7️⃣ Return final result
    # -----------------------------
    return {
        "summary": summary,
        "major_category": major_category,
        "sub_category": sub_category,
        "similar_tickets": similar_ticket_texts,
        "suggested_reply": suggested_reply
    }