from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.controllers.documentos_controller import router as documentos_router
from src.api.controllers.health_controller import router as health_router
from src.api.error_handlers import register_exception_handlers
from src.api.middlewares import (
    InMemoryRateLimitMiddleware,
    MaxBodySizeMiddleware,
    RequestContextMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from src.infrastructure.observability.logging import configure_logging
from src.infrastructure.persistence.db_context import ensure_database_ready
from src.shared.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging()
    ensure_database_ready()

    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        description="Microsservico para cadastro e busca de documentos por termo.",
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(MaxBodySizeMiddleware, max_bytes=settings.max_request_size_bytes)
    app.add_middleware(InMemoryRateLimitMiddleware, settings=settings)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(documentos_router, prefix="/documentos", tags=["Documentos"])
    app.include_router(health_router, tags=["Infra"])
    return app


app = create_app()
