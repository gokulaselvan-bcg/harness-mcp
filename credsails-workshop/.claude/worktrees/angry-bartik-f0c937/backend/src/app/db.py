"""SQLAlchemy engine/session + Base.

Sync engine + sync Session (matches the reference project). A per-connection
PRAGMA foreign_keys=ON listener enforces FKs in SQLite (off by default), applied
the same way in alembic/env.py so migrations enforce FKs too.
"""
from __future__ import annotations

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


# Append-only + tamper-evident audit_log: block UPDATE/DELETE (INSERT stays free).
# Kept here so both the migration's reset path and reset_database() agree.
AUDIT_TRIGGERS = (
    "CREATE TRIGGER IF NOT EXISTS audit_log_no_update "
    "BEFORE UPDATE ON audit_log BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;",
    "CREATE TRIGGER IF NOT EXISTS audit_log_no_delete "
    "BEFORE DELETE ON audit_log BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;",
)


engine = create_engine(
    f"sqlite:///{settings.db_path}",
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _enforce_sqlite_fk(dbapi_connection, connection_record):  # noqa: ANN001
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_session():
    """FastAPI dependency: a request-scoped Session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_audit_triggers(bind) -> None:  # noqa: ANN001
    for ddl in AUDIT_TRIGGERS:
        bind.execute(text(ddl))


def reset_database() -> None:
    """Reset to a clean schema for the single-borrower demo.

    The append-only trigger forbids deleting audit_log rows, so we DROP + recreate
    (DROP TABLE bypasses the BEFORE DELETE trigger) rather than row-deleting. Imports
    models lazily so all tables are registered on Base.metadata before drop/create.
    """
    from . import models  # noqa: F401

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        create_audit_triggers(conn)
