"""
Alembic environment configuration.

Reads DATABASE_URL from app.core.config.settings and imports all ORM models
so that autogenerate can detect schema changes.
"""

import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Ensure backend_v2/ is on sys.path so `app.*` imports work ─────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# ── Import app settings and all models ────────────────────────────────────
from app.core.config import settings  # noqa: E402
from app.models.base import Base  # noqa: E402

# Import every model module so Base.metadata knows about all tables
from app.models import user, resume, interview, security  # noqa: E402, F401

# ── Alembic Config object ────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url from our app settings (not from alembic.ini)
config.set_main_option("sqlalchemy.url", settings.database_url)

# Set up Python logging from the .ini file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData object for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Creates an engine and runs migrations against the live database.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
