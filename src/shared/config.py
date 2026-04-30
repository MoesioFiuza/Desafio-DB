from functools import lru_cache
from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "desafio-documentos-api"
    environment: str = Field(default="development", pattern="^(development|staging|production)$")
    api_version: str = "1.0.0"

    database_url: str = Field(
        ...,
        description="URL de conexão com o PostgreSQL.",
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_pool_timeout_seconds: int = 30
    database_pool_recycle_seconds: int = 1800

    cors_allowed_origins: list[str] = Field(default_factory=list)
    max_request_size_bytes: int = 1_048_576
    rate_limit_requests_per_minute: int = 120
    rate_limit_backend: str = Field(default="inmemory", pattern="^(inmemory|distributed)$")

    skip_database_ready: bool = False

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+psycopg://")):
            raise ValueError("DATABASE_URL deve apontar para PostgreSQL.")
        return value

    @model_validator(mode="after")
    def validate_runtime_safety_guards(self) -> "Settings":
        if self.environment == "production":
            if self.skip_database_ready:
                raise ValueError("SKIP_DATABASE_READY nao pode ser true em production.")
            if not self.cors_allowed_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS deve ser definido em production.")
            if "*" in self.cors_allowed_origins:
                raise ValueError("CORS_ALLOWED_ORIGINS nao pode conter '*' em production.")
            if self.rate_limit_backend == "inmemory":
                raise ValueError(
                    "RATE_LIMIT_BACKEND=inmemory nao e permitido em production. "
                    "Use backend distribuido (ex.: Redis/API Gateway)."
                )
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError("Configuracao invalida. Verifique variaveis de ambiente.") from exc
