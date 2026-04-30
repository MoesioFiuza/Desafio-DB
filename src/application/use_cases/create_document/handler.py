import logging

from sqlalchemy.exc import SQLAlchemyError
from src.application.contracts.unit_of_work import UnitOfWork
from src.application.use_cases.create_document.command import CreateDocumentCommand
from src.domain.entities.documento import Documento
from src.domain.value_objects.coordenada import Coordenada
from src.domain.value_objects.documento_id import DocumentoId

logger = logging.getLogger(__name__)


class CreateDocumentHandler:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, command: CreateDocumentCommand) -> Documento:
        coordenada = Coordenada(latitude=command.latitude, longitude=command.longitude)

        documento = Documento(
            id=DocumentoId.new(),
            titulo=command.titulo,
            autor=command.autor,
            conteudo=command.conteudo,
            data=command.data,
            coordenada=coordenada,
        )
        try:
            self._unit_of_work.documentos.add(documento)
            self._unit_of_work.commit()
        except (SQLAlchemyError, OSError) as exc:
            self._unit_of_work.rollback()
            logger.exception(
                "Falha ao persistir documento",
                extra={
                    "event": "create_document_persistence_error",
                    "titulo": command.titulo,
                    "autor": command.autor,
                    "error_type": type(exc).__name__,
                },
            )
            raise
        return documento
