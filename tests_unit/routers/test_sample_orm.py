import uuid
from datetime import timezone, datetime
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock
from uuid import UUID

from assertpy import assert_that
from fastapi.testclient import TestClient
from sqlalchemy import Select

from app.model.entity.sample_entity import SampleEntity
from app.model.response.sample import Sample

SAMPLE_ORM_ENDPOINT = "/context/samples/orm"


def test_sample_orm_read_by_id(mock_async_session: AsyncMock, test_client: TestClient):
    input_id: UUID = uuid.uuid4()
    db_entity: SampleEntity = SampleEntity(
        id=input_id,
        username=f"user-{input_id}",
        bool_field=True,
        float_field=0.5,
        decimal_field=Decimal("0.8"),
        created_datetime=datetime.now(timezone.utc),
        updated_datetime=datetime.now(timezone.utc),
        version=1,
    )
    mock_result: MagicMock = MagicMock()
    mock_result.one_or_none.return_value = db_entity
    mock_async_session.exec.return_value = mock_result
    expected: Sample = Sample(**db_entity.model_dump())

    response = test_client.get(f"{SAMPLE_ORM_ENDPOINT}/{input_id}")
    assert_that(response.status_code).is_equal_to(200)
    result: Sample = Sample(**response.json())
    assert_that(result).is_equal_to(expected)

    assert_that(mock_async_session.exec.call_args_list).is_length(1)
    args, kwargs = mock_async_session.exec.call_args
    sent_query = args[0]

    assert_that(sent_query).is_instance_of(Select)
    query_str = str(sent_query.compile())
    assert_that(query_str).contains_ignoring_case("SELECT")
    assert_that(query_str).contains_ignoring_case("sample_table")
    assert_that(query_str).contains_ignoring_case("WHERE")
    assert_that(query_str).contains_ignoring_case("sample_table.id")
