from typing import Any
from uuid import UUID

from pydantic.dataclasses import dataclass

from app.model.response.sample_document import DocumentMetadata


@dataclass(frozen=True)
class SampleDocumentCreate:
    sample_id: UUID
    json_data: DocumentMetadata
    secondary_json_dict: dict[str, Any]
