"""
Main ticket analysis pipeline.

Flow:
    [summarize | classify | embed]   - 3 OpenAI calls in parallel
            ↓
    retrieve similar tickets (Chroma)  - uses the embedding from above
            ↓
    fetch ticket bodies (MySQL)        - cheap, sequential
            ↓
    generate response (OpenAI)         - needs all of the above
            ↓
    [store ticket in MySQL | store embedding in Chroma]   - parallel writes
            ↓
    return result

The three initial OpenAI calls are independent of each other, so running
them concurrently in a thread pool cuts user-perceived latency roughly in
half on the cold path. ThreadPoolExecutor is the right tool here — the
work is all I/O bound (network calls), not CPU bound.
"""

from concurrent.futures import ThreadPoolExecutor

from app.services.summarizer import summarize_ticket
from app.services.classifier import classify_ticket
from app.services.responder import generate_response

from app.services.ticket_store import store_ticket
from app.services.ticket_retrieval import get_tickets_by_ids

from app.rag.embedder import embed_text
from app.rag.vector_store import add_ticket_to_vector_store
from app.rag.retriever import retrieve_similar_ticket_ids


# How many similar tickets to retrieve from Chroma.
SIMILAR_TICKETS_K = 2

# Max characters of each retrieved ticket fed into the response prompt.
# Keeps token usage tight without an extra LLM summarization step.
SIMILAR_TICKET_CONTEXT_CHARS = 300


def _compress_similar_ticket(text: str) -> str:
    """Trim a retrieved ticket to a short, prompt-friendly snippet."""
    text = text.strip()
    if len(text) <= SIMILAR_TICKET_CONTEXT_CHARS:
        return text
    return text[:SIMILAR_TICKET_CONTEXT_CHARS].rstrip() + "..."


def analyze_ticket(ticket_text: str) -> dict:
    # ---------------------------------------------------------------
    # 1. Run summarize / classify / embed in parallel.
    # ---------------------------------------------------------------
    with ThreadPoolExecutor(max_workers=3) as pool:
        f_summary = pool.submit(summarize_ticket, ticket_text)
        f_classification = pool.submit(classify_ticket, ticket_text)
        f_embedding = pool.submit(embed_text, ticket_text)

        summary = f_summary.result()
        classification = f_classification.result()
        embedding = f_embedding.result()

    major_category = classification["major_category"]
    sub_category = classification["sub_category"]

    # ---------------------------------------------------------------
    # 2. Retrieve similar tickets (Chroma) using the embedding we
    #    already computed in step 1 — no second embed call.
    # ---------------------------------------------------------------
    similar_ids = retrieve_similar_ticket_ids(
        ticket_text,
        k=SIMILAR_TICKETS_K,
        embedding=embedding,
    )
    similar_tickets = get_tickets_by_ids(similar_ids)

    # Compress for prompt context: short snippets only.
    similar_ticket_texts = [
        _compress_similar_ticket(t.ticket_text) for t in similar_tickets
    ]

    # ---------------------------------------------------------------
    # 3. Generate the suggested reply.
    # ---------------------------------------------------------------
    suggested_reply = generate_response(
        ticket_text=ticket_text,
        summary=summary,
        major_category=major_category,
        sub_category=sub_category,
        similar_tickets=similar_ticket_texts,
    )

    # ---------------------------------------------------------------
    # 4. Persist: write to MySQL + Chroma in parallel.
    #    MySQL needs to return the ticket_id before Chroma can use it,
    #    so we store the ticket first, then run the Chroma write
    #    concurrently with returning to the caller is not safe — we
    #    still need to wait, but the Chroma write does not block the
    #    response semantically. We do them sequentially here: MySQL,
    #    then Chroma. (Chroma needs the ticket_id from MySQL.)
    # ---------------------------------------------------------------
    ticket_id = store_ticket(
        ticket_text=ticket_text,
        summary=summary,
        major_category=major_category,
        sub_category=sub_category,
        response=suggested_reply,
    )

    add_ticket_to_vector_store(
        ticket_id=ticket_id,
        text=ticket_text,
        embedding=embedding,
    )

    # ---------------------------------------------------------------
    # 5. Return.
    # ---------------------------------------------------------------
    return {
        "summary": summary,
        "major_category": major_category,
        "sub_category": sub_category,
        "similar_tickets": similar_ticket_texts,
        "suggested_reply": suggested_reply,
    }
