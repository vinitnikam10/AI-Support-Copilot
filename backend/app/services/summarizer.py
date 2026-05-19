from app.core.openai_client import get_openai_client
from app.core.config import TEMP_DEFAULT
from app.core.router import pick_model


def summarize_ticket(ticket_text: str) -> str:
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
        model=pick_model("summarize", ticket_text),
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMP_DEFAULT,
    )

    return response.choices[0].message.content
