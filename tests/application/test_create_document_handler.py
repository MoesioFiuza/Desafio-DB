from datetime import date
from unittest.mock import MagicMock

import pytest
from src.application.use_cases.create_document.command import CreateDocumentCommand
from src.application.use_cases.create_document.handler import CreateDocumentHandler
from src.domain.value_objects.coordenada import Coordenada
from tests.fakes.in_memory_repository import InMemoryUnitOfWork


def test_create_persists_and_returns_documento() -> None:
    uow = InMemoryUnitOfWork()
    handler = CreateDocumentHandler(unit_of_work=uow)
    command = CreateDocumentCommand(
        titulo="Livro",
        autor="Autor",
        conteudo="Texto com palavra informacao",
        data=date(2025, 3, 1),
        latitude=-30.0,
        longitude=-51.0,
    )
    created = handler.execute(command)

    assert created.titulo == "Livro"
    assert created.coordenada == Coordenada(latitude=-30.0, longitude=-51.0)
    assert len(uow.documentos._items) == 1
    assert uow.documentos._items[0].id == created.id


def test_create_rollbacks_when_add_fails() -> None:
    uow = MagicMock()
    uow.documentos.add.side_effect = OSError("persistencia indisponivel")
    handler = CreateDocumentHandler(unit_of_work=uow)
    command = CreateDocumentCommand(
        titulo="T",
        autor="A",
        conteudo="C",
        data=date(2025, 1, 1),
        latitude=1.0,
        longitude=2.0,
    )
    with pytest.raises(OSError):
        handler.execute(command)
    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_create_rejects_empty_titulo_nothing_persisted() -> None:
    from src.domain.exceptions.domain_errors import DomainValidationError

    uow = InMemoryUnitOfWork()
    handler = CreateDocumentHandler(unit_of_work=uow)
    command = CreateDocumentCommand(
        titulo="   ",
        autor="A",
        conteudo="C",
        data=date(2025, 1, 1),
        latitude=0.0,
        longitude=0.0,
    )
    with pytest.raises(DomainValidationError):
        handler.execute(command)
    assert len(uow.documentos._items) == 0
