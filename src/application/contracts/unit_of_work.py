from typing import Protocol

from src.application.contracts.repositories.documento_repository import DocumentoRepository


class UnitOfWork(Protocol):
    documentos: DocumentoRepository

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
