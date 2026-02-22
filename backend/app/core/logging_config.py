"""
Structured logging configuration using structlog.

Call ``setup_logging()`` once at application startup (in main.py).

Features:
- JSON output in production, coloured console output in development
- Request-ID propagation via contextvars
- stdlib logging integration (captures uvicorn, sqlalchemy, etc.)
"""

from __future__ import annotations

import logging
import sys

import structlog

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure structlog and stdlib logging for the application.

    * ``development`` → human-readable coloured console output, DEBUG level
    * ``staging`` / ``production`` → JSON lines, INFO level
    """
    is_dev = settings.ENVIRONMENT.lower() == "development"
    log_level = logging.DEBUG if is_dev else logging.INFO

    # -- Shared processors applied to every log event ----------------------
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,          # inject request_id etc.
        structlog.stdlib.add_log_level,                   # level field
        structlog.stdlib.add_logger_name,                 # logger name
        structlog.processors.TimeStamper(fmt="iso"),      # ISO-8601 timestamp
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_dev:
        # Pretty console renderer for local development
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer()
    else:
        # Machine-readable JSON for production log aggregation
        renderer = structlog.processors.JSONRenderer()

    # -- Configure structlog -----------------------------------------------
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # -- Wire stdlib logging through structlog formatter -------------------
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers (avoids duplicate output on reload)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Quieten noisy third-party loggers
    for name in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.WARNING)
