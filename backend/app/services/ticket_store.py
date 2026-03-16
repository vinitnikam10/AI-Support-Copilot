from app.core.database import SessionLocal
from app.models.ticket_db import Ticket


def store_ticket(ticket_text, summary, major_category, sub_category, response):
    ticket = Ticket(
        ticket_text=ticket_text,
        summary=summary,
        major_category=major_category,
        sub_category=sub_category,
        ai_response=response
    )

    db = SessionLocal()
    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket.id
    finally:
        db.close()
