from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
