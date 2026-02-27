# Production Readiness Assessment

## Verdict: Not Production-Ready

InterviewAce has a solid security-aware foundation and good AI integration, but it is **missing critical infrastructure, tooling, and patterns** that every production service needs before handling real users.

---

## What Is Already Good

| Area | What Exists |
|---|---|
| Security headers | CSP, HSTS, X-Frame-Options, Referrer-Policy via middleware |
| Password policy | bcrypt 12 rounds, complexity regex, history of last 5 passwords |
| Token lifecycle | Short-lived access (15 min) + refresh (7 days) + blacklist table |
| Login protection | Attempt tracking + account lockout model |
| Input validation | Pydantic v2 on every request body and response |
| File safety | Extension whitelist + 10 MB size cap |
| API versioning | `/api/v1` prefix in place |
| Config management | pydantic-settings + `.env` separation |

---

## Critical Gaps

### 1. Wildcard CORS — **High Risk**
**File:** [backend/main.py](../backend/main.py)
```python
allow_origins=["*"]   # ← comment says replace in production, but it hasn't been
```
The `setup_middleware` in `middleware.py` correctly reads `settings.ALLOWED_ORIGINS`, but `main.py` also adds a second CORS middleware with `*` before calling `setup_middleware`. This double-adds middleware and leaves the wildcard active.

**Fix:** Remove the `CORSMiddleware` block from `main.py` entirely. Let `setup_middleware` handle it.

---

### 2. No Database Migrations (Alembic)
**File:** [backend/app/db/init_db.py](../backend/app/db/init_db.py)

`Base.metadata.create_all()` only works on a fresh, empty database. Any schema change in production (adding a column, renaming a table) will **silently fail or corrupt data** without migrations.

**Fix:**
```bash
pip install alembic
alembic init alembic
# configure alembic.ini and env.py to use settings.DATABASE_URL
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

### 3. Synchronous LLM Calls Block the Event Loop
**Files:** [backend/app/services/resume_parser.py](../backend/app/services/resume_parser.py), [backend/app/services/interview_orchestrator.py](../backend/app/services/interview_orchestrator.py)

Gemini API calls are made synchronously inside FastAPI route handlers. A single slow LLM call (2–10 seconds) blocks the entire server thread while processing. Under even modest load this causes request timeouts for all other users.

**Fix:** Use a task queue (Celery + Redis) for resume parsing and question generation. Return a `202 Accepted` with a task ID; poll for completion.
```
POST /resume/       → enqueue parse task → 202 { "task_id": "..." }
GET  /resume/tasks/{task_id} → check status
```

---

### 4. In-Memory Rate Limiting
**File:** [backend/app/core/middleware.py](../backend/app/core/middleware.py)

```python
self.requests: Dict[str, List[float]] = {}  # lives in process memory
```
- Resets on every server restart
- Does not work with multiple workers (each worker has its own dict)
- Not shared across horizontal replicas

**Fix:** Replace with Redis-backed rate limiting using `slowapi` or `fastapi-limiter`.
```bash
pip install slowapi redis
```

---

### 5. No Tests
There are zero test files anywhere in the repository.

**Minimum needed for production:**
```
tests/
  unit/
    test_security.py          # JWT, bcrypt, token blacklist
    test_resume_parser.py     # text extraction, validation
    test_interview_orchestrator.py
  integration/
    test_auth_endpoints.py    # register → login → refresh → logout
    test_resume_endpoints.py  # upload → analysis
    test_interview_endpoints.py # start → answer → complete
  conftest.py                 # shared fixtures, test DB
```

```bash
pip install pytest pytest-asyncio httpx factory-boy
```

---

### 6. No Docker / Containerization
No `Dockerfile`, no `docker-compose.yml`. Deployment is entirely manual.

**Minimum `docker-compose.yml`:**
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_DB: interview_ace
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres

  api:
    build: ./backend
    depends_on: [db]
    ports: ["8000:8000"]
    environment:
      - POSTGRES_SERVER=db
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
```

---

### 7. No CI/CD Pipeline
No `.github/workflows/`, no automated test runs, no linting enforcement, no deployment automation.

**Minimum GitHub Actions workflow:**
```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v
      - run: ruff check backend/
```

---

### 8. No Health Check Endpoint
Load balancers and orchestrators (Kubernetes, ECS, Railway) require a health check to determine if a replica is alive. There is no `/health` or `/ping` route.

**Fix:**
```python
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}
```

---

### 9. Insecure Default `SECRET_KEY`
**File:** [backend/app/core/config.py](../backend/app/core/config.py)
```python
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
```
If `SECRET_KEY` is not set, the app silently starts with a public, predictable key. Any user can forge valid JWTs.

**Fix:** Raise an error if not set:
```python
SECRET_KEY: str = os.getenv("SECRET_KEY")  # type: ignore
# then in __init__ or validator:
if not SECRET_KEY or SECRET_KEY == "your-secret-key-here":
    raise ValueError("SECRET_KEY must be set to a secure random value")
```

---

### 10. No Structured / Centralized Logging
Individual files use `logging.getLogger(__name__)` with no centralized configuration. In production you need:
- JSON-formatted log output (for log aggregation tools like Datadog, CloudWatch, Loki)
- Request ID tracing across log lines
- Log level control per environment

**Fix:**
```python
# backend/app/core/logging_config.py
import logging, json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "time": self.formatTime(record),
        })

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
```

---

### 11. No Error Monitoring
No Sentry, Rollbar, or equivalent. Unhandled exceptions in production are invisible unless you grep raw logs.

**Fix:**
```bash
pip install sentry-sdk[fastapi]
```
```python
# main.py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=0.1)
```

---

### 12. Local File Storage for Uploads
**File:** [backend/app/core/config.py](../backend/app/core/config.py) — `UPLOAD_DIR: str = "uploads"`

Files are stored on the local filesystem. This breaks when:
- Running multiple server replicas (files only exist on one node)
- The server restarts and the container is replaced
- You need CDN delivery

**Fix:** Replace `file_handler.py` with an S3-compatible storage layer (AWS S3, Cloudflare R2, MinIO).
```bash
pip install boto3
```

---

### 13. Token Blacklist Grows Without Pruning
**File:** [backend/app/models/security.py](../backend/app/models/security.py)

`TokenBlacklist` rows are inserted on every logout and never deleted. The table will grow indefinitely and every token validation query will get slower over time.

**Fix:** Add a cleanup job or use a TTL. Simplest approach with a scheduled task:
```python
db.query(TokenBlacklist).filter(TokenBlacklist.expires_at < datetime.utcnow()).delete()
```
Or move token blacklisting to Redis with automatic key expiry (`EXPIRE`).

---

### 14. spaCy NER Pipeline Loaded at Module Import
**File:** [backend/app/services/resume_parser.py](../backend/app/services/resume_parser.py)
```python
hf_ner = pipeline("ner", grouped_entities=True)  # line at module level
```
This runs on every worker startup, potentially downloading a large model, and makes startup time unpredictable. It also loads the model in all processes even in environments where Gemini never fails.

**Fix:** Lazy-load the pipeline inside `_fallback_parse()` using `functools.lru_cache`.
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_hf_ner():
    from transformers import pipeline
    return pipeline("ner", grouped_entities=True)
```

---

### 15. No `.env.example`
There is no `.env.example` file. New contributors have no reference for which variables are required.

**Fix:** Create `.env.example` in the project root with all keys and placeholder values.

---

### 16. No Pagination on List Endpoints
`GET /interview/history` and `GET /resume/` return all records. As users accumulate data these queries will become full table scans.

**Fix:** Add `skip`/`limit` or cursor-based pagination to all list endpoints.
```python
@router.get("/history")
def get_history(skip: int = 0, limit: int = 20, ...):
    return db.query(InterviewSession).offset(skip).limit(limit).all()
```

---

### 17. No `asyncpg` / Async Database Driver
FastAPI is async but the SQLAlchemy engine uses the synchronous `psycopg2` driver. Every DB query blocks an OS thread.

**Fix:** Switch to `asyncpg` + `SQLAlchemy[asyncio]`:
```bash
pip install asyncpg sqlalchemy[asyncio]
```
```python
engine = create_async_engine("postgresql+asyncpg://...")
```

---

### 18. No Role-Based Access Control (RBAC)
`User` model has no `role` field. There is no admin panel, no distinction between admin and regular user. All authenticated users can access any resource if they know the ID.

---

## Priority Checklist

| Priority | Item |
|---|---|
| 🔴 Critical | Fix wildcard CORS in `main.py` |
| 🔴 Critical | Require `SECRET_KEY` — no insecure default |
| 🔴 Critical | Add Alembic migrations |
| 🔴 Critical | Write tests (at minimum integration tests for auth + resume + interview) |
| 🟠 High | Move LLM calls to background task queue (Celery + Redis) |
| 🟠 High | Replace in-memory rate limiting with Redis |
| 🟠 High | Add health check endpoint |
| 🟠 High | Add structured JSON logging |
| 🟠 High | Add Sentry for error monitoring |
| 🟡 Medium | Dockerize the application |
| 🟡 Medium | Set up CI/CD pipeline |
| 🟡 Medium | Move file storage to S3/R2 |
| 🟡 Medium | Add pagination to list endpoints |
| 🟡 Medium | Lazy-load spaCy NER pipeline |
| 🟡 Medium | Add token blacklist TTL pruning |
| 🟢 Low | Create `.env.example` |
| 🟢 Low | Switch to async SQLAlchemy + asyncpg |
| 🟢 Low | Add RBAC / user roles |
