from datetime import date
import pytest
from src.application.use_cases.search_documents.handler import SearchDocumentsHandler
from src.application.use_cases.search_documents.query import SearchDocumentsQuery
from src.domain.exceptions.domain_errors import DomainValidationError
from tests.fakes.in_memory_repository import InMemoryUnitOfWork


def _seed(uow: InMemoryUnitOfWork) -> None:
    from src.application.use_cases.create_document.handler import CreateDocumentHandler
    from src.application.use_cases.create_document.command import CreateDocumentCommand

    handler = CreateDocumentHandler(unit_of_work=uow)
    handler.execute(
        CreateDocumentCommand(
            titulo="Carros classicos",
            autor="Joao",
            conteudo="Guia de restauracao de veiculos.",
            data=date(2025, 1, 10),
            latitude=-29.99,
            longitude=-51.17,
        )
    )
    handler.execute(
        CreateDocumentCommand(
            titulo="Bicicletas",
            autor="Maria",
            conteudo="Mobilidade urbana e trilhas.",
            data=date(2025, 2, 1),
            latitude=-30.05,
            longitude=-51.20,
        )
    )


def test_search_requires_latitude_longitude_pair() -> None:
    uow = InMemoryUnitOfWork()
    h = SearchDocumentsHandler(repository=uow.documentos)
    with pytest.raises(DomainValidationError, match="juntas"):
        h.execute(
            SearchDocumentsQuery(palavra_chave="x", latitude=-30.0, longitude=None),
        )


def test_search_token_mode_filters_documents() -> None:
    uow = InMemoryUnitOfWork()
    _seed(uow)
    h = SearchDocumentsHandler(repository=uow.documentos)
    results = h.execute(SearchDocumentsQuery(palavra_chave="carros"))
    assert len(results) == 1
    assert "Carros" in results[0].titulo


def test_search_phrase_requires_full_substring() -> None:
    uow = InMemoryUnitOfWork()
    _seed(uow)
    h = SearchDocumentsHandler(repository=uow.documentos)
    results = h.execute(SearchDocumentsQuery(busca="bicicletas urbanas"))
    assert len(results) == 0
    results2 = h.execute(SearchDocumentsQuery(busca="Mobilidade urbana"))
    assert len(results2) == 1


def test_search_geo_orders_nearest_first() -> None:
    uow = InMemoryUnitOfWork()
    _seed(uow)
    from src.application.use_cases.create_document.handler import CreateDocumentHandler
    from src.application.use_cases.create_document.command import CreateDocumentCommand

    CreateDocumentHandler(unit_of_work=uow).execute(
        CreateDocumentCommand(
            titulo="Guia distante",
            autor="Ana",
            conteudo="Guia de trilha distante.",
            data=date(2025, 3, 1),
            latitude=-31.5,
            longitude=-52.5,
        )
    )
    h = SearchDocumentsHandler(repository=uow.documentos)
    results = h.execute(
        SearchDocumentsQuery(
            palavra_chave="guia",
            latitude=-29.99,
            longitude=-51.17,
        )
    )
    assert len(results) == 2
    assert results[0].titulo == "Carros classicos"
    assert results[1].titulo == "Guia distante"


def test_conteudo_preview_truncates() -> None:
    uow = InMemoryUnitOfWork()
    from src.application.use_cases.create_document.handler import CreateDocumentHandler
    from src.application.use_cases.create_document.command import CreateDocumentCommand

    CreateDocumentHandler(unit_of_work=uow).execute(
        CreateDocumentCommand(
            titulo="T",
            autor="A",
            conteudo="ABCDEFGHIJ",
            data=date(2025, 1, 1),
            latitude=0.0,
            longitude=0.0,
        )
    )
    h = SearchDocumentsHandler(repository=uow.documentos)
    out = h.execute(
        SearchDocumentsQuery(palavra_chave="ABC", conteudo_preview_max=4),
    )
    assert out[0].conteudo == "ABCD..."
