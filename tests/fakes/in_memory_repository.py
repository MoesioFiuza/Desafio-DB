from src.domain.entities.documento import Documento
from src.domain.services.distancia_service import DistanciaService
from src.domain.value_objects.coordenada import Coordenada
from src.domain.value_objects.termo_busca import TermoBusca
from src.shared.enums import SearchMode


class InMemoryDocumentRepository:

    def __init__(self) -> None:
        self._items: list[Documento] = []

    def add(self, documento: Documento) -> None:
        self._items.append(documento)

    def search_by_term(
        self,
        termo: TermoBusca,
        mode: SearchMode,
        limit: int = 100,
        offset: int = 0,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[tuple[Documento, float]]:
        term = termo.value
        matches: list[tuple[Documento, float]] = []
        for doc in self._items:
            if not self._document_matches(doc, term, mode):
                continue
            matches.append((doc, 1.0))

        if latitude is not None and longitude is not None:
            origin = Coordenada(latitude=latitude, longitude=longitude)
            matches.sort(
                key=lambda it: (
                    DistanciaService.haversine_km(origin, it[0].coordenada),
                    -it[0].data.toordinal(),
                    str(it[0].id.value),
                )
            )
        else:
            matches.sort(key=lambda it: (-it[0].data.toordinal(), str(it[0].id.value)))

        safe_limit = max(1, min(limit, 500))
        safe_offset = max(0, min(offset, 1_000_000))
        return matches[safe_offset : safe_offset + safe_limit]

    @staticmethod
    def _document_matches(documento: Documento, term: str, mode: SearchMode) -> bool:
        haystack = f"{documento.titulo} {documento.autor} {documento.conteudo}".lower()
        if mode == SearchMode.PHRASE:
            return term.lower() in haystack
        for word in term.lower().split():
            if not word:
                continue
            if word not in haystack:
                return False
        return bool(term.strip())


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self._repo = InMemoryDocumentRepository()
        self.documentos: InMemoryDocumentRepository = self._repo

    def commit(self) -> None:
        return

    def rollback(self) -> None:
        return
