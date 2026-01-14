from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field


class SampleEntity(SQLModel, table=True):
    @declared_attr
    def __tablename__(cls) -> str:
        return "sample_table"

    id: UUID = Field(primary_key=True)
    username: str
    bool_field: Optional[bool] = Field(default=None)
    float_field: Optional[float] = Field(default=None)
    decimal_field: Optional[Decimal] = Field(default=None)
    created_datetime: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    updated_datetime: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    version: int
