from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field, Column, DateTime


class SampleDocumentEntity(SQLModel, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "sample_documents"

    id: UUID = Field(primary_key=True)
    sample_id: UUID
    json_data: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    secondary_json_dict: Dict[str, Any] = Field(default={}, sa_column=Column(JSONB))
    created_datetime: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
