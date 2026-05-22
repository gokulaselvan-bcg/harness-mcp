"""Runtime configuration sourced from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_DB_PATH = "data/harness.db"
DEFAULT_BACKUP_DIR = "backups"
DEFAULT_LOG_PATH = "sdlc_mcp.log"


@dataclass(frozen=True)
class Config:
    db_path: Path
    backup_dir: Path
    log_path: Path
    migrations_dir: Path

    @classmethod
    def from_env(cls) -> "Config":
        repo_root = Path(__file__).resolve().parents[2]
        return cls(
            db_path=Path(os.environ.get("SDLC_MCP_DB", DEFAULT_DB_PATH)).resolve(),
            backup_dir=Path(os.environ.get("SDLC_MCP_BACKUP_DIR", DEFAULT_BACKUP_DIR)).resolve(),
            log_path=Path(os.environ.get("SDLC_MCP_LOG", DEFAULT_LOG_PATH)).resolve(),
            migrations_dir=Path(os.environ.get("SDLC_MCP_MIGRATIONS", repo_root / "migrations")).resolve(),
        )
