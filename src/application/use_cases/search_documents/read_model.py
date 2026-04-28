from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True, slots=True)
class DocumentReadModel:
    id: UUID
    titulo: str
    autor: str
    conteudo: str
    data: date
    latitude: float | None
    longitude: float | None
    score: float
