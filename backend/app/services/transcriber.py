"""
Audio transcription service.

Thin wrapper around OpenAI's /audio/transcriptions endpoint. The frontend
records short clips via MediaRecorder (push-to-talk style) and uploads
them here; we return the transcript text.

This is NOT a realtime/streaming transcription. One file in, one
transcript out.
"""

from typing import BinaryIO

from app.core.openai_client import get_openai_client
from app.core.config import MODEL_TRANSCRIBE


def transcribe_audio(audio_file: BinaryIO, filename: str = "audio.webm") -> str:
    """
    Transcribe a single audio clip. `audio_file` is any binary stream
    (UploadFile.file from FastAPI works directly).

    Returns the plain transcript text.
    """
    client = get_openai_client()

    # The OpenAI client uses the filename to infer the audio format,
    # so we explicitly pass (name, stream) as a tuple.
    response = client.audio.transcriptions.create(
        model=MODEL_TRANSCRIBE,
        file=(filename, audio_file),
    )

    return response.text
