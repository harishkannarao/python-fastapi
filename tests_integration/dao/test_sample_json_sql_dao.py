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

from app.dao import sample_sql_dao, sample_jsonb_sql_dao
from app.model.request.sample import SampleCreate
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample_document import DocumentMetadata, SampleDocument


@pytest_asyncio.fixture(autouse=True)
async def setup_teardown(get_database: Database) -> AsyncGenerator[None, None]:
    await sample_jsonb_sql_dao.delete_sample_documents(get_database)
    await sample_sql_dao.delete_samples(get_database)

    yield

    await sample_jsonb_sql_dao.delete_sample_documents(get_database)
    await sample_sql_dao.delete_samples(get_database)


@pytest.mark.asyncio
async def test_sample_document_create_and_read(get_database: Database):
    start_time: datetime = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
    sample_id: UUID = await create_random_sample(get_database)

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
        get_database, create_request
    )
    read_document_by_id: SampleDocument = (
        await sample_jsonb_sql_dao.read_sample_document_by_id(
            get_database, sample_document_id
        )
    )

    end_time: datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=2)

    assert_that(read_document_by_id.id).is_not_none()
    assert_that(read_document_by_id.sample_id).is_equal_to(sample_id)
    assert_that(read_document_by_id.json_data.id).is_equal_to(
        create_request.json_data.id
    )
    assert_that(read_document_by_id.json_data.tags).is_length(2)
    assert_that(read_document_by_id.json_data.tags).contains("tag-2", "tag-1")
    assert_that(read_document_by_id.secondary_json_dict["test"]).is_equal_to(
        create_request.secondary_json_dict["test"]
    )
    assert_that(read_document_by_id.secondary_json_dict["nested"]["sub"]).is_equal_to(
        create_request.secondary_json_dict["nested"]["sub"]
    )
    assert_that(
        DeepDiff(
            jsonable_encoder(create_request.secondary_json_dict),
            jsonable_encoder(read_document_by_id.secondary_json_dict),
            ignore_order=True,
        )
    ).is_empty()
    assert_that(read_document_by_id.created_datetime).is_between(start_time, end_time)


@pytest.mark.asyncio
async def test_sample_document_read_by_json_id(get_database: Database):
    sample_id: UUID = await create_random_sample(get_database)

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
        get_database, create_request
    )
    read_document_by_id: SampleDocument = (
        await sample_jsonb_sql_dao.read_sample_document_by_id(
            get_database, sample_document_id
        )
    )
    read_document_by_json_id: SampleDocument = (
        await sample_jsonb_sql_dao.read_sample_document_by_json_id(
            get_database, create_request.json_data.id
        )
    )
    assert_that(read_document_by_json_id).is_equal_to(read_document_by_id)


@pytest.mark.asyncio
async def test_sample_document_read_all(get_database: Database):
    sample_id: UUID = await create_random_sample(get_database)

    create_request_1: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample_id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=("tag-1", "tag-2")),
        secondary_json_dict={
            "test": "value",
            "nested": {"sub": "value"},
            "array": [{"key": "test-value"}],
        },
    )

    sample_document_id_1: UUID = await sample_jsonb_sql_dao.create_sample_document(
        get_database, create_request_1
    )
    read_document_by_id_1: SampleDocument = (
        await sample_jsonb_sql_dao.read_sample_document_by_id(
            get_database, sample_document_id_1
        )
    )

    create_request_2: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample_id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=()),
        secondary_json_dict={},
    )

    sample_document_id_2: UUID = await sample_jsonb_sql_dao.create_sample_document(
        get_database, create_request_2
    )
    read_document_by_id_2: SampleDocument = (
        await sample_jsonb_sql_dao.read_sample_document_by_id(
            get_database, sample_document_id_2
        )
    )

    read_all: list[SampleDocument] = await sample_jsonb_sql_dao.read_sample_documents(
        get_database,
    )
    assert_that(read_all).is_length(2)
    assert_that(read_all[0]).is_equal_to(read_document_by_id_1)
    assert_that(read_all[1]).is_equal_to(read_document_by_id_2)


@pytest.mark.asyncio
async def test_sample_document_delete_all(get_database: Database):
    sample_id: UUID = await create_random_sample(get_database)

    create_request_1: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample_id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=("tag-1", "tag-2")),
        secondary_json_dict={
            "test": "value",
            "nested": {"sub": "value"},
            "array": [{"key": "test-value"}],
        },
    )

    await sample_jsonb_sql_dao.create_sample_document(get_database, create_request_1)

    create_request_2: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample_id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=()),
        secondary_json_dict={},
    )

    await sample_jsonb_sql_dao.create_sample_document(get_database, create_request_2)

    read_all_before_delete: list[
        SampleDocument
    ] = await sample_jsonb_sql_dao.read_sample_documents(get_database)
    assert_that(read_all_before_delete).is_length(2)

    await sample_jsonb_sql_dao.delete_sample_documents(get_database)

    read_all_after_delete: list[
        SampleDocument
    ] = await sample_jsonb_sql_dao.read_sample_documents(get_database)
    assert_that(read_all_after_delete).is_empty()


async def create_random_sample(get_database: Database) -> UUID:
    create_sample_request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.1,
        decimal_field=Decimal(3.4),
    )
    return await sample_sql_dao.create_sample(get_database, create_sample_request)
