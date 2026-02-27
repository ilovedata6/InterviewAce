from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.middleware import setup_middleware

# Configure structured logging before anything else
setup_logging()

# ── Sentry error monitoring ───────────────────────────────────────────────
# Only initialised when SENTRY_DSN is provided (disabled in local dev).
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        release=f"interviewace@{settings.VERSION}",
        traces_sample_rate=1.0 if settings.ENVIRONMENT == "development" else 0.2,
        profiles_sample_rate=0.1,
        send_default_pii=False,
        enable_tracing=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup / shutdown hooks."""
    # ── startup ────────────────────────────────────────────────────────────
    yield
    # ── shutdown ───────────────────────────────────────────────────────────
    from app.infrastructure.cache.redis_client import close_redis

    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AI-powered interview preparation platform.  Upload your resume, "
        "run personalised mock interviews, and receive detailed AI feedback — "
        "all through a single REST API."
    ),
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    contact={"name": "InterviewAce Team", "url": "https://github.com/interviewace"},
    openapi_tags=[
        {
            "name": "authentication",
            "description": "Register, login, token refresh, password management, and email verification.",
        },
        {
            "name": "interview",
            "description": "Start mock-interview sessions, submit answers, and retrieve AI-generated feedback.",
        },
        {
            "name": "resume",
            "description": "Upload, list, update, and delete resumes. Parsing runs asynchronously via Celery.",
        },
        {
            "name": "tasks",
            "description": "Poll the status of long-running background tasks (e.g. resume parsing).",
        },
        {
            "name": "health",
            "description": "Liveness and readiness probes for load-balancers and orchestrators.",
        },
    ],
)

# Set up all middleware (CORS, security headers, rate limiting, request ID)
# CORS is configured via settings.ALLOWED_ORIGINS — no wildcard
setup_middleware(app)

# Register domain exception → HTTP response handlers
register_exception_handlers(app)

# Health / readiness probes (no prefix — accessible at /health, /ready)
app.include_router(health_router)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
