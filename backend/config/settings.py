"""
Application settings loaded from environment variables / .env file.
Uses Pydantic BaseSettings for validation and type coercion.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "PCA – Personal Communication Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./pca.db"

    # ── AI Provider ──────────────────────────────────────────────────────────
    ACTIVE_PROVIDER: Literal[
        "mock", "gemini", "openai", "claude", "deepseek", "ollama"
    ] = "mock"

    # API keys — optional; only the active provider's key is required
    GOOGLE_API_KEY: str = Field(default="", alias="GOOGLE_API_KEY")
    OPENAI_API_KEY: str = Field(default="", alias="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = Field(default="", alias="ANTHROPIC_API_KEY")
    DEEPSEEK_API_KEY: str = Field(default="", alias="DEEPSEEK_API_KEY")

    # Ollama — local model endpoint
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Gemini model name
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # OpenAI model name
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Claude model name
    CLAUDE_MODEL: str = "claude-3-5-haiku-20241022"

    # DeepSeek model name
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ── AI Call Settings ─────────────────────────────────────────────────────
    AI_TIMEOUT_SECONDS: int = 45
    AI_MAX_RETRIES: int = 2

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton Settings instance."""
    return Settings()
