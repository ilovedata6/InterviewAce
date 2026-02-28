# Deploying InterviewAce — Free Tier (2026)

> **Total cost: $0/month** using Vercel + Render + Neon + Upstash free tiers.

---

## Architecture Overview

```
┌─────────────────┐     HTTPS     ┌─────────────────────┐
│  Vercel (CDN)   │ ────────────▶ │  Render (FastAPI)   │
│  Next.js 16     │               │  uvicorn :8000      │
│  Frontend       │               └─────────┬───────────┘
└─────────────────┘                         │
                                            │
                              ┌─────────────┼─────────────┐
                              ▼             ▼             ▼
                      ┌────────────┐ ┌───────────┐ ┌───────────────┐
                      │  Neon      │ │ Upstash   │ │ Render Worker │
                      │ PostgreSQL │ │ Redis     │ │ Celery        │
                      └────────────┘ └───────────┘ └───────────────┘
```

| Service | Platform | Free Tier Limits |
|---------|----------|-----------------|
| Frontend | **Vercel** | 100 GB bandwidth, serverless edge, auto-SSL |
| Backend API | **Render** | 750 hrs/mo, sleeps after 15 min inactivity |
| Celery Worker | **Render** | Background worker, same free limits |
| PostgreSQL | **Neon** | 0.5 GB storage, auto-suspend after 5 min |
| Redis | **Upstash** | 10K commands/day, 256 MB, serverless |

### Free Tier Limitations
- **Render**: Services sleep after 15 min idle → ~30s cold start on first request
- **Neon**: DB suspends after 5 min idle → ~1s cold start on first query
- **Upstash**: 10K commands/day limit (sufficient for demo/portfolio use)
- **File uploads**: Render free tier has ephemeral disk — uploaded files lost on redeploy (parsed resume data persists in DB)

---

## Prerequisites

- GitHub account with the InterviewAce repo pushed (`main` branch)
- At least one LLM API key: [OpenAI](https://platform.openai.com/api-keys) or [Google Gemini](https://aistudio.google.com/apikey)

---

## Step 1 — PostgreSQL (Neon)

1. Go to [neon.tech](https://neon.tech) → **Sign Up** (GitHub SSO)
2. **Create Project**:
   - Name: `interviewace`
   - Region: **US East** (closest to Render's free tier region)
   - Postgres version: **16**
3. Copy the **Connection String** from the dashboard:
   ```
   postgresql://neondb_owner:xxxx@ep-cool-name-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. **Save this URL** — you'll need it for both Render services.

### Run Migrations

You need to run Alembic migrations against the Neon database. From your local machine:

```bash
cd backend

# Set the DATABASE_URL temporarily
export DATABASE_URL="postgresql://neondb_owner:xxxx@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Run all migrations
alembic upgrade head
```

> **Windows PowerShell**:
> ```powershell
> cd backend
> $env:DATABASE_URL = "postgresql://neondb_owner:xxxx@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
> $env:SECRET_KEY = "temporary-key-for-migration-only-at-least-32-characters-long"
> alembic upgrade head
> ```

---

## Step 2 — Redis (Upstash)

1. Go to [upstash.com](https://upstash.com) → **Sign Up** (GitHub SSO)
2. **Create Database**:
   - Name: `interviewace-redis`
   - Type: **Regional**
   - Region: **US East 1** (match Neon region)
   - Enable **TLS** (default)
3. Copy the **Redis URL** from the dashboard (starts with `rediss://`):
   ```
   rediss://default:xxxx@us1-xxxx-xxxx.upstash.io:6379
   ```
4. **Save this URL** — you'll need it for both Render services.

---

## Step 3 — Backend API + Celery Worker (Render)

### Option A: Blueprint Deploy (Recommended)

1. Go to [render.com](https://render.com) → **Sign Up** (GitHub SSO)
2. Navigate to **Blueprints** → **New Blueprint Instance**
3. Connect your **InterviewAce** GitHub repo
4. Render detects `render.yaml` and creates:
   - `interviewace-api` (Web Service)
   - `interviewace-worker` (Background Worker)
5. **Set environment variables** for both services:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Neon connection string (from Step 1) |
| `REDIS_URL` | Upstash Redis URL (from Step 2) |
| `OPENAI_API_KEY` | Your OpenAI key (or leave empty if using Gemini only) |
| `GEMINI_API_KEY` | Your Gemini key (or leave empty if using OpenAI only) |
| `ALLOWED_ORIGINS` | `["https://your-app.vercel.app"]` ← update after Step 4 |
| `FRONTEND_URL` | `https://your-app.vercel.app` ← update after Step 4 |

6. Click **Apply** → Render builds and deploys both services.
7. Note your API URL: `https://interviewace-api.onrender.com`

### Option B: Manual Deploy

If Blueprint doesn't work, create services manually:

**Web Service:**
1. Dashboard → **New** → **Web Service**
2. Connect GitHub repo → branch `main`
3. Root Directory: `backend`
4. Runtime: **Docker**
5. Plan: **Free**
6. Set all env vars from the table above
7. Deploy

**Background Worker:**
1. Dashboard → **New** → **Background Worker**
2. Connect same repo → branch `main`
3. Root Directory: `backend`
4. Runtime: **Docker**
5. Docker Command: `celery -A app.infrastructure.tasks.celery_app worker --loglevel=info --pool=solo --concurrency=1`
6. Plan: **Free**
7. Set same env vars
8. Deploy

---

## Step 4 — Frontend (Vercel)

1. Go to [vercel.com](https://vercel.com) → **Sign Up** (GitHub SSO)
2. **Import Project** → select your InterviewAce repo
3. **Configure**:
   - Framework: **Next.js** (auto-detected)
   - Root Directory: `frontend`
   - Build Command: `pnpm build` (auto-detected from `vercel.json`)
4. **Environment Variables** → Add:

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://interviewace-api.onrender.com/api/v1` |
| `NEXT_PUBLIC_APP_NAME` | `InterviewAce` |
| `NEXT_PUBLIC_APP_URL` | `https://your-app.vercel.app` ← Vercel assigns this |

5. Click **Deploy** → wait for build to complete (~2 min)
6. Note your frontend URL (e.g., `https://interviewace.vercel.app`)

### Update Backend CORS

Now go back to **Render Dashboard** → `interviewace-api` → Environment:

- `ALLOWED_ORIGINS` → `["https://interviewace.vercel.app"]`
- `FRONTEND_URL` → `https://interviewace.vercel.app`

Do the same for `interviewace-worker`. Render will auto-redeploy.

---

## Step 5 — Verify Deployment

1. **Health check**: `https://interviewace-api.onrender.com/health`
   - Expected: `{"status": "healthy", ...}`
   - First request may take ~30s (cold start)

2. **Frontend**: Visit your Vercel URL
   - Register a new account
   - Upload a resume → verify parsing starts
   - Start a mock interview

3. **API Docs**: `https://interviewace-api.onrender.com/docs`

---

## Custom Domain (Optional)

### Vercel (Frontend)
1. Vercel Dashboard → your project → **Settings** → **Domains**
2. Add your domain (e.g., `interviewace.com`)
3. Point DNS: `CNAME → cname.vercel-dns.com`

### Render (Backend API)
1. Render Dashboard → `interviewace-api` → **Settings** → **Custom Domains**
2. Add subdomain (e.g., `api.interviewace.com`)
3. Point DNS as instructed

Remember to update:
- Render: `ALLOWED_ORIGINS` → include your custom domain
- Render: `FRONTEND_URL` → your custom domain
- Vercel: `BACKEND_URL` → your custom API domain

---

## SMTP Email Setup (Optional)

For real email sending (verification, password reset), use Gmail SMTP:

1. Enable 2FA on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Set in Render env vars:

| Variable | Value |
|----------|-------|
| `SMTP_SERVER` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `your-email@gmail.com` |
| `SMTP_PASSWORD` | `your-16-char-app-password` |
| `EMAIL_FROM` | `your-email@gmail.com` |
| `EMAIL_DEV_MODE` | `false` |

---

## Troubleshooting

### Backend won't start
- Check Render logs: Dashboard → `interviewace-api` → **Logs**
- Verify `DATABASE_URL` includes `?sslmode=require`
- Verify `SECRET_KEY` is at least 32 characters (Render auto-generates this)

### Frontend can't reach backend
- Verify `BACKEND_URL` in Vercel env vars ends with `/api/v1`
- Check `ALLOWED_ORIGINS` on Render includes exact Vercel URL (with `https://`, no trailing slash)
- First request takes ~30s due to Render cold start

### Resume upload fails
- Celery worker must be running — check Render `interviewace-worker` logs
- Verify worker has same `DATABASE_URL` and `REDIS_URL` as the API

### Database connection fails
- Neon auto-suspends after 5 min — first query takes ~1s to wake
- Ensure URL format: `postgresql://user:pass@host/db?sslmode=require`

### Upstash daily limit reached
- Free tier: 10K commands/day
- If exceeded, Celery tasks will fail until reset (midnight UTC)
- Consider upgrading to Pay-as-you-go ($0.20/100K commands)

---

## Cost Summary

| Service | Plan | Monthly Cost |
|---------|------|-------------|
| Vercel | Hobby | **$0** |
| Render (API) | Free | **$0** |
| Render (Worker) | Free | **$0** |
| Neon (Postgres) | Free | **$0** |
| Upstash (Redis) | Free | **$0** |
| OpenAI / Gemini | Pay-per-use | ~$0.01–0.10/interview |
| **Total** | | **$0/month** + LLM usage |

> The only real cost is LLM API usage. Using `gpt-4o-mini` or `gemini-2.0-flash` keeps this very low (~$0.01–0.05 per interview session).
