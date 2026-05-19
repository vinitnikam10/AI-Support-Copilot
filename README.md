# AI Support Copilot

An AI-powered support assistant that helps customer support teams analyze, classify, and respond to tickets faster — built for healthcare SaaS platforms managing EMR and billing workflows.

---

## What It Does

Paste a support ticket (or dictate it via the microphone) and the system automatically:

1. **Summarizes** the ticket — extracts the problem, impact, and urgency
2. **Classifies** it into a hierarchical category (e.g., `Billing → ERA`)
3. **Finds similar past tickets** using semantic search (RAG)
4. **Generates a suggested response** informed by the classification, summary, and historical context
5. **Stores everything** in a cloud database for future retrieval

Voice input uses push-to-talk transcription — tap the mic, speak, tap again to stop, and the transcript fills the input box. You manually review and submit afterward.

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
       ├── /analyze-ticket  ──┐
       │                       │
       └── /transcribe-audio   │
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

### Request flow — `POST /analyze-ticket`

The summarize, classify, and embed steps are independent of each other,
so they run **in parallel** in a thread pool. The embedding is then reused
by the retriever and the vector store write — no double-embed.

```
POST /analyze-ticket { "text": "..." }
  │
  ├─ [in parallel]
  │     ├─ Summarize ticket (OpenAI)
  │     ├─ Classify ticket (OpenAI → JSON → validate against taxonomy)
  │     └─ Embed ticket text (OpenAI embeddings)
  │
  ├─ Query Chroma for similar tickets (using embedding from above)
  ├─ Fetch similar ticket details from MySQL
  ├─ Compress retrieved tickets (truncate to ~300 chars, top-2 only)
  ├─ Generate response (OpenAI, using summary + classification + similar tickets)
  ├─ Store ticket + results in MySQL
  ├─ Store embedding in Chroma (reuses the embedding from above)
  │
  └─ Return: { summary, major_category, sub_category, similar_tickets, suggested_reply }
```

### Request flow — `POST /transcribe-audio`

```
POST /transcribe-audio  (multipart: audio file)
  │
  └─ OpenAI gpt-4o-mini-transcribe → { "transcript": "..." }
```

The frontend records via the browser MediaRecorder API (webm format),
uploads the blob to the backend, and inserts the returned transcript
into the ticket input textarea. **It is push-to-talk only** — not realtime
streaming, not a voice agent.

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
  → Chroma Cloud vector search (cosine similarity, top-2 results)
  → Retrieve full ticket details from MySQL
  → Truncate each to ~300 chars to keep prompt context tight
  → Feed compressed similar tickets into response generation prompt
```

This means the AI's suggested responses improve over time as more tickets are stored — each new ticket becomes part of the knowledge base for future queries.

---

## Model Strategy

Models are centralized in [`backend/app/core/config.py`](backend/app/core/config.py) and selected per-task via [`backend/app/core/router.py`](backend/app/core/router.py). All names are env-overridable.

| Purpose | Default Model | Env Var |
|---|---|---|
| Summarize / classify / respond (fast path) | `gpt-4o-mini` | `MODEL_FAST` |
| Difficult tickets (future routing — not used yet) | `gpt-4o` | `MODEL_STRONG` |
| Embeddings | `text-embedding-3-small` | `MODEL_EMBEDDING` |
| Audio transcription | `gpt-4o-mini-transcribe` | `MODEL_TRANSCRIBE` |

The router (`pick_model(task, ticket_text)`) currently always returns `MODEL_FAST`. The signature is the seam for future routing logic that may upgrade specific cases to `MODEL_STRONG` based on heuristics like ticket length or ambiguity.

Temperatures are also centralized:
- `TEMP_DEFAULT = 0.3` — summary, response
- `TEMP_DETERMINISTIC = 0.0` — classifier (always)

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19, Vite 7, Tailwind CSS 3, Axios, markdown-to-jsx |
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **AI / LLM** | OpenAI API (gpt-4o-mini for text, text-embedding-3-small for vectors, gpt-4o-mini-transcribe for audio) |
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
│   │   ├── main.py                    # FastAPI app, routes (/analyze-ticket, /transcribe-audio), CORS, error handling
│   │   │
│   │   ├── api/                       # Reserved for future route splits
│   │   │   ├── routes.py
│   │   │   ├── tickets.py
│   │   │   └── insights.py
│   │   │
│   │   ├── config/
│   │   │   └── ticket_taxonomy.py     # Classification categories
│   │   │
│   │   ├── core/
│   │   │   ├── config.py              # Models, temperatures, DB URL, OpenAI key (all env-driven)
│   │   │   ├── router.py              # Model selection seam — pick_model(task, text)
│   │   │   ├── logging.py             # Shared logger setup (stdout → Cloud Logging)
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
│   │   │   ├── retriever.py           # Semantic search (accepts precomputed embedding)
│   │   │   └── vector_store.py        # Store embeddings in Chroma (accepts precomputed embedding)
│   │   │
│   │   ├── services/
│   │   │   ├── summarizer.py          # Ticket summarization (OpenAI, via router)
│   │   │   ├── classifier.py          # Hierarchical classification (OpenAI, deterministic)
│   │   │   ├── responder.py           # Response generation (OpenAI + compressed RAG context)
│   │   │   ├── transcriber.py         # Audio → text (OpenAI transcription)
│   │   │   ├── rag_pipeline.py        # Pipeline orchestrator (parallelized)
│   │   │   ├── ticket_store.py        # Write ticket to MySQL
│   │   │   └── ticket_retrieval.py    # Read tickets from MySQL
│   │   │
│   │   └── utils/
│   │       └── text_cleaner.py        # Text preprocessing (future)
│   │
│   ├── tests/
│   │   └── test_pipeline.py           # Component + end-to-end tests
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
│   │   ├── index.css                  # Tailwind directives + global styles
│   │   ├── api/
│   │   │   └── apiClient.js           # axios client — VITE_API_URL based
│   │   ├── components/
│   │   │   ├── TicketInput.jsx        # Ticket text input with integrated mic & submit
│   │   │   ├── MicButton.jsx          # Push-to-talk recorder → /transcribe-audio
│   │   │   ├── ResultCard.jsx         # Shared card wrapper for result sections
│   │   │   ├── SummaryCard.jsx        # Markdown-rendered summary
│   │   │   ├── ClassificationCard.jsx # Category chips
│   │   │   ├── SimilarTickets.jsx     # Collapsible similar ticket list
│   │   │   ├── SuggestedReply.jsx     # Markdown-rendered reply with copy button
│   │   │   └── SkeletonResults.jsx    # Shimmer loaders shown during analysis
│   │   └── pages/
│   │       ├── TicketPage.jsx         # Main page (orchestrates components)
│   │       └── Dashboard.jsx          # Analytics dashboard (future)
│   │
│   ├── .env.development               # VITE_API_URL → localhost:8000
│   ├── .env.production                # VITE_API_URL → Cloud Run URL
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── public/favicon.svg             # Brand favicon
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
├── prompts/                           # Reserved for future prompt template files
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
git clone git@github.com:vinitnikam10/AI-Support-Copilot.git
cd support-ai-copilot
```

### 2. Backend setup

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory (or at the repo root — both are loaded):

```env
OPENAI_API_KEY=sk-...

# Optional model overrides — defaults shown below
MODEL_FAST=gpt-4o-mini
MODEL_STRONG=gpt-4o
MODEL_EMBEDDING=text-embedding-3-small
MODEL_TRANSCRIBE=gpt-4o-mini-transcribe
TEMP_DEFAULT=0.3

CHROMA_HOST=api.trychroma.com
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

If connecting to the production Cloud SQL instance from a new machine, you must whitelist your current public IP in the Cloud SQL Console → Connections → Networking → Authorized networks. Local connections bypass this.

### 4. Run the backend

```bash
cd backend
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. The frontend dev server is configured to hit this URL via `VITE_API_URL` in `.env.development`.

### 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## Testing

The project includes a test suite covering every component of the pipeline.

```bash
cd backend
source venv/bin/activate
pytest tests/test_pipeline.py -v
```

Tests hit the real OpenAI API and Chroma Cloud (not mocked) and write to your configured MySQL DB.

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
npm run build       # builds with VITE_API_URL from .env.production
cd ..
firebase deploy
```

### Database → Google Cloud SQL

The MySQL database runs on Google Cloud SQL (db-f1-micro tier). The `tickets` table stores all processed tickets with their AI-generated summaries, classifications, and suggested responses.

Cloud Run connects to Cloud SQL using the [Cloud SQL Python Connector](https://github.com/GoogleCloudPlatform/cloud-sql-python-connector) — no public IP or VPC configuration needed.

---

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `OPENAI_API_KEY` | Backend | OpenAI API key for LLM, embeddings, and transcription |
| `MODEL_FAST` | Backend | Default model for summary/classify/respond (default: `gpt-4o-mini`) |
| `MODEL_STRONG` | Backend | Reserved for future routing (default: `gpt-4o`) |
| `MODEL_EMBEDDING` | Backend | Embedding model (default: `text-embedding-3-small`) |
| `MODEL_TRANSCRIBE` | Backend | Transcription model (default: `gpt-4o-mini-transcribe`) |
| `TEMP_DEFAULT` | Backend | Temperature for summary/response (default: `0.3`) |
| `CHROMA_API_KEY` | Backend | Chroma Cloud API key |
| `CHROMA_TENANT` | Backend | Chroma Cloud tenant ID |
| `CHROMA_DATABASE` | Backend | Chroma Cloud database name |
| `DATABASE_URL` | Backend (local) | MySQL connection string for local development |
| `INSTANCE_CONNECTION_NAME` | Backend (Cloud Run) | Cloud SQL instance connection name |
| `DB_USER` | Backend (Cloud Run) | Cloud SQL username |
| `DB_PASSWORD` | Backend (Cloud Run) | Cloud SQL password |
| `DB_NAME` | Backend (Cloud Run) | Cloud SQL database name |
| `VITE_API_URL` | Frontend | Backend base URL (set per-environment via `.env.development` and `.env.production`) |

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
  "summary": "**Problem:** The ERA allowed amount for CPT 97110 differs from the expected contract value...",
  "major_category": "Billing",
  "sub_category": "ERA",
  "similar_tickets": [
    "ERA allowed amount incorrect",
    "ERA mismatch due to contract configuration"
  ],
  "suggested_reply": "Please verify the contract configuration for CPT 97110..."
}
```

Summary and suggested reply may include lightweight markdown (`**bold**`, lists). The frontend renders this with `markdown-to-jsx`.

### `POST /transcribe-audio`

Transcribe a single audio clip recorded by the frontend mic. **Not** a streaming endpoint — one file in, one transcript out.

**Request:** `multipart/form-data` with a single `audio` field (any OpenAI-supported format — webm, mp3, m4a, wav, etc.)

**Response:**
```json
{ "transcript": "I cannot create an appointment in the scheduler" }
```

---

## Future Improvements

- **Confidence scores** — surface classification and response confidence in the UI
- **Similarity score indicators** — Chroma returns distances; expose them as relevance hints
- **Active model routing** — `core/router.py` is a stub today; route hard tickets to `MODEL_STRONG`
- **Slack integration** — auto ticket ingestion from Slack channels
- **Ticket analytics dashboard** — visualize trends by category, volume, resolution time
- **Automated routing** — assign tickets to the right team based on classification
- **Knowledge base integration** — pull from internal docs alongside similar tickets
- **Structured RAG metadata** — filter similar tickets by category for more relevant retrieval
- **Feedback loop** — let agents rate suggested responses to improve quality over time
- **Multi-tenant support** — serve multiple organizations from a single deployment
- **Secret management** — move all secrets out of `deploy.sh` into GCP Secret Manager

---

## License

This project is for educational and demonstration purposes.
