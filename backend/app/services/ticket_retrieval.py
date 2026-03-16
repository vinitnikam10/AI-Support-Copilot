from app.core.database import SessionLocal
from app.models.ticket_db import Ticket


def get_tickets_by_ids(ticket_ids):
    db = SessionLocal()
    try:
        tickets = (
            db.query(Ticket)
            .filter(Ticket.id.in_(ticket_ids))
            .all()
        )
        return tickets
    finally:
        db.close()
