# AI Support Copilot

An AI-powered support assistant that helps customer support teams analyze, classify, and respond to tickets faster — built for healthcare SaaS platforms managing EMR and billing workflows.

---

## What It Does

Paste a support ticket (or a Slack message from a client) and the system automatically:

1. **Summarizes** the ticket — extracts the problem, impact, and urgency
2. **Classifies** it into a hierarchical category (e.g., `Billing → ERA`)
3. **Finds similar past tickets** using semantic search (RAG)
4. **Generates a suggested response** informed by the classification, summary, and historical context
5. **Stores everything** in a cloud database for future retrieval

---

## Example

**Input ticket:**

> ERA allowed amount mismatch for CPT 97110

**Output:**

| Field | Value |
|---|---|
| **Summary** | The ERA allowed amount for CPT 97110 doesn't match the expected contract value. High urgency — may cause payment posting errors. |
| **Category** | Billing → ERA |
| **Similar Tickets** | "ERA allowed amount incorrect", "ERA mismatch due to contract configuration" |
| **Suggested Reply** | "Please verify the contract configuration for CPT 97110 in your fee schedule. This is commonly caused by outdated contract files..." |

---

## Architecture

```
React Frontend (Firebase Hosting)
       │
       ▼
FastAPI Backend (Google Cloud Run)
       │
       ▼
AI Processing Pipeline
 ├── Summarizer (OpenAI)
 ├── Classifier (OpenAI + taxonomy validation)
 ├── Embedder (OpenAI text-embedding-3-small)
 ├── RAG Retriever (Chroma Cloud)
 └── Response Generator (OpenAI + full context)
       │
       ▼
Storage
 ├── Google Cloud SQL / MySQL (structured ticket data)
 └── Chroma Cloud (vector embeddings for semantic search)
```

### Request Flow

```
POST /analyze-ticket { "text": "..." }
  │
  ├─ 1. Summarize ticket (OpenAI)
  ├─ 2. Classify ticket (OpenAI → JSON → validate against taxonomy)
  ├─ 3. Embed ticket text (OpenAI embeddings)
  ├─ 4. Query Chroma for similar tickets (vector similarity search)
  ├─ 5. Fetch similar ticket details from MySQL
  ├─ 6. Generate response (OpenAI, using summary + classification + similar tickets)
  ├─ 7. Store ticket + results in MySQL
  ├─ 8. Store embedding in Chroma
  │
  └─ Return: { summary, major_category, sub_category, similar_tickets, suggested_reply }
```

---

## Classification Taxonomy

Tickets are classified into a **major category** and a **sub-category**:

```
EMR
 ├── Scheduler
 ├── Appointments
 ├── Patients
 ├── Documents
 ├── Insurance Cards
 ├── Treatment Sheets
 ├── SOAP Notes
 ├── Doctors / Therapists
 ├── Clinics
 ├── Patient Wallet
 ├── To-Do Dashboard
 └── EMR Reports

Billing
 ├── Claims
 ├── Charges
 ├── ERA
 ├── Payments
 ├── CPT Codes
 ├── Modifiers
 ├── Claim Status
 ├── Adjustments and Remarks
 ├── Billing Reports
 ├── Invoices
 ├── Refunds
 ├── Billing Rules
 ├── Authorization
 └── Eligibility

Misc
 ├── Login Issue
 ├── Technical Error
 └── General Query
```

The classifier uses OpenAI with `temperature=0` for deterministic results and validates the output against this taxonomy — if the LLM returns a category that doesn't exist, it falls back to `Misc → General Query`.

---

## RAG Pipeline (Retrieval Augmented Generation)

The system uses semantic search to find similar past tickets:

```
New ticket text
  → OpenAI embedding (text-embedding-3-small, 1536 dimensions)
  → Chroma Cloud vector search (cosine similarity, top-k results)
  → Retrieve full ticket details from MySQL
  → Feed similar tickets into response generation prompt
```

This means the AI's suggested responses improve over time as more tickets are stored — each new ticket becomes part of the knowledge base for future queries.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React, Vite, Axios |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI / LLM** | OpenAI API (GPT-4.1-mini for text, text-embedding-3-small for vectors) |
| **Vector Database** | Chroma Cloud |
| **Relational Database** | MySQL 8.0 (Google Cloud SQL) |
| **Hosting (Backend)** | Google Cloud Run |
| **Hosting (Frontend)** | Firebase Hosting |

---

## Project Structure

```
support-ai-copilot/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app, routes, CORS
│   │   │
│   │   ├── api/                       # Route handlers (future expansion)
│   │   │   ├── routes.py
│   │   │   ├── tickets.py
│   │   │   └── insights.py
│   │   │
│   │   ├── config/
│   │   │   └── ticket_taxonomy.py     # Classification categories
│   │   │
│   │   ├── core/
│   │   │   ├── config.py              # Environment variables (OpenAI, DB)
│   │   │   ├── database.py            # SQLAlchemy engine (Cloud SQL + local)
│   │   │   └── openai_client.py       # Shared OpenAI client
│   │   │
│   │   ├── models/
│   │   │   ├── ticket.py              # Pydantic request model
│   │   │   └── ticket_db.py           # SQLAlchemy ORM model
│   │   │
│   │   ├── rag/
│   │   │   ├── chroma_client.py       # Chroma Cloud connection
│   │   │   ├── embedder.py            # OpenAI text → vector embedding
│   │   │   ├── retriever.py           # Semantic search (find similar tickets)
│   │   │   └── vector_store.py        # Store embeddings in Chroma
│   │   │
│   │   ├── services/
│   │   │   ├── summarizer.py          # Ticket summarization (OpenAI)
│   │   │   ├── classifier.py          # Hierarchical classification (OpenAI)
│   │   │   ├── responder.py           # Response generation (OpenAI + RAG context)
│   │   │   ├── rag_pipeline.py        # Main pipeline orchestrator
│   │   │   ├── ticket_store.py        # Write ticket to MySQL
│   │   │   └── ticket_retrieval.py    # Read tickets from MySQL
│   │   │
│   │   └── utils/
│   │       └── text_cleaner.py        # Text preprocessing (future)
│   │
│   ├── tests/
│   │   └── test_pipeline.py           # 24 tests covering every component
│   │
│   ├── storage/                       # Local Chroma DB (dev only)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── deploy.sh                      # Cloud Run deployment script
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── apiClient.js           # Axios client → backend API
│   │   ├── components/
│   │   │   ├── TicketInput.jsx         # Ticket text input form
│   │   │   ├── SummaryCard.jsx         # Displays AI summary
│   │   │   ├── ClassificationCard.jsx  # Shows Major → Sub category
│   │   │   ├── SimilarTickets.jsx      # Lists similar past tickets
│   │   │   └── SuggestedReply.jsx      # Shows AI-generated response
│   │   └── pages/
│   │       ├── TicketPage.jsx          # Main page (orchestrates components)
│   │       └── Dashboard.jsx           # Analytics dashboard (future)
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── scripts/
│   ├── ingest_tickets.py              # Bulk-load tickets into vector store
│   └── test_chroma.py                 # Quick Chroma connectivity test
│
├── data/
│   └── sample_tickets.json            # Sample ticket data for testing
│
├── prompts/
│   ├── summarize_ticket.txt           # Prompt templates (future)
│   ├── classify_ticket.txt
│   └── generate_response.txt
│
├── docs/
│   └── architecture.md
│
├── firebase.json                      # Firebase hosting config
├── docker-compose.yml
└── .gitignore
```

---

## Setup & Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account (for Cloud SQL and Cloud Run)
- OpenAI API key
- Chroma Cloud account

### 1. Clone the repository

```bash
git clone https://github.com/your-username/support-ai-copilot.git
cd support-ai-copilot
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini

CHROMA_API_KEY=your_chroma_api_key
CHROMA_TENANT=your_chroma_tenant
CHROMA_DATABASE=your_chroma_database

DATABASE_URL=mysql+pymysql://root:password@localhost/support_ai
```

### 3. Database setup (local)

```bash
mysql -u root -e "CREATE DATABASE IF NOT EXISTS support_ai"

mysql -u root support_ai -e "
CREATE TABLE IF NOT EXISTS tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_text TEXT,
    summary TEXT,
    major_category VARCHAR(50),
    sub_category VARCHAR(50),
    ai_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
```

### 4. Run the backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

### 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

## Testing

The project includes 24 tests covering every component of the pipeline.

### Install test dependencies

```bash
cd backend
pip install pytest httpx
```

### Run all tests

```bash
pytest tests/test_pipeline.py -v
```

### Run tests by component

```bash
# Config and environment
pytest tests/test_pipeline.py::TestConfig -v

# Summarizer
pytest tests/test_pipeline.py::TestSummarizer -v

# Classifier (most critical — tests JSON parsing + taxonomy validation)
pytest tests/test_pipeline.py::TestClassifier -v

# Embedder + Vector Store + Retriever
pytest tests/test_pipeline.py::TestEmbedder -v
pytest tests/test_pipeline.py::TestVectorStore -v
pytest tests/test_pipeline.py::TestRetriever -v

# Response generator
pytest tests/test_pipeline.py::TestResponder -v

# MySQL read/write
pytest tests/test_pipeline.py::TestTicketStore -v
pytest tests/test_pipeline.py::TestTicketRetrieval -v

# Full end-to-end pipeline
pytest tests/test_pipeline.py::TestFullPipeline -v

# FastAPI endpoints
pytest tests/test_pipeline.py::TestAPI -v
```

---

## Deployment

### Backend → Google Cloud Run

```bash
cd backend
./deploy.sh
```

The `deploy.sh` script deploys with all required environment variables and Cloud SQL connection. See the file for the full command.

Key deployment flags:
- `--add-cloudsql-instances` connects Cloud Run to Cloud SQL natively
- `INSTANCE_CONNECTION_NAME` tells the Cloud SQL Python Connector which instance to use
- The backend auto-detects whether it's running locally or on Cloud Run and uses the appropriate database connection method

### Frontend → Firebase Hosting

```bash
cd frontend
npm run build
firebase deploy
```

### Database → Google Cloud SQL

The MySQL database runs on Google Cloud SQL (db-f1-micro tier). The `tickets` table stores all processed tickets with their AI-generated summaries, classifications, and suggested responses.

Cloud Run connects to Cloud SQL using the [Cloud SQL Python Connector](https://github.com/GoogleCloudPlatform/cloud-sql-python-connector) — no public IP or VPC configuration needed.

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `OPENAI_API_KEY` | Backend | OpenAI API key for LLM and embeddings |
| `OPENAI_MODEL` | Backend | Model name (default: `gpt-4.1-mini`) |
| `CHROMA_API_KEY` | Backend | Chroma Cloud API key |
| `CHROMA_TENANT` | Backend | Chroma Cloud tenant ID |
| `CHROMA_DATABASE` | Backend | Chroma Cloud database name |
| `DATABASE_URL` | Backend (local) | MySQL connection string for local development |
| `INSTANCE_CONNECTION_NAME` | Backend (Cloud Run) | Cloud SQL instance connection name |
| `DB_USER` | Backend (Cloud Run) | Cloud SQL username |
| `DB_PASSWORD` | Backend (Cloud Run) | Cloud SQL password |
| `DB_NAME` | Backend (Cloud Run) | Cloud SQL database name |

---

## API Reference

### `GET /`

Health check.

**Response:** `{"status": "running"}`

### `POST /analyze-ticket`

Analyze a support ticket through the full AI pipeline.

**Request:**
```json
{
  "text": "ERA allowed amount mismatch for CPT 97110"
}
```

**Response:**
```json
{
  "summary": "The ERA allowed amount for CPT 97110 differs from the expected contract value...",
  "major_category": "Billing",
  "sub_category": "ERA",
  "similar_tickets": [
    "ERA allowed amount incorrect",
    "ERA mismatch due to contract configuration"
  ],
  "suggested_reply": "Please verify the contract configuration for CPT 97110..."
}
```

---

## Future Improvements

- **Slack integration** — automatic ticket ingestion from Slack channels
- **Ticket analytics dashboard** — visualize trends by category, volume, resolution time
- **Automated routing** — assign tickets to the right team based on classification
- **Knowledge base integration** — pull from internal docs alongside similar tickets
- **Structured RAG metadata** — filter similar tickets by category for more relevant retrieval
- **Feedback loop** — let agents rate suggested responses to improve quality over time
- **Confidence scores** — show classification and response confidence levels
- **Multi-tenant support** — serve multiple organizations from a single deployment

---

## License

This project is for educational and demonstration purposes.
