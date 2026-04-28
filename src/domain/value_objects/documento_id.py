from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DocumentoId:
    value: UUID

    @classmethod
    def new(cls) -> "DocumentoId":
        return cls(value=uuid4())
