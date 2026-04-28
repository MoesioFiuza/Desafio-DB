from src.domain.exceptions.domain_errors import DomainValidationError
from src.shared.enums import SearchMode


class SearchPolicyService:
    @staticmethod
    def resolve_mode(palavra_chave: str | None, busca: str | None) -> SearchMode:
        if bool(palavra_chave) == bool(busca):
            raise DomainValidationError("Informe exatamente um entre palavraChave e busca.")
        return SearchMode.PHRASE if busca else SearchMode.TOKEN
