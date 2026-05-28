"""
Model routing seam.

Right now every task uses MODEL_FAST. This module exists so that future
routing logic (e.g. "use MODEL_STRONG when the ticket is long/ambiguous")
can be added without touching individual services.

Usage:
    from app.core.router import pick_model
    model = pick_model("classify")
"""

from app.core.config import MODEL_FAST


def pick_model(task: str, ticket_text: str | None = None) -> str:
    """
    Return the model ID for a given task.

    task: one of "summarize", "classify", "respond".
    ticket_text: the ticket being processed — reserved for future heuristics
                 (length, keywords) that may upgrade the model to MODEL_STRONG.

    Today this always returns MODEL_FAST. The signature is the contract that
    future routing code will fulfill.
    """
    return MODEL_FAST
