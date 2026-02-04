from datetime import datetime
from typing import Any, Mapping
from uuid import UUID

from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class DocumentMetadata:
    id: UUID
    tags: tuple[str, ...]


@dataclass(frozen=True)
class SampleDocument:
    id: UUID
    sample_id: UUID
    json_data: DocumentMetadata
    secondary_json_dict: Mapping[str, Any]
    created_datetime: datetime
