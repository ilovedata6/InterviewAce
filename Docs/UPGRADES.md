# InterviewAce — Professional Backend Upgrades

> **Date:** 2026-02-22  
> **Scope:** Backend only  
> **Goal:** Elevate InterviewAce from a working prototype to a production-grade, maintainable, and scalable backend service.

---

## Table of Contents

1. [Architecture Overhaul — Layered Clean Architecture (OOP)](#1-architecture-overhaul--layered-clean-architecture-oop)
2. [LLM Provider Migration — OpenAI Primary + Gemini Fallback](#2-llm-provider-migration--openai-primary--gemini-fallback)
3. [Database Migrations — Alembic](#3-database-migrations--alembic)
4. [Async Database Layer — asyncpg + SQLAlchemy AsyncIO](#4-async-database-layer--asyncpg--sqlalchemy-asyncio)
5. [Configuration & Secrets Hardening](#5-configuration--secrets-hardening)
6. [CORS Fix — Remove Wildcard](#6-cors-fix--remove-wildcard)
7. [Background Task Processing — Celery + Redis](#7-background-task-processing--celery--redis)
8. [Redis-Backed Rate Limiting](#8-redis-backed-rate-limiting)
9. [Structured JSON Logging + Request Tracing](#9-structured-json-logging--request-tracing)
10. [Error Monitoring — Sentry](#10-error-monitoring--sentry)
11. [Health Check & Readiness Probes](#11-health-check--readiness-probes)
12. [Testing — pytest + Coverage](#12-testing--pytest--coverage)
13. [Pagination on List Endpoints](#13-pagination-on-list-endpoints)
14. [Token Blacklist Pruning & Redis Migration](#14-token-blacklist-pruning--redis-migration)
15. [Lazy-Load Heavy ML Models](#15-lazy-load-heavy-ml-models)
16. [Cloud File Storage — S3 / R2](#16-cloud-file-storage--s3--r2)
17. [Role-Based Access Control (RBAC)](#17-role-based-access-control-rbac)
18. [Docker & Docker Compose](#18-docker--docker-compose)
19. [CI/CD — GitHub Actions](#19-cicd--github-actions)
20. [Developer Experience — .env.example, pre-commit, linting](#20-developer-experience--envexample-pre-commit-linting)
21. [API Versioning & OpenAPI Enhancements](#21-api-versioning--openapi-enhancements)
22. [Soft Deletes & Audit Trail](#22-soft-deletes--audit-trail)
23. [CHANGELOG.md Maintenance](#23-changelogmd-maintenance)

---

## 1. Architecture Overhaul — Layered Clean Architecture (OOP)

### Current State
The codebase uses a flat layered monolith with procedural-style service functions (especially `resume_parser.py`) and direct ORM coupling inside endpoint handlers. No dependency inversion, no interfaces, no repository abstraction.

### What Changes
Adopt a **Clean Architecture** layout with strict dependency rules:

```
backend/
├── main.py                          # App bootstrap only
└── app/
    ├── api/                         # Presentation Layer (Controllers)
    │   └── v1/
    │       └── endpoints/
    │           ├── auth/
    │           ├── interview/
    │           └── resume/
    │
    ├── core/                        # Cross-cutting concerns
    │   ├── config.py
    │   ├── security.py
    │   ├── middleware.py
    │   ├── logging_config.py
    │   └── exceptions.py            # Custom domain exceptions
    │
    ├── domain/                      # Domain Layer (Pure business logic — NO framework imports)
    │   ├── entities/                # Domain entities (plain Python classes / dataclasses)
    │   │   ├── user.py
    │   │   ├── resume.py
    │   │   └── interview.py
    │   ├── value_objects/           # Immutable value types (Email, Score, etc.)
    │   ├── interfaces/             # Abstract base classes (contracts)
    │   │   ├── i_user_repository.py
    │   │   ├── i_resume_repository.py
    │   │   ├── i_interview_repository.py
    │   │   ├── i_llm_provider.py
    │   │   ├── i_file_storage.py
    │   │   └── i_email_service.py
    │   └── services/               # Domain services (orchestration of domain logic)
    │       ├── interview_service.py
    │       └── resume_service.py
    │
    ├── application/                 # Application Layer (Use Cases)
    │   ├── use_cases/
    │   │   ├── auth/
    │   │   │   ├── register_user.py
    │   │   │   ├── login_user.py
    │   │   │   └── ...
    │   │   ├── interview/
    │   │   │   ├── start_session.py
    │   │   │   ├── submit_answer.py
    │   │   │   └── ...
    │   │   └── resume/
    │   │       ├── upload_resume.py
    │   │       ├── analyze_resume.py
    │   │       └── ...
    │   └── dto/                    # Data Transfer Objects (input/output for use cases)
    │       ├── auth_dto.py
    │       ├── interview_dto.py
    │       └── resume_dto.py
    │
    ├── infrastructure/             # Infrastructure Layer (Implementations)
    │   ├── persistence/
    │   │   ├── models/             # SQLAlchemy ORM models (moved here)
    │   │   ├── repositories/       # Concrete repo implementations
    │   │   │   ├── user_repository.py
    │   │   │   ├── resume_repository.py
    │   │   │   └── interview_repository.py
    │   │   └── database.py         # Engine, session factory
    │   ├── llm/
    │   │   ├── openai_provider.py  # Primary — OpenAI GPT-5.2
    │   │   ├── gemini_provider.py  # Fallback — Gemini
    │   │   └── llm_factory.py      # Factory with fallback chain
    │   ├── storage/
    │   │   ├── local_storage.py
    │   │   └── s3_storage.py
    │   └── email/
    │       └── smtp_email_service.py
    │
    └── schemas/                    # Pydantic request/response schemas (API layer DTOs)
        ├── auth.py
        ├── interview.py
        ├── resume.py
        └── common.py
```

### Key Principles
| Principle | How Applied |
|---|---|
| **Dependency Inversion** | Domain layer defines interfaces (`ABC`); infrastructure implements them |
| **Single Responsibility** | Each use case = one class with one `execute()` method |
| **Open/Closed** | New LLM providers (Claude, Llama) added without touching existing code |
| **Repository Pattern** | All DB access goes through repository interfaces; endpoints never import SQLAlchemy |
| **Dependency Injection** | FastAPI `Depends()` wires concrete implementations at the API layer |

### Why
- Testable: mock any interface boundary
- Swappable: change DB, LLM, storage without touching business logic
- Maintainable: clear ownership per layer, enforced by import rules

---

## 2. LLM Provider Migration — OpenAI Primary + Gemini Fallback

### Current State
- Primary: `google-genai` (Gemini 2.0 Flash) — synchronous calls
- Fallback: HuggingFace NER (partially disabled, commented out)
- `LLMClient` is a single class tightly coupled to the Gemini SDK
- Model name hardcoded (`"gemini-2.0-flash"`) in multiple places

### What Changes

#### 2a. Abstract LLM Interface
```python
# app/domain/interfaces/i_llm_provider.py
from abc import ABC, abstractmethod

class ILLMProvider(ABC):
    @abstractmethod
    async def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Returns raw text completion."""
        ...

    @abstractmethod
    async def generate_json(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        """Returns parsed JSON completion."""
        ...
```

#### 2b. OpenAI Implementation (Primary)
```python
# app/infrastructure/llm/openai_provider.py
from openai import AsyncOpenAI

class OpenAIProvider(ILLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-5.2-2025-12-11"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},  # native JSON mode
            temperature=0.7,
        )
        return json.loads(response.choices[0].message.content)
```

#### 2c. Gemini Implementation (Fallback)
```python
# app/infrastructure/llm/gemini_provider.py
from google import genai

class GeminiProvider(ILLMProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model
    # ... async wrapper around sync SDK
```

#### 2d. LLM Factory with Automatic Fallback
```python
# app/infrastructure/llm/llm_factory.py
class LLMProviderFactory:
    def __init__(self, providers: list[ILLMProvider]):
        self.providers = providers  # ordered by priority

    async def generate_json(self, system_prompt: str, user_prompt: str, schema: dict) -> dict:
        last_error = None
        for provider in self.providers:
            try:
                return await provider.generate_json(system_prompt, user_prompt, schema)
            except Exception as e:
                logger.warning(f"{provider.__class__.__name__} failed: {e}")
                last_error = e
        raise LLMProviderError(f"All LLM providers failed. Last error: {last_error}")
```

#### 2e. Configuration
```env
# .env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2-2025-12-11
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash
LLM_PRIMARY=openai
LLM_FALLBACK=gemini
```

#### 2f. Dependencies Update
```
# Remove
google-genai            → keep as fallback only
transformers            → remove (NER fallback replaced by Gemini)
torch                   → remove (saves ~2 GB)
spacy                   → remove

# Add
openai>=1.60.0
```

### Why
- **GPT-5.2** is significantly stronger for structured JSON generation and interview Q&A evaluation
- **Native JSON mode** eliminates regex cleaning of markdown fences
- **Gemini** as fallback provides resilience without Gemini being the bottleneck
- Removing `torch` + `transformers` + `spacy` cuts the Docker image by ~2+ GB and eliminates the slow startup from NER model loading

---

## 3. Database Migrations — Alembic

### Current State
`Base.metadata.create_all()` in `init_db.py`. No migration history. Schema changes require manual DB wipes.

### What Changes
```
backend/
├── alembic/
│   ├── env.py              # Reads DATABASE_URL from settings
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py  # Auto-generated initial migration
├── alembic.ini
```

### Setup Steps
1. `pip install alembic`
2. `alembic init alembic`
3. Point `env.py` → `settings.DATABASE_URL` and import `Base.metadata`
4. `alembic revision --autogenerate -m "initial schema"`
5. `alembic upgrade head`
6. Remove `Base.metadata.create_all()` from startup

### Migration Workflow Going Forward
```bash
# After any model change:
alembic revision --autogenerate -m "add_role_to_users"
alembic upgrade head

# Rollback:
alembic downgrade -1
```

### Why
- Safe, reversible schema changes in production
- Migration history in version control
- Required for any serious deployment pipeline

---

## 4. Async Database Layer — asyncpg + SQLAlchemy AsyncIO

### Current State
Synchronous `psycopg2-binary` driver. Every DB query blocks an OS thread. FastAPI's async benefit is negated.

### What Changes
```python
# app/infrastructure/persistence/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

### Dependencies
```
# Remove
psycopg2-binary

# Add
asyncpg
sqlalchemy[asyncio]
```

### Why
- Non-blocking DB access aligns with FastAPI's async architecture
- Higher throughput under concurrent load
- Prerequisite for production scalability

---

## 5. Configuration & Secrets Hardening

### Current State
- `SECRET_KEY` defaults to `"your-secret-key-here"` — anyone can forge JWTs
- `GEMINI_API_KEY` loaded via `os.getenv()` scattered across files instead of centralized `settings`
- No `.env.example`

### What Changes

#### 5a. Fail-Fast on Missing Secrets
```python
# app/core/config.py
class Settings(BaseSettings):
    SECRET_KEY: str  # No default — app crashes if missing
    OPENAI_API_KEY: str  # Required
    GEMINI_API_KEY: str  # Required for fallback

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if v in ("your-secret-key-here", "", "changeme"):
            raise ValueError("SECRET_KEY must be set to a secure random value")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        return v
```

#### 5b. Centralize All Config
All API keys, model names, and feature flags go through `Settings`. No more `os.getenv()` scattered in service files.

#### 5c. Create `.env.example`
```env
# .env.example
SECRET_KEY=generate-a-64-char-random-string
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/interview_ace

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.2-2025-12-11
GEMINI_API_KEY=AIza...
GEMINI_MODEL=gemini-2.0-flash

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=

ALLOWED_ORIGINS=["http://localhost:3000"]
SENTRY_DSN=
REDIS_URL=redis://localhost:6379/0
```

### Why
- Prevents accidental deployment with insecure defaults
- Single source of truth for all configuration
- Onboarding new developers becomes trivial

---

## 6. CORS Fix — Remove Wildcard

### Current State
`main.py` adds `CORSMiddleware` with `allow_origins=["*"]` **before** `setup_middleware()` also adds CORS. Double middleware, wildcard active.

### What Changes
- **Remove** the `CORSMiddleware` block from `main.py`
- `setup_middleware()` in `middleware.py` already reads `settings.ALLOWED_ORIGINS` — let it be the single CORS handler
- Set `ALLOWED_ORIGINS` explicitly in `.env`

### Why
- Wildcard CORS + `allow_credentials=True` is a security vulnerability
- Double CORS middleware causes unpredictable header behavior

---

## 7. Background Task Processing — Celery + Redis

### Current State
LLM calls (resume parsing, question generation, answer evaluation) are synchronous and block the request thread for 2–10+ seconds. Under load, this starves all other users.

### What Changes
- Add `celery` + `redis` as task queue
- Resume parsing → async task → returns `202 Accepted` + task ID
- Question generation → async task
- New endpoints: `GET /tasks/{task_id}` to poll status

```python
# app/infrastructure/tasks/celery_app.py
from celery import Celery

celery_app = Celery("interview_ace", broker=settings.REDIS_URL)

@celery_app.task
def parse_resume_task(file_path: str, user_id: str):
    # ... calls ResumeService.parse()
    pass
```

### Dependencies
```
celery[redis]>=5.4
redis>=5.0
```

### Why
- LLM latency doesn't block HTTP threads
- Users get immediate response with progress tracking
- Horizontally scalable: add more Celery workers independently

---

## 8. Redis-Backed Rate Limiting

### Current State
In-memory `dict` — resets on restart, doesn't work with multiple workers.

### What Changes
- Replace `RateLimitMiddleware` with `slowapi` backed by Redis
- Per-endpoint rate limits (e.g., `/auth/login` → 5/min, `/resume/` → 10/min)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, storage_uri=settings.REDIS_URL)
```

### Dependencies
```
slowapi>=0.1.9
```

### Why
- Persistent across restarts / deployments
- Shared across all workers and replicas
- Granular per-endpoint control

---

## 9. Structured JSON Logging + Request Tracing

### Current State
`logging.getLogger(__name__)` with default `StreamHandler`. No structured format, no request IDs.

### What Changes
- Centralized logging config in `app/core/logging_config.py`
- JSON-formatted output for log aggregators (Datadog, CloudWatch, Loki)
- Request ID middleware: generates UUID per request, injects into all log lines
- Correlation across LLM calls, DB queries, and HTTP responses

```python
# app/core/logging_config.py
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.BoundLogger,
)
```

### Dependencies
```
structlog>=24.0
```

### Why
- Enables debugging in production without SSH access
- Request tracing across distributed components (API → Celery → LLM → DB)
- Required for any serious observability setup

---

## 10. Error Monitoring — Sentry

### Current State
No error tracking. Unhandled exceptions are invisible unless someone reads raw logs.

### What Changes
```python
# main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration(), SqlalchemyIntegration()],
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
)
```

### Dependencies
```
sentry-sdk[fastapi]>=2.0
```

### Why
- Instant alerts on production errors
- Stack traces with local variables
- Performance monitoring out of the box

---

## 11. Health Check & Readiness Probes

### Current State
No health endpoint. Load balancers and orchestrators can't determine service status.

### What Changes
```python
@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok", "version": settings.VERSION}

@app.get("/ready", tags=["infra"])
async def readiness(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ready", "db": "ok"}
```

### Why
- Required for Kubernetes, ECS, Railway, and any reverse proxy
- Distinguishes between "app is running" and "app can serve traffic"

---

## 12. Testing — pytest + Coverage

### Current State
Zero tests.

### What Changes
```
tests/
├── conftest.py                    # Shared fixtures (test DB, auth tokens, mock LLM)
├── unit/
│   ├── test_security.py           # JWT encode/decode, bcrypt
│   ├── test_resume_service.py     # Business logic, no I/O
│   ├── test_interview_service.py
│   └── test_llm_factory.py        # Fallback chain
├── integration/
│   ├── test_auth_endpoints.py     # Register → Login → Refresh → Logout
│   ├── test_resume_endpoints.py   # Upload → Analyze → List → Delete
│   └── test_interview_endpoints.py
└── fixtures/
    ├── sample_resume.pdf
    └── sample_resume.docx
```

### Dependencies
```
pytest>=8.0
pytest-asyncio>=0.24
httpx>=0.27               # async test client for FastAPI
factory-boy>=3.3
coverage>=7.0
```

### Coverage Target
- Minimum: **80%** line coverage before merge (enforced by CI)

### Why
- Prevents regressions on every change
- Confidence to refactor architecture
- Required for CI/CD pipeline

---

## 13. Pagination on List Endpoints

### Current State
`GET /interview/history` and `GET /resume/` return all records. Full table scans on growing datasets.

### What Changes
- Standard `skip`/`limit` pagination on all list endpoints
- Return `total_count` in response metadata
- Default `limit=20`, max `limit=100`

```python
# app/schemas/common.py
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int
    has_more: bool
```

### Why
- Prevents unbounded queries
- Better UX for frontend pagination
- Reduces DB load

---

## 14. Token Blacklist Pruning & Redis Migration

### Current State
`TokenBlacklist` table grows indefinitely. Every `is_blacklisted` check scans increasing rows.

### What Changes
**Option A (Quick):** Scheduled cleanup job
```python
# Celery beat task — runs every hour
@celery_app.task
def prune_expired_tokens():
    db.query(TokenBlacklist).filter(TokenBlacklist.expires_at < datetime.utcnow()).delete()
```

**Option B (Better):** Migrate token blacklist to Redis with auto-expiry
```python
# On logout:
redis.setex(f"blacklist:{token_jti}", ttl=access_token_ttl, value="1")

# On auth check:
is_blacklisted = redis.exists(f"blacklist:{token_jti}")
```

### Why
- Prevents query degradation over time
- Redis approach eliminates the DB table entirely for this use case

---

## 15. Lazy-Load Heavy ML Models

### Current State
`hf_ner = pipeline("ner", grouped_entities=True)` runs at module import → downloads model on every worker startup, even if never used.

### What Changes
If keeping HuggingFace as a tertiary fallback:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_hf_ner():
    from transformers import pipeline
    return pipeline("ner", grouped_entities=True)
```

**Recommended:** Remove HuggingFace NER entirely. With OpenAI primary + Gemini fallback, a third LLM fallback is unnecessary. This also removes `torch` (~2 GB) from dependencies.

### Why
- Faster startup
- Smaller Docker image
- Two LLM providers is sufficient redundancy

---

## 16. Cloud File Storage — S3 / R2

### Current State
Resumes saved to local `uploads/` directory. Breaks with multiple replicas, lost on container restart.

### What Changes
- Abstract `IFileStorage` interface in domain layer
- `LocalStorage` for development
- `S3Storage` for production (works with AWS S3, Cloudflare R2, MinIO)

```python
class S3Storage(IFileStorage):
    def __init__(self, bucket: str, client: boto3.client):
        self.bucket = bucket
        self.client = client

    async def save(self, file: UploadFile, key: str) -> str:
        self.client.upload_fileobj(file.file, self.bucket, key)
        return f"s3://{self.bucket}/{key}"
```

### Dependencies
```
boto3>=1.35
```

### Why
- Persistent across deploys
- CDN-ready
- Works with horizontal scaling

---

## 17. Role-Based Access Control (RBAC)

### Current State
No `role` field on `User`. All authenticated users have identical permissions. No admin panel.

### What Changes
- Add `role` column to `users` table (`user`, `admin`, `moderator`)
- Role-checking dependency for protected endpoints
- Admin-only endpoints for user management, system stats

```python
class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

def require_role(role: UserRole):
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(403, "Insufficient permissions")
        return current_user
    return dependency
```

### Why
- Required for admin dashboards
- Prevents unauthorized access to admin-level operations
- Foundation for multi-tenant features

---

## 18. Docker & Docker Compose

### Current State
No containerization. Manual deployment only.

### What Changes
```
backend/
├── Dockerfile
├── .dockerignore
docker-compose.yml
docker-compose.override.yml    # dev overrides (volume mounts, debug)
```

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: interview_ace
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  api:
    build: ./backend
    depends_on: [db, redis]
    ports: ["8000:8000"]
    env_file: .env

  celery_worker:
    build: ./backend
    command: celery -A app.infrastructure.tasks.celery_app worker -l info
    depends_on: [redis, db]
    env_file: .env

volumes:
  pgdata:
```

### Why
- Reproducible environments
- One-command local setup: `docker compose up`
- Foundation for cloud deployments

---

## 19. CI/CD — GitHub Actions

### Current State
No automation. No test runs, no linting, no deploy triggers.

### What Changes
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - run: ruff check backend/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_DB: test_db, POSTGRES_USER: test, POSTGRES_PASSWORD: test }
        ports: ["5432:5432"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v4
```

### Dependencies
```
ruff           # linter + formatter
```

### Why
- Automated quality gates on every push/PR
- Catch regressions before merge
- Foundation for automated deployments

---

## 20. Developer Experience — .env.example, pre-commit, linting

### What Changes
- `.env.example` with all required variables and placeholders
- `pre-commit` hooks for:
  - `ruff check` (lint)
  - `ruff format` (format)
  - `mypy` (type checking)
- `pyproject.toml` for unified tool configuration

```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
select = ["E", "W", "F", "I", "N", "UP", "B", "A", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### Why
- Consistent code style across contributors
- Type safety catches bugs before runtime
- Faster onboarding

---

## 21. API Versioning & OpenAPI Enhancements

### What Changes
- Keep `/api/v1` as current
- Add `/api/v2` stub for future breaking changes
- Enrich OpenAPI metadata:
  - Detailed endpoint descriptions
  - Request/response examples
  - Error response schemas
  - Tags with descriptions

### Why
- Non-breaking API evolution
- Auto-generated, accurate API docs for frontend team

---

## 22. Soft Deletes & Audit Trail

### Current State
Hard deletes everywhere. No record of who deleted what or when.

### What Changes
- Add `deleted_at` (nullable timestamp) to key tables
- All "delete" operations set `deleted_at` instead of `DELETE`
- Query filters automatically exclude soft-deleted records
- Optional: `AuditLog` table for important mutations

```python
class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(UUID, nullable=True)

    @hybrid_property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
```

### Why
- Data recovery capability
- Compliance and audit requirements
- Prevents accidental permanent data loss

---

## 23. CHANGELOG.md Maintenance

### What Changes
- Create `CHANGELOG.md` in project root
- Follow [Keep a Changelog](https://keepachangelog.com/) format
- Update on every feature branch merge
- Categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`

### Why
- Clear release history for the team
- Required for professional open-source or enterprise projects
- Makes rollback decisions easier

---

## Priority Matrix

| Priority | Upgrade | Effort |
|---|---|---|
| 🔴 P0 — Critical | 6. CORS Fix | 15 min |
| 🔴 P0 — Critical | 5. Secrets Hardening | 1 hour |
| 🔴 P0 — Critical | 3. Alembic Migrations | 2 hours |
| 🔴 P0 — Critical | 1. Clean Architecture Refactor | 2–3 days |
| 🟠 P1 — High | 2. OpenAI + Gemini Fallback | 4–6 hours |
| 🟠 P1 — High | 4. Async DB (asyncpg) | 4–6 hours |
| 🟠 P1 — High | 9. Structured Logging | 2–3 hours |
| 🟠 P1 — High | 12. Tests | 2–3 days |
| 🟡 P2 — Medium | 7. Celery + Redis Tasks | 1 day |
| 🟡 P2 — Medium | 8. Redis Rate Limiting | 2–3 hours |
| 🟡 P2 — Medium | 10. Sentry | 30 min |
| 🟡 P2 — Medium | 11. Health Check | 30 min |
| 🟡 P2 — Medium | 13. Pagination | 2–3 hours |
| 🟡 P2 — Medium | 14. Token Blacklist Pruning | 1–2 hours |
| 🟡 P2 — Medium | 15. Lazy-Load ML Models | 1 hour |
| 🟡 P2 — Medium | 17. RBAC | 3–4 hours |
| 🟢 P3 — Low | 16. S3 File Storage | 3–4 hours |
| 🟢 P3 — Low | 18. Docker & Compose | 2–3 hours |
| 🟢 P3 — Low | 19. CI/CD | 2–3 hours |
| 🟢 P3 — Low | 20. DX (linting, pre-commit) | 1–2 hours |
| 🟢 P3 — Low | 21. API Versioning | 1–2 hours |
| 🟢 P3 — Low | 22. Soft Deletes | 2–3 hours |
| 🟢 P3 — Low | 23. CHANGELOG | 15 min |

---

## Dependency Changes Summary

### Add
```
openai>=1.60.0
asyncpg
sqlalchemy[asyncio]
alembic>=1.14
celery[redis]>=5.4
redis>=5.0
slowapi>=0.1.9
structlog>=24.0
sentry-sdk[fastapi]>=2.0
boto3>=1.35
pytest>=8.0
pytest-asyncio>=0.24
httpx>=0.27
factory-boy>=3.3
coverage>=7.0
ruff
mypy
pre-commit
```

### Remove (or make optional)
```
torch                   # ~2 GB, replaced by OpenAI/Gemini fallback
transformers            # no longer needed for NER fallback
spacy                   # no longer needed
psycopg2-binary         # replaced by asyncpg
google-genai            # keep, but only for fallback path
```

---

*This document lives in `Docs/UPGRADES.md` and will be updated as upgrades are implemented.*
