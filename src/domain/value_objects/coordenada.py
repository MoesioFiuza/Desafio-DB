from dataclasses import dataclass
from src.domain.exceptions.domain_errors import DomainValidationError


@dataclass(frozen=True, slots=True)
class Coordenada:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not (-90.0 <= self.latitude <= 90.0):
            raise DomainValidationError("Latitude deve estar entre -90 e 90.")
        if not (-180.0 <= self.longitude <= 180.0):
            raise DomainValidationError("Longitude deve estar entre -180 e 180.")
