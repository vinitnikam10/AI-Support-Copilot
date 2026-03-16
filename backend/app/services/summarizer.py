from app.core.openai_client import get_openai_client
from app.core.config import OPENAI_MODEL


def summarize_ticket(ticket_text: str):
    client = get_openai_client()
    prompt = f"""
You are a support assistant for a healthcare EMR and billing platform.

Summarize the following support ticket.

Ticket:
{ticket_text}

Provide:
- Problem
- Impact
- Urgency
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content