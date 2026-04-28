from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True, slots=True)
class Result(Generic[T, E]):
    value: T | None = None
    error: E | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None
