from src.application.contracts.repositories.documento_repository import DocumentoRepository
from src.application.use_cases.search_documents.read_model import DocumentReadModel
from src.application.use_cases.search_documents.query import SearchDocumentsQuery
from src.domain.entities.documento import Documento
from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.services.search_policy_service import SearchPolicyService
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
        documentos_with_score = self._repository.search_by_term(
            termo=termo,
            mode=mode,
            limit=query.limit,
            offset=query.offset,
            latitude=query.latitude,
            longitude=query.longitude,
        )

        max_chars = query.conteudo_preview_max
        return [
            self._to_read_model(documento, score=score, conteudo_max_chars=max_chars)
            for documento, score in documentos_with_score
        ]

    @staticmethod
    def _to_read_model(
        documento: Documento,
        score: float,
        conteudo_max_chars: int | None,
    ) -> DocumentReadModel:
        conteudo = documento.conteudo
        if conteudo_max_chars is not None and len(conteudo) > conteudo_max_chars:
            conteudo = conteudo[:conteudo_max_chars] + "..."

        return DocumentReadModel(
            id=documento.id.value,
            titulo=documento.titulo,
            autor=documento.autor,
            conteudo=conteudo,
            data=documento.data,
            latitude=documento.coordenada.latitude,
            longitude=documento.coordenada.longitude,
            score=score,
        )
