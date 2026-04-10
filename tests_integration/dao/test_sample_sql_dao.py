import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from assertpy import assert_that
from databases import Database
from pytest import MonkeyPatch

from app.dao import sample_sql_dao
from app.model.request.sample import SampleCreate, SampleUpdate
from app.model.response.sample import Sample


@pytest_asyncio.fixture(autouse=True)
async def setup_dao_database(
    get_database: Database, monkeypatch: MonkeyPatch
) -> AsyncGenerator[None, None]:
    monkeypatch.setattr("app.dao.sample_sql_dao.database", get_database)
    await sample_sql_dao.delete_samples()

    yield

    await sample_sql_dao.delete_samples()


@pytest.mark.asyncio
async def test_sample_read_all_with_offset_and_limit():
    create_request_1: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=1,
        decimal_field=Decimal(1),
    )
    sample_id_1: UUID = await sample_sql_dao.create_sample(create_request_1)

    create_request_2: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2,
        decimal_field=Decimal(2),
    )
    sample_id_2: UUID = await sample_sql_dao.create_sample(create_request_2)

    create_request_3: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=3,
        decimal_field=Decimal(3),
    )
    sample_id_3: UUID = await sample_sql_dao.create_sample(create_request_3)

    read_1: list[Sample] = await sample_sql_dao.read_samples(0, 2)
    read_1_ids: list[UUID] = [sample.id for sample in read_1]
    assert_that(read_1_ids).is_length(2)
    assert_that(read_1_ids[0]).is_equal_to(sample_id_1)
    assert_that(read_1_ids[1]).is_equal_to(sample_id_2)

    read_2: list[Sample] = await sample_sql_dao.read_samples(1, 2)
    read_2_ids: list[UUID] = [sample.id for sample in read_2]
    assert_that(read_2_ids).is_length(2)
    assert_that(read_2_ids[0]).is_equal_to(sample_id_2)
    assert_that(read_2_ids[1]).is_equal_to(sample_id_3)


@pytest.mark.asyncio
async def test_sample_delete_all():
    create_request_1: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=1,
        decimal_field=Decimal(1),
    )
    sample_id_1: UUID = await sample_sql_dao.create_sample(create_request_1)

    create_request_2: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2,
        decimal_field=Decimal(2),
    )
    sample_id_2: UUID = await sample_sql_dao.create_sample(create_request_2)

    create_request_3: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=3,
        decimal_field=Decimal(3),
    )
    sample_id_3: UUID = await sample_sql_dao.create_sample(create_request_3)

    await sample_sql_dao.delete_samples()

    read_after_delete: list[Sample] = await sample_sql_dao.read_samples(0, 1)

    assert_that(read_after_delete).is_empty()
    assert_that(await sample_sql_dao.read_sample_by_id(sample_id_1)).is_none()
    assert_that(await sample_sql_dao.read_sample_by_id(sample_id_2)).is_none()
    assert_that(await sample_sql_dao.read_sample_by_id(sample_id_3)).is_none()


@pytest.mark.asyncio
async def test_sample_create_and_read():
    start_time: datetime = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
    create_request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.1,
        decimal_field=Decimal(3.4),
    )
    sample_id: UUID = await sample_sql_dao.create_sample(create_request)

    read_by_id: Sample = await sample_sql_dao.read_sample_by_id(sample_id)

    end_time: datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=2)

    assert_that(read_by_id.id).is_not_none()
    assert_that(read_by_id.username).is_equal_to(create_request.username)
    assert_that(read_by_id.bool_field).is_equal_to(create_request.bool_field)
    assert_that(read_by_id.float_field).is_equal_to(create_request.float_field)
    assert_that(read_by_id.decimal_field).is_equal_to(create_request.decimal_field)
    assert_that(read_by_id.created_datetime).is_between(start_time, end_time)
    assert_that(read_by_id.updated_datetime).is_between(start_time, end_time)


@pytest.mark.asyncio
async def test_sample_delete():
    create_request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.1,
        decimal_field=Decimal(3.4),
    )
    sample_id: UUID = await sample_sql_dao.create_sample(create_request)

    read_by_id: Sample = await sample_sql_dao.read_sample_by_id(sample_id)

    assert_that(read_by_id.id).is_not_none()

    deleted_id = await sample_sql_dao.delete_by_id(sample_id)

    assert_that(deleted_id).is_equal_to(sample_id)

    read_after_delete = await sample_sql_dao.read_sample_by_id(sample_id)

    assert_that(read_after_delete).is_none()


@pytest.mark.asyncio
async def test_sample_update_and_read():
    start_time: datetime = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
    create_request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
    )
    sample_id: UUID = await sample_sql_dao.create_sample(create_request)

    created_sample: Sample = await sample_sql_dao.read_sample_by_id(sample_id)

    create_end_time: datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=2)

    assert_that(created_sample.id).is_not_none()
    assert_that(created_sample.username).is_equal_to(create_request.username)
    assert_that(created_sample.bool_field).is_none()
    assert_that(created_sample.float_field).is_none()
    assert_that(created_sample.decimal_field).is_none()
    assert_that(created_sample.created_datetime).is_between(start_time, create_end_time)
    assert_that(created_sample.updated_datetime).is_between(start_time, create_end_time)

    update_request: SampleUpdate = SampleUpdate(
        id=created_sample.id,
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=3.1,
        decimal_field=Decimal(2.5),
        old_version=created_sample.version,
        new_version=created_sample.version + 1,
    )

    update_ids: list[UUID] = await sample_sql_dao.update_sample(update_request)

    update_end_time: datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=2)

    assert_that(update_ids).is_length(1)
    assert_that(update_ids).contains_only(sample_id)

    updated_sample: Sample = await sample_sql_dao.read_sample_by_id(sample_id)

    assert_that(updated_sample.id).is_equal_to(sample_id)
    assert_that(updated_sample.username).is_equal_to(update_request.username)
    assert_that(updated_sample.bool_field).is_equal_to(update_request.bool_field)
    assert_that(updated_sample.float_field).is_equal_to(update_request.float_field)
    assert_that(updated_sample.decimal_field).is_equal_to(update_request.decimal_field)
    assert_that(updated_sample.created_datetime).is_equal_to(
        created_sample.created_datetime
    )
    assert_that(updated_sample.updated_datetime).is_between(start_time, update_end_time)
