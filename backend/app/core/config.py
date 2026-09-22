"""
Application configuration.

All settings are loaded from environment variables (see .env.example).
No secrets are ever hardcoded here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    APP_NAME: str = "CodeShieldAI"
    APP_ENV: str = "development"
    API_V1_PREFIX: str = "/api"
    DEBUG: bool = True

    # CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://codeshield:codeshield@localhost:5432/codeshieldai"

    # --- Auth ---
    JWT_SECRET_KEY: str = "dev-only-insecure-secret-change-me"  # MUST be overridden in .env for any real use
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    COOKIE_SECURE: bool = False  # set True in production (HTTPS) — cookies won't be sent over plain HTTP otherwise
    FRONTEND_URL: str = "http://localhost:5173"  # where the browser is redirected after Google OAuth completes

    # --- Google OAuth (optional — /api/auth/google returns 503 until these are set) ---
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # LLM / Groq
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we don't re-parse the environment on every call."""
    return Settings()
