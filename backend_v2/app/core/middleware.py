from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
from typing import Dict, List

import structlog

from app.core.config import settings

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        for header, value in self.security_headers.items():
            response.headers[header] = value
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limit = settings.RATE_LIMIT
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW
        self.requests: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()

        # Clean up old requests
        if client_ip in self.requests:
            self.requests[client_ip] = [
                t for t in self.requests[client_ip]
                if current_time - t < self.rate_limit_window
            ]

        # Check rate limit
        if client_ip in self.requests and len(self.requests[client_ip]) >= self.rate_limit:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(self.rate_limit_window)}
            )

        # Record request
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append(current_time)

        response = await call_next(request)
        return response

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Generate a unique request ID for every incoming request.

    * Stores the ID in ``structlog.contextvars`` so every log line
      within the request automatically includes ``request_id``.
    * Copies the ID to the ``X-Request-ID`` response header so clients
      and load-balancers can correlate logs.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request/response with method, path, status and duration."""

    async def dispatch(self, request: Request, call_next):
        logger = structlog.get_logger("http.access")
        start = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            "request",
            method=request.method,
            path=str(request.url.path),
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response


def setup_middleware(app: FastAPI):
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware) 

    # Request ID middleware (outermost — runs first)
    app.add_middleware(RequestIDMiddleware)

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)