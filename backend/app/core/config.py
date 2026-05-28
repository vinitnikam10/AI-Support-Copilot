import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------------------------------------------
# OpenAI credentials
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# -----------------------------------------------------------------------------
# Model configuration
#
# All model IDs are centralized here so individual services never hardcode
# names. Override any of these via env vars without code changes.
# -----------------------------------------------------------------------------

# Fast/cheap model for the everyday pipeline (summary, classification, reply).
MODEL_FAST = os.getenv("MODEL_FAST", "gpt-4o-mini")

# Stronger model reserved for difficult tickets. Wired up via core.router but
# not actively selected yet — see router.pick_model().
MODEL_STRONG = os.getenv("MODEL_STRONG", "gpt-4o")

# Embedding model for the RAG pipeline.
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING", "text-embedding-3-small")

# Transcription model for the voice input endpoint.
MODEL_TRANSCRIBE = os.getenv("MODEL_TRANSCRIBE", "gpt-4o-mini-transcribe")


# -----------------------------------------------------------------------------
# Generation parameters
# -----------------------------------------------------------------------------

# Default temperature for natural-language tasks (summary, response).
TEMP_DEFAULT = float(os.getenv("TEMP_DEFAULT", "0.3"))

# Deterministic temperature for structured tasks (classification).
TEMP_DETERMINISTIC = 0.0


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root@localhost/support_ai",
)


# -----------------------------------------------------------------------------
# Backward-compatible alias.
# Older code referenced OPENAI_MODEL directly. Keep this alias so any caller
# we missed doesn't break — but new code should use MODEL_FAST.
# -----------------------------------------------------------------------------
OPENAI_MODEL = MODEL_FAST
