"""initial schema

Forward-only. Tables (and their partial-unique `superseded_by IS NULL` indexes,
which carry their `sqlite_where` from the model definitions) are created from
Base.metadata. The append-only audit triggers can't live in metadata, so they're
authored here as raw DDL — they fire only on UPDATE/DELETE, leaving INSERT free.

Revision ID: 0001_initial
Revises:
"""
from __future__ import annotations

from alembic import op

from app.db import Base
import app.models  # noqa: F401  (registers tables on Base.metadata)

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS audit_log_no_update
        BEFORE UPDATE ON audit_log
        BEGIN
            SELECT RAISE(ABORT, 'audit_log is append-only');
        END;
        """
    )
    op.execute(
        """
        CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
        BEFORE DELETE ON audit_log
        BEGIN
            SELECT RAISE(ABORT, 'audit_log is append-only');
        END;
        """
    )


def downgrade() -> None:
    raise NotImplementedError("forward-only migrations")
