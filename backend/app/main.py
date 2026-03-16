from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.ticket import TicketRequest
from app.services.rag_pipeline import analyze_ticket

app = FastAPI(title="Support AI Copilot")

# Allow frontend requests
origins = [
    "http://localhost:5173",
    "https://support-ai-copilot.web.app",
    "https://support-ai-copilot.firebaseapp.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/analyze-ticket")
def analyze(ticket: TicketRequest):
    result = analyze_ticket(ticket.text)
    return result