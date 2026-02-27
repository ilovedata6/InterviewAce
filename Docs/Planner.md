# InterviewAce — Implementation Planner

> **Purpose:** One feature per phase. Each phase = one or more atomic commits. Complete one phase fully before starting the next.  
> **Status Legend:** ⬜ Not Started · 🟡 In Progress · ✅ Done

---

## Phase 0 — Foundation & Housekeeping
> *Goal: Set up the scaffolding that every future phase depends on.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 0.1 | Create `CHANGELOG.md` with initial entry | `docs: add CHANGELOG.md` | ✅ |
| 0.2 | Create `.env.example` with all required variables | `chore: add .env.example` | ✅ |
| 0.3 | Fix wildcard CORS in `main.py` — remove duplicate middleware, use `settings.ALLOWED_ORIGINS` | `fix: remove wildcard CORS, use settings.ALLOWED_ORIGINS` | ✅ |
| 0.4 | Harden `SECRET_KEY` — fail-fast if missing or insecure default | `security: require strong SECRET_KEY, no insecure defaults` | ✅ |
| 0.5 | Add `pyproject.toml` with ruff, mypy, pytest config | `chore: add pyproject.toml with tool configs` | ✅ |

**Checkpoint:** App boots with `.env` only, rejects bad secrets, CORS is locked down.

---

## Phase 1 — Alembic Migrations
> *Goal: Replace `create_all()` with tracked, reversible migrations.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 1.1 | Install `alembic`, run `alembic init alembic` | `feat: initialize alembic for DB migrations` | ✅ |
| 1.2 | Configure `alembic/env.py` to use `settings.DATABASE_URL` and `Base.metadata` | `feat: wire alembic env.py to app settings and models` | ✅ |
| 1.3 | Generate initial migration: `alembic revision --autogenerate -m "initial schema"` | `feat: add initial alembic migration` | ✅ |
| 1.4 | Remove `Base.metadata.create_all()` from `init_db.py` and app startup | `refactor: remove create_all, migrations handle schema` | ✅ |
| 1.5 | Update `CHANGELOG.md` | `docs: update changelog for alembic` | ✅ |

**Checkpoint:** `alembic upgrade head` creates all tables. `alembic downgrade base` removes them.

---

## Phase 2 — Clean Architecture Scaffold
> *Goal: Create the new directory structure with interfaces and move code layer by layer.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 2.1 | Create `domain/` layer: `entities/`, `interfaces/`, `value_objects/`, `services/` | `refactor: add domain layer scaffold` | ✅ |
| 2.2 | Define domain interfaces: `ILLMProvider`, `IUserRepository`, `IResumeRepository`, `IInterviewRepository`, `IFileStorage`, `IEmailService` | `refactor: define domain interfaces (ABCs)` | ✅ |
| 2.3 | Create `application/` layer: `use_cases/`, `dto/` | `refactor: add application layer scaffold` | ✅ |
| 2.4 | Create `infrastructure/` layer: `persistence/`, `llm/`, `storage/`, `email/` | `refactor: add infrastructure layer scaffold` | ✅ |
| 2.5 | Move SQLAlchemy models from `app/models/` → `app/infrastructure/persistence/models/` | `refactor: move ORM models to infrastructure layer` | ✅ |
| 2.6 | Implement `UserRepository`, `ResumeRepository`, `InterviewRepository` (concrete classes implementing domain interfaces) | `refactor: implement repository pattern` | ✅ |
| 2.7 | Create `app/core/exceptions.py` — centralized domain exceptions | `refactor: add custom domain exceptions` | ✅ |
| 2.8 | Update all import paths and verify app boots | `refactor: update imports for clean architecture` | ✅ |
| 2.9 | Update `CHANGELOG.md` | `docs: update changelog for clean architecture` | ✅ |

**Checkpoint:** All existing features work identically. Directory structure matches Clean Architecture. No domain layer imports from infrastructure.

---

## Phase 3 — LLM Provider Migration (OpenAI + Gemini Fallback)
> *Goal: Switch primary LLM to OpenAI GPT-5.2 with Gemini as automatic fallback.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 3.1 | Add `openai>=1.60.0` to requirements, add `OPENAI_API_KEY` and `OPENAI_MODEL` to `Settings` | `feat: add openai dependency and config` | ✅ |
| 3.2 | Implement `OpenAIProvider(ILLMProvider)` with async `generate_json()` and `generate_completion()` | `feat: implement OpenAI LLM provider` | ✅ |
| 3.3 | Refactor existing Gemini code into `GeminiProvider(ILLMProvider)` | `refactor: extract Gemini into provider implementing ILLMProvider` | ✅ |
| 3.4 | Implement `LLMProviderFactory` with ordered fallback chain | `feat: add LLM factory with automatic fallback` | ✅ |
| 3.5 | Wire `LLMProviderFactory` into `InterviewOrchestrator` and `ResumeParser` via dependency injection | `refactor: inject LLM provider via factory into services` | ✅ |
| 3.6 | Update prompts for OpenAI JSON mode (remove markdown fence cleaning) | `refactor: update prompts for OpenAI native JSON mode` | ✅ |
| 3.7 | Remove `torch`, `transformers`, `spacy` from requirements (optional: keep as dev dependency) | `chore: remove heavy ML deps, OpenAI+Gemini replaces NER` | ✅ |
| 3.8 | Test both providers independently + fallback scenario | `test: verify OpenAI primary and Gemini fallback` | ✅ |
| 3.9 | Update `CHANGELOG.md` | `docs: update changelog for LLM migration` | ✅ |

**Checkpoint:** `/resume/` upload uses OpenAI. If OpenAI fails, Gemini takes over transparently. Docker image is ~2 GB smaller.

---

## Phase 4 — Async Database Layer
> *Goal: Non-blocking DB access with asyncpg.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 4.1 | Add `asyncpg` to requirements; keep `psycopg2-binary` for Alembic CLI | `feat: add asyncpg async DB driver` | ✅ |
| 4.2 | Rewrite `db/session.py` with `create_async_engine`, `async_sessionmaker`, `AsyncSession` | `refactor: async database session factory` | ✅ |
| 4.3 | Add `async_database_url` property to config; update `get_db()` to async generator | `refactor: make get_db async generator` | ✅ |
| 4.4 | Convert all repository interfaces + implementations to async (`await session.execute(...)`) | `refactor: convert repositories to async` | ✅ |
| 4.5 | Convert all endpoint handlers and services to `async def` with `select()` pattern | `refactor: make all endpoints async` | ✅ |
| 4.6 | Alembic `env.py` kept sync (CLI tool); uses `settings.database_url` with psycopg2 driver | `chore: alembic env.py stays sync by design` | ✅ |
| 4.7 | Install asyncpg, verify imports, confirm session module loads | `test: verify async DB operations` | ✅ |
| 4.8 | Update `CHANGELOG.md` | `docs: update changelog for async DB` | ✅ |

**Checkpoint:** All DB operations are non-blocking. `psycopg2` retained for Alembic only.

---

## Phase 5 — Structured Logging + Health Check
> *Goal: Production-grade observability.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 5.1 | Add `structlog` to requirements | `feat: add structlog dependency` | ✅ |
| 5.2 | Create `app/core/logging_config.py` — JSON formatter, request ID processor | `feat: structured JSON logging with structlog` | ✅ |
| 5.3 | Add request-ID middleware: generate UUID per request, add to all logs + response headers | `feat: request ID middleware for log correlation` | ✅ |
| 5.4 | Replace all `logging.getLogger()` calls with `structlog.get_logger()` | `refactor: migrate all loggers to structlog` | ✅ |
| 5.5 | Add `GET /health` and `GET /ready` endpoints | `feat: add health and readiness endpoints` | ✅ |
| 5.6 | Update `CHANGELOG.md` | `docs: update changelog for logging and health` | ✅ |

**Checkpoint:** All logs are JSON. Every request has a traceable ID. `/health` and `/ready` respond.

---

## Phase 6 — Testing Foundation
> *Goal: Test infrastructure + critical path coverage.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 6.1 | Add `pytest`, `pytest-asyncio`, `httpx`, `factory-boy`, `coverage` to requirements | `chore: add test dependencies` | ✅ |
| 6.2 | Create `tests/conftest.py` — test DB, async client, auth fixtures, mock LLM | `test: add test conftest with fixtures` | ✅ |
| 6.3 | Write unit tests for `security.py` (JWT, bcrypt, token validation) | `test: unit tests for security module` | ✅ |
| 6.4 | Write unit tests for `LLMProviderFactory` (fallback chain) | `test: unit tests for LLM factory fallback` | ✅ |
| 6.5 | Write integration tests for auth endpoints (register → login → refresh → logout) | `test: integration tests for auth flow` | ✅ |
| 6.6 | Write integration tests for resume endpoints (upload → analyze → list → delete) | `test: integration tests for resume flow` | ✅ |
| 6.7 | Write integration tests for interview endpoints (start → answer → complete → summary) | `test: integration tests for interview flow` | ✅ |
| 6.8 | Add test fixtures: `sample_resume.pdf`, `sample_resume.docx` | `test: add sample resume fixtures` | ✅ |
| 6.9 | Update `CHANGELOG.md` | `docs: update changelog for testing` | ✅ |

**Checkpoint:** `pytest tests/ -v --cov=app` passes with ≥80% coverage on critical paths.

---

## Phase 7 — Redis, Rate Limiting, Token Pruning
> *Goal: Redis-backed infrastructure for rate limiting and token management.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 7.1 | Add `redis`, `slowapi` to requirements; add `REDIS_URL` to settings | `feat: add redis and slowapi dependencies` | ✅ |
| 7.2 | Replace in-memory `RateLimitMiddleware` with `slowapi` + Redis backend | `feat: Redis-backed rate limiting with slowapi` | ✅ |
| 7.3 | Add per-endpoint rate limits (login: 5/min, resume upload: 10/min, etc.) | `feat: granular per-endpoint rate limits` | ✅ |
| 7.4 | Migrate token blacklist to Redis with key expiry (or add Celery beat pruning task) | `feat: token blacklist auto-pruning` | ✅ |
| 7.5 | Update `CHANGELOG.md` | `docs: update changelog for redis integration` | ✅ |

**Checkpoint:** Rate limits persist across restarts. Expired tokens auto-cleanup.

---

## Phase 8 — Background Tasks (Celery)
> *Goal: LLM calls no longer block HTTP threads.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 8.1 | Add `celery[redis]` to requirements | `feat: add celery for background tasks` | ✅ |
| 8.2 | Create `app/infrastructure/tasks/celery_app.py` — Celery app config | `feat: celery app configuration` | ✅ |
| 8.3 | Create `parse_resume_task` — async resume parsing via Celery | `feat: async resume parsing via celery task` | ✅ |
| 8.4 | Update `/resume/` endpoint to return `202 Accepted` + task ID | `refactor: resume upload returns 202 with task ID` | ✅ |
| 8.5 | Add `GET /tasks/{task_id}` endpoint to check task status | `feat: task status polling endpoint` | ✅ |
| 8.6 | Add Celery worker to `docker-compose.yml` | `chore: add celery worker service to compose` | ✅ |
| 8.7 | Update `CHANGELOG.md` | `docs: update changelog for celery` | ✅ |

**Checkpoint:** Resume upload returns instantly. Parsing happens in background. Client polls for result.

---

## Phase 9 — Sentry + Error Monitoring
> *Goal: Instant visibility into production errors.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 9.1 | Add `sentry-sdk[fastapi]` to requirements; add `SENTRY_DSN` to settings | `feat: add sentry error monitoring` | ✅ |
| 9.2 | Initialize Sentry in `main.py` with FastAPI + SQLAlchemy integrations | `feat: initialize sentry with fastapi integration` | ✅ |
| 9.3 | Add `ENVIRONMENT` setting (dev/staging/prod) for Sentry environment tagging | `feat: environment-aware sentry config` | ✅ |
| 9.4 | Update `CHANGELOG.md` | `docs: update changelog for sentry` | ✅ |

**Checkpoint:** Unhandled exceptions appear in Sentry dashboard with full context.

---

## Phase 10 — Pagination + RBAC
> *Goal: Bounded queries and role-based access.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 10.1 | Create `PaginatedResponse` schema with `items`, `total`, `skip`, `limit`, `has_more` | `feat: add paginated response schema` | ✅ |
| 10.2 | Add pagination to `GET /resume/` and `GET /interview/history` | `feat: paginate resume and interview list endpoints` | ✅ |
| 10.3 | Add `role` column to `users` table + Alembic migration | `feat: add user roles (user, admin, moderator)` | ✅ |
| 10.4 | Create `require_role()` dependency for role-gated endpoints | `feat: role-based access control dependency` | ✅ |
| 10.5 | Update `CHANGELOG.md` | `docs: update changelog for pagination and RBAC` | ✅ |

**Checkpoint:** List endpoints return paginated results. Admin endpoints require admin role.

---

## Phase 11 — Docker & Docker Compose
> *Goal: One-command local setup and deployment-ready containers.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 11.1 | Create `backend/Dockerfile` (multi-stage, slim image) | `chore: add Dockerfile for backend` | ⬜ |
| 11.2 | Create `backend/.dockerignore` | `chore: add .dockerignore` | ⬜ |
| 11.3 | Create `docker-compose.yml` (api, db, redis, celery worker) | `chore: add docker-compose for full stack` | ⬜ |
| 11.4 | Create `docker-compose.override.yml` for dev (volume mounts, hot reload) | `chore: add docker-compose dev overrides` | ⬜ |
| 11.5 | Update `CHANGELOG.md` | `docs: update changelog for docker` | ⬜ |

**Checkpoint:** `docker compose up` starts the entire stack. `docker compose down -v` cleans up.

---

## Phase 12 — CI/CD Pipeline
> *Goal: Automated quality gates and deployment.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 12.1 | Create `.github/workflows/ci.yml` — lint (ruff) + test (pytest) + coverage | `ci: add GitHub Actions CI pipeline` | ✅ |
| 12.2 | Add coverage threshold enforcement (fail if <80%) | `ci: enforce 80% coverage threshold` | ✅ |
| 12.3 | Add `pre-commit` config (`.pre-commit-config.yaml`) | `chore: add pre-commit hooks` | ✅ |
| 12.4 | Update `CHANGELOG.md` | `docs: update changelog for CI/CD` | ✅ |

**Checkpoint:** PRs are blocked if tests fail or coverage drops below 80%.

---

## Phase 13 — Cloud Storage + Soft Deletes
> *Goal: Production file storage and data safety.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 13.1 | Implement `S3Storage(IFileStorage)` with boto3 | `feat: S3 file storage implementation` | ⬜ |
| 13.2 | Add storage toggle in config: `STORAGE_BACKEND=local|s3` | `feat: configurable storage backend` | ⬜ |
| 13.3 | Add `SoftDeleteMixin` — `deleted_at`, `deleted_by` columns | `feat: soft delete mixin for models` | ⬜ |
| 13.4 | Apply soft deletes to `resumes` and `interview_sessions` + migration | `feat: enable soft deletes on resumes and sessions` | ⬜ |
| 13.5 | Update repository queries to exclude soft-deleted records | `refactor: filter soft-deleted records in repositories` | ⬜ |
| 13.6 | Update `CHANGELOG.md` | `docs: update changelog for storage and soft deletes` | ⬜ |

**Checkpoint:** Files stored in S3 (or local in dev). Deleted records are recoverable.

---

## Phase 14 — Final Polish
> *Goal: Documentation, API docs, and cleanup.*

| # | Task | Commit Message | Status |
|---|---|---|---|
| 14.1 | Enrich OpenAPI schema — descriptions, examples, error schemas per endpoint | `docs: enrich OpenAPI endpoint documentation` | ✅ |
| 14.2 | Update all `Docs/` files to reflect new architecture | `docs: update architecture and API docs` | ✅ |
| 14.3 | Final `CHANGELOG.md` entry for v2.0.0 release | `docs: finalize CHANGELOG for v2.0.0` | ✅ |
| 14.4 | Update `README.md` with new setup instructions | `docs: update README for new stack` | ✅ |
| 14.5 | Tag release: `git tag v2.0.0` | — | ⬜ |

**Checkpoint:** All docs accurate. `v2.0.0` tagged and ready.

---

## Execution Rules

1. **One phase at a time.** Do not start Phase N+1 until Phase N is fully complete and committed.
2. **Atomic commits.** Each row in the table above = one commit.
3. **Test before commit.** Every commit should leave the app in a bootable, working state.
4. **Update CHANGELOG.** Last task in every phase is a changelog entry.
5. **No partial phases.** If a phase is half-done, finish it before moving on.

---

## Progress Tracker

| Phase | Name | Status |
|---|---|---|
| 0 | Foundation & Housekeeping | ✅ |
| 1 | Alembic Migrations | ✅ |
| 2 | Clean Architecture Scaffold | ✅ |
| 3 | LLM Provider Migration | ✅ |
| 4 | Async Database Layer | ✅ |
| 5 | Structured Logging + Health Check | ✅ |
| 6 | Testing Foundation | ✅ |
| 7 | Redis, Rate Limiting, Token Pruning | ✅ |
| 8 | Background Tasks (Celery) | ✅ |
| 9 | Sentry + Error Monitoring | ✅ |
| 10 | Pagination + RBAC | ✅ |
| 11 | Docker & Docker Compose | ⬜ |
| 12 | CI/CD Pipeline | ✅ |
| 13 | Cloud Storage + Soft Deletes | ⬜ |
| 14 | Final Polish | ✅ |

---

*This planner lives in `Docs/Planner.md`. Update task statuses as you go.*
