# Changelog

All notable changes to InterviewAce will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `UPGRADES.md` — comprehensive backend upgrade plan (23 items)
- `Planner.md` — phased implementation plan (15 phases, one feature at a time)
- `CHANGELOG.md` — this file
- **Redis + Rate Limiting + Token Pruning** (Phase 7):
  - `redis>=5.0.0` and `slowapi>=0.1.9` added to requirements
  - `app/infrastructure/cache/redis_client.py` — async Redis client singleton with `RedisTokenBlacklist` and `RedisRateLimit` helpers
  - Replaced in-memory `RateLimitMiddleware` with `slowapi.SlowAPIMiddleware` backed by Redis
  - Per-endpoint rate limits: login `5/min`, register `10/min`, resume upload `10/min`, password reset `3/min`
  - Token blacklist migrated to Redis with automatic TTL expiry (DB kept as fallback + audit trail)
  - `check_token_revocation()` now checks Redis first, falls back to DB if Redis is unavailable
  - `revoke_tokens()` stores JTI in both Redis (with TTL) and DB (for durability)
  - Health readiness probe (`/ready`) now checks Redis connectivity in addition to DB
  - `main.py` uses `lifespan` context manager — graceful Redis shutdown on app exit
- **Background Tasks — Celery** (Phase 8):
  - `celery[redis]>=5.4.0` added to requirements
  - `app/infrastructure/tasks/celery_app.py` — Celery app configured with Redis as broker + backend
  - `app/infrastructure/tasks/resume_tasks.py` — `parse_resume_task` runs LLM parsing in background worker
  - `app/infrastructure/tasks/maintenance.py` — `prune_expired_tokens` runs hourly via Celery Beat to clean stale DB rows
  - `POST /resume/upload` now returns `202 Accepted` with `task_id` instead of blocking on LLM call
  - `GET /api/v1/tasks/{task_id}` — poll Celery task status (PENDING → STARTED → SUCCESS/FAILURE)
  - `ResumeUploadResponse` schema extended with optional `task_id` field
- **Structured Logging** (Phase 5):
  - `structlog>=24.0.0` added to requirements — JSON logs in production, coloured console in development
  - `app/core/logging_config.py` — `setup_logging()` configures structlog pipeline + stdlib integration
  - `RequestIDMiddleware` — generates UUID per request, propagates via `structlog.contextvars`, adds `X-Request-ID` response header
  - `RequestLoggingMiddleware` — logs method, path, status, and duration (ms) for every request
  - Migrated 7 files from `logging.getLogger` to `structlog.get_logger` with structured key=value format:
    `openai_provider.py`, `gemini_provider.py`, `factory.py`, `ai_analyzer.py`, `resume_parser.py`, `interview_orchestrator.py`, `llm_client.py`
  - `GET /health` liveness probe (returns `{"status": "healthy"}`)
  - `GET /ready` readiness probe (checks DB connectivity via `SELECT 1`)
  - `app/api/health.py` — health router mounted at root (no `/api/v1` prefix)
- **Testing Foundation** (Phase 6):
  - Test dependencies added: `pytest>=8.0.0`, `pytest-asyncio>=0.24.0`, `httpx>=0.27.0`, `factory-boy>=3.3.0`, `coverage>=7.0.0`, `aiosqlite>=0.20.0`
  - `backend_v2/tests/conftest.py` — shared fixtures: in-memory async SQLite, HTTPX `AsyncClient`, `test_user`, `auth_token`, `MockLLMProvider`
  - `pyproject.toml` — `testpaths` updated to `backend_v2/tests`
  - Unit tests: `test_security.py` (password complexity, hashing, JWT, CSRF, email verification tokens)
  - Unit tests: `test_llm_factory.py` (fallback chain: primary success, primary fail → fallback, both fail, factory function)
  - Integration tests: `test_auth.py` (register, login, /me, refresh, logout, duplicate registration, invalid credentials)
  - Integration tests: `test_interview.py` (start session with mock LLM, next question, answer, complete — with error cases)
  - Integration tests: `test_resume.py` (upload with mock LLM, validation errors, unauthenticated)
  - Integration tests: `test_health.py` (liveness and readiness probes)
- `.env.example` — all required environment variables with placeholder values
- `pyproject.toml` — unified config for ruff, mypy, pytest, coverage
- `backend_v2/` — new backend folder for upgraded implementation
- Alembic migration system (`backend_v2/alembic/`) with initial schema migration
- `alembic.ini` configured to read DATABASE_URL from app settings
- `alembic/env.py` imports all ORM models for autogenerate support
- **Clean Architecture scaffold** — three new layers:
  - `domain/entities/` — pure Python business objects (`UserEntity`, `ResumeEntity`, `InterviewSessionEntity`, `InterviewQuestionEntity`)
  - `domain/interfaces/` — abstract contracts (`IUserRepository`, `IResumeRepository`, `IInterviewRepository`, `ILLMProvider`, `IFileStorage`, `IEmailService`)
  - `domain/value_objects/enums.py` — `ResumeStatus` and `FileType` as single source of truth
  - `domain/exceptions.py` — domain exception hierarchy (12 exception classes)
  - `application/use_cases/` — placeholder for auth, resume, interview use cases
  - `application/dto/` — placeholder for data transfer objects
  - `infrastructure/persistence/models/` — canonical ORM model location
  - `infrastructure/persistence/repositories/` — `UserRepository`, `ResumeRepository`, `InterviewRepository` implementing domain ABCs
  - `infrastructure/llm/`, `infrastructure/storage/`, `infrastructure/email/` — adapter placeholders
- `app/core/exceptions.py` — exception-to-HTTP handler mapping (domain exceptions → JSON responses)
- `backend_v2/Docs/ARCHITECTURE.md` — Clean Architecture documentation
- **LLM Provider Infrastructure** (Phase 3):
  - `infrastructure/llm/openai_provider.py` — `OpenAIProvider(ILLMProvider)` using OpenAI SDK with JSON mode, model `gpt-5.2-2025-12-11`
  - `infrastructure/llm/gemini_provider.py` — `GeminiProvider(ILLMProvider)` refactored from legacy code with markdown fence cleaning
  - `infrastructure/llm/factory.py` — `LLMProviderWithFallback` composite + `get_llm_provider()` factory
  - `services/ai_analyzer.py` — background resume re-analysis service using LLM provider chain
- **Async Database Layer** (Phase 4):
  - `asyncpg>=0.30.0` added to requirements for native async PostgreSQL connectivity
  - `config.py` — `async_database_url` property auto-converts `postgresql://` → `postgresql+asyncpg://`
  - `db/session.py` — fully async: `create_async_engine`, `async_sessionmaker`, `AsyncSession`, async `get_db()` generator
  - Pool tuning: `pool_pre_ping=True`, `pool_size=10`, `max_overflow=20`, `expire_on_commit=False`

### Changed
- Renamed `backend/` → `backend_v1/` (preserved as reference)
- `config.py` — SECRET_KEY now required with strong validation (min 32 chars, no insecure defaults)
- `config.py` — added OPENAI_API_KEY, OPENAI_MODEL, GEMINI_MODEL, ENVIRONMENT, REDIS_URL, SENTRY_DSN settings
- `config.py` — ALLOWED_ORIGINS is now a proper Pydantic field with JSON/CSV parsing
- `config.py` — removed all scattered `os.getenv()` calls; all config via pydantic-settings
- `config.py` — SMTP_PORT changed from `str` to `int`
- `config.py` — DATABASE_URL constructed via `database_url` property instead of class-level f-string
- `session.py` — uses `settings.database_url` property
- `init_db.py` — removed `Base.metadata.create_all()` and `drop_db()`; schema now managed by Alembic
- `middleware.py` — rate limiter reads from `settings.RATE_LIMIT` instead of hardcoded values
- `requirements.txt` — added `alembic>=1.14.0`
- **ORM models relocated** from `app/models/` to `app/infrastructure/persistence/models/` (old paths become re-export wrappers)
- **Enums relocated** — `ResumeStatus`, `FileType` moved from `app/schemas/resume.py` to `app/domain/value_objects/enums.py`; schemas now import from domain
- `alembic/env.py` — updated to import models from `app.infrastructure.persistence.models`
- `main.py` — registers domain exception handlers via `register_exception_handlers()`
- **LLM migration** (Phase 3):
  - Primary LLM switched from Gemini to OpenAI GPT-5.2 (`gpt-5.2-2025-12-11`)
  - Gemini retained as automatic fallback via `LLMProviderWithFallback` composite
  - `config.py` — added `LLM_PRIMARY_PROVIDER`, `LLM_TIMEOUT`, `LLM_MAX_RETRIES` settings
  - `services/resume_parser.py` — removed module-level Gemini client and HF NER pipeline; now accepts `ILLMProvider` via DI
  - `services/interview_orchestrator.py` — `InterviewOrchestrator` accepts `ILLMProvider` via constructor; removed `os.getenv("GEMINI_API_KEY")`
  - `services/interview_orchestrator.py` — `complete_interview_session()` uses `get_llm_provider()` instead of ad-hoc `LLMClient`
  - `utils/llm_client.py` — replaced with backward-compat deprecation shim delegating to `get_llm_provider()`
  - System/user prompts updated to include "respond with valid JSON only" for OpenAI JSON mode compatibility
  - `requirements.txt` — added `openai>=1.60.0`, `google-genai>=1.0.0`
- **Async Database Layer** (Phase 4):
  - `core/security.py` — all 12 DB-touching functions converted to async (`check_password_history`, `record_password_history`, `verify_token`, `check_token_revocation`, `revoke_tokens`, `check_login_attempts`, `record_login_attempt`, `create_user_session`, `update_session_activity`, `deactivate_session`, `get_current_user`, `get_current_user_from_refresh_token`)
  - `api/deps.py` — `get_current_user` dependency now async with `select()` + `await`
  - All 4 services converted to async: `auth_service.py`, `resume_parser.py`, `interview_orchestrator.py`, `ai_analyzer.py`
  - All 10 auth endpoints converted: `Session` → `AsyncSession`, `db.query()` → `await db.execute(select())`
  - All 7 interview endpoints converted to async
  - All 6 resume endpoints converted to async
  - Repository interfaces (`domain/interfaces/repositories.py`) — all method signatures now `async def`
  - Repository implementations (`UserRepository`, `ResumeRepository`, `InterviewRepository`) — all methods now async with `select()` pattern
  - `resume/management.py` — `status` param renamed to `status_filter` with `Query(alias="status")` to avoid shadowing
  - Alembic `env.py` intentionally kept sync (CLI tool, not in async event loop); uses `settings.database_url` (sync psycopg2 driver)

### Removed
- `torch==2.2.0`, `transformers==4.37.2`, `spacy==3.7.2` and 20+ transitive deps (~2 GB) removed from `requirements.txt`
- Module-level `hf_ner = pipeline("ner", ...)` in `resume_parser.py` (no longer downloads 1.3 GB model on import)
- `_parse_with_gemini()`, `_fallback_parse()`, `clean_gemini_json()` functions from `resume_parser.py`
- Direct Gemini SDK usage from `llm_client.py` and `interview_orchestrator.py`

### Security
- Removed wildcard CORS (`allow_origins=["*"]`) from `main.py`
- CORS is now handled solely by `setup_middleware()` using `settings.ALLOWED_ORIGINS`
- App refuses to start if SECRET_KEY is missing, too short, or a known insecure value

---

## [1.0.0] - 2026-02-22

### Added
- FastAPI backend with Uvicorn
- User authentication (register, login, logout, refresh, email verification, password reset, change password)
- JWT access tokens (15 min) + refresh tokens (7 days) with blacklist
- Password policy enforcement (bcrypt 12 rounds, complexity rules, history of last 5)
- Login attempt tracking and account lockout
- Resume upload (PDF, DOCX) with 10 MB limit
- Resume AI analysis via Google Gemini 2.0 Flash
- HuggingFace NER fallback for resume parsing
- Resume versioning (parent/child chains)
- Resume sharing via public tokens
- Resume export
- Interview session creation linked to resume
- AI-generated interview questions (12–15 per session: technical, behavioral, project-based)
- Answer submission with AI evaluation (score + feedback)
- Session completion with final score and summary
- Interview history
- Security headers middleware (CSP, HSTS, X-Frame-Options, X-XSS-Protection)
- In-memory rate limiting (100 req/min per IP)
- API versioning (`/api/v1`)
- Pydantic v2 validation on all request/response schemas
- PostgreSQL database with SQLAlchemy 2.0 ORM
- SMTP email service for verification and password reset
- Project documentation (PROJECT_OVERVIEW, ARCHITECTURE, DATABASE_SCHEMA, API_REFERENCE, PRODUCTION_READINESS)
