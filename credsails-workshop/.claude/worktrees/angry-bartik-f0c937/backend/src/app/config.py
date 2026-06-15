"""Runtime configuration, read from .env (pydantic-settings).

The live/stub LLM switch keys off whether ANTHROPIC_API_KEY is the placeholder/missing.
"""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]  # .../backend
PROJECT_DIR = BACKEND_DIR.parent                   # .../credsails-demo

_PLACEHOLDER_KEYS = {"", "dummy-key-replace-me", "your-key-here"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = "dummy-key-replace-me"
    anthropic_model: str = "claude-sonnet-4-5"
    llm_timeout_seconds: float = 120.0

    db_path: Path = BACKEND_DIR / "credsails.db"
    data_dir: Path = PROJECT_DIR / "data"

    @property
    def placeholder_key(self) -> bool:
        return self.anthropic_api_key.strip() in _PLACEHOLDER_KEYS

    @property
    def llm_mode(self) -> str:
        """'stub' (deterministic, offline) or 'live' (real Claude calls)."""
        return "stub" if self.placeholder_key else "live"


settings = Settings()
