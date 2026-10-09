"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    environment: str = "development"
    app_name: str = "Clean Loop API"
    app_version: str = "1.0.0"
    debug: bool = True

    # Database (Supabase/PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cleanloop"
    database_sync_url: str = "postgresql://postgres:postgres@localhost:5432/cleanloop"

    # Supabase Configuration
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""

    # Security
    secret_key: str = "your-super-secret-key-change-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    cors_origins: str = '["http://localhost:3000","http://localhost:5173","https://your-frontend.vercel.app"]'

    # File Storage (Supabase Storage)
    storage_bucket: str = "clean-loop-assets"
    storage_public_url: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string."""
        import json
        return json.loads(self.cors_origins)

    @property
    def is_supabase_configured(self) -> bool:
        """Check if Supabase is configured."""
        return bool(self.supabase_url and self.supabase_key)

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()