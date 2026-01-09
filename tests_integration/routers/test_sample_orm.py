import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response

from app.model.request.sample import SampleCreate
from app.model.response.sample import Sample

SAMPLE_ORM_ENDPOINT = "/context/samples/orm"


def test_sample_orm_create(test_client: TestClient):
    delete_all_samples(test_client)

    request_entity: SampleCreate = SampleCreate(
        username=f"user-1-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.8,
        decimal_field=Decimal("0.5"),
    )
    http_response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_response.status_code).is_equal_to(200)
    response_entity: Sample = Sample(**http_response.json())
    assert_created_response_entity(response_entity, request_entity)


def test_sample_orm_read_by_id(test_client: TestClient):
    delete_all_samples(test_client)

    request_entity: SampleCreate = SampleCreate(
        username=f"user-1-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.8,
        decimal_field=Decimal("0.5"),
    )
    http_create_response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_create_response.status_code).is_equal_to(200)
    created_entity: Sample = Sample(**http_create_response.json())
    assert_created_response_entity(created_entity, request_entity)

    http_read_by_id_response = test_client.get(
        f"{SAMPLE_ORM_ENDPOINT}/{created_entity.id}"
    )
    assert_that(http_read_by_id_response.status_code).is_equal_to(200)
    read_entity: Sample = Sample(**http_read_by_id_response.json())
    assert_that(read_entity).is_equal_to(created_entity)


def delete_all_samples(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def assert_created_response_entity(actual: Sample, expected: SampleCreate) -> None:
    assert_that(actual.id).is_not_none()
    now = datetime.now(timezone.utc)
    one_minute_ago = now - timedelta(minutes=1)
    one_minute_hence = now + timedelta(minutes=1)
    assert_that(actual.created_datetime).is_between(one_minute_ago, one_minute_hence)
    assert_that(actual.updated_datetime).is_between(one_minute_ago, one_minute_hence)
    assert_that(actual.version).is_equal_to(1)
    assert_that(actual.username).is_equal_to(expected.username)
    assert_that(actual.bool_field).is_equal_to(expected.bool_field)
    assert_that(actual.float_field).is_equal_to(expected.float_field)
    assert_that(actual.decimal_field).is_equal_to(expected.decimal_field)
