"""
AI Support Copilot — Test Suite

Tests every component of the pipeline:
  1. Summarizer
  2. Classifier
  3. Embedder
  4. Vector Store (Chroma)
  5. Retriever
  6. Responder
  7. Ticket Store (MySQL write)
  8. Ticket Retrieval (MySQL read)
  9. Full Pipeline (end-to-end)

Setup:
  cd backend
  pip install pytest
  pytest tests/test_pipeline.py -v

Notes:
  - Requires .env with OPENAI_API_KEY, CHROMA_*, DATABASE_URL
  - Tests hit real OpenAI API and Chroma Cloud (not mocked)
  - Tests write to your real MySQL DB (use a test database if you prefer)
  - Run with -v for verbose output showing each test
"""

import os
import sys
import json
import pytest

# -------------------------------------------------------
# Make sure we can import from app/
# -------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()


# -------------------------------------------------------
# Sample test data
# -------------------------------------------------------
SAMPLE_TICKETS = [
    "ERA allowed amount lower than expected contract value for CPT 97110",
    "Patient cannot log in to the portal after password reset",
    "SOAP note not saving for Dr. Smith's 2pm appointment",
    "Claim rejected due to missing modifier GP",
    "Eligibility check failing for Medicare patient",
]


# =======================================================
# TEST 1: Config loads correctly
# =======================================================
class TestConfig:

    def test_openai_key_loaded(self):
        """OPENAI_API_KEY should be set in .env"""
        from app.core.config import OPENAI_API_KEY
        assert OPENAI_API_KEY is not None, "OPENAI_API_KEY is not set in .env"
        assert len(OPENAI_API_KEY) > 10, "OPENAI_API_KEY looks too short"

    def test_openai_model_loaded(self):
        """OPENAI_MODEL should have a default value"""
        from app.core.config import OPENAI_MODEL
        assert OPENAI_MODEL is not None
        print(f"  Model: {OPENAI_MODEL}")

    def test_database_url_loaded(self):
        """DATABASE_URL should be available"""
        from app.core.config import DATABASE_URL
        assert DATABASE_URL is not None
        assert "mysql" in DATABASE_URL or "sqlite" in DATABASE_URL
        print(f"  DB URL: {DATABASE_URL[:30]}...")


# =======================================================
# TEST 2: OpenAI client creation
# =======================================================
class TestOpenAIClient:

    def test_client_creation(self):
        """Should create an OpenAI client without errors"""
        from app.core.openai_client import get_openai_client
        client = get_openai_client()
        assert client is not None


# =======================================================
# TEST 3: Summarizer
# =======================================================
class TestSummarizer:

    def test_summarize_returns_string(self):
        """Summarizer should return a non-empty string"""
        from app.services.summarizer import summarize_ticket

        ticket = SAMPLE_TICKETS[0]
        result = summarize_ticket(ticket)

        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert len(result) > 20, "Summary is too short"
        print(f"  Input:   {ticket}")
        print(f"  Summary: {result[:100]}...")


# =======================================================
# TEST 4: Classifier
# =======================================================
class TestClassifier:

    def test_returns_dict(self):
        """Classifier must return a dict, not a string"""
        from app.services.classifier import classify_ticket

        ticket = SAMPLE_TICKETS[0]  # ERA/Billing ticket
        result = classify_ticket(ticket)

        assert isinstance(result, dict), (
            f"CRITICAL: classifier returned {type(result)}, not dict. "
            f"Value: {result}"
        )

    def test_has_required_keys(self):
        """Result must have major_category and sub_category"""
        from app.services.classifier import classify_ticket

        result = classify_ticket(SAMPLE_TICKETS[0])

        assert "major_category" in result, "Missing major_category key"
        assert "sub_category" in result, "Missing sub_category key"

    def test_billing_ticket(self):
        """ERA ticket should be classified as Billing"""
        from app.services.classifier import classify_ticket

        result = classify_ticket(
            "ERA allowed amount lower than expected contract value for CPT 97110"
        )

        assert result["major_category"] == "Billing", (
            f"Expected 'Billing', got '{result['major_category']}'"
        )
        print(f"  Category: {result['major_category']} > {result['sub_category']}")

    def test_emr_ticket(self):
        """SOAP note ticket should be classified as EMR"""
        from app.services.classifier import classify_ticket

        result = classify_ticket(
            "SOAP note not saving for Dr. Smith's 2pm appointment"
        )

        assert result["major_category"] == "EMR", (
            f"Expected 'EMR', got '{result['major_category']}'"
        )
        print(f"  Category: {result['major_category']} > {result['sub_category']}")

    def test_misc_ticket(self):
        """Login issue should be classified as Misc"""
        from app.services.classifier import classify_ticket

        result = classify_ticket(
            "Patient cannot log in to the portal after password reset"
        )

        assert result["major_category"] == "Misc", (
            f"Expected 'Misc', got '{result['major_category']}'"
        )
        print(f"  Category: {result['major_category']} > {result['sub_category']}")

    def test_categories_in_taxonomy(self):
        """Returned categories must exist in TICKET_TAXONOMY"""
        from app.services.classifier import classify_ticket
        from app.config.ticket_taxonomy import TICKET_TAXONOMY

        result = classify_ticket(SAMPLE_TICKETS[0])

        major = result["major_category"]
        sub = result["sub_category"]

        assert major in TICKET_TAXONOMY, (
            f"Major category '{major}' not in taxonomy"
        )
        assert sub in TICKET_TAXONOMY[major], (
            f"Sub category '{sub}' not in taxonomy[{major}]"
        )


# =======================================================
# TEST 5: Embedder
# =======================================================
class TestEmbedder:

    def test_embed_returns_list(self):
        """Embedder should return a list of floats"""
        from app.rag.embedder import embed_text

        result = embed_text("test ticket about billing")

        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 100, f"Embedding too short: {len(result)} dimensions"
        assert isinstance(result[0], float), "Embedding values should be floats"
        print(f"  Embedding dimensions: {len(result)}")


# =======================================================
# TEST 6: Vector Store (Chroma write)
# =======================================================
class TestVectorStore:

    def test_add_ticket(self):
        """Should store a ticket embedding in Chroma without errors"""
        from app.rag.vector_store import add_ticket_to_vector_store

        # Use a high ID to avoid conflicts with real data
        add_ticket_to_vector_store(
            ticket_id=99999,
            text="Test ticket: ERA mismatch for CPT 97110"
        )
        print("  Stored test ticket 99999 in Chroma")


# =======================================================
# TEST 7: Retriever (Chroma read)
# =======================================================
class TestRetriever:

    def test_retrieve_returns_list(self):
        """Retriever should return a list of string IDs"""
        from app.rag.retriever import retrieve_similar_ticket_ids

        # First make sure there's something to find
        from app.rag.vector_store import add_ticket_to_vector_store
        add_ticket_to_vector_store(99998, "ERA allowed amount incorrect")

        results = retrieve_similar_ticket_ids(
            "ERA amount mismatch", k=3
        )

        assert isinstance(results, list), f"Expected list, got {type(results)}"
        print(f"  Similar ticket IDs: {results}")

    def test_ids_are_strings(self):
        """Chroma returns IDs as strings — verify this"""
        from app.rag.retriever import retrieve_similar_ticket_ids

        results = retrieve_similar_ticket_ids("billing claim issue", k=1)

        if results:
            assert isinstance(results[0], str), (
                f"Expected string IDs, got {type(results[0])}"
            )


# =======================================================
# TEST 8: Responder
# =======================================================
class TestResponder:

    def test_generate_response_with_full_context(self):
        """Responder should accept all 5 params and return a string"""
        from app.services.responder import generate_response

        result = generate_response(
            ticket_text="ERA allowed amount mismatch for CPT 97110",
            summary="Allowed amount differs from expected contract value.",
            major_category="Billing",
            sub_category="ERA",
            similar_tickets=[
                "ERA allowed amount incorrect",
                "ERA mismatch due to contract configuration"
            ]
        )

        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert len(result) > 20, "Response is too short"
        print(f"  Response: {result[:100]}...")

    def test_generate_response_no_similar_tickets(self):
        """Should work even with empty similar tickets list"""
        from app.services.responder import generate_response

        result = generate_response(
            ticket_text="Cannot log in to portal",
            summary="User unable to access the system.",
            major_category="Misc",
            sub_category="Login Issue",
            similar_tickets=[]
        )

        assert isinstance(result, str)
        assert len(result) > 20


# =======================================================
# TEST 9: MySQL — Ticket Store (write)
# =======================================================
class TestTicketStore:

    def test_store_and_get_id(self):
        """Should store a ticket and return an integer ID"""
        from app.services.ticket_store import store_ticket

        ticket_id = store_ticket(
            ticket_text="Test ticket for unit testing",
            summary="This is a test summary",
            major_category="Misc",
            sub_category="General Query",
            response="This is a test response"
        )

        assert isinstance(ticket_id, int), (
            f"Expected int ID, got {type(ticket_id)}"
        )
        assert ticket_id > 0
        print(f"  Stored ticket with ID: {ticket_id}")


# =======================================================
# TEST 10: MySQL — Ticket Retrieval (read)
# =======================================================
class TestTicketRetrieval:

    def test_get_by_ids_with_strings(self):
        """Should handle string IDs (as returned by Chroma)"""
        from app.services.ticket_store import store_ticket
        from app.services.ticket_retrieval import get_tickets_by_ids

        # Store a ticket first so we have a known ID
        ticket_id = store_ticket(
            ticket_text="Retrieval test ticket",
            summary="Test",
            major_category="Misc",
            sub_category="General Query",
            response="Test response"
        )

        # Pass as STRING (like Chroma would)
        results = get_tickets_by_ids([str(ticket_id)])

        assert len(results) >= 1, "Should find at least 1 ticket"
        assert results[0].ticket_text == "Retrieval test ticket"
        print(f"  Retrieved ticket ID {ticket_id} successfully")

    def test_empty_ids_returns_empty(self):
        """Empty ID list should return empty list, not crash"""
        from app.services.ticket_retrieval import get_tickets_by_ids

        results = get_tickets_by_ids([])
        assert results == []

    def test_invalid_ids_returns_empty(self):
        """Non-numeric IDs should be skipped gracefully"""
        from app.services.ticket_retrieval import get_tickets_by_ids

        results = get_tickets_by_ids(["abc", "not_a_number"])
        assert results == []


# =======================================================
# TEST 11: Full Pipeline (end-to-end)
# =======================================================
class TestFullPipeline:

    def test_analyze_ticket_end_to_end(self):
        """
        Full pipeline test:
          ticket → summarize → classify → retrieve → respond → store

        This is the most important test.
        If this passes, the whole system works.
        """
        from app.services.rag_pipeline import analyze_ticket

        result = analyze_ticket(
            "ERA allowed amount lower than expected contract value for CPT 97110"
        )

        # Check all expected keys are present
        assert "summary" in result, "Missing 'summary' in result"
        assert "major_category" in result, "Missing 'major_category' in result"
        assert "sub_category" in result, "Missing 'sub_category' in result"
        assert "similar_tickets" in result, "Missing 'similar_tickets' in result"
        assert "suggested_reply" in result, "Missing 'suggested_reply' in result"

        # Check types
        assert isinstance(result["summary"], str)
        assert isinstance(result["major_category"], str)
        assert isinstance(result["sub_category"], str)
        assert isinstance(result["similar_tickets"], list)
        assert isinstance(result["suggested_reply"], str)

        # Check classification is reasonable
        assert result["major_category"] == "Billing", (
            f"Expected 'Billing', got '{result['major_category']}'"
        )

        print(f"\n  Summary:     {result['summary'][:80]}...")
        print(f"  Category:    {result['major_category']} > {result['sub_category']}")
        print(f"  Similar:     {len(result['similar_tickets'])} tickets found")
        print(f"  Reply:       {result['suggested_reply'][:80]}...")


# =======================================================
# TEST 12: API endpoint (FastAPI)
# =======================================================
class TestAPI:

    def test_health_endpoint(self):
        """GET / should return status running"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "running"

    def test_analyze_endpoint(self):
        """POST /analyze-ticket should return full result"""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/analyze-ticket",
            json={"text": "Claim rejected due to missing modifier GP"}
        )

        assert response.status_code == 200

        data = response.json()
        assert "summary" in data
        assert "major_category" in data
        assert "sub_category" in data
        assert "suggested_reply" in data

        print(f"\n  API returned: {data['major_category']} > {data['sub_category']}")