import uuid
from datetime import timezone, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, AsyncMock
from uuid import UUID

from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import select

from app.model.entity.sample_entity import SampleEntity
from app.model.request.sample import SampleUpdate
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
    args, kwargs = mock_async_session.exec.call_args_list[0]
    actual_query = args[0]
    actual_compiled_query = actual_query.compile()

    expected_query = select(SampleEntity).where(SampleEntity.id == input_id)
    expected_compiled_query = expected_query.compile()

    assert_that(actual_compiled_query.string).is_equal_to(
        expected_compiled_query.string
    )
    assert_that(actual_compiled_query.params).is_equal_to(
        expected_compiled_query.params
    )


def test_sample_orm_read_by_id_returns_404(
    mock_async_session: AsyncMock, test_client: TestClient
):
    input_id: UUID = uuid.uuid4()
    mock_result: MagicMock = MagicMock()
    mock_result.one_or_none.return_value = None
    mock_async_session.exec.return_value = mock_result

    response = test_client.get(f"{SAMPLE_ORM_ENDPOINT}/{input_id}")
    assert_that(response.status_code).is_equal_to(404)
    assert_that(response.json()).is_none()


def test_sample_orm_update_returns_200(
    mock_session: MagicMock, test_client: TestClient
):
    update_request: SampleUpdate = SampleUpdate(
        id=uuid.uuid4(),
        old_version=1,
        new_version=2,
        username=f"updated-user-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
    )
    existing_db_entity: SampleEntity = SampleEntity(
        id=update_request.id,
        username=f"user-{update_request.id}",
        bool_field=True,
        float_field=0.5,
        decimal_field=Decimal("0.8"),
        created_datetime=datetime.now(timezone.utc) - timedelta(seconds=5),
        updated_datetime=datetime.now(timezone.utc) - timedelta(seconds=5),
        version=1,
    )
    mock_result: MagicMock = MagicMock()
    mock_result.one_or_none.return_value = existing_db_entity
    mock_session.exec.return_value = mock_result

    response = test_client.post(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(update_request)
    )
    assert_that(response.status_code).is_equal_to(200)
    updated: Sample = Sample(**response.json())
    assert_that(updated.username).is_equal_to(update_request.username)
    assert_that(updated.bool_field).is_equal_to(update_request.bool_field)
    assert_that(updated.float_field).is_equal_to(update_request.float_field)
    assert_that(updated.decimal_field).is_equal_to(update_request.decimal_field)
    assert_that(updated.version).is_equal_to(update_request.new_version)
    assert_that(updated.created_datetime).is_equal_to(
        existing_db_entity.created_datetime
    )
    assert_that(updated.updated_datetime).is_after(
        existing_db_entity.updated_datetime - timedelta(seconds=1)
    )
    assert_that(updated.updated_datetime).is_before(
        datetime.now(timezone.utc) + timedelta(seconds=2)
    )

    assert_that(mock_session.exec.call_args_list).is_length(1)
    args, kwargs = mock_session.exec.call_args_list[0]
    actual_query = args[0]
    actual_compiled_query = actual_query.compile()

    expected_query = (
        select(SampleEntity)
        .where(SampleEntity.id == update_request.id)
        .where(SampleEntity.version == update_request.old_version)
    )
    expected_compiled_query = expected_query.compile()

    assert_that(actual_compiled_query.string).is_equal_to(
        expected_compiled_query.string
    )
    assert_that(actual_compiled_query.params).is_equal_to(
        expected_compiled_query.params
    )

    assert_that(mock_session.add.call_args_list).is_length(1)
    args, kwargs = mock_session.add.call_args_list[0]
    saved_entity: SampleEntity = args[0]
    assert_that(saved_entity.username).is_equal_to(update_request.username)
    assert_that(saved_entity.bool_field).is_equal_to(update_request.bool_field)
    assert_that(saved_entity.float_field).is_equal_to(update_request.float_field)
    assert_that(saved_entity.decimal_field).is_equal_to(update_request.decimal_field)
    assert_that(saved_entity.version).is_equal_to(update_request.new_version)
    assert_that(saved_entity.created_datetime).is_equal_to(
        existing_db_entity.created_datetime
    )
    assert_that(saved_entity.updated_datetime).is_after(
        existing_db_entity.updated_datetime - timedelta(seconds=1)
    )
    assert_that(saved_entity.updated_datetime).is_before(
        datetime.now(timezone.utc) + timedelta(seconds=2)
    )

    assert_that(mock_session.flush.call_args_list).is_length(1)
    assert_that(mock_session.refresh.call_args_list).is_length(1)


def test_sample_orm_update_returns_409(
    mock_session: MagicMock, test_client: TestClient
):
    update_request: SampleUpdate = SampleUpdate(
        id=uuid.uuid4(),
        old_version=1,
        new_version=2,
        username=f"updated-user-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
    )

    mock_result: MagicMock = MagicMock()
    mock_result.one_or_none.return_value = None
    mock_session.exec.return_value = mock_result

    response = test_client.post(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(update_request)
    )
    assert_that(response.status_code).is_equal_to(409)
    assert_that(response.json()).is_none()

    assert_that(mock_session.exec.call_args_list).is_length(1)

    assert_that(mock_session.add.call_args_list).is_length(0)
    assert_that(mock_session.flush.call_args_list).is_length(0)
    assert_that(mock_session.refresh.call_args_list).is_length(0)
