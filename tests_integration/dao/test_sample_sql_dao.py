from datetime import datetime, timezone, timedelta
import uuid
from decimal import Decimal

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
    start_time: datetime = datetime.now(tz=timezone.utc)
    request: SampleCreate = SampleCreate(
        username=f"usr-{uuid.uuid4()}",
        bool_field=True,
        float_field=2.1,
        decimal_field=Decimal(3.4),
    )
    create_result: Sample = await sample_sql_dao.create_sample(request)

    assert_that(create_result.id).is_not_none()
    assert_that(create_result.username).is_equal_to(request.username)
    assert_that(create_result.bool_field).is_equal_to(request.bool_field)
    assert_that(create_result.float_field).is_equal_to(request.float_field)
    assert_that(create_result.decimal_field).is_equal_to(request.decimal_field)
    assert_that(create_result.created_datetime).is_between(
        start_time, datetime.now(tz=timezone.utc) + timedelta(seconds=2)
    )
    assert_that(create_result.updated_datetime).is_between(
        start_time, datetime.now(tz=timezone.utc) + timedelta(seconds=2)
    )
