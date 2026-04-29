from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class CreateDocumentCommand:
    titulo: str
    autor: str
    conteudo: str
    data: date
    latitude: float
    longitude: float
