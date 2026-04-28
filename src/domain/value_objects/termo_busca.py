from dataclasses import dataclass

from src.domain.exceptions.domain_errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class TermoBusca:
    value: str

    def __post_init__(self) -> None:
        termo = self.value.strip()
        if not termo:
            raise DomainValidationError("O termo de busca nao pode ser vazio.")
        if len(termo) > 200:
            raise DomainValidationError("O termo de busca deve ter no maximo 200 caracteres.")
        object.__setattr__(self, "value", termo)
