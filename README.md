# RAG Knowledge Base

A production-grade AI knowledge base application using Retrieval Augmented Generation (RAG). Upload documents (PDF, Markdown, text), ask questions, and get answers with citations from your documents.

## Architecture

```
User uploads doc → FastAPI → File stored + DB row → Celery task (Redis)
  → Parse (pymupdf) → Chunk (recursive split, 512 chars, 64 overlap)
  → Embed (sentence-transformers, 384-dim) → Store in pgvector

User asks question → Embed query → pgvector cosine similarity (HNSW)
  → Top-k chunks → Assemble prompt (system + context + history)
  → LiteLLM streams from Ollama/OpenAI → SSE to frontend with citations
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend API | Python FastAPI |
| Database | PostgreSQL 16 + pgvector |
| Task Queue | Celery + Redis |
| LLM | LiteLLM (Ollama / OpenAI) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |

### System Components

- **Document Ingestion Service** — Parses uploaded files (PDF via pymupdf, Markdown, plain text) and extracts raw text
- **Chunking Pipeline** — Recursive character splitting with configurable size (512) and overlap (64)
- **Embedding Pipeline** — Generates 384-dimensional normalized vectors using sentence-transformers
- **Vector Search** — pgvector cosine similarity with HNSW indexing for sub-millisecond search
- **Chat Orchestration** — RAG pipeline: embed query → retrieve chunks → build prompt → stream LLM response via SSE
- **LLM Abstraction** — LiteLLM provides a unified interface to Ollama (local) or OpenAI (cloud)

## Quick Start

### Prerequisites

- Docker and Docker Compose

### Run

```bash
# Clone and start
cd rag-knowledge-base
cp .env.example .env
make up

# Pull the LLM model (first time only)
make pull-model
```

Services will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Usage

1. Open http://localhost:3000
2. Create a workspace
3. Upload documents (PDF, Markdown, or text files)
4. Wait for processing to complete (status badge turns green)
5. Start a new chat conversation
6. Ask questions — responses include citations from your documents

## API Endpoints

Base path: `/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| POST | `/workspaces` | Create workspace |
| GET | `/workspaces` | List workspaces |
| GET | `/workspaces/{id}` | Get workspace |
| PATCH | `/workspaces/{id}` | Update workspace |
| DELETE | `/workspaces/{id}` | Delete workspace |
| POST | `/workspaces/{id}/documents` | Upload document (multipart) |
| GET | `/workspaces/{id}/documents` | List documents |
| GET | `/documents/{id}` | Get document detail |
| DELETE | `/documents/{id}` | Delete document |
| POST | `/documents/{id}/reindex` | Reindex document |
| GET | `/documents/{id}/status` | Poll processing status |
| POST | `/workspaces/{id}/search` | Semantic vector search |
| POST | `/workspaces/{id}/conversations` | Create conversation |
| GET | `/workspaces/{id}/conversations` | List conversations |
| GET | `/conversations/{id}/messages` | Get messages |
| POST | `/conversations/{id}/chat` | Chat (SSE streaming) |
| DELETE | `/conversations/{id}` | Delete conversation |

## Project Structure

```
rag-knowledge-base/
├── docker-compose.yml          # 6-service stack
├── Makefile                    # Common operations
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI route handlers
│   │   ├── models/             # SQLAlchemy models (pgvector)
│   │   ├── schemas/            # Pydantic request/response
│   │   ├── services/           # Business logic (RAG pipeline)
│   │   ├── tasks/              # Celery background tasks
│   │   └── middleware/         # Rate limiting, logging
│   ├── alembic/                # Database migrations
│   └── tests/                  # pytest test suite
└── frontend/
    └── src/
        ├── app/                # Next.js App Router pages
        ├── components/         # React components
        ├── hooks/              # Custom hooks (useChat, etc.)
        └── lib/                # API client, SSE parser, utils
```

## Database Schema

- **workspaces** — Project containers
- **documents** — Uploaded files with processing status
- **chunks** — Text segments with pgvector embeddings (HNSW indexed)
- **conversations** — Chat sessions within workspaces
- **messages** — Chat messages with citation metadata

## Configuration

All configuration is via environment variables (see `.env.example`).

### Switch LLM Provider

```bash
# Use Ollama (default, local)
LLM_MODEL=ollama/llama3.2
OLLAMA_API_BASE=http://ollama:11434

# Use OpenAI
LLM_MODEL=openai/gpt-4o-mini
OPENAI_API_KEY=sk-...
```

### Tune RAG Parameters

```bash
CHUNK_SIZE=512          # Characters per chunk
CHUNK_OVERLAP=64        # Overlap between chunks
EMBEDDING_MODEL=all-MiniLM-L6-v2   # sentence-transformers model
EMBEDDING_DIMENSION=384
```

## Development

```bash
make up              # Start all services
make logs            # Tail logs
make test-backend    # Run backend tests
make test-frontend   # Run frontend tests
make lint            # Lint both projects
make db-migrate      # Run migrations
make backend-shell   # Shell into backend container
```

## Testing

```bash
# Backend (pytest + pytest-asyncio)
make test-backend

# Frontend (vitest + testing-library)
make test-frontend

# All tests
make test
```

## CI/CD

GitHub Actions runs on push/PR to main:
- Backend: ruff lint + format, mypy type check, pytest with pgvector service container
- Frontend: ESLint, TypeScript check, vitest

## License

MIT
