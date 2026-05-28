import json

from app.core.openai_client import get_openai_client
from app.core.config import TEMP_DETERMINISTIC
from app.core.router import pick_model
from app.config.ticket_taxonomy import TICKET_TAXONOMY


def classify_ticket(ticket_text: str) -> dict:
    client = get_openai_client()

    taxonomy_text = ""
    for major, subs in TICKET_TAXONOMY.items():
        taxonomy_text += f"\n{major}:\n"
        for sub in subs:
            taxonomy_text += f"- {sub}\n"

    prompt = f"""
You are a support ticket classifier.

Classify the ticket into one MAJOR category and one SUBCATEGORY.

Use ONLY the categories below.

Categories:

{taxonomy_text}

Return response in JSON format:

{{
"major_category": "...",
"sub_category": "..."
}}

Ticket:
{ticket_text}
"""

    response = client.chat.completions.create(
        model=pick_model("classify", ticket_text),
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMP_DETERMINISTIC,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences — LLMs often wrap JSON in ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

    result = json.loads(raw)

    # Validate categories exist in our taxonomy
    major = result.get("major_category", "")
    sub = result.get("sub_category", "")

    if major not in TICKET_TAXONOMY:
        result["major_category"] = "Misc"
        result["sub_category"] = "General Query"
    elif sub not in TICKET_TAXONOMY[major]:
        result["sub_category"] = TICKET_TAXONOMY[major][0]

    return result
