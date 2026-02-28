# Getting Started — InterviewAce

Complete guide to setting up and running the InterviewAce application locally.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Clone the Repository](#clone-the-repository)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running Everything Together](#running-everything-together)
6. [Docker (Optional)](#docker-optional)
7. [Running Tests](#running-tests)
8. [Environment Variables Reference](#environment-variables-reference)
9. [Troubleshooting](#troubleshooting)
10. [How to Report Issues](#how-to-report-issues)

---

## Prerequisites

| Tool         | Version  | Check command            |
| ------------ | -------- | ------------------------ |
| Python       | ≥ 3.11   | `python --version`       |
| Node.js      | ≥ 22     | `node --version`         |
| pnpm         | ≥ 10     | `pnpm --version`         |
| PostgreSQL   | ≥ 15     | `psql --version`         |
| Redis        | ≥ 7      | `redis-cli ping`         |
| Git          | ≥ 2      | `git --version`          |
| Docker (opt) | ≥ 24     | `docker --version`       |

### Installing pnpm

```bash
corepack enable
corepack prepare pnpm@10 --activate
```

Or: `npm install -g pnpm`

---

## Clone the Repository

```bash
git clone https://github.com/ilovedata6/InterviewAce.git
cd InterviewAce
```

---

## Backend Setup

### 1. Create a Python virtual environment

```bash
cd backend
python -m venv venv

# Activate it:
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r ../requirements.txt
```

### 3. Create the `.env` file

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

Edit `backend/.env` with your actual values:

```dotenv
# REQUIRED — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-64-char-hex-string-here

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=interview_ace

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM API Keys (at least one needed for interview features)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Email (leave defaults for dev — emails print to console)
EMAIL_DEV_MODE=True
```

### 4. Create the database

```bash
createdb interview_ace      # or use pgAdmin / psql
```

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the backend server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at **http://localhost:8000**. Docs at **http://localhost:8000/docs**.

### 7. Start Celery worker (separate terminal)

```bash
cd backend
celery -A app.infrastructure.tasks.celery_app worker --loglevel=info
```

> **Note:** Celery is needed for background tasks like resume analysis. The app will work without it, but analysis won't complete.

---

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
pnpm install
```

> **Windows PowerShell users:** If you get an execution policy error, run this first:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### 2. Create the `.env.local` file

```bash
copy .env.example .env.local    # Windows
# cp .env.example .env.local    # macOS / Linux
```

The defaults should work for local development:

```dotenv
BACKEND_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=InterviewAce
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Start the development server

```bash
pnpm dev
```

The frontend will be available at **http://localhost:3000**.

---

## Running Everything Together

You need **4 processes** running simultaneously in separate terminals:

| # | Terminal | Directory    | Command                                 |
|---|----------|--------------|-----------------------------------------|
| 1 | PostgreSQL | —          | Running as a service / `pg_ctl start`   |
| 2 | Redis    | —            | `redis-server` or running as a service  |
| 3 | Backend  | `backend/`   | `uvicorn main:app --reload --port 8000` |
| 4 | Celery   | `backend/`   | `celery -A app.infrastructure.tasks.celery_app worker --loglevel=info --pool=threads` |
| 5 | Frontend | `frontend/`  | `pnpm dev`                              |

**Quick start order:**
1. Make sure PostgreSQL and Redis are running
2. Start backend (terminal 3)
3. Start Celery worker (terminal 4)
4. Start frontend (terminal 5)
5. Open http://localhost:3000

---

## Docker (Optional)

Run everything with a single command:

```bash
# From the project root
docker compose up --build
```

This starts PostgreSQL, Redis, Backend, Celery, and Frontend automatically.

To bring it down:
```bash
docker compose down
```

To reset the database:
```bash
docker compose down -v    # removes volumes
docker compose up --build
```

> **Note:** The backend needs a Dockerfile at `backend/Dockerfile`. If it doesn't exist yet, you'll need to create one or run the backend outside Docker.

---

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Unit Tests

```bash
cd frontend
pnpm test              # run once
pnpm test:watch        # watch mode
pnpm test:coverage     # with coverage report
```

### Frontend E2E Tests (Playwright)

```bash
cd frontend
# First time only — install browsers:
npx playwright install chromium

# Run E2E tests (requires backend running):
pnpm test:e2e
pnpm test:e2e:ui       # interactive UI mode
```

### Linting & Formatting

```bash
# Backend
ruff check backend/
ruff format --check backend/

# Frontend
cd frontend
pnpm lint
pnpm format:check
```

---

## Environment Variables Reference

### Backend (`backend/.env`)

| Variable                | Required | Default              | Description                          |
|------------------------|----------|----------------------|--------------------------------------|
| `SECRET_KEY`           | **Yes**  | —                    | JWT signing key (≥32 chars)         |
| `POSTGRES_SERVER`      | No       | `localhost`          | Database host                        |
| `POSTGRES_USER`        | No       | `postgres`           | Database username                    |
| `POSTGRES_PASSWORD`    | No       | `postgres`           | Database password                    |
| `POSTGRES_DB`          | No       | `interview_ace`      | Database name                        |
| `REDIS_URL`            | No       | `redis://localhost:6379/0` | Redis connection URL           |
| `OPENAI_API_KEY`       | No       | —                    | OpenAI API key (primary LLM)        |
| `GEMINI_API_KEY`       | No       | —                    | Google Gemini API key (fallback LLM) |
| `EMAIL_DEV_MODE`       | No       | `True`               | Print emails to console in dev       |
| `FRONTEND_URL`         | No       | `http://localhost:3000` | Used for email links              |
| `ALLOWED_ORIGINS`      | No       | `["http://localhost:3000"]` | CORS origins (JSON array or CSV) |

### Frontend (`frontend/.env.local`)

| Variable               | Required | Default                      | Description                          |
|-----------------------|----------|------------------------------|--------------------------------------|
| `BACKEND_URL`          | No       | `http://localhost:8000/api/v1` | Backend API URL (server-side only) |
| `NEXT_PUBLIC_APP_NAME` | No       | `InterviewAce`               | App name shown in UI                 |
| `NEXT_PUBLIC_APP_URL`  | No       | `http://localhost:3000`      | Public app URL                       |

---

## Troubleshooting

### Common Issues

#### "Execution policy" error on Windows PowerShell
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```
This must be run in **every new terminal session**.

#### Backend won't start — "SECRET_KEY must be at least 32 characters"
Generate a proper key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Put the output in your `backend/.env` as `SECRET_KEY=<value>`.

#### Database connection refused
- Make sure PostgreSQL is running: `pg_isready`
- Check your `.env` matches your PostgreSQL config
- Create the database: `createdb interview_ace`

#### Redis connection refused
- Make sure Redis is running: `redis-cli ping` (should say `PONG`)
- On Windows, use WSL or Docker for Redis

#### Frontend "Module not found" errors
```bash
cd frontend
rm -rf node_modules .next
pnpm install
pnpm dev
```

#### Build warnings about middleware deprecation
The warning `⚠ Please use 'proxy' instead` from Next.js 16 is expected and harmless. The middleware functions correctly.

#### Resume analysis never completes
Make sure the Celery worker is running in a separate terminal. Analysis is processed as a background task.

#### Alembic migration errors
```bash
cd backend
alembic stamp head    # mark current state
alembic upgrade head  # rerun migrations
```

#### Port already in use
```bash
# Find what's using port 8000 (backend)
netstat -ano | findstr :8000
# Kill the process
taskkill /PID <pid> /F

# Or use a different port:
uvicorn main:app --reload --port 8001
```

---

## How to Report Issues

When something isn't working, provide the following information so I can fix it quickly:

### Template

```
**What I tried to do:**
[Describe what you were attempting]

**What happened instead:**
[Describe the error or unexpected behavior]

**Error message (if any):**
[Copy the full error message from the terminal or browser console]

**Steps to reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Environment:**
- OS: [Windows/macOS/Linux]
- Terminal: [at the backend/frontend/browser]
- Branch: [output of `git branch --show-current`]
```

### Tips for effective bug reports

1. **Copy the full error** — don't paraphrase. Include the complete stack trace.
2. **Specify which terminal** — is the error from the backend, frontend, Celery, database, or browser?
3. **Include the browser console** — press `F12` → Console tab → copy any red errors.
4. **Mention the page** — which URL were you on when the error happened?
5. **Include the command you ran** — if it's a terminal error, show the exact command.

### Example bug report

```
**What I tried to do:**
Start the frontend with `pnpm dev`

**What happened instead:**
It shows "Module not found: Can't resolve '@/components/ui/button'"

**Error message:**
Module not found: Can't resolve '@/components/ui/button'
  Import trace for requested module:
    ./src/app/(auth)/login/page.tsx

**Steps to reproduce:**
1. cd frontend
2. pnpm dev

**Environment:**
- OS: Windows 11
- Terminal: PowerShell
- Branch: feature/frontend-scaffold
```

This helps me pinpoint the exact issue and provide a fix immediately.
