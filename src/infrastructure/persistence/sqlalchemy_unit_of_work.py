from sqlalchemy.orm import Session

from src.infrastructure.persistence.repositories.documento_repository_sqlalchemy import (
    DocumentoRepositorySqlAlchemy,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session: Session) -> None:
        self._session = session
        self.documentos = DocumentoRepositorySqlAlchemy(session=session)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
