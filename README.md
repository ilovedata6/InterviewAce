# Interview Ace

An AI-powered backend that helps users prepare for job interviews by analysing their resume and conducting personalised mock interviews with real-time AI feedback.

## Features

- **Resume Analysis**
  - Upload PDF / DOCX resumes (up to 10 MB)
  - Background LLM-powered parsing via Celery (returns 202 Accepted + task ID)
  - Structured JSON output: name, skills, experience, education, inferred role

- **Mock Interviews**
  - AI-generated questions (12–15 per session: technical, behavioural, project-based)
  - Per-answer AI evaluation with score and feedback
  - Session completion with final score and summary

- **Authentication & Security**
  - JWT access (15 min) + refresh (7 days) tokens
  - Email verification, password reset, password change (history-based)
  - Role-based access control (user / admin / moderator)
  - Redis-backed rate limiting (slowapi) and token blacklist

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.109 + Uvicorn (async ASGI) |
| Database | PostgreSQL + asyncpg (SQLAlchemy 2.0 async) |
| Migrations | Alembic |
| Cache | Redis 5+ |
| Rate Limiting | slowapi (Redis backend) |
| Background Tasks | Celery 5.4 (Redis broker) |
| LLM (primary) | OpenAI GPT-5.2 (JSON mode) |
| LLM (fallback) | Google Gemini 2.0 Flash |
| Auth | JWT (bcrypt 12 rounds, password history) |
| Logging | structlog (JSON prod / coloured dev) |
| Monitoring | Sentry (optional, via `SENTRY_DSN`) |
| Testing | pytest + httpx + aiosqlite (65+ tests, ≥80% coverage) |
| Linting | Ruff + pre-commit |

## Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 5+

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/InterviewAce.git
   cd InterviewAce
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Linux / macOS
   source .venv/bin/activate
   # Windows
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables — copy the example and fill in values:
   ```bash
   cp backend/.env.example backend/.env
   ```

   Key variables:
   ```
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=interview_ace
   SECRET_KEY=<min-32-char-random-string>
   REDIS_URL=redis://localhost:6379/0
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=...
   ```

5. Run database migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

6. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```

7. Start a Celery worker (separate terminal):
   ```bash
   celery -A app.infrastructure.tasks.celery_app worker --loglevel=info
   ```

8. (Optional) Start Celery Beat for scheduled tasks:
   ```bash
   celery -A app.infrastructure.tasks.celery_app beat --loglevel=info
   ```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
InterviewAce/
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── Docs/
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DATABASE_SCHEMA.md
│   ├── Planner.md
│   └── ...
├── backend/                        # Active backend
│   ├── main.py
│   ├── alembic/
│   ├── app/
│   │   ├── api/                       # REST endpoints
│   │   │   ├── health.py
│   │   │   └── v1/endpoints/
│   │   │       ├── auth/
│   │   │       ├── interview/
│   │   │       ├── resume/
│   │   │       └── tasks.py
│   │   ├── core/                      # Config, middleware, security
│   │   ├── db/                        # Async session management
│   │   ├── domain/                    # Entities, interfaces, exceptions
│   │   ├── infrastructure/
│   │   │   ├── cache/                 # Redis client
│   │   │   ├── llm/                   # OpenAI + Gemini providers
│   │   │   ├── persistence/           # ORM models + repositories
│   │   │   └── tasks/                 # Celery tasks
│   │   ├── schemas/                   # Pydantic models
│   │   ├── services/                  # Business orchestration
│   │   └── utils/                     # File handling, email
│   └── tests/                         # pytest test suite
└── backend_v1/                        # Legacy backend (reference only)
```

## Running Tests

```bash
cd backend
python -m pytest tests/ -v --tb=short
```

Coverage report:
```bash
coverage run -m pytest tests/
coverage report --fail-under=80
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run `pre-commit install` to enable lint hooks
4. Commit your changes
5. Push to the branch
6. Create a Pull Request

## License

MIT License