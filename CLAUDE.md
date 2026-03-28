# CLAUDE.md — Sentinel Project Context

## What is Sentinel?

Sentinel is a multi-user SaaS platform that deploys persistent AI agents to continuously monitor financial markets (stocks, ETFs, crypto). Each user's agent ingests data from multiple sources, builds an evolving "belief state" (thesis + conviction score) about each tracked asset, and delivers intelligence through daily briefings, anomaly alerts, and an interactive dashboard.

Think: Bloomberg Terminal meets an AI research analyst — for individual investors and small teams.

## Current Status

**Phase 1 (Foundation)** — in progress. Project skeleton is built, Docker Compose runs all services, database schema has `assets` and `price_data` tables (hypertable) created via Alembic migrations. Price poller worker implemented (yfinance, pending network fix). Next step: implement Stack Auth integration, then agent/watchlist models.

Phases 2-6 are not started yet. Placeholder files exist for all future modules with TODO comments indicating which phase they belong to.

## Architecture Overview

```
Frontend (React + Vite + TypeScript + TailwindCSS)
    │
    ▼  REST + WebSocket (proxied via Vite dev server)
API Gateway (FastAPI, Python 3.12)
    │
    ├── Agent Core (belief engine, RAG, reasoning chain, anomaly detection)
    ├── Celery Workers (data ingestion: news, SEC filings, prices, social, crypto)
    └── Data Layer
         ├── PostgreSQL 16 (users, agents, beliefs, briefings, alerts)
         ├── pgvector extension (document embeddings for RAG retrieval)
         ├── TimescaleDB extension (price time-series data)
         └── Redis (Celery broker, caching, WebSocket pub/sub)
```

## Tech Stack

- **Backend**: FastAPI, Python 3.12, SQLAlchemy (async), Alembic, Celery + Celery Beat, Redis
- **Frontend**: React 18, Vite, TypeScript, TailwindCSS, shadcn/ui, Recharts, Lightweight Charts (TradingView), Zustand
- **Database**: PostgreSQL 16 with pgvector and TimescaleDB extensions
- **AI**: Anthropic Claude API (Sonnet) for agent reasoning/analysis, OpenAI text-embedding-3-small for document embeddings
- **Data sources**: Alpha Vantage / yfinance (stock prices), CoinGecko (crypto), NewsAPI / Finnhub (news), Reddit API via PRAW (social sentiment), SEC EDGAR (government filings)
- **Payments**: Stripe (subscription billing)
- **Auth**: Stack Auth (managed SaaS) — handles email/password, sessions, Google OAuth. Backend verifies JWTs via Stack Auth's JWKS endpoint using PyJWT.
- **Deployment**: Docker Compose locally, AWS ECS/EC2 for production (later)

## Repo Structure

```
sentinel/
├── docker-compose.yml              # Dev environment (Postgres, Redis, backend, Celery, frontend)
├── docker-compose.prod.yml         # Production overrides
├── .env.example                    # All environment variables (copy to .env)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py                  # Migration config, imports all models
│   │   ├── script.py.mako          # Migration template
│   │   └── versions/               # Generated migration files
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point, route registration
│   │   ├── config.py               # Settings via pydantic-settings, loads from env
│   │   ├── database.py             # Async SQLAlchemy engine, session factory, Base class
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── asset.py            # ✅ Implemented — Asset (stock/etf/crypto)
│   │   │   ├── price_data.py       # ✅ Implemented — PriceData (TimescaleDB hypertable)
│   │   │   ├── user.py             # Placeholder — Phase 1
│   │   │   ├── agent.py            # Placeholder — Phase 1
│   │   │   ├── belief.py           # Placeholder — Phase 3
│   │   │   ├── article.py          # Placeholder — Phase 2
│   │   │   ├── filing.py           # Placeholder — Phase 2
│   │   │   ├── briefing.py         # Placeholder — Phase 4
│   │   │   └── alert.py            # Placeholder — Phase 3
│   │   ├── schemas/                # Pydantic request/response schemas (empty)
│   │   ├── api/                    # FastAPI route handlers
│   │   │   ├── auth.py             # Placeholder — Phase 1
│   │   │   ├── agents.py           # Placeholder — Phase 1
│   │   │   ├── assets.py           # Placeholder — Phase 1
│   │   │   ├── briefings.py        # Placeholder — Phase 4
│   │   │   ├── alerts.py           # Placeholder — Phase 3
│   │   │   └── billing.py          # Placeholder — Phase 6
│   │   ├── core/                   # Agent brain
│   │   │   ├── belief_engine.py    # Placeholder — Phase 3
│   │   │   ├── memory_manager.py   # Placeholder — Phase 3 (RAG + context assembly)
│   │   │   ├── reasoning_chain.py  # Placeholder — Phase 3 (multi-step LLM pipeline)
│   │   │   ├── anomaly_detector.py # Placeholder — Phase 3
│   │   │   └── briefing_generator.py # Placeholder — Phase 4
│   │   ├── workers/                # Celery background tasks
│   │   │   ├── celery_app.py       # ✅ Implemented — Celery config + beat schedule
│   │   │   ├── price_poller.py     # Stub — Phase 2 (fetches OHLCV data)
│   │   │   ├── news_fetcher.py     # Stub — Phase 2
│   │   │   ├── sec_crawler.py      # Stub — Phase 2
│   │   │   ├── social_scraper.py   # Stub — Phase 2
│   │   │   ├── crypto_monitor.py   # Stub — Phase 2
│   │   │   ├── embedding_pipeline.py # Stub — Phase 2
│   │   │   └── agent_runner.py     # Stub — Phase 3
│   │   ├── services/               # Business logic layer
│   │   │   ├── auth_service.py     # Placeholder — Phase 1
│   │   │   ├── agent_service.py    # Placeholder — Phase 1
│   │   │   ├── asset_service.py    # Placeholder — Phase 1
│   │   │   └── stripe_service.py   # Placeholder — Phase 6
│   │   └── utils/
│   │       ├── llm_client.py       # Placeholder — Phase 3 (Anthropic API wrapper)
│   │       ├── embedding_client.py # Placeholder — Phase 2 (OpenAI embeddings wrapper)
│   │       └── rate_limiter.py     # Placeholder — Phase 6
│   └── tests/
│       └── test_health.py          # ✅ Implemented — smoke test
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts              # ✅ Proxies /api and /ws to backend
│   ├── tailwind.config.js          # ✅ Custom colors: brand, surface, bullish/bearish/neutral
│   ├── postcss.config.js
│   ├── index.html
│   └── src/
│       ├── main.tsx                # React entry point with BrowserRouter
│       ├── App.tsx                 # Route definitions
│       ├── index.css               # Tailwind directives
│       ├── api/
│       │   └── client.ts           # ✅ Implemented — API client with auth header injection
│       ├── pages/
│       │   └── DashboardPage.tsx   # ✅ Implemented — placeholder landing page
│       ├── stores/
│       │   └── authStore.ts        # ✅ Implemented — Zustand auth state
│       ├── components/             # Empty subdirs with .gitkeep (layout, dashboard, agents, etc.)
│       └── utils/                  # Empty
│
└── infra/
    ├── init.sql                    # Enables pgvector, TimescaleDB, uuid-ossp extensions
    └── nginx.conf                  # Production reverse proxy config
```

## Key Concepts

### Belief State (core data model)
The central concept. Each agent maintains a belief state per tracked asset — a structured JSON object containing:
- `conviction` (0.0 to 1.0) — how bullish/bearish the agent is
- `thesis` — natural language summary of the agent's current view
- `key_factors` — weighted factors driving the thesis (each with signal: bullish/bearish/neutral)
- `evidence_refs` — document IDs supporting the thesis
- Belief states are **append-only** — every update creates a new row, giving full history for the belief timeline visualization

### Agent Lifecycle
Agents run on a schedule (Celery Beat). Each run:
1. **Gather context** — load current belief state, query pgvector for relevant recent documents, fetch latest prices
2. **Analyze** — multi-step LLM call (Claude Sonnet) with structured output
3. **Update belief** — merge analysis into existing belief, compute new conviction score, store as new row
4. **Detect anomalies** — compare to previous state, generate alerts if delta exceeds threshold
5. **Generate briefing** — if scheduled, compile changes across all watched assets into a markdown briefing

### Agent Memory
- **Short-term**: latest 24h of articles, 7 days of price data, current belief state (assembled per run)
- **Long-term**: each run produces a summary that gets embedded and stored in pgvector. Future runs retrieve top-k relevant past summaries via cosine similarity.

## SaaS Tiers (Free Tier is MVP target)

| Feature | Free | Pro ($19/mo) | Team ($49/mo) |
|---|---|---|---|
| Active agents | 1 | 5 | 15 |
| Watched assets | 5 | 25 | 100 |
| Briefing frequency | Weekly | Daily | Real-time |
| Alert types | Price only | All | All + custom |
| Belief history | 30 days | 1 year | Unlimited |

**Current focus: Free tier — 1 agent, 1 stock, basic price monitoring.**

## Sprint Plan (175 hours total)

| Phase | Hours | Focus |
|---|---|---|
| 1. Foundation | 40h | Auth, DB schema, API skeleton, React shell |
| 2. Data Ingestion | 30h | 5 source workers + embedding pipeline |
| 3. Agent Core | 35h | Belief engine, RAG, reasoning chain, anomaly detection |
| 4. Briefings | 15h | AI-generated briefings with citations + email |
| 5. Frontend Dashboard | 40h | Full UI with charts, belief timeline, real-time alerts |
| 6. SaaS & Polish | 15h | Stripe billing, tier enforcement, landing page |

## Database Schema (implemented tables)

```sql
-- assets table
assets (
  id VARCHAR PRIMARY KEY,        -- e.g. "AAPL", "BTC-USD"
  symbol VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  asset_type ENUM(stock, etf, crypto) NOT NULL,
  exchange VARCHAR,
  metadata_json JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
)

-- price_data table (TimescaleDB hypertable)
price_data (
  time TIMESTAMPTZ NOT NULL,     -- composite PK with asset_id
  asset_id VARCHAR NOT NULL,
  open FLOAT NOT NULL,
  high FLOAT NOT NULL,
  low FLOAT NOT NULL,
  close FLOAT NOT NULL,
  volume BIGINT DEFAULT 0
)
```

### Future tables (not yet created)
- `users` — id (Stack Auth user ID), email, name, plan_tier (no password_hash — Stack Auth owns passwords)
- `agents` — id, user_id, name, status, config_json
- `agent_watchlist` — agent_id, asset_id
- `belief_states` — agent_id, asset_id, conviction_score, thesis, key_factors (JSONB), evidence_refs
- `articles` — source, url, title, summary, sentiment_score, embedding vector(1536)
- `filings` — asset_id, filing_type, summary, key_metrics (JSONB), embedding vector(1536)
- `price_data` — TimescaleDB hypertable (OHLCV time-series)
- `social_mentions` — asset_id, platform, sentiment, content_summary
- `briefings` — agent_id, content_md, sources (JSONB)
- `alerts` — agent_id, asset_id, alert_type, severity, message
- `subscriptions` — user_id, stripe_customer_id, plan, status

## Code Conventions

### Backend (Python)
- **Async everywhere** — all FastAPI routes and DB queries use async/await
- **SQLAlchemy 2.0 style** — declarative models inheriting from `Base` in `database.py`
- **Pydantic for validation** — request/response schemas in `schemas/` directory
- **Business logic in services** — routes call services, services call models/external APIs
- **Celery for background work** — all data ingestion and agent runs are Celery tasks
- **Alembic for migrations** — never modify the DB schema manually; always create a migration
- **Settings via pydantic-settings** — all config loaded from env vars through `app/config.py`

### Frontend (TypeScript)
- **Functional components only** — no class components
- **Zustand for state** — lightweight stores in `stores/` directory
- **API client** — all backend calls go through `api/client.ts` which handles auth headers
- **TailwindCSS** — utility classes, no CSS modules or styled-components
- **Path aliases** — `@/` maps to `src/` (configured in tsconfig and vite config)
- **Custom colors** — `brand-*` (blue), `surface-*` (gray), `bullish` (green), `bearish` (red), `neutral` (amber)

### General
- Environment variables in `.env`, never hardcoded
- Docker Compose for local dev — `docker compose up` runs everything
- All services communicate via container names (e.g., `db`, `redis`, `backend`)
- Vite dev server proxies `/api/*` to `backend:8000` and `/ws/*` for WebSocket

## Running the Project

```bash
# Start everything
docker compose up --build

# Run alembic migrations
docker compose exec backend alembic upgrade head

# Generate a new migration after model changes
docker compose exec backend alembic revision --autogenerate -m "description"

# Run tests
docker compose exec backend pytest

# Backend logs
docker compose logs -f backend

# Celery worker logs
docker compose logs -f celery_worker

# Access Postgres directly
docker compose exec db psql -U sentinel -d sentinel

# Access the API docs
# http://localhost:8000/docs (Swagger)
# http://localhost:8000/redoc (ReDoc)
```

## Environment Variables

All defined in `.env.example`. API keys added as each phase requires them:
- Phase 1: STACK_PROJECT_ID, STACK_SECRET_SERVER_KEY (Stack Auth — already obtained)
- Phase 2: ALPHA_VANTAGE_API_KEY (or use yfinance for free), NEWS_API_KEY, REDDIT_CLIENT_ID/SECRET
- Phase 3: ANTHROPIC_API_KEY, OPENAI_API_KEY
- Phase 6: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, SENDGRID_API_KEY

## Important Implementation Notes

- **pgvector** is a Postgres extension — no separate vector DB service needed. Embeddings are stored as `vector(1536)` columns.
- **TimescaleDB** is also a Postgres extension — `price_data` becomes a hypertable for optimized time-series queries. The hypertable conversion happens in a migration after table creation: `SELECT create_hypertable('price_data', 'time');`
- **Belief states are append-only** — never UPDATE, always INSERT a new row. This preserves full history for the belief timeline feature.
- **Celery tasks that hit external APIs** should always handle rate limits, retries, and failures gracefully. Use `@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)`.
- **The free tier MVP** focuses on a single stock for a single agent. Multi-asset, multi-agent, and billing come later.
- **Stack Auth integration**: Frontend uses `@stackframe/stack` SDK — `useUser()` hook provides the current user, `user.getAuthJson()` returns the access token. Token is sent to FastAPI as `x-stack-access-token` header (not `Authorization: Bearer`). Backend verifies using PyJWT + Stack Auth's JWKS endpoint: `https://api.stack-auth.com/api/v1/projects/<project-id>/.well-known/jwks.json`. Algorithm is `ES256`, audience is the project ID.
- **`auth_service.py` is not used** — Stack Auth replaces all manual auth logic. The file can be deleted.
