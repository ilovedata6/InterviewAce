# InterviewAce

AI-powered interview preparation platform. Upload your resume, get it analysed by an LLM, then run personalised mock interviews with real-time AI feedback — all through a modern Next.js dashboard.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/node-22+-green?logo=node.js&logoColor=white" />
  <img src="https://img.shields.io/badge/Next.js-16-black?logo=next.js" />
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

---

## Features

### Resume Module
- Upload **PDF / DOCX** resumes (up to 10 MB)
- Background LLM-powered parsing via **Celery** (returns `202 Accepted` + task ID)
- Structured JSON output — name, skills, experience, education, inferred role, confidence score
- Resume **versioning** (parent / child chains) and **public share** tokens
- Export resume data

### Interview Module
- AI-generated questions (12–15 per session: technical, behavioural, project-based)
- Per-answer AI evaluation with **score + feedback**
- Session completion with final score and overall summary
- Stateful question-by-question navigation
- Full interview **history** with pagination

### Authentication & Security
- JWT access tokens (15 min) + refresh tokens (7 days)
- Email verification, password reset, change password (last 5 blocked)
- **Role-based access control** — `user` / `admin` / `moderator`
- Redis-backed rate limiting (slowapi) and token blacklist
- Login-attempt tracking and account lockout
- Deactivated-user blocking (login + existing tokens)

### Admin Panel
- Platform statistics dashboard (users, interviews, resumes, scores)
- User management — list, deactivate / reactivate, change roles
- Self-deactivation guard

### Dashboard & Analytics
- Total interviews, average score, category breakdowns
- Score trend chart, interview frequency chart, skill radar
- Recent activity feed and quick-action shortcuts

---

## Tech Stack

### Backend

| Layer | Technology |
|---|---|
| Framework | **FastAPI 0.109** + Uvicorn (async ASGI) |
| Database | **PostgreSQL 16** + asyncpg (SQLAlchemy 2.0 async) |
| Migrations | Alembic |
| Cache / Broker | **Redis 7** |
| Rate Limiting | slowapi (Redis backend) |
| Background Tasks | **Celery 5.4** (Redis broker + backend) |
| LLM (primary) | OpenAI GPT-5.2 (JSON mode) |
| LLM (fallback) | Google Gemini 2.0 Flash |
| Auth | JWT (bcrypt 12 rounds, password history) |
| Logging | structlog (JSON prod / coloured dev) |
| Monitoring | Sentry (optional) |
| Testing | pytest + httpx + aiosqlite (≥ 80 % coverage) |
| Linting | Ruff + pre-commit |

### Frontend

| Layer | Technology |
|---|---|
| Framework | **Next.js 16** (App Router, standalone output) |
| Language | TypeScript 5 |
| UI | **Tailwind CSS 4** + **Radix UI** + **shadcn/ui** |
| State | Zustand 5 + TanStack React Query 5 |
| Forms | React Hook Form 7 + Zod 4 |
| Charts | Recharts 3 |
| Toasts | Sonner 2 |
| Testing | Vitest + Testing Library + Playwright |
| Linting | ESLint 9 + Prettier |

### Infrastructure

| Tool | Purpose |
|---|---|
| Docker Compose | One-command local stack (Postgres, Redis, Backend, Celery, Frontend) |
| GitHub Actions | CI — lint → test → coverage enforcement |
| pre-commit | Ruff, trailing whitespace, YAML/TOML checks, secret detection |

---

## Prerequisites

| Tool | Version | Check |
|---|---|---|
| Python | ≥ 3.11 | `python --version` |
| Node.js | ≥ 22 | `node --version` |
| pnpm | ≥ 10 | `pnpm --version` |
| PostgreSQL | ≥ 15 | `psql --version` |
| Redis | ≥ 7 | `redis-cli ping` |
| Docker (opt.) | ≥ 24 | `docker --version` |

---

## Quick Start

### 1 — Clone

```bash
git clone https://github.com/ilovedata6/InterviewAce.git
cd InterviewAce
```

### 2 — Backend

```bash
cd backend
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r ../requirements.txt

copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux
```

Edit `backend/.env`:

```dotenv
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_hex(32))">
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=interview_ace
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

Run migrations and start the server:

```bash
alembic upgrade head
uvicorn main:app --reload          # → http://localhost:8000
```

Start the Celery worker (separate terminal):

```bash
celery -A app.infrastructure.tasks.celery_app worker --loglevel=info
```

### 3 — Frontend

```bash
cd frontend
pnpm install
pnpm dev                            # → http://localhost:3000
```

### 4 — Docker (alternative)

```bash
docker compose up -d                # Postgres + Redis + Backend + Celery + Frontend
```

---

## API Documentation

| Docs | URL |
|---|---|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Health (liveness) | `GET /health` |
| Readiness | `GET /ready` |

---

## Project Structure

```
InterviewAce/
├── docker-compose.yml
├── pyproject.toml                          # Ruff, mypy, pytest, coverage config
├── requirements.txt                        # Python dependencies
├── CHANGELOG.md
├── GETTING_STARTED.md
│
├── Docs/                                   # Project documentation
│   ├── PROJECT_OVERVIEW.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DATABASE_SCHEMA.md
│   ├── FRONTEND_ARCHITECTURE.md
│   ├── FRONTEND_STACK_DECISION.md
│   ├── PRODUCTION_READINESS.md
│   └── ...
│
├── backend/                                # FastAPI application
│   ├── main.py                             # App entry-point + lifespan
│   ├── alembic.ini
│   ├── alembic/                            # DB migrations
│   │   └── versions/                       # 4 migration scripts
│   └── app/
│       ├── api/
│       │   ├── deps.py                     # Shared deps (get_current_user, require_role)
│       │   ├── health.py                   # /health + /ready probes
│       │   └── v1/endpoints/
│       │       ├── auth/                   # 11 auth endpoints
│       │       │   ├── register.py
│       │       │   ├── login.py
│       │       │   ├── logout.py
│       │       │   ├── me.py
│       │       │   ├── refresh.py
│       │       │   ├── verify_email.py
│       │       │   ├── resend_verification.py
│       │       │   ├── change_password.py
│       │       │   ├── reset_password_request.py
│       │       │   └── reset_password_confirm.py
│       │       ├── interview/              # 8 interview endpoints
│       │       │   ├── start.py
│       │       │   ├── session.py
│       │       │   ├── next_question.py
│       │       │   ├── answer.py
│       │       │   ├── complete.py
│       │       │   ├── summary.py
│       │       │   └── history.py
│       │       ├── resume/                 # 7 resume endpoints
│       │       │   ├── upload.py
│       │       │   ├── management.py
│       │       │   ├── analysis.py
│       │       │   ├── version.py
│       │       │   ├── sharing.py
│       │       │   └── export.py
│       │       ├── admin.py                # Admin stats + user management
│       │       ├── dashboard.py            # Dashboard aggregations
│       │       └── tasks.py                # Celery task polling
│       ├── application/                    # Use-cases + DTOs (Clean Architecture)
│       │   ├── dto/
│       │   │   ├── auth.py
│       │   │   ├── interview.py
│       │   │   └── resume.py
│       │   └── use_cases/
│       │       ├── auth/
│       │       ├── interview/
│       │       └── resume/
│       ├── core/                           # Cross-cutting concerns
│       │   ├── config.py                   # pydantic-settings (all env vars)
│       │   ├── security.py                 # JWT, bcrypt, sessions, token blacklist
│       │   ├── middleware.py               # Security headers, rate limiting
│       │   ├── exceptions.py               # Domain → HTTP error mapping
│       │   └── logging_config.py           # structlog pipeline
│       ├── db/
│       │   ├── session.py                  # Async engine + session factory
│       │   └── init_db.py
│       ├── domain/                         # Pure business logic
│       │   ├── entities/                   # UserEntity, ResumeEntity, InterviewSessionEntity
│       │   ├── interfaces/                 # Repository & service ABCs
│       │   ├── value_objects/enums.py      # UserRole, ResumeStatus, FileType
│       │   └── exceptions.py               # Domain exception hierarchy
│       ├── infrastructure/                 # External adapters
│       │   ├── cache/
│       │   │   └── redis_client.py         # Async Redis + token blacklist + rate-limit helpers
│       │   ├── llm/
│       │   │   ├── openai_provider.py      # OpenAI GPT-5.2 (JSON mode)
│       │   │   ├── gemini_provider.py      # Gemini 2.0 Flash fallback
│       │   │   └── factory.py              # LLMProviderWithFallback composite
│       │   ├── persistence/
│       │   │   ├── models/                 # SQLAlchemy ORM models (user, resume, interview, security)
│       │   │   └── repositories/           # Async repos (user, resume, interview, auth)
│       │   └── tasks/
│       │       ├── celery_app.py           # Celery config (Redis broker)
│       │       ├── resume_tasks.py         # Background resume parsing
│       │       └── maintenance.py          # Token pruning (Celery Beat)
│       ├── schemas/                        # Pydantic request / response models
│       │   ├── auth.py
│       │   ├── interview.py
│       │   ├── resume.py
│       │   ├── security.py
│       │   ├── user.py
│       │   └── base.py                     # PaginatedResponse[T]
│       ├── services/                       # Business orchestration
│       │   ├── auth_service.py
│       │   ├── interview_orchestrator.py
│       │   ├── resume_parser.py
│       │   ├── resume_exporter.py
│       │   └── ai_analyzer.py
│       └── utils/                          # File handling, email
│   └── tests/                              # pytest suite
│       ├── conftest.py                     # Shared fixtures (async SQLite, mock LLM)
│       ├── unit/
│       │   ├── test_security.py
│       │   └── test_llm_factory.py
│       └── integration/
│           ├── test_auth.py
│           ├── test_interview.py
│           ├── test_resume.py
│           └── test_health.py
│
└── frontend/                               # Next.js 16 application
    ├── package.json
    ├── next.config.ts                      # standalone output
    ├── tsconfig.json                       # strict, @/* path alias
    ├── Dockerfile
    ├── playwright.config.ts
    ├── vitest.config.ts
    └── src/
        ├── middleware.ts                   # Auth redirect middleware
        ├── app/
        │   ├── layout.tsx                  # Root layout (providers, fonts)
        │   ├── page.tsx                    # Landing / hero page
        │   ├── globals.css                 # Tailwind base styles
        │   ├── (auth)/                     # Auth route group
        │   │   ├── login/
        │   │   ├── register/
        │   │   ├── forgot-password/
        │   │   ├── reset-password/
        │   │   └── verify-email/
        │   ├── (app)/                      # Authenticated route group
        │   │   ├── dashboard/              # Stats, charts, quick actions
        │   │   ├── interviews/             # List → start → session → summary
        │   │   ├── resumes/                # List → upload → detail
        │   │   ├── profile/
        │   │   └── admin/                  # Stats + user management (role-gated)
        │   └── api/                        # BFF route handlers (server → backend proxy)
        │       ├── auth/
        │       ├── interviews/
        │       ├── resumes/
        │       ├── dashboard/
        │       └── admin/
        ├── components/
        │   ├── ui/                         # shadcn/ui primitives (button, card, dialog, …)
        │   ├── layout/                     # AppNavbar, AppSidebar, AuthLayout
        │   ├── auth/                       # LoginForm, RegisterForm
        │   ├── dashboard/                  # StatsCards, ScoreTrend, SkillRadar, …
        │   ├── interview/                  # QuestionDisplay, AnswerInput, ProgressBar, …
        │   ├── resume/                     # ResumeCard, UploadZone, Analysis, Versions
        │   ├── admin/                      # UserTable
        │   ├── guards/                     # AdminGuard
        │   ├── providers/                  # AuthProvider, QueryProvider
        │   └── shared/                     # DeleteConfirmDialog
        ├── hooks/                          # useAuth, useDashboard, useInterview, useResumes
        ├── lib/
        │   ├── api-client.ts               # Typed HTTP client (get/post/put/patch/delete)
        │   ├── bff.ts                      # Server-side backend proxy helper
        │   ├── constants.ts
        │   ├── utils.ts                    # cn() + helpers
        │   ├── zod-resolver.ts
        │   └── validations/                # Zod schemas (auth, interview, resume)
        ├── stores/                         # Zustand (auth-store, interview-store)
        └── types/                          # TypeScript interfaces (auth, interview, resume, dashboard)
```

---

## Running Tests

### Backend

```bash
cd backend
python -m pytest tests/ -v --tb=short

# With coverage
coverage run -m pytest tests/
coverage report --fail-under=80
```

### Frontend

```bash
cd frontend
pnpm test              # Vitest unit tests
pnpm test:e2e          # Playwright end-to-end tests
```

---

## Documentation

Detailed docs live in the [`Docs/`](Docs/) folder:

| Document | Description |
|---|---|
| [PROJECT_OVERVIEW.md](Docs/PROJECT_OVERVIEW.md) | High-level feature set and tech stack |
| [ARCHITECTURE.md](Docs/ARCHITECTURE.md) | Clean Architecture layers and data flow |
| [API_REFERENCE.md](Docs/API_REFERENCE.md) | Endpoint catalogue with request / response examples |
| [DATABASE_SCHEMA.md](Docs/DATABASE_SCHEMA.md) | All tables, columns, indexes, and relationships |
| [FRONTEND_ARCHITECTURE.md](Docs/FRONTEND_ARCHITECTURE.md) | Next.js app structure, BFF pattern, state management |
| [FRONTEND_STACK_DECISION.md](Docs/FRONTEND_STACK_DECISION.md) | Framework and library selection rationale |
| [PRODUCTION_READINESS.md](Docs/PRODUCTION_READINESS.md) | Deployment checklist and hardening guide |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Step-by-step setup walkthrough |
| [CHANGELOG.md](CHANGELOG.md) | Release history |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Run `pre-commit install` to enable lint hooks
4. Commit your changes
5. Push to the branch
6. Open a Pull Request

---

## License

MIT