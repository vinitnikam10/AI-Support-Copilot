from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import get_logger
from app.models.ticket import TicketRequest
from app.services.rag_pipeline import analyze_ticket
from app.services.transcriber import transcribe_audio

log = get_logger(__name__)

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
    text_preview = ticket.text[:80].replace("\n", " ")
    log.info("analyze-ticket request: %r", text_preview)

    try:
        result = analyze_ticket(ticket.text)
    except Exception:
        log.exception("analyze-ticket failed")
        raise HTTPException(
            status_code=500,
            detail="Ticket analysis failed. Please try again.",
        )

    log.info(
        "analyze-ticket ok: %s > %s",
        result.get("major_category"),
        result.get("sub_category"),
    )
    return result


@app.post("/transcribe-audio")
async def transcribe(audio: UploadFile = File(...)):
    log.info("transcribe-audio request: %s (%s)", audio.filename, audio.content_type)

    try:
        transcript = transcribe_audio(audio.file, filename=audio.filename or "audio.webm")
    except Exception:
        log.exception("transcribe-audio failed")
        raise HTTPException(
            status_code=500,
            detail="Audio transcription failed. Please try again.",
        )

    log.info("transcribe-audio ok: %d chars", len(transcript))
    return {"transcript": transcript}
