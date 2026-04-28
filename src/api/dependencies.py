from fastapi import Depends
from sqlalchemy.orm import Session

from src.application.use_cases.create_document.handler import CreateDocumentHandler
from src.application.use_cases.search_documents.handler import SearchDocumentsHandler
from src.infrastructure.persistence.db_context import get_session
from src.infrastructure.persistence.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork


def get_create_document_handler(
    session: Session = Depends(get_session),
) -> CreateDocumentHandler:
    unit_of_work = SqlAlchemyUnitOfWork(session=session)
    return CreateDocumentHandler(unit_of_work=unit_of_work)


def get_search_documents_handler(
    session: Session = Depends(get_session),
) -> SearchDocumentsHandler:
    repository = SqlAlchemyUnitOfWork(session=session).documentos
    return SearchDocumentsHandler(repository=repository)
