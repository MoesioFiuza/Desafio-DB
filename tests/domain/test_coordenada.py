import pytest
from src.domain.exceptions.domain_errors import DomainValidationError
from src.domain.value_objects.coordenada import Coordenada


def test_coordenada_porto_alegre_ok() -> None:
    c = Coordenada(latitude=-30.03, longitude=-51.22)
    assert c.latitude == -30.03


@pytest.mark.parametrize(
    "lat,lon",
    [
        (91.0, 0.0),
        (-91.0, 0.0),
        (0.0, 181.0),
        (0.0, -181.0),
    ],
)
def test_coordenada_out_of_range_raises(lat: float, lon: float) -> None:
    with pytest.raises(DomainValidationError):
        Coordenada(latitude=lat, longitude=lon)
