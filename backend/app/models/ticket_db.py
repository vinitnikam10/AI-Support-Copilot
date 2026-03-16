from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Ticket(Base):

    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    ticket_text = Column(Text)

    summary = Column(Text)

    major_category = Column(String(50))
    
    sub_category = Column(String(50))

    ai_response = Column(Text)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )