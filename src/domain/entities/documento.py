from dataclasses import dataclass
from datetime import date
from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.value_objects.coordenada import Coordenada
from src.domain.value_objects.documento_id import DocumentoId


@dataclass(slots=True)
class Documento:
    id: DocumentoId
    titulo: str
    autor: str
    conteudo: str
    data: date
    coordenada: Coordenada

    def __post_init__(self) -> None:
        self.titulo = self.titulo.strip()
        self.autor = self.autor.strip()
        self.conteudo = self.conteudo.strip()

        if not self.titulo:
            raise DomainValidationError("Titulo e obrigatorio.")
        if not self.autor:
            raise DomainValidationError("Autor e obrigatorio.")
        if not self.conteudo:
            raise DomainValidationError("Conteudo e obrigatorio.")
