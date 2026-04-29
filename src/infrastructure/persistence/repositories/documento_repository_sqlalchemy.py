from datetime import date
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.application.contracts.repositories.documento_repository import DocumentoRepository
from src.domain.entities.documento import Documento
from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.value_objects.coordenada import Coordenada
from src.domain.value_objects.documento_id import DocumentoId
from src.domain.value_objects.termo_busca import TermoBusca
from src.infrastructure.persistence.models.documento_model import DocumentoModel
from src.shared.enums import SearchMode


class DocumentoRepositorySqlAlchemy(DocumentoRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, documento: Documento) -> None:
        model = DocumentoModel(
            id=documento.id.value,
            titulo=documento.titulo,
            autor=documento.autor,
            conteudo=documento.conteudo,
            data=documento.data,
            latitude=documento.coordenada.latitude,
            longitude=documento.coordenada.longitude,
        )
        self._session.add(model)

    def search_by_term(
        self,
        termo: TermoBusca,
        mode: SearchMode,
        limit: int = 100,
        offset: int = 0,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> list[tuple[Documento, float]]:
        tsquery_function = "plainto_tsquery" if mode == SearchMode.TOKEN else "phraseto_tsquery"
        safe_limit = max(1, min(limit, 500))
        safe_offset = max(0, min(offset, 1_000_000))
        use_geo = latitude is not None and longitude is not None

        if use_geo:
            statement = text(
                f"""
                SELECT
                  id, titulo, autor, conteudo, data, latitude, longitude,
                  ts_rank(search_vector, {tsquery_function}('portuguese', :term)) AS score,
                  (location <-> ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography) AS dist_m
                FROM documentos
                WHERE search_vector @@ {tsquery_function}('portuguese', :term)
                ORDER BY dist_m ASC NULLS LAST, score DESC, data DESC
                LIMIT :limit OFFSET :offset
                """
            )
            result = self._session.execute(
                statement,
                {
                    "term": termo.value,
                    "limit": safe_limit,
                    "offset": safe_offset,
                    "lat": latitude,
                    "lon": longitude,
                },
            )
        else:
            statement = text(
                f"""
                SELECT
                  id, titulo, autor, conteudo, data, latitude, longitude,
                  ts_rank(search_vector, {tsquery_function}('portuguese', :term)) AS score
                FROM documentos
                WHERE search_vector @@ {tsquery_function}('portuguese', :term)
                ORDER BY score DESC, data DESC
                LIMIT :limit OFFSET :offset
                """
            )
            result = self._session.execute(
                statement,
                {"term": termo.value, "limit": safe_limit, "offset": safe_offset},
            )
        rows = result.mappings().all()
        return [(self._to_domain_row(row), float(row["score"])) for row in rows]

    @staticmethod
    def _to_domain(model: DocumentoModel) -> Documento:
        if model.latitude is None or model.longitude is None:
            raise DomainValidationError("Documento persistido sem coordenadas validas.")
        coordenada = Coordenada(latitude=model.latitude, longitude=model.longitude)

        return Documento(
            id=DocumentoId(value=model.id),
            titulo=model.titulo,
            autor=model.autor,
            conteudo=model.conteudo,
            data=model.data,
            coordenada=coordenada,
        )

    @staticmethod
    def _to_domain_row(row: dict[str, object]) -> Documento:
        coordenada = None
        latitude = row["latitude"]
        longitude = row["longitude"]
        if latitude is not None and longitude is not None:
            coordenada = Coordenada(latitude=float(latitude), longitude=float(longitude))

        return Documento(
            id=DocumentoId(value=UUID(str(row["id"]))),
            titulo=str(row["titulo"]),
            autor=str(row["autor"]),
            conteudo=str(row["conteudo"]),
            data=date.fromisoformat(str(row["data"])) if not isinstance(row["data"], date) else row["data"],
            coordenada=coordenada,
        )
