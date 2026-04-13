import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from assertpy import assert_that
from databases import Database
from deepdiff import DeepDiff
from fastapi.encoders import jsonable_encoder
from pytest import MonkeyPatch

from app.dao import sample_sql_dao, sample_jsonb_sql_dao
from app.model.request.sample import SampleCreate
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import DocumentMetadata, SampleDocument


@pytest_asyncio.fixture(autouse=True)
async def setup_dao_database(
    get_database: Database, monkeypatch: MonkeyPatch
) -> AsyncGenerator[None, None]:
    monkeypatch.setattr("app.dao.sample_jsonb_sql_dao.database", get_database)
    monkeypatch.setattr("app.dao.sample_sql_dao.database", get_database)
    await sample_sql_dao.delete_samples()

    yield

    await sample_sql_dao.delete_samples()


@pytest.mark.asyncio
async def test_sample_document_create_and_read():
    start_time: datetime = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
    sample_id: UUID = await create_random_sample()

    create_request: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample_id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=("tag-1", "tag-2")),
        secondary_json_dict={
            "test": "value",
            "nested": {"sub": "value"},
            "array": [{"key": "test-value"}],
        },
    )

    sample_document_id: UUID = await sample_jsonb_sql_dao.create_sample_document(
        create_request
    )
    read_document_by_id: SampleDocument = (
        await sample_jsonb_sql_dao.read_sample_document_by_id(sample_document_id)
    )

    end_time: datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=2)

    assert_that(read_document_by_id.id).is_not_none()
    assert_that(read_document_by_id.sample_id).is_equal_to(sample_id)
    assert_that(
        DeepDiff(
            jsonable_encoder(create_request.json_data),
            jsonable_encoder(read_document_by_id.json_data),
            ignore_order=True,
        )
    ).is_empty()
    assert_that(
        DeepDiff(
            jsonable_encoder(create_request.secondary_json_dict),
            jsonable_encoder(read_document_by_id.secondary_json_dict),
            ignore_order=True,
        )
    ).is_empty()
    assert_that(read_document_by_id.created_datetime).is_between(start_time, end_time)


async def create_random_sample() -> UUID:
    create_sample_request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.1,
        decimal_field=Decimal(3.4),
    )
    return await sample_sql_dao.create_sample(create_sample_request)
