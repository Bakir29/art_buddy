# Art Buddy — Agentic Coding Guidelines

This document covers the complete setup, tooling, and development conventions for the Art Buddy project. It is intended as the single source of truth for any developer or AI agent working on this codebase.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Structure](#2-repository-structure)
3. [Environment Variables](#3-environment-variables)
4. [Docker & Docker Compose](#4-docker--docker-compose)
5. [PostgreSQL + pgvector](#5-postgresql--pgvector)
6. [Backend — FastAPI](#6-backend--fastapi)
7. [Alembic — Database Migrations](#7-alembic--database-migrations)
8. [Frontend — React + Vite + TypeScript](#8-frontend--react--vite--typescript)
9. [n8n — Workflow Automation](#9-n8n--workflow-automation)
10. [MCP — Model Context Protocol](#10-mcp--model-context-protocol)
11. [RAG — Retrieval Augmented Generation](#11-rag--retrieval-augmented-generation)
12. [OpenAI Integration](#12-openai-integration)
13. [Deployment — Render](#13-deployment--render)
14. [Agentic Coding Conventions](#14-agentic-coding-conventions)

---

## 1. Project Overview

Art Buddy is an AI-powered art learning platform. Users complete lessons, take quizzes, and receive personalised feedback. The system uses:

- A **FastAPI** backend with **PostgreSQL** (+ **pgvector** for semantic search)
- A **React/TypeScript** frontend built with **Vite**
- A **RAG** pipeline for intelligent lesson content retrieval
- An **MCP** server for tool-based AI agent interactions
- **n8n** (cloud) for event-driven email/notification workflows
- **Render** for hosting both the backend (Docker) and frontend (static)

---

## 2. Repository Structure

```
art_buddy/
├── backend/
│   ├── app/
│   │   ├── auth/            # JWT authentication
│   │   ├── controllers/     # FastAPI route handlers
│   │   ├── entities/        # SQLAlchemy ORM models
│   │   ├── repositories/    # DB query layer
│   │   ├── services/        # Business logic
│   │   ├── mcp/             # MCP server + tool registry
│   │   ├── rag/             # Embeddings, ingestion, RAG service
│   │   ├── workflows/       # n8n event system + workflow manager
│   │   ├── config.py        # Pydantic settings (reads from .env)
│   │   └── database.py      # SQLAlchemy engine + session factory
│   ├── alembic/             # DB migration scripts
│   ├── n8n/workflows/       # n8n workflow JSON files (webhook-only)
│   ├── tests/
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── main.py              # FastAPI app entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── api/             # Axios API client (api.ts)
│   │   └── stores/          # Zustand state
│   ├── package.json
│   └── vite.config.ts
├── n8n-workflows/           # Alternative/reference workflow JSONs
├── docs/
├── render.yaml              # Render IaC config
└── start.ps1                # Local dev launch script
```

---

## 3. Environment Variables

### Backend (`backend/.env`)

Copy `backend/.env.example` and fill in values:

```env
# Database
DATABASE_URL=postgresql://art_buddy:password@localhost:5433/art_buddy_db
POSTGRES_USER=art_buddy
POSTGRES_PASSWORD=password
POSTGRES_DB=art_buddy_db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=sk-...

# n8n
N8N_WEBHOOK_URL=https://bakiribu.app.n8n.cloud/webhook

# Frontend origin (CORS)
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

> **Important:** `N8N_WEBHOOK_URL` must point to the live n8n cloud URL in production. The default `http://localhost:5678/webhook` only works when running n8n locally via Docker.

### Frontend (`frontend/.env` or `frontend/.env.local`)

```env
VITE_API_URL=http://localhost:8000
```

In production this is set in `render.yaml` to `https://art-buddy-backend.onrender.com`.

---

## 4. Docker & Docker Compose

Docker is used to run the full local stack: **PostgreSQL**, the **FastAPI backend**, and (optionally) **n8n**.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and **running**
- Docker Compose v2+

### Start the local stack

```powershell
cd backend
docker compose up --build
```

This starts:

| Service   | Port   | Description                        |
|-----------|--------|------------------------------------|
| postgres  | 5433   | PostgreSQL 15 + pgvector extension |
| backend   | 8000   | FastAPI app (hot-reload)           |
| n8n       | 5678   | n8n workflow engine (optional)     |

### Key Docker rules

- **Never** run `docker compose up` without Docker Desktop open — it will silently fail.
- The `postgres` service uses the `pgvector/pgvector:pg15` image, which includes the `vector` extension. Do **not** swap for a plain `postgres` image or vector operations will break.
- Volume `postgres_data` persists the database between restarts. To reset: `docker compose down -v`.
- The `init-db.sql` file runs only on **first** container creation. To re-run it, destroy the volume first.

### Dockerfile (backend)

The backend Dockerfile builds a production-ready image:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 5. PostgreSQL + pgvector

### Why pgvector?

The RAG system stores **OpenAI embeddings** (1536-dimensional vectors) directly in PostgreSQL using the `pgvector` extension. This eliminates the need for a separate vector database (e.g. Pinecone, Weaviate).

### Extension setup

The `init-db.sql` script enables the extension on first boot:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Vector columns in models

```python
from pgvector.sqlalchemy import Vector

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    embedding = Column(Vector(1536))
```

### Similarity search

```python
# Cosine similarity — lower distance = more similar
results = db.query(KnowledgeChunk)\
    .order_by(KnowledgeChunk.embedding.cosine_distance(query_vector))\
    .limit(5)\
    .all()
```

### Local connection

```
Host:     localhost
Port:     5433   ← mapped from container's 5432
Database: art_buddy_db
User:     art_buddy
Password: password
```

Use any PostgreSQL client (TablePlus, pgAdmin, DBeaver) with these credentials.

---

## 6. Backend — FastAPI

### Stack

| Library             | Purpose                              |
|---------------------|--------------------------------------|
| `fastapi`           | Web framework + automatic OpenAPI    |
| `uvicorn`           | ASGI server                          |
| `sqlalchemy`        | ORM                                  |
| `pydantic`          | Request/response validation          |
| `pydantic-settings` | Settings from `.env`                 |
| `python-jose`       | JWT tokens                           |
| `passlib[bcrypt]`   | Password hashing                     |
| `httpx`             | Async HTTP client (n8n calls)        |
| `alembic`           | DB migrations                        |
| `psycopg2-binary`   | PostgreSQL driver                    |

### Entry point

```
backend/main.py  →  creates FastAPI app, registers all routers, starts CORS
```

### Run locally (without Docker)

```powershell
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Requires PostgreSQL already running (port 5433).

### API docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Background tasks pattern

All workflow handlers use FastAPI `BackgroundTasks`. **Always** capture user data (email, name) from `current_user` **before** passing to the background task, because the DB session may be closed by the time the task runs:

```python
@router.post("/simulate/daily-reminder")
async def simulate_daily_reminder(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_email = current_user.email   # capture BEFORE background task
    user_name = current_user.name

    async def handle():
        await workflow_manager.handle_daily_reminder(
            user_email=user_email,
            user_name=user_name,
        )
    background_tasks.add_task(handle)
    return {"status": "queued"}
```

---

## 7. Alembic — Database Migrations

### Setup

```powershell
cd backend
alembic init alembic   # already done — do not re-run
```

### Create a new migration

```powershell
alembic revision --autogenerate -m "describe your change"
```

### Apply migrations

```powershell
alembic upgrade head
```

### Rollback

```powershell
alembic downgrade -1
```

### Rules

- Never modify the database schema directly in SQL while the app is running.
- Always create a migration after changing a SQLAlchemy model.
- The `DATABASE_URL` in `.env` must be set before running any alembic command.
- On Render, migrations run automatically as part of the Docker startup — check `main.py` for the `alembic upgrade head` invocation pattern if used.

---

## 8. Frontend — React + Vite + TypeScript

### Stack

| Library                  | Purpose                              |
|--------------------------|--------------------------------------|
| React 18                 | UI framework                         |
| TypeScript               | Type safety                          |
| Vite                     | Build tool + dev server              |
| React Router v6          | Client-side routing                  |
| Zustand                  | Global state management              |
| TanStack Query v5        | Server state / data fetching         |
| Axios                    | HTTP client                          |
| React Hook Form + Zod    | Forms + schema validation            |
| Tailwind CSS             | Utility-first styling                |
| Framer Motion            | Animations                           |
| Recharts                 | Data visualisation                   |
| react-hot-toast          | Toast notifications                  |

### Dev server

```powershell
cd frontend
npm install
npm run dev        # starts on http://localhost:3000
```

### Build for production

```powershell
npm run build      # outputs to frontend/dist/
```

### API client

All backend calls go through `frontend/src/api/api.ts`. When adding a new endpoint:

1. Add a typed function in `api.ts`
2. Use TanStack Query (`useQuery` / `useMutation`) in the component
3. Never call `axios` directly from a component

### Environment

The backend URL is read from `VITE_API_URL`. In development this defaults to `http://localhost:8000`. In production it is injected by Render via `render.yaml`.

---

## 9. n8n — Workflow Automation

### What it does

n8n listens for webhook events from the backend and sends emails (via Gmail) when specific user events occur.

### Workflow events

| Event                     | Webhook path          | Trigger                          |
|---------------------------|-----------------------|----------------------------------|
| Daily practice reminder   | `/daily-practice`     | Simulate or scheduled cron       |
| Lesson completion         | `/lesson-complete`    | User completes a lesson          |
| Low performance           | `/low-performance`    | User scores below threshold      |
| Weekly progress summary   | `/weekly-summary`     | Simulate or Monday 9am cron      |
| User engagement tracker   | `/engagement`         | Inactivity / streak events       |

### Workflow JSON files

Workflow definitions live in `backend/n8n/workflows/`. Each file contains **only the Webhook trigger node** — you connect additional nodes (e.g., Gmail Send Email) manually in the n8n UI after importing.

**Format of each file:**
```json
{
  "id": "art-buddy-wf-XXX",
  "name": "Workflow Name",
  "nodes": [
    {
      "name": "Webhook Node",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 2,
      "parameters": {
        "httpMethod": "POST",
        "path": "<webhook-path>",
        "responseMode": "lastNode",
        "options": {}
      }
    }
  ],
  "connections": {},
  "active": true,
  "settings": { "executionOrder": "v1" },
  "tags": [{ "name": "art-buddy" }]
}
```

### Importing a workflow into n8n cloud

1. Go to `https://bakiribu.app.n8n.cloud`
2. **Workflows** → **Import from file** → select the JSON
3. After import, add your **Gmail Send Email** node and connect it to the webhook
4. Set the workflow to **Active** (toggle in top-right)

### Gmail node setup (n8n)

- Node type: `n8n-nodes-base.gmail` (typeVersion 2)
- Credential: OAuth2 with your Google account
- In the **Send To** field reference: `{{ $json.body.data.user_email }}` or the field your backend sends

### Backend → n8n flow

1. Backend endpoint fires `event_system.py → _trigger_workflow()`
2. `_trigger_workflow()` sends an HTTP POST to `{N8N_WEBHOOK_URL}/{path}`
3. n8n receives the webhook and executes the workflow
4. Gmail node sends the email

### Local n8n (Docker)

When running locally with Docker Compose, n8n is available at `http://localhost:5678`.
- Username: `admin`
- Password: `password`
- Set `N8N_WEBHOOK_URL=http://localhost:5678/webhook` in `backend/.env`

### Production n8n (Cloud)

- URL: `https://bakiribu.app.n8n.cloud`
- Webhook base: `https://bakiribu.app.n8n.cloud/webhook`
- Set `N8N_WEBHOOK_URL=https://bakiribu.app.n8n.cloud/webhook` in Render environment variables

### Testing a webhook directly

```powershell
Invoke-RestMethod -Method POST `
  -Uri "https://bakiribu.app.n8n.cloud/webhook/daily-practice" `
  -ContentType "application/json" `
  -Body '{"event_type":"practice.daily_due","data":{"user_email":"test@example.com","user_name":"Test"}}'
```

Expected response: `"Workflow was started"`

---

## 10. MCP — Model Context Protocol

The backend exposes an **MCP server** (`backend/app/mcp/`) that allows AI agents to interact with the Art Buddy system using structured tools.

### Files

| File               | Purpose                                      |
|--------------------|----------------------------------------------|
| `server.py`        | MCP server entry point, registers tools      |
| `tool_registry.py` | Defines available tools and their schemas    |
| `schemas.py`       | Pydantic schemas for tool inputs/outputs     |

### Adding a new MCP tool

1. Define the tool schema in `schemas.py`
2. Register it in `tool_registry.py` with `name`, `description`, and `input_schema`
3. Implement the handler function and wire it in `server.py`
4. Test with `backend/test_mcp_system.py` or `test_mcp_simple.py`

### MCP conventions

- Tool names use `snake_case`
- All inputs and outputs are typed with Pydantic models
- Tools should be **idempotent** where possible
- Never expose raw SQL through MCP tools — always go through the repository layer

---

## 11. RAG — Retrieval Augmented Generation

The RAG pipeline powers intelligent lesson content retrieval and AI-assisted feedback.

### Files

| File                  | Purpose                                          |
|-----------------------|--------------------------------------------------|
| `embedding_service.py`| Generates OpenAI embeddings for text chunks      |
| `ingestion.py`        | Splits documents into chunks and stores them     |
| `knowledge_manager.py`| Manages the knowledge base (add/delete/update)   |
| `rag_service.py`      | Retrieves relevant chunks for a given query      |

### How it works

1. **Ingestion**: Lesson content is split into chunks → each chunk is embedded via `text-embedding-ada-002` → stored in the `knowledge_chunks` table with a `vector(1536)` column.
2. **Retrieval**: A user query is embedded → cosine similarity search against stored embeddings → top-k chunks returned.
3. **Generation**: Retrieved chunks are injected as context into an OpenAI prompt → response returned to user.

### Seeding the knowledge base

```powershell
cd backend
python setup_knowledge_base.py
```

### Key rules

- Never query the vector DB without a valid OpenAI API key — embeddings will fail silently.
- The embedding model is `text-embedding-ada-002` (1536 dimensions). Do not change this without migrating all existing embeddings.
- Chunk size and overlap are configured in `ingestion.py`. Changing these requires re-ingesting all content.

---

## 12. OpenAI Integration

OpenAI is used for:
- **Embeddings**: `text-embedding-ada-002` for RAG
- **Completions**: `gpt-4` or `gpt-3.5-turbo` for AI feedback

### Configuration

Set `OPENAI_API_KEY` in `backend/.env` (locally) and in the Render dashboard (production). The key is **never** committed to git.

### Client

```python
from app.config import get_openai_client

client = get_openai_client()
response = client.embeddings.create(
    model="text-embedding-ada-002",
    input="your text here"
)
```

### Development without a key

If `OPENAI_API_KEY` is not set, the system will initialise with a fake key. Embedding and completion calls will fail — use mock data or seed the DB with pre-generated embeddings for local dev.

---

## 13. Deployment — Render

### Infrastructure as Code

`render.yaml` at the repo root defines the full deployment:

- **art-buddy-db**: PostgreSQL 15 (free tier)
- **art-buddy-backend**: Docker web service (builds from `backend/Dockerfile`)
- **art-buddy-frontend**: Static site (Vite build from `frontend/`)

### Backend deployment

Render builds the Docker image and runs the container. Key env vars set in `render.yaml`:

| Variable                  | Source               |
|---------------------------|----------------------|
| `DATABASE_URL`            | Auto from DB service |
| `SECRET_KEY`              | Auto-generated       |
| `OPENAI_API_KEY`          | Set manually         |
| `N8N_WEBHOOK_URL`         | `render.yaml` value  |
| `FRONTEND_URL`            | `render.yaml` value  |

### Frontend deployment

Render runs `npm install && npm run build` and serves `frontend/dist/` as a static site. The `/*` rewrite rule ensures React Router works correctly.

### Deploying changes

1. `git push origin main` — Render auto-deploys on push
2. Check **Events** tab in Render dashboard to confirm the deploy completed
3. Check **Logs** tab for runtime errors

### Manual deploy

If an env var was changed in the Render dashboard, trigger a manual deploy:
**Render → art-buddy-backend → Manual Deploy → Deploy latest commit**

### Render `postgres://` fix

Render provides `DATABASE_URL` starting with `postgres://` but SQLAlchemy requires `postgresql://`. This is handled automatically in `config.py`:

```python
if v.startswith('postgres://'):
    return v.replace('postgres://', 'postgresql://', 1)
```

---

## 14. Agentic Coding Conventions

These rules apply to both human developers and AI agents working on this codebase.

### General

- **Read before editing**: Always inspect the target file before making changes. Never assume structure.
- **Minimal footprint**: Only change what is necessary. Avoid touching unrelated files.
- **No guessing env vars**: If an environment variable is needed, check `config.py` and `.env.example` first.
- **Background task safety**: When using FastAPI `BackgroundTasks`, always extract any DB-loaded data (user email, IDs) from the current request context **before** scheduling the task.

### Database

- All schema changes go through Alembic — never raw `ALTER TABLE`.
- Use the repository pattern — controllers should not contain raw SQLAlchemy queries.
- Close DB sessions explicitly or use `with` context managers. Never rely on garbage collection.

### n8n Workflows

- Webhook JSON files in `backend/n8n/workflows/` contain **only the Webhook node**. Additional processing nodes are added manually in the n8n UI.
- All JSON files must be valid UTF-8 **without BOM**. Use `System.Text.UTF8Encoding($false)` when writing from PowerShell.
- After modifying workflow JSON files, commit them: `git add backend/n8n/workflows/ && git commit`.
- Always test webhooks directly with `Invoke-RestMethod` before debugging the backend.

### Frontend

- All API calls go through `src/api/api.ts` — never call `axios` directly from components.
- Use TanStack Query for all server state; use Zustand only for client-side global UI state.
- Toast messages should reflect the actual operation result, not a hardcoded "mock mode" string.

### Git

- Commit messages follow the pattern: `type: short description`
  - `fix:` bug fixes
  - `feat:` new features
  - `refactor:` code restructuring without behaviour change
  - `docs:` documentation only
- Never commit secrets, API keys, or `.env` files.
- `.env` is in `.gitignore` — use `.env.example` to document required variables.

### Debugging checklist

When a workflow button click does not trigger n8n:

1. Check Render **Logs** for `Workflow triggered successfully` or an error
2. Confirm `N8N_WEBHOOK_URL` in Render **Environment** tab is the cloud URL, not `localhost`
3. Confirm a deploy happened **after** the env var was set (check **Events** tab)
4. Test the webhook directly with `Invoke-RestMethod` to isolate n8n vs backend
5. Check n8n **Executions** tab for the specific workflow — is it Active?

### Testing

```powershell
cd backend
pytest                          # run all tests
pytest tests/test_rag_system.py # run specific test file
```

Key test files:
- `test_mcp_system.py` — MCP tool integration
- `test_rag_system.py` — RAG retrieval pipeline
- `test_login.py` — Auth flow
- `test_quiz_endpoint.py` — Quiz submission
