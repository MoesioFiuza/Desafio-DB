from src.domain.services.distancia_service import DistanciaService
from src.domain.value_objects.coordenada import Coordenada


def test_haversine_same_point_zero_km() -> None:
    p = Coordenada(latitude=-30.0, longitude=-51.0)
    assert DistanciaService.haversine_km(p, p) == 0.0


def test_haversine_known_short_distance_order() -> None:
    ref = Coordenada(latitude=-30.0, longitude=-51.0)
    nearer = Coordenada(latitude=-30.01, longitude=-51.0)
    farther = Coordenada(latitude=-31.0, longitude=-52.0)
    d1 = DistanciaService.haversine_km(ref, nearer)
    d2 = DistanciaService.haversine_km(ref, farther)
    assert d1 < d2
