import pytest

from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.value_objects.termo_busca import TermoBusca


def test_termo_busca_trimmed_ok() -> None:
    t = TermoBusca("  informacao  ")
    assert t.value == "informacao"


def test_termo_busca_empty_raises() -> None:
    with pytest.raises(DomainValidationError, match="vazio"):
        TermoBusca("   ")


def test_termo_busca_too_long_raises() -> None:
    with pytest.raises(DomainValidationError, match="200"):
        TermoBusca("x" * 201)
