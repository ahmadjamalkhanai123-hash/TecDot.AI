"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/unified_ai_platform_dev"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/unified_ai_platform_dev"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Environment
    environment: str = "development"

    # CORS - comma-separated in .env
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]


# Global settings instance
settings = Settings()
