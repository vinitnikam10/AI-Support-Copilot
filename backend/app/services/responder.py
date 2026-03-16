from typing import List
from app.core.openai_client import get_openai_client
from app.core.config import OPENAI_MODEL


def generate_response(
    ticket_text: str,
    summary: str,
    major_category: str,
    sub_category: str,
    similar_tickets: List[str]
) -> str:
    client = get_openai_client()

    similar_tickets_text = ""
    if similar_tickets:
        formatted = "\n".join(f"- {t}" for t in similar_tickets)
        similar_tickets_text = f"\nSimilar past tickets for reference:\n{formatted}\n"

    prompt = f"""
You are a customer support agent for a healthcare EMR and billing system.

Ticket Summary: {summary}
Category: {major_category} > {sub_category}
{similar_tickets_text}
Original Ticket:
{ticket_text}

Draft a helpful, professional, and concise support response based on the above context.
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
