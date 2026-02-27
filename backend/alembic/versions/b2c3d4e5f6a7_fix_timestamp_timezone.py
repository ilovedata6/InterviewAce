"""fix timestamp timezone columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-26 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Tables/columns to migrate to TIMESTAMP WITH TIME ZONE.
# Each tuple: (table, column)
_TIMESTAMP_COLUMNS = [
    # interview columns that explicitly accept Python timezone-aware datetimes
    ("interview_sessions", "started_at"),
    ("interview_sessions", "completed_at"),
    # TimestampMixin columns — only those currently WITHOUT TIME ZONE
    ("interview_sessions", "created_at"),
    ("interview_sessions", "updated_at"),
    ("interview_questions", "created_at"),
    ("interview_questions", "updated_at"),
    ("users", "created_at"),
    ("users", "updated_at"),
    ("resumes", "created_at"),
    ("resumes", "updated_at"),
    ("user_sessions", "updated_at"),  # created_at already WITH TIME ZONE
    ("password_history", "updated_at"),  # created_at already WITH TIME ZONE
    ("password_reset_tokens", "created_at"),  # no updated_at column
    ("login_attempts", "updated_at"),  # created_at already WITH TIME ZONE
    ("token_blacklist", "updated_at"),  # created_at already WITH TIME ZONE
]


def upgrade() -> None:
    for table, column in _TIMESTAMP_COLUMNS:
        op.execute(
            f"ALTER TABLE {table} "
            f"ALTER COLUMN {column} TYPE TIMESTAMP WITH TIME ZONE "
            f"USING {column} AT TIME ZONE 'UTC'"
        )


def downgrade() -> None:
    for table, column in reversed(_TIMESTAMP_COLUMNS):
        op.execute(
            f"ALTER TABLE {table} "
            f"ALTER COLUMN {column} TYPE TIMESTAMP WITHOUT TIME ZONE "
            f"USING {column} AT TIME ZONE 'UTC'"
        )
