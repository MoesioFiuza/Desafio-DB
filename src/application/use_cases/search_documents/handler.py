from src.application.contracts.repositories.documento_repository import DocumentoRepository
from src.application.use_cases.search_documents.read_model import DocumentReadModel
from src.application.use_cases.search_documents.query import SearchDocumentsQuery
from src.domain.entities.documento import Documento
from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.services.distancia_service import DistanciaService
from src.domain.services.search_policy_service import SearchPolicyService
from src.domain.value_objects.coordenada import Coordenada
from src.domain.value_objects.termo_busca import TermoBusca


class SearchDocumentsHandler:
    def __init__(self, repository: DocumentoRepository) -> None:
        self._repository = repository

    def execute(self, query: SearchDocumentsQuery) -> list[DocumentReadModel]:
        if (query.latitude is None) != (query.longitude is None):
            raise DomainValidationError("latitude e longitude devem ser informadas juntas.")

        mode = SearchPolicyService.resolve_mode(query.palavra_chave, query.busca)
        raw_term = query.busca if query.busca else query.palavra_chave

        termo = TermoBusca(raw_term or "")
        documentos_with_score = self._repository.search_by_term(termo=termo, mode=mode, limit=query.limit)

        if query.latitude is None:
            return [self._to_read_model(documento, score=score) for documento, score in documentos_with_score]

        origem = Coordenada(latitude=query.latitude, longitude=query.longitude)

        def sort_key(item: tuple[Documento, float]) -> tuple[float, float, str]:
            documento, score = item
            distance_km = DistanciaService.haversine_km(origem, documento.coordenada)
            return (distance_km, -score, str(documento.id.value))

        ordered = sorted(documentos_with_score, key=sort_key)
        return [self._to_read_model(documento, score=score) for documento, score in ordered]

    @staticmethod
    def _to_read_model(documento: Documento, score: float) -> DocumentReadModel:
        return DocumentReadModel(
            id=documento.id.value,
            titulo=documento.titulo,
            autor=documento.autor,
            conteudo=documento.conteudo,
            data=documento.data,
            latitude=documento.coordenada.latitude,
            longitude=documento.coordenada.longitude,
            score=score,
        )
