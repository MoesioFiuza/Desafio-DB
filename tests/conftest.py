import os

os.environ.setdefault("SKIP_DATABASE_READY", "true")
os.environ.setdefault("RATE_LIMIT_REQUESTS_PER_MINUTE", "999999")

import pytest
from fastapi.testclient import TestClient

from src.api.dependencies import get_create_document_handler, get_search_documents_handler
from src.application.use_cases.create_document.handler import CreateDocumentHandler
from src.application.use_cases.search_documents.handler import SearchDocumentsHandler
from src.main import create_app
from src.shared.config import get_settings
from tests.fakes.in_memory_repository import InMemoryUnitOfWork


@pytest.fixture
def in_memory_uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork()


@pytest.fixture
def client(in_memory_uow: InMemoryUnitOfWork) -> TestClient:
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_create_document_handler] = lambda: CreateDocumentHandler(
        unit_of_work=in_memory_uow,
    )
    app.dependency_overrides[get_search_documents_handler] = lambda: SearchDocumentsHandler(
        repository=in_memory_uow.documentos,
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    get_settings.cache_clear()
