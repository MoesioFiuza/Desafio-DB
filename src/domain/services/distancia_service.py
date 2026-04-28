from math import asin, cos, radians, sin, sqrt

from src.domain.value_objects.coordenada import Coordenada


class DistanciaService:
    """Service de dominio para calculo de distancia entre coordenadas."""

    @staticmethod
    def haversine_km(origem: Coordenada, destino: Coordenada) -> float:
        raio_terra_km = 6371.0

        d_lat = radians(destino.latitude - origem.latitude)
        d_lon = radians(destino.longitude - origem.longitude)

        lat1 = radians(origem.latitude)
        lat2 = radians(destino.latitude)

        a = sin(d_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(d_lon / 2) ** 2
        c = 2 * asin(sqrt(a))
        return raio_terra_km * c
