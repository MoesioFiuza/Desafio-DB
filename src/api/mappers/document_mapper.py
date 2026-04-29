from src.api.dtos.responses import DocumentResponse
from src.application.use_cases.search_documents.read_model import DocumentReadModel
from src.domain.entities.documento import Documento


def to_document_response_from_domain(documento: Documento) -> DocumentResponse:
    return DocumentResponse(
        id=documento.id.value,
        titulo=documento.titulo,
        autor=documento.autor,
        conteudo=documento.conteudo,
        data=documento.data,
        latitude=documento.coordenada.latitude if documento.coordenada else None,
        longitude=documento.coordenada.longitude if documento.coordenada else None,
        score=None,
    )


def to_document_response_from_read_model(model: DocumentReadModel) -> DocumentResponse:
    return DocumentResponse(
        id=model.id,
        titulo=model.titulo,
        autor=model.autor,
        conteudo=model.conteudo,
        data=model.data,
        latitude=model.latitude,
        longitude=model.longitude,
        score=model.score,
    )
