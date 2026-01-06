from decimal import Decimal
from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class SampleCreate:
    username: str
    bool_field: bool | None
    float_field: float | None
    decimal_field: Decimal | None


@dataclass(frozen=True)
class SampleUpdate:
    id: UUID
    username: str
    bool_field: bool | None
    float_field: float | None
    decimal_field: Decimal | None
    old_version: int
    new_version: int
