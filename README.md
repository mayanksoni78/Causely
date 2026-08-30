# Causely — AI Incident Investigator

Causely is an evidence-driven AI incident investigation platform that helps developers find the root cause of software problems using code, logs, databases, external services, and AI reasoning.

When an application fails, developers normally have to search through GitHub code, logs, databases, recent commits, and external services manually. Causely brings these sources together and uses an AI investigation pipeline to find the most likely root cause.

Causely is **not simply a chatbot**.

User reports incident &rarr; Causely selects useful sources &rarr; Retrieves evidence &rarr; Searches code/logs/data &rarr; Ranks relevant evidence &rarr; Generates hypotheses &rarr; Verifies hypotheses &rarr; Calculates confidence &rarr; Produces an explainable investigation result

---

## Key Features

- **AI-powered incident investigation**: Automate root cause analysis with rigorous hypothesis testing.
- **LangGraph investigation workflow**: Multi-agent reasoning pipeline for evidence verification.
- **RAG-based evidence retrieval**: Connect your infrastructure to an intelligent index.
- **BM25 + Vector Search**: Combines exact keyword matches with semantic understanding.
- **Reciprocal Rank Fusion**: Ranks evidence across multiple disparate sources using CrossEncoder reranking.
- **Timeline reconstruction**: Automatically builds a chronology of the incident.
- **Multi-hypothesis reasoning**: Explores multiple causes and verifies each one against the evidence.
- **Confidence scoring**: transparently grades conclusions based on corroboration, recency, and retrieval relevance.
- **Multi-project architecture**: Isolate incidents, evidence, and configuration by project.
- **Tenant/project isolation**: Hardened multi-tenant backend architecture.
- **Secure API key storage**: Bring your own keys securely.
- **Connectors**: GitHub, Static Log Analysis, Grafana Loki, PostgreSQL, MongoDB, Razorpay, Generic REST APIs.

---

## How It Works

Causely uses a structured reasoning pipeline to investigate your issues.

```
          User
           |
     React Frontend
           |
     FastAPI Backend
           |
 Project & Source Selection
           |
      Connectors
           |
   Evidence Retrieval
           |
   BM25 + Vector Search
           |
 Reciprocal Rank Fusion
           |
       Reranking
           |
       LangGraph
           |
Hypothesis & Verification
           |
Root Cause & Confidence
```

---

## Tech Stack

| Part | Technology | Purpose |
|------|------------|---------|
| Frontend | React + Vite + TypeScript | Fast, dense, IDE-like user interface |
| Backend | FastAPI + Python | Asynchronous API and business logic |
| Database | PostgreSQL | Persistent storage for users, projects, and incidents |
| Vector Store| pgvector | Vector embeddings for semantic search |
| ORM | SQLAlchemy | Database access layer |
| Migrations| Alembic | Database schema migrations |
| Authentication | JWT + HttpOnly cookies | Secure session management |
| AI Workflow | LangGraph | Complex, multi-stage investigation logic |
| Embeddings | Sentence Transformers | Local semantic embeddings |
| Keyword Search| BM25 | Exact/keyword text retrieval |
| LLM | Gemini | Core reasoning and hypothesis generation |

---

## Project Structure

- `frontend/src/`: React application.
- `frontend/src/pages/`: Main application pages (Dashboard, Incidents, Settings).
- `frontend/src/components/`: Reusable UI components.
- `frontend/src/lib/`: API, authentication, and shared utilities.
- `backend/src/api/`: FastAPI routes and endpoints.
- `backend/src/connectors/`: Integrations for GitHub, logs, databases, Razorpay, etc.
- `backend/src/retrieval/`: BM25, vector search, embeddings, RAG retrieval.
- `backend/src/pipeline/`: LangGraph incident investigation workflow.
- `backend/src/models/`: Database schema models.
- `backend/src/core/`: Authentication, database connectivity, configuration.
- `backend/alembic/`: Database migrations.

---

## Requirements

Before starting, install:
- Node.js (v18+)
- npm
- Python (v3.11+)
- PostgreSQL (or a Supabase connection string)
- Gemini API Key

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/causely-v2.git
cd causely-v2
```

### 2. Backend Setup

Configure the backend API and database.

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Unix: source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://user:password@localhost/causely
JWT_SECRET=your_super_secret_jwt_string
ENCRYPTION_KEY=your_32_byte_base64_encoded_key_here
GEMINI_API_KEY=your_gemini_api_key_here
FRONTEND_URL=http://localhost:5173
```
*Tip: If using Supabase, get your connection string from the Dashboard > Settings > Database.*

Run the database migrations to set up the schema:
```bash
alembic upgrade head
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend/` directory (optional if backend is on 8000):
```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Running Causely Locally

**Terminal 1 (Backend):**
```bash
cd backend

# On Windows (PowerShell):
.\.venv\Scriptsctivate

# On Mac/Linux:
source .venv/bin/activate

# Start the server:
uvicorn src.main:app --reload
```
The API will be available at `http://localhost:8000`.

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
The application will be available at `http://localhost:5173`.

---

## First Investigation

1. Create a local account and log in.
2. Select your default project from the sidebar.
3. Navigate to **Sources** and connect a data source (e.g., upload a static log file, or connect your GitHub repository).
4. Navigate to **New Incident**.
5. Describe the problem clearly (e.g., "Users cannot complete payment. Getting ERR_BLOCKED_BY_CLIENT on lumberjack.razorpay.com").
6. Click **Start Investigation**.
7. Watch the LangGraph pipeline trace as Causely plans sources, retrieves evidence, reconstructs a timeline, generates hypotheses, and verifies them.
8. Review the final confidence score, verified root cause, and remediation steps!

---

## Projects & Team

Causely features a complete multi-project architecture. A single account can manage multiple isolated projects (e.g., "E-Commerce", "Internal Tools").
Each project has its own:
- Incidents & Evidence
- Connected Sources
- User Roles (Owner, Admin, Member)

This isolation is enforced at the database level to ensure your evidence never bleeds across workspaces.

---

## Security

- **Secure sessions:** Authentication uses secure HttpOnly cookies. No JWTs are stored in LocalStorage.
- **Secure secrets:** Connected API keys and database credentials are encrypted at rest using `ENCRYPTION_KEY`. Secrets are never returned to the frontend.
- **Tenant Isolation:** All endpoints strictly enforce tenant and project isolation.
- **Read-Only Connections:** Causely connectors only query your infrastructure. They are built to be read-only.

---

## Contributing

1. Fork the repository
2. Clone your fork
3. Create a feature branch
4. Make changes
5. Run backend tests (`cd backend && pytest`)
6. Run frontend build (`cd frontend && npm run build`)
7. Create a Pull Request

---

## License

This project is licensed under the MIT License.
