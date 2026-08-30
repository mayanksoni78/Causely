# Causely — AI Incident Investigator

Causely is an evidence-driven AI incident investigation platform that correlates code changes, logs, databases, external services, and historical incident evidence to determine probable root causes.

Unlike traditional chatbots, Causely operates on the core principle of **"Evidence first, reasoning second."** Every investigation conclusion is rigorously backed by retrieved evidence rather than unsupported AI guessing.

## Why Causely?

Modern software architectures are highly distributed. When an incident occurs, engineers spend hours manually piecing together evidence from GitHub, application logs, production databases, and external platforms (like Stripe or Auth0). Causely automates this correlation phase through an intelligent retrieval pipeline and a deterministic AI reasoning graph.

## Key Capabilities

- **Automated Evidence Retrieval**: Pulls context from logs, databases, source code, and third-party APIs.
- **Explainable Reasoning**: Traces the exact logic path from raw evidence to final hypothesis.
- **Cross-Source Correlation**: Reconstructs the timeline of events across entirely disparate systems.
- **Tenant Isolation**: Secure, multi-tenant architecture designed to strictly enforce project-level authorization.

## Architecture

```mermaid
flowchart TB
    U[User]

    subgraph FE[Frontend]
        R[React + TypeScript + Vite]
        A[Auth Provider]
        P[Project Context]
        UI[Dashboard / Incidents / Sources / Settings]
    end

    subgraph BE[FastAPI Backend]
        API[REST API]
        AUTH[JWT + HttpOnly Cookie]
        PROJECT[Project/Tenant Authorization]
        SOURCE[Source Management]
        INCIDENT[Incident API]
        SETTINGS[LLM Settings]
    end

    subgraph DATA[Data Layer]
        DB[(Supabase PostgreSQL)]
        ORM[SQLAlchemy]
        MIG[Alembic]
        VECTOR[(pgvector)]
    end

    subgraph RETRIEVAL[Evidence Retrieval]
        CHUNK[Chunking]
        EMBED[Embeddings]
        BM25[BM25 Search]
        VECTORSEARCH[Vector Search]
        FUSION[Reciprocal Rank Fusion]
        RERANK[CrossEncoder Reranking]
    end

    subgraph PIPELINE[Investigation Pipeline]
        GRAPH[LangGraph]
        TIMELINE[Timeline Reconstruction]
        HYPOTHESIS[Hypothesis Generation]
        VERIFY[Evidence Verification]
        CONF[Confidence Scoring]
        REPORT[Final Investigation Report]
    end

    subgraph SOURCES[Evidence Sources]
        GH[GitHub]
        GHA[GitHub Actions]
        LOGS[Loki / Static Logs]
        PG[External PostgreSQL]
        MONGO[MongoDB]
        EXT[Stripe / Razorpay / Auth0 / Generic REST]
    end

    subgraph LLM[LLM]
        GEMINI[Gemini]
        OLLAMA[Optional Ollama]
    end

    U --> R
    R --> API
    A --> AUTH
    P --> PROJECT

    API --> AUTH
    API --> PROJECT
    API --> SOURCE
    API --> INCIDENT
    API --> SETTINGS

    API --> ORM
    ORM --> DB
    MIG --> DB

    SOURCE --> SOURCES
    
    %% Static Logs are indexed
    SOURCES -- Static Logs --> CHUNK
    
    %% Other connectors are fetched on demand
    SOURCES -- APIs & DBs --> FETCH[Dynamic Fetch]

    CHUNK --> EMBED
    CHUNK --> BM25
    EMBED --> VECTORSEARCH
    BM25 --> FUSION
    VECTORSEARCH --> FUSION
    
    %% Fused indexed chunks and dynamically fetched chunks merge here
    FUSION --> RERANK
    FETCH --> RERANK

    INCIDENT --> GRAPH
    RERANK --> GRAPH

    GRAPH --> TIMELINE
    GRAPH --> HYPOTHESIS
    HYPOTHESIS --> VERIFY
    VERIFY --> CONF
    CONF --> REPORT

    GRAPH --> GEMINI
    GRAPH --> OLLAMA

    VECTORSEARCH --> VECTOR
    ORM --> VECTOR
```

## End-to-End Investigation Flow

```mermaid
flowchart LR
    I[User Reports Incident]
    S[Select Project]
    P[Plan Sources]
    R[Retrieve Evidence]
    B[BM25]
    V[Vector Search]
    F[Rank Fusion]
    C[CrossEncoder Reranking]
    T[Timeline Reconstruction]
    H[Generate Hypotheses]
    X[Verify Against Evidence]
    SC[Confidence Scoring]
    O[Explainable Root Cause Report]

    I --> S
    S --> P
    P --> R
    R --> B
    R --> V
    B --> F
    V --> F
    F --> C
    C --> T
    T --> H
    H --> X
    X --> SC
    SC --> O
```

## Authentication Architecture

Causely uses a robust HTTP-only cookie authentication pattern.
1. The frontend POSTs credentials to the FastAPI `/auth/login` endpoint.
2. The backend hashes passwords using `bcrypt` and validates them against the database.
3. Upon success, a JWT is generated and returned securely via an `HttpOnly` cookie.
4. Subsequent authenticated requests automatically include the cookie. Using `HttpOnly` prevents client-side JavaScript from directly reading the authentication cookie, and therefore significantly reduces the impact of token theft through XSS.
5. A backend dependency (`get_current_user`) decodes the JWT and verifies the user's active session.

## Multi-Tenant / Multi-Project Architecture

Data is strictly segmented to ensure absolute privacy between organizations.
- **Tenant Isolation**: Every user belongs to a Tenant.
- **Project Isolation**: Every Tenant can have multiple Projects.
- **Project Membership**: Users are explicitly granted roles within Projects.
- **Project-Scoped Operations**: Requests affecting sources or incidents require an `X-Project-ID` header. The backend explicitly verifies `str(project.id) == project_id` and ensures the current user holds active project membership.

## Database Architecture

The **Causely Application Database** operates purely on **Supabase PostgreSQL**.
- **Supabase**: Configured via the `DATABASE_URL` environment variable.
- **SQLAlchemy**: Used as the primary ORM for executing database transactions.
- **Alembic**: Used for database schema migrations.
- **pgvector**: Used on the Supabase instance to store and query dense vector embeddings.

*Note: The application database is strictly Supabase. Any local PostgreSQL instances provided via Docker are entirely optional and meant for external connection testing, not for hosting the core application state.*

## Source Connectors

Causely connects to various external systems to pull in incident evidence.

**Code & Version Control**
- GitHub
- GitHub Actions

**Logs**
- Grafana Loki
- Static Logs

**Databases**
- PostgreSQL (Strictly read-only access enforced)
- MongoDB

**External Services**
- Stripe
- Razorpay
- Auth0
- Generic REST API

When a user configures a source, the backend validates the connection, encrypts sensitive credentials using a symmetric `ENCRYPTION_KEY`, and persists the metadata to Supabase. At investigation time, the connectors retrieve context without exposing credentials back to the user.

## Credential Security

All sensitive source credentials (e.g., GitHub tokens, database connection strings, Stripe API keys) are strictly protected:
- Validated and encrypted before database insertion using a server-side `ENCRYPTION_KEY`.
- Never logged in plaintext.
- Never returned in `GET /sources` lists. The frontend only receives safe metadata and status identifiers.
- External PostgreSQL connections enforce a read-only configuration check; the backend rejects the registration if the connector's permission report `is_read_only` flag is false.

## RAG / Retrieval Architecture

Before the LLM starts reasoning, Causely surfaces the most relevant information:
1. Static log sources are ingested, chunked, and saved into `pgvector` prior to investigation.
2. During an investigation, dynamic connectors (e.g., GitHub, PostgreSQL, Stripe) fetch live evidence on-demand based on the investigation state.
3. Simultaneously, relevant indexed chunks are pulled via both **Vector Search** (semantic) and **BM25 Search** (keyword matching).
4. **Reciprocal Rank Fusion** (RRF) merges the indexed vector and keyword results.
5. **CrossEncoder Reranking** evaluates both the fused indexed evidence and the dynamically fetched evidence together, ordering them by exact contextual relevance before passing to the LLM.

## AI Investigation Pipeline

Causely uses **LangGraph** to model the incident investigation as a deterministic state machine:
- **Intake**: Extracts incident properties (timeframe, service, error signature).
- **Source Planning**: Determines which connected sources contain relevant evidence.
- **Retrieval & Reranking**: Executes the RAG pipeline.
- **Timeline**: Reconstructs a chronological sequence of events based on retrieved logs and code changes.
- **Hypothesis Generation**: Proposes logical explanations for the failure.
- **Evidence Verification**: Validates each hypothesis against the actual retrieved data.
- **Confidence Scoring**: Assigns a final confidence score based on the strength of verified evidence.
- **Synthesis**: Compiles an explainable final report.

## LLM Configuration

The application dynamically supports tenant-specific models:
- **Google Gemini**: Standard support includes current non-preview generation models (e.g., `gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-2.5-flash`). Deprecated models are actively rejected.
- **Ollama**: Supported as a local/offline fallback alternative (e.g., `llama3`, `mistral`).
Settings are configured on a per-workspace basis and stored in `TenantSettings`.

## Tech Stack

| Layer | Technology | Role |
|-------|------------|------|
| **Frontend** | React, TypeScript, Vite | User Interface |
| **Backend** | FastAPI, Python 3.11+ | REST API & Application Logic |
| **Database** | Supabase PostgreSQL, pgvector | Core Application State & Embeddings |
| **ORM** | SQLAlchemy | Database Object Mapping |
| **Migrations** | Alembic | Schema Version Control |
| **Authentication**| JWT, HttpOnly Cookies, bcrypt | Security & Session Management |
| **AI Workflow** | LangGraph | State Machine Orchestration |
| **LLM** | Google Gemini / Ollama | Generative Reasoning |
| **Retrieval** | BM25, pgvector, CrossEncoder | Hybrid Evidence Search |

## Repository Structure

```text
Causely/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── lib/
│   │   └── pages/
│   ├── package.json
│   ├── vite.config.ts
│   └── .env.local
│
├── backend/
│   ├── src/
│   │   ├── api/
│   │   ├── connectors/
│   │   ├── core/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── pipeline/
│   │   ├── retrieval/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
│
├── docker-compose.yml
└── README.md
```

## Local Development Requirements

- **Python**: 3.11 or higher
- **Node.js**: v18 or higher
- **Supabase**: Active PostgreSQL cloud project (or self-hosted equivalent)
- **Git**

## Environment Configuration

Copy the example environment files and replace placeholders with your actual secrets.

### Backend (`backend/.env`)
```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@aws-0-ap-southeast-2.pooler.supabase.com:5432/postgres
JWT_SECRET=your_secure_random_string_here
JWT_ALGORITHM=HS256
GEMINI_API_KEY=your_gemini_api_key_here
ENCRYPTION_KEY=your_base64_encoded_32_byte_key_here
FRONTEND_URL=http://localhost:5173
```

### Frontend (`frontend/.env.local`)
```env
VITE_API_BASE_URL=http://localhost:8000
```
*(Do NOT commit your `.env` files or expose `.env` variables to version control!)*

## Database Setup

Initialize your Supabase database schema using Alembic migrations:

```bash
cd backend
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

alembic upgrade head
```

## Running the Backend

Open Terminal 1:
```bash
cd backend
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate
# Activate virtual environment (Linux/macOS)
source .venv/bin/activate

# Install dependencies using pip (pyproject.toml compatibility)
pip install -e .

# Run the FastAPI server
uvicorn src.main:app --reload --port 8000
```
Backend will be available at `http://localhost:8000`.

## Running the Frontend

Open Terminal 2:
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173`.

## Running Optional Docker Services

If you wish to host an Ollama model locally or spin up a throwaway PostgreSQL database to act as an external test source (NOT for the application database itself), use the provided docker-compose configuration:

```bash
docker-compose up -d
```

## First Investigation

1. Navigate to `http://localhost:5173` and create an account.
2. Log in and select or create a Project workspace.
3. Head to the **Connect Sources** page and supply a read-only database connection or a GitHub Personal Access Token.
4. Click **Test Connection** to verify backend connectivity.
5. Create a new Incident from the dashboard and describe the symptoms.
6. Start the investigation to observe the LangGraph pipeline retrieving chunks, reconstructing a timeline, validating hypotheses, and rendering an explainable root cause report!

## Security Architecture

Causely enforces defense-in-depth across the entire stack:
- **Authentication**: JWTs are stored strictly in `HttpOnly` cookies to thwart Cross-Site Scripting (XSS).
- **Passwords**: Hashed with robust `bcrypt` salt rounds.
- **Authorization**: API routes rigorously enforce multi-tenant isolation. Users cannot list, edit, or delete evidence belonging to unassociated projects.
- **Data Protection**: Third-party source credentials (e.g., Stripe API keys, DB connection strings) are systematically encrypted at rest via `cryptography.fernet`.
- **Least Privilege**: External PostgreSQL integrations enforce read-only `is_read_only` verification. Connections demanding write capabilities are preemptively denied.

## API Overview

| Area | Example Endpoints |
|------|------------------|
| **Auth** | `/auth/signup`, `/auth/login`, `/auth/me`, `/auth/logout` |
| **Projects** | `/projects`, `/projects/{id}`, `/projects/{id}/members` |
| **Incidents** | `/incidents`, `/incidents/{id}`, `/incidents/{id}/trace` |
| **Sources** | `/sources`, `/sources/{id}`, `/sources/{id}/test`, `/sources/github` |
| **Settings** | `/settings`, `/settings/test-llm`, `/settings/clear-data` |
| **Approvals** | `/approvals`, `/approvals/{id}/approve`, `/approvals/{id}/execute` |

## Testing

Backend test execution is handled via `pytest`:
```bash
cd backend
pytest
```
*Note: Depending on local environments, some duplicate test modules may require path resolution flags or virtual environment exclusions.*

Frontend compilation checking:
```bash
cd frontend
npm run build
```

## Known Limitations

- **Background Tasks**: Currently, the investigation pipeline executes via FastAPI `BackgroundTasks`, rendering it process-local. It does not yet utilize a durable queue system (like Celery/Redis).
- **Static Log Rollbacks**: Exception handling safely rolls back `SQLAlchemy` source creation if chunking/indexing fails to prevent orphan resources, but massive log file ingestion may timeout typical HTTP requests.
- **Limited Connectors**: While the architecture supports arbitrary sources, the pipeline currently only actively references the explicitly implemented connectors.
- **Test File Collision**: A known duplicate `test_health.py` file in the backend root may cause local Pytest collection warnings depending on your test discovery config.

## Future Improvements

*The following features are conceptually planned but **not yet implemented** in the current branch:*
- Migration to a distributed background worker queue (e.g., Celery or Temporal) for resilient long-running investigations.
- Enhanced telemetry, automated evaluation scores, and observability dashboards.
- Formalized deployments for Kubernetes and ECS.
- Extended third-party connector support natively integrated into the LangGraph workflow.

## Contributing

Please ensure you adhere to the project's coding standards. All new source connectors must map seamlessly through the frontend API helpers to discrete FastApi backend routes, and strictly respect `project_id` scoping boundaries.

## License

This project is licensed under the MIT License.