-- Enable required PostgreSQL extensions
-- This runs automatically on first database creation

CREATE EXTENSION IF NOT EXISTS vector;       -- pgvector for embedding search
CREATE EXTENSION IF NOT EXISTS timescaledb;   -- TimescaleDB for time-series data
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- UUID generation
