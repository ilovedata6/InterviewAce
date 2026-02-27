# InterviewAce — Architecture Guide

> **Version 2.0.0** — Reflects the `backend/` codebase after all upgrade phases.

---

## High-Level Architecture

```
                ┌──────────────┐
                │   Clients    │
                │ (Browser/App)│
                └──────┬───────┘
                       │  HTTPS
                ┌──────▼───────┐
                │   FastAPI    │  ← Uvicorn ASGI
                │   (main.py)  │
                └──┬───┬───┬───┘
                   │   │   │
        ┌──────────┘   │   └──────────┐
        ▼              ▼              ▼
  ┌──────────┐  ┌───────────┐  ┌──────────┐
  │ PostgreSQL│  │   Redis   │  │  Celery  │
  │ (asyncpg) │  │ (cache +  │  │ (workers)│
  │           │  │  rate-lim)│  │          │
  └──────────┘  └───────────┘  └──────────┘
```

### Request Flow

1. **Middleware stack** — CORS, security headers, `SlowAPIMiddleware` (Redis-backed rate limiting), request-ID injection, structured request logging.
2. **Router dispatch** — `/api/v1/auth`, `/api/v1/interview`, `/api/v1/resume`, `/api/v1/tasks`, plus root-level `/health` and `/ready`.
3. **Dependency injection** — `get_db()` (async session), `get_current_user()` (JWT auth), `require_role()` (RBAC).
4. **Service layer** — business orchestration (`InterviewOrchestrator`, `ResumeParser`, `AuthService`).
5. **LLM provider chain** — OpenAI (primary) → Gemini (fallback) via `LLMProviderWithFallback`.
6. **Persistence** — async SQLAlchemy 2.0 with `asyncpg`, managed by Alembic migrations.

---

## Directory Structure

```
backend/
├── main.py                           # FastAPI app, Sentry init, lifespan hooks
├── alembic/                          # Database migrations
├── app/
│   ├── api/                          # Presentation layer
│   │   ├── health.py                 # /health, /ready probes
│   │   ├── deps.py                   # Shared dependencies (get_current_user, require_role)
│   │   └── v1/
│   │       ├── api.py                # Router aggregation
│   │       └── endpoints/
│   │           ├── auth/             # 8 auth endpoints (login, register, logout, …)
│   │           ├── interview/        # 7 interview endpoints (start, answer, next, …)
│   │           ├── resume/           # upload, management (CRUD)
│   │           └── tasks.py          # Celery task status polling
│   ├── core/                         # Cross-cutting concerns
│   │   ├── config.py                 # pydantic-settings: all env vars
│   │   ├── middleware.py             # CORS, security headers, slowapi rate limiter
│   │   ├── security.py              # JWT, password hashing, session management
│   │   ├── logging_config.py        # structlog pipeline setup
│   │   └── exceptions.py            # Domain exception → HTTP response mapping
│   ├── db/                           # Async database session
│   │   ├── session.py                # create_async_engine, async_sessionmaker, get_db()
│   │   └── init_db.py               # Legacy init (schema via Alembic now)
│   ├── domain/                       # Pure business logic (no framework imports)
│   │   ├── entities/                 # Dataclass business objects
│   │   ├── interfaces/               # ABCs (IUserRepository, ILLMProvider, …)
│   │   ├── value_objects/enums.py    # ResumeStatus, FileType, UserRole
│   │   └── exceptions.py            # Domain exception hierarchy (12 classes)
│   ├── infrastructure/              # Framework adapters
│   │   ├── cache/
│   │   │   └── redis_client.py      # Async Redis singleton, token blacklist, rate limit helpers
│   │   ├── llm/
│   │   │   ├── openai_provider.py   # OpenAI GPT (primary)
│   │   │   ├── gemini_provider.py   # Google Gemini (fallback)
│   │   │   └── factory.py           # LLMProviderWithFallback + get_llm_provider()
│   │   ├── persistence/
│   │   │   ├── models/              # Canonical ORM models (User, Resume, InterviewSession, …)
│   │   │   └── repositories/        # Concrete repository implementations
│   │   └── tasks/
│   │       ├── celery_app.py        # Celery config (Redis broker + backend)
│   │       ├── resume_tasks.py      # parse_resume_task (background LLM parsing)
│   │       └── maintenance.py       # prune_expired_tokens (hourly Celery Beat)
│   ├── models/                       # Re-export wrappers → infrastructure/persistence/models
│   ├── schemas/                      # Pydantic request/response schemas
│   ├── services/                     # Service layer (orchestrators, parsers)
│   └── utils/                        # File handling, email utilities
└── tests/                            # pytest + httpx async integration tests
```

---

## Technology Stack

| Component | Technology | Notes |
|---|---|---|
| Web framework | FastAPI 0.109 + Uvicorn | Fully async ASGI |
| Database | PostgreSQL + asyncpg | Async driver, pool: 10 + 20 overflow |
| ORM | SQLAlchemy 2.0 (async) | `select()` pattern, `expire_on_commit=False` |
| Migrations | Alembic | `alembic upgrade head` |
| Cache / PubSub | Redis 5+ | Token blacklist TTL, rate limit backend |
| Rate limiting | slowapi (Redis-backed) | Per-endpoint limits (5–10 req/min) |
| Background tasks | Celery 5.4 (Redis broker) | Resume parsing, token pruning |
| LLM (primary) | OpenAI GPT-5.2 | JSON mode, structured output |
| LLM (fallback) | Google Gemini 2.0 Flash | Markdown fence cleaning |
| Auth | JWT (access 15m + refresh 7d) | bcrypt 12 rounds, password history |
| Logging | structlog | JSON in prod, coloured console in dev |
| Error monitoring | Sentry (optional) | Enabled when `SENTRY_DSN` is set |
| Testing | pytest + httpx + aiosqlite | 65+ tests, ≥80% coverage |
| Linting | Ruff + pre-commit | CI enforced |

---

## Security Architecture

| Mechanism | Implementation |
|---|---|
| Authentication | JWT access + refresh tokens; `get_current_user` dependency |
| RBAC | `UserRole` enum (`user`, `admin`, `moderator`); `require_role()` dependency |
| Password policy | Min 8 chars, complexity rules, bcrypt 12 rounds, last-5 history |
| Token revocation | Dual-write: Redis (TTL-based, fast) + DB (audit trail) |
| Login protection | Attempt tracking + account lockout |
| Rate limiting | slowapi + Redis (per-endpoint, per-IP) |
| CORS | `settings.ALLOWED_ORIGINS` (no wildcard) |
| Security headers | CSP, HSTS, X-Frame-Options, X-Content-Type-Options |
| Request tracing | UUID request ID in structlog context + `X-Request-ID` header |

---

## LLM Provider Architecture

```
ILLMProvider (ABC)
├── OpenAIProvider   — primary (JSON mode, gpt-5.2)
├── GeminiProvider   — fallback (markdown cleaning)
└── LLMProviderWithFallback — composite: try primary → fallback
```

`get_llm_provider()` factory returns the composite. Configuration via `LLM_PRIMARY_PROVIDER`, `OPENAI_API_KEY`, `GEMINI_API_KEY` env vars.

---

## Domain Exception Hierarchy

All extend `DomainException(message, code)` and are auto-mapped to HTTP responses in `app/core/exceptions.py`:

| Exception | HTTP Status |
|---|---|
| `EntityNotFoundError` | 404 |
| `AuthenticationError` | 401 |
| `AuthorizationError` | 403 |
| `TokenError` | 401 |
| `DuplicateEntityError` | 409 |
| `ValidationError` | 422 |
| `PasswordPolicyError` | 422 |
| `FileValidationError` | 400 |
| `ResumeProcessingError` | 500 |
| `LLMProviderError` | 503 |
| `EmailDeliveryError` | 500 |

---

## Background Tasks (Celery)

| Task | Schedule | Purpose |
|---|---|---|
| `parse_resume_task` | On demand (upload) | LLM-based resume parsing |
| `prune_expired_tokens` | Hourly (Celery Beat) | Clean stale token blacklist rows from DB |

Workers: `celery -A app.infrastructure.tasks.celery_app worker`
Beat: `celery -A app.infrastructure.tasks.celery_app beat`

---

## Health Probes

| Endpoint | Purpose | Checks |
|---|---|---|
| `GET /health` | Liveness | Process running (always 200) |
| `GET /ready` | Readiness | PostgreSQL `SELECT 1` + Redis `PING` |

Both are mounted at root (no `/api/v1` prefix) for load-balancer compatibility.
