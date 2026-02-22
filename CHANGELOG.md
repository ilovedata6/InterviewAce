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
