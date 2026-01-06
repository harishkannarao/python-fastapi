from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Sample:
    id: UUID
    username: str
    bool_field: bool | None
    float_field: float | None
    decimal_field: Decimal | None
    created_datetime: datetime
    updated_datetime: datetime
    version: int
