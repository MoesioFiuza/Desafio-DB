from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchDocumentsQuery:
    palavra_chave: str | None = None
    busca: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    limit: int = 100
    offset: int = 0
    conteudo_preview_max: int | None = None
