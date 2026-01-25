from typing import Any
from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class DocumentMetadata:
    id: UUID
    tags: list[str]


@dataclass(frozen=True)
class SampleDocument:
    id: UUID
    sample_id: UUID
    json_data: DocumentMetadata
    secondary_json_dict: dict[str, Any]
