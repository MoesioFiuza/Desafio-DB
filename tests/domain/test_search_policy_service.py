import pytest

from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.services.search_policy_service import SearchPolicyService
from src.shared.enums import SearchMode


def test_resolve_token_mode_from_palavra_chave() -> None:
    assert SearchPolicyService.resolve_mode("informacao", None) == SearchMode.TOKEN


def test_resolve_phrase_mode_from_busca() -> None:
    assert SearchPolicyService.resolve_mode(None, "carros antigos") == SearchMode.PHRASE


@pytest.mark.parametrize("pk,busca", [(None, None), ("a", "b"), ("", "")])
def test_resolve_none_or_both_raises(pk: str | None, busca: str | None) -> None:
    with pytest.raises(DomainValidationError, match="exatamente um"):
        SearchPolicyService.resolve_mode(pk, busca)
