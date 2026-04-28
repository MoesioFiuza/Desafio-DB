from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.application.use_cases.search_documents.read_model import DocumentReadModel
from src.domain.entities.documento import Documento


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    titulo: str
    autor: str
    conteudo: str
    data: date
    latitude: float | None = None
    longitude: float | None = None
    score: float | None = None

    @classmethod
    def from_domain(cls, documento: Documento) -> "DocumentResponse":
        return cls(
            id=documento.id.value,
            titulo=documento.titulo,
            autor=documento.autor,
            conteudo=documento.conteudo,
            data=documento.data,
            latitude=documento.coordenada.latitude if documento.coordenada else None,
            longitude=documento.coordenada.longitude if documento.coordenada else None,
        )

    @classmethod
    def from_read_model(cls, model: DocumentReadModel) -> "DocumentResponse":
        return cls(
            id=model.id,
            titulo=model.titulo,
            autor=model.autor,
            conteudo=model.conteudo,
            data=model.data,
            latitude=model.latitude,
            longitude=model.longitude,
            score=model.score,
        )
