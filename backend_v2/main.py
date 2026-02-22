from fastapi import FastAPI
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.api import api_router
from app.api.health import router as health_router
from app.core.middleware import setup_middleware
from app.core.exceptions import register_exception_handlers

# Configure structured logging before anything else
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered interview preparation platform",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
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