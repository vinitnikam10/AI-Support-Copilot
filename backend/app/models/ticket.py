from pydantic import BaseModel


class TicketRequest(BaseModel):
    text: str