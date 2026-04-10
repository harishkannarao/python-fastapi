from datetime import datetime, timezone, timedelta
import uuid
from decimal import Decimal
from uuid import UUID

from assertpy import assert_that
import pytest
import pytest_asyncio
from databases import Database
from pytest import MonkeyPatch

from app.dao import sample_sql_dao
from app.model.request.sample import SampleCreate
from app.model.response.sample import Sample


@pytest_asyncio.fixture(autouse=True)
def setup_dao_database(get_database: Database, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr("app.dao.sample_sql_dao.database", get_database)


@pytest.mark.asyncio
async def test_sample_create_and_read():
    start_time: datetime = datetime.now(tz=timezone.utc) - timedelta(seconds=2)
    request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.1,
        decimal_field=Decimal(3.4),
    )
    sample_id: UUID = await sample_sql_dao.create_sample(request)

    read_by_id: Sample = await sample_sql_dao.read_sample_by_id(sample_id)

    end_time: datetime = datetime.now(tz=timezone.utc) + timedelta(seconds=2)

    assert_that(read_by_id.id).is_not_none()
    assert_that(read_by_id.username).is_equal_to(request.username)
    assert_that(read_by_id.bool_field).is_equal_to(request.bool_field)
    assert_that(read_by_id.float_field).is_equal_to(request.float_field)
    assert_that(read_by_id.decimal_field).is_equal_to(request.decimal_field)
    assert_that(read_by_id.created_datetime).is_between(start_time, end_time)
    assert_that(read_by_id.updated_datetime).is_between(start_time, end_time)
