# CLAUDE.md — Sentinel Project Context

## What is Sentinel?

Sentinel is a multi-user SaaS platform that deploys persistent AI agents to continuously monitor financial markets (stocks, ETFs, crypto). Each user's agent ingests data from multiple sources, builds an evolving "belief state" (thesis + conviction score) about each tracked asset, and delivers intelligence through daily briefings, anomaly alerts, and an interactive dashboard.

Think: Bloomberg Terminal meets an AI research analyst — for individual investors and small teams.

## Current Status

**Phase 1 (Foundation)** — complete. Project skeleton is built, Docker Compose runs all services, database schema has `assets`, `price_data`, `users`, `agents`, `agent_watchlist`, `belief_states`, `articles`, and `briefings` tables created via Alembic migrations. Stack Auth integration implemented. Agent CRUD, belief listing, and briefings endpoints working. Agent runner, reasoning chain (Gemini), briefing generator, anomaly detector, belief engine, memory manager all implemented.

**Phase 2 (Data Ingestion)** — price poller (Alpha Vantage, to be migrated to Finnhub) and news fetcher (newsapi.org, to be migrated to Finnhub) implemented. Embedding pipeline implemented. SEC crawler, social scraper, crypto monitor are stubs.

Phases 3-6 are not started yet. Placeholder files exist for all future modules with TODO comments indicating which phase they belong to.

## Architecture Overview

```
Frontend (React + Vite + TypeScript + TailwindCSS)
    │
    ▼  REST + WebSocket (proxied via Vite dev server)
API Gateway (FastAPI, Python 3.12)
    │
    ├── Agent Core (belief engine, RAG, reasoning chain, anomaly detection)
    ├── Celery Workers (data ingestion: news, prices, social, crypto, embeddings)
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
- **AI**: Gemini 3.1 Flash Lite Preview (`gemini-3.1-flash-lite-preview`) for agent reasoning/analysis, OpenAI `text-embedding-3-small` for document embeddings
- **Data sources**: Finnhub (stock prices + company news — free tier, no daily cap, commercially licensed), CoinGecko (crypto), Reddit API via PRAW (social sentiment), SEC EDGAR (government filings)
- **Payments**: Stripe (subscription billing)
- **Auth**: Stack Auth (managed SaaS) — handles email/password, sessions, Google OAuth. Backend verifies JWTs via Stack Auth's JWKS endpoint using PyJWT.
- **Deployment**: Docker Compose locally, Railway or Fly.io for production MVP (migrate to AWS when scale demands it — note: AWS RDS does not support TimescaleDB, use EC2 with self-managed Postgres or Timescale Cloud instead)

## Data Source Notes

**Finnhub replaces both Alpha Vantage and NewsAPI.** One API key, free tier covers 60 req/min with no daily cap, commercially licensed for production use. Covers US stock OHLCV candles, real-time quotes, and company news with 1 year history. `price_poller.py` and `news_fetcher.py` should both be migrated to use the `finnhub-python` SDK.

**Do not use yfinance in production** — it scrapes Yahoo Finance's unofficial API and is explicitly for personal/educational use only per Yahoo's ToS.

**Do not use newsapi.org in production** — their free tier is dev/testing only and is blocked in commercial/production environments.

## SaaS Tiers (MVP: Free + Pro only)

| Feature            | Free        | Pro ($19/mo)      |
| ------------------ | ----------- | ----------------- |
| Active agents      | 1           | 5                 |
| Watched assets     | 5           | 25                |
| Agent runs         | 6×/day      | 6×/day            |
| Briefing frequency | Weekly      | Daily (07:00 UTC) |
| Alert types        | Price only  | All               |
| Belief history     | 30 days     | 1 year            |
| LLM calls/month    | ~900        | ~4,500            |
| Variable cost/user | ~$0.05      | ~$1.60            |
| Gross margin       | loss leader | ~91%              |

**Team tier ($49/mo — 15 agents, 100 assets, real-time briefings, custom alerts, unlimited history) is planned but deferred until after MVP launch.** Add a "Team plan coming soon — join the waitlist" CTA on the pricing page to capture early interest.

**Current focus: Free tier — 1 agent, core stocks, basic price monitoring.**

## Pricing & Cost Notes

- **LLM**: Gemini 3.1 Flash Lite Preview — $0.25/1M input tokens, $1.50/1M output tokens. Each agent run = ~1 LLM call per watched asset (~1,200 input / ~300 output tokens). Briefing generation has zero LLM cost — it reads existing belief states from the DB.
- **Infrastructure**: ~$35-45/mo base on Railway or Fly.io for the full Docker stack. Break-even is 2–3 Pro users.
- **Finnhub**: Free tier sufficient until ~300 simultaneously active tracked symbols across all users. No action needed at MVP scale.
- **Embeddings**: OpenAI text-embedding-3-small at $0.02/1M tokens — negligible cost.
- **Stripe**: 2.9% + $0.30 per charge = ~$0.85/Pro user/month.

## Agent Execution Schedule (from celery_app.py)

| Task                     | Schedule               | LLM cost                              |
| ------------------------ | ---------------------- | ------------------------------------- |
| `fetch_prices`           | Every 5 min            | None — Finnhub only                   |
| `fetch_news`             | Every 15 min           | None — Finnhub only                   |
| `embed_document`         | Every 15 min           | None — OpenAI embeddings only         |
| `run_due_agents`         | Every 4 hours (6×/day) | Yes — 1 Gemini call per asset per run |
| `generate_all_briefings` | Daily at 07:00 UTC     | None — DB read + markdown render only |

**Tier enforcement not yet implemented.** Before charging users, add plan_tier checks inside `run_agent()` in `agent_runner.py` to skip or throttle Free users appropriately (weekly briefing, price-only alerts).

## Sprint Plan (175 hours total)

| Phase                 | Hours | Focus                                                  |
| --------------------- | ----- | ------------------------------------------------------ |
| 1. Foundation         | 40h   | Auth, DB schema, API skeleton, React shell             |
| 2. Data Ingestion     | 30h   | Finnhub price + news workers, embedding pipeline       |
| 3. Agent Core         | 35h   | Belief engine, RAG, reasoning chain, anomaly detection |
| 4. Briefings          | 15h   | AI-generated briefings with citations + email          |
| 5. Frontend Dashboard | 40h   | Full UI with charts, belief timeline, real-time alerts |
| 6. SaaS & Polish      | 15h   | Stripe billing, tier enforcement, landing page         |

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

-- users table
users (
  id VARCHAR PRIMARY KEY,        -- Stack Auth user ID
  email VARCHAR UNIQUE NOT NULL,
  name VARCHAR NOT NULL,
  plan_tier ENUM(free, pro, team) NOT NULL DEFAULT 'free',
  created_at TIMESTAMPTZ DEFAULT NOW()
)

-- agents table
agents (
  id VARCHAR PRIMARY KEY,
  user_id VARCHAR FK → users.id,
  name VARCHAR NOT NULL,
  status ENUM(active, paused) NOT NULL DEFAULT 'active',
  config_json JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
)

-- agent_watchlist (join table)
agent_watchlist (agent_id, asset_id) -- composite PK

-- belief_states table (append-only, never UPDATE)
belief_states (
  id VARCHAR PRIMARY KEY,
  agent_id VARCHAR FK → agents.id,
  asset_id VARCHAR FK → assets.id,
  conviction FLOAT NOT NULL,     -- 0.0 = max bearish, 1.0 = max bullish
  thesis TEXT NOT NULL,
  key_factors JSONB,
  evidence_refs JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
)

-- articles table
articles (
  id VARCHAR PRIMARY KEY,
  asset_id VARCHAR,
  source VARCHAR NOT NULL,
  url VARCHAR UNIQUE NOT NULL,
  title VARCHAR NOT NULL,
  summary TEXT,
  sentiment_score FLOAT,
  published_at TIMESTAMPTZ,
  embedding vector(1536),        -- OpenAI text-embedding-3-small
  created_at TIMESTAMPTZ DEFAULT NOW()
)

-- briefings table
briefings (
  id VARCHAR PRIMARY KEY,
  agent_id VARCHAR NOT NULL,
  content_md TEXT NOT NULL,
  sources JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
)
```

### Future tables (not yet created)

- `filings` — asset_id, filing_type, summary, key_metrics (JSONB), embedding vector(1536)
- `social_mentions` — asset_id, platform, sentiment, content_summary
- `alerts` — agent_id, asset_id, alert_type, severity, message
- `subscriptions` — user_id, stripe_customer_id, plan, status

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
│   │   │   ├── asset.py            # ✅ Implemented
│   │   │   ├── price_data.py       # ✅ Implemented — TimescaleDB hypertable
│   │   │   ├── user.py             # ✅ Implemented
│   │   │   ├── agent.py            # ✅ Implemented
│   │   │   ├── belief.py           # ✅ Implemented
│   │   │   ├── article.py          # ✅ Implemented
│   │   │   ├── briefing.py         # ✅ Implemented
│   │   │   ├── filing.py           # Placeholder — Phase 2
│   │   │   └── alert.py            # Placeholder — Phase 3
│   │   ├── api/                    # FastAPI route handlers
│   │   │   ├── auth.py             # ✅ Implemented — Stack Auth JWT verification
│   │   │   ├── agents.py           # ✅ Implemented — CRUD + beliefs + briefings
│   │   │   ├── assets.py           # Placeholder — Phase 1
│   │   │   ├── briefings.py        # Placeholder — Phase 4
│   │   │   ├── alerts.py           # Placeholder — Phase 3
│   │   │   └── billing.py          # Placeholder — Phase 6
│   │   ├── core/                   # Agent brain
│   │   │   ├── belief_engine.py    # ✅ Implemented — get/save belief states
│   │   │   ├── memory_manager.py   # ✅ Implemented — RAG + context assembly
│   │   │   ├── reasoning_chain.py  # ✅ Implemented — Gemini 3.1 Flash Lite
│   │   │   ├── anomaly_detector.py # ✅ Implemented — conviction delta detection
│   │   │   └── briefing_generator.py # ✅ Implemented — DB read + markdown render
│   │   ├── workers/                # Celery background tasks
│   │   │   ├── celery_app.py       # ✅ Implemented — Celery config + beat schedule
│   │   │   ├── price_poller.py     # ✅ Implemented — needs migration to Finnhub
│   │   │   ├── news_fetcher.py     # ✅ Implemented — needs migration to Finnhub
│   │   │   ├── embedding_pipeline.py # ✅ Implemented — OpenAI embeddings
│   │   │   ├── agent_runner.py     # ✅ Implemented — orchestrates full agent cycle
│   │   │   ├── sec_crawler.py      # Stub — Phase 2
│   │   │   ├── social_scraper.py   # Stub — Phase 2
│   │   │   └── crypto_monitor.py   # Stub — Phase 2
│   │   ├── services/
│   │   │   ├── agent_service.py    # Placeholder — Phase 1
│   │   │   ├── asset_service.py    # Placeholder — Phase 1
│   │   │   └── stripe_service.py   # Placeholder — Phase 6
│   │   └── utils/
│   │       ├── llm_client.py       # Placeholder — Phase 3
│   │       ├── embedding_client.py # Placeholder — Phase 2
│   │       └── rate_limiter.py     # Placeholder — Phase 6
│   └── tests/
│       └── test_health.py          # ✅ Implemented — smoke test
│
├── frontend/
│   ├── src/
│   │   ├── main.tsx                # React entry point with BrowserRouter + StackProvider
│   │   ├── App.tsx                 # Route definitions
│   │   ├── api/client.ts           # ✅ Implemented — API client with auth header injection
│   │   ├── pages/
│   │   │   ├── DashboardPage.tsx   # ✅ Implemented — agent list + create form
│   │   │   ├── AgentDetailPage.tsx # ✅ Implemented — belief history + conviction chart
│   │   │   ├── BriefingsPage.tsx   # ✅ Implemented — briefing list + markdown render
│   │   │   ├── SignInPage.tsx      # ✅ Implemented
│   │   │   └── SignUpPage.tsx      # ✅ Implemented
│   │   ├── components/NavBar.tsx   # ✅ Implemented
│   │   ├── stores/authStore.ts     # ✅ Implemented — Zustand auth state
│   │   └── stack/                  # Stack Auth client + handler
│
└── infra/
    ├── init.sql                    # Enables pgvector, TimescaleDB, uuid-ossp extensions
    └── nginx.conf                  # Production reverse proxy config
```

## Key Concepts

### Belief State (core data model)

Each agent maintains a belief state per tracked asset:

- `conviction` (0.0 to 1.0) — 0 = max bearish, 0.5 = neutral, 1.0 = max bullish
- `thesis` — 2-3 sentence natural language summary of the agent's current view
- `key_factors` — weighted factors driving the thesis (each with signal: bullish/bearish/neutral)
- `evidence_refs` — article IDs supporting the thesis
- Belief states are **append-only** — never UPDATE, always INSERT a new row. This preserves full history for the belief timeline.

### Agent Lifecycle

Agents run every 4 hours via Celery Beat. Each run, for each asset in the watchlist:

1. **Gather context** — load current belief state, query pgvector for relevant recent articles, fetch latest prices
2. **Analyze** — single Gemini 3.1 Flash Lite call with structured JSON output
3. **Update belief** — insert new belief_state row (never update existing)
4. **Detect anomalies** — compare conviction delta to previous state, log alert if delta > 0.2
5. **Generate briefing** — at scheduled time, compile latest beliefs into markdown (no LLM call)

### Briefing Generation

`briefing_generator.py` reads the most recent belief state per asset from the DB and renders markdown. There is no LLM call — this is pure DB + string formatting. Cost is $0.

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

- Phase 1: `STACK_PROJECT_ID`, `STACK_SECRET_SERVER_KEY` (Stack Auth — already obtained)
- Phase 2: `FINNHUB_API_KEY` (replaces both ALPHA_VANTAGE_API_KEY and NEWS_API_KEY), `REDDIT_CLIENT_ID/SECRET`
- Phase 3: `GEMINI_API_KEY` (reasoning chain), `OPENAI_API_KEY` (embeddings only)
- Phase 6: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `SENDGRID_API_KEY`

## Important Implementation Notes

- **pgvector** is a Postgres extension — no separate vector DB service needed. Embeddings stored as `vector(1536)` columns.
- **TimescaleDB** is also a Postgres extension — `price_data` is a hypertable. AWS RDS does not support TimescaleDB — use EC2 self-managed Postgres or Timescale Cloud for production.
- **Belief states are append-only** — never UPDATE, always INSERT. Preserves full timeline history.
- **Celery tasks that hit external APIs** should handle rate limits, retries, and failures gracefully. Use `@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)`.
- **Tier enforcement** — not yet implemented. Before billing, add `user.plan_tier` checks in `agent_runner.py` to enforce Free (weekly briefing, price-only alerts) vs Pro (daily briefing, all alerts).
- **Stack Auth integration** — Frontend uses `@stackframe/stack` SDK. `user.getAuthJson()` returns the access token, sent as `x-stack-access-token` header. Backend verifies via PyJWT + Stack Auth's JWKS endpoint: `https://api.stack-auth.com/api/v1/projects/<project-id>/.well-known/jwks.json`. Algorithm: `ES256`, audience: project ID.
- **`auth_service.py` is not used** — Stack Auth owns auth. File can be deleted.
