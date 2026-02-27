"""add interview config fields, question metadata, and indexes

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2025-01-15 00:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Interview Sessions: add configuration columns ─────────────────
    op.add_column(
        "interview_sessions",
        sa.Column("difficulty", sa.String(20), nullable=True, server_default="mixed"),
    )
    op.add_column(
        "interview_sessions",
        sa.Column("question_count", sa.Integer(), nullable=True, server_default="12"),
    )
    op.add_column("interview_sessions", sa.Column("focus_areas", sa.JSON(), nullable=True))
    op.add_column("interview_sessions", sa.Column("score_breakdown", sa.JSON(), nullable=True))

    # Back-fill existing rows then make NOT NULL
    op.execute("UPDATE interview_sessions SET difficulty = 'mixed' WHERE difficulty IS NULL")
    op.execute("UPDATE interview_sessions SET question_count = 12 WHERE question_count IS NULL")
    op.alter_column("interview_sessions", "difficulty", nullable=False, server_default=None)
    op.alter_column("interview_sessions", "question_count", nullable=False, server_default=None)

    # ── Interview Questions: add metadata columns ─────────────────────
    op.add_column(
        "interview_questions",
        sa.Column("category", sa.String(30), nullable=True, server_default="general"),
    )
    op.add_column(
        "interview_questions",
        sa.Column("difficulty", sa.String(20), nullable=True, server_default="medium"),
    )
    op.add_column(
        "interview_questions", sa.Column("time_taken_seconds", sa.Integer(), nullable=True)
    )
    op.add_column(
        "interview_questions",
        sa.Column("order_index", sa.Integer(), nullable=True, server_default="0"),
    )

    # Back-fill existing rows then make NOT NULL
    op.execute("UPDATE interview_questions SET category = 'general' WHERE category IS NULL")
    op.execute("UPDATE interview_questions SET difficulty = 'medium' WHERE difficulty IS NULL")
    op.execute("UPDATE interview_questions SET order_index = 0 WHERE order_index IS NULL")
    op.alter_column("interview_questions", "category", nullable=False, server_default=None)
    op.alter_column("interview_questions", "difficulty", nullable=False, server_default=None)
    op.alter_column("interview_questions", "order_index", nullable=False, server_default=None)

    # ── Indexes for performance ───────────────────────────────────────
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])
    op.create_index(
        "ix_interview_sessions_user_completed", "interview_sessions", ["user_id", "completed_at"]
    )
    op.create_index("ix_interview_questions_session_id", "interview_questions", ["session_id"])
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_index("ix_resumes_status", "resumes", ["status"])


def downgrade() -> None:
    op.drop_index("ix_resumes_status", table_name="resumes")
    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_index("ix_interview_questions_session_id", table_name="interview_questions")
    op.drop_index("ix_interview_sessions_user_completed", table_name="interview_sessions")
    op.drop_index("ix_interview_sessions_user_id", table_name="interview_sessions")

    op.drop_column("interview_questions", "order_index")
    op.drop_column("interview_questions", "time_taken_seconds")
    op.drop_column("interview_questions", "difficulty")
    op.drop_column("interview_questions", "category")

    op.drop_column("interview_sessions", "score_breakdown")
    op.drop_column("interview_sessions", "focus_areas")
    op.drop_column("interview_sessions", "question_count")
    op.drop_column("interview_sessions", "difficulty")
