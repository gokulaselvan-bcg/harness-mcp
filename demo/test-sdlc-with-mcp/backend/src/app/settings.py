"""Application settings loaded from environment or .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized typed settings; the only place env vars are read."""

    model_config = SettingsConfigDict(env_file=".env", extra="forbid")

    database_url: str = "sqlite:///./tasks.db"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
