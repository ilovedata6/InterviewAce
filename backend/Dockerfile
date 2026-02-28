# ── InterviewAce Backend — Production Dockerfile ───────────
# Multi-stage build for FastAPI + Celery
# ────────────────────────────────────────────────────────────

# ── Stage 1: Builder ───────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Production runner ─────────────────────────────
FROM python:3.11-slim AS runner

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 curl && \
    rm -rf /var/lib/apt/lists/* && \
    addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads && chown -R appuser:appgroup /app/uploads

USER appuser

# Render injects $PORT — default to 8000 for local Docker runs
EXPOSE 8000

# Use shell form so $PORT env var is expanded at runtime
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
