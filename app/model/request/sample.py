from decimal import Decimal
from typing import Mapping, Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.model.response.sample_document import DocumentMetadata


@dataclass(frozen=True)
class SampleCreate:
    username: str
    bool_field: bool | None
    float_field: float | None
    decimal_field: Decimal | None


@dataclass(frozen=True)
class SampleDocumentInlineCreate:
    json_data: DocumentMetadata
    secondary_json_dict: Mapping[str, Any]


@dataclass(frozen=True)
class SampleCreateWithDocuments:
    sample: SampleCreate
    documents: tuple[SampleDocumentInlineCreate, ...]


@dataclass(frozen=True)
class SampleUpdate:
    id: UUID
    username: str
    bool_field: bool | None
    float_field: float | None
    decimal_field: Decimal | None
    old_version: int
    new_version: int
