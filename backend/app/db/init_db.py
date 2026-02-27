"""
Database initialization module.

Schema creation is now handled by Alembic migrations.
Use:  alembic upgrade head    — to apply all migrations
      alembic downgrade -1    — to rollback one step
      alembic revision --autogenerate -m "description"  — after model changes

This module is kept for optional seed data and legacy compat.
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    Initialize the database.

    Schema is managed by Alembic migrations — run `alembic upgrade head`.
    This function can be used for seeding initial data if needed.
    """
    logger.info(
        "Database schema is managed by Alembic. "
        "Run 'alembic upgrade head' from backend/ to apply migrations."
    )


if __name__ == "__main__":
    init_db()
