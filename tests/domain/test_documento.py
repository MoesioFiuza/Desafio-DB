from datetime import date

import pytest

from src.domain.entities.documento import Documento
from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.value_objects.coordenada import Coordenada
from src.domain.value_objects.documento_id import DocumentoId


def _doc(**kwargs: object) -> Documento:
    defaults = {
        "id": DocumentoId.new(),
        "titulo": "Titulo",
        "autor": "Autor",
        "conteudo": "Conteudo",
        "data": date(2025, 1, 1),
        "coordenada": Coordenada(latitude=-30.0, longitude=-51.0),
    }
    defaults.update(kwargs)
    return Documento(**defaults)


def test_documento_strip_fields() -> None:
    d = _doc(titulo="  x  ", autor=" y ", conteudo=" z ")
    assert d.titulo == "x"
    assert d.autor == "y"
    assert d.conteudo == "z"


@pytest.mark.parametrize("field", ["titulo", "autor", "conteudo"])
def test_documento_empty_required_field_raises(field: str) -> None:
    kwargs = {field: "   "}
    with pytest.raises(DomainValidationError):
        _doc(**kwargs)
