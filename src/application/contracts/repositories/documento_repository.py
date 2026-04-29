from typing import Protocol

from src.domain.entities.documento import Documento
from src.domain.value_objects.termo_busca import TermoBusca
from src.shared.enums import SearchMode


class DocumentoRepository(Protocol):
    def add(self, documento: Documento) -> None:
        ...

    def search_by_term(
        self,
        termo: TermoBusca,
        mode: SearchMode,
        limit: int = 100,
    ) -> list[tuple[Documento, float]]:
        ...
