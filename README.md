# Sentinel — Autonomous Market Intelligence Agent

A multi-user SaaS platform that deploys persistent AI agents to continuously monitor financial markets (stocks, ETFs, crypto), build evolving "belief states" about tracked assets, and deliver actionable intelligence through daily briefings, anomaly alerts, and interactive dashboards.

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/sentinel.git
cd sentinel

# 2. Copy environment variables
cp .env.example .env
# Fill in your API keys in .env

# 3. Start everything
docker compose up --build

# 4. Access the app
# Backend API:  http://localhost:8000
# API Docs:     http://localhost:8000/docs
# Frontend:     http://localhost:5173
```

## Architecture

```
Frontend (React + Vite + TypeScript)
        │
        ▼ REST + WebSocket
API Gateway (FastAPI)
        │
   ┌────┼────┐
   ▼    ▼    ▼
Agent  Data  Ingestion
Core   Layer Workers (Celery)
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, shadcn/ui, Recharts |
| Backend | FastAPI, Python 3.12, SQLAlchemy, Celery |
| Database | PostgreSQL 16 + pgvector + TimescaleDB |
| Cache/Queue | Redis |
| AI | Anthropic Claude (analysis), OpenAI (embeddings) |
| Payments | Stripe |

## Project Structure

```
sentinel/
├── backend/          # FastAPI + Celery workers
│   ├── app/
│   │   ├── api/      # Route handlers
│   │   ├── core/     # Agent brain (belief engine, reasoning, RAG)
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── workers/  # Celery tasks (data ingestion)
│   │   └── utils/    # Shared utilities
│   └── tests/
├── frontend/         # React + Vite app
│   └── src/
├── infra/            # Docker, nginx, DB init scripts
└── docker-compose.yml
```

## Development

```bash
# Run backend only
cd backend && uvicorn app.main:app --reload

# Run frontend only
cd frontend && npm run dev

# Run celery worker
cd backend && celery -A app.workers.celery_app worker --loglevel=info

# Run celery beat (scheduler)
cd backend && celery -A app.workers.celery_app beat --loglevel=info

# Run database migrations
cd backend && alembic upgrade head
```

## License

MIT
