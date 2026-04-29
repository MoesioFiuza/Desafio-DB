from functools import lru_cache
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "desafio-documentos-api"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    api_version: str = "1.0.0"

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/documentos",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout_seconds: int = 30
    database_pool_recycle_seconds: int = 1800

    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["*"])
    max_request_size_bytes: int = 1_048_576
    rate_limit_requests_per_minute: int = 120

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL deve apontar para PostgreSQL.")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError("Configuracao invalida. Verifique variaveis de ambiente.") from exc
