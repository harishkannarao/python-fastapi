import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from assertpy import assert_that
from fastapi.testclient import TestClient

from httpx import Response

from app.model.request.sample import SampleCreate, SampleUpdate
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


def test_sample_orm_read_all(test_client: TestClient):
    delete_all_samples(test_client)

    create_1: SampleCreate = SampleCreate(
        username=f"user-1-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.8,
        decimal_field=Decimal("0.5"),
    )
    create_1_response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(create_1)
    )
    assert_that(create_1_response.status_code).is_equal_to(200)
    sample_1: Sample = Sample(**create_1_response.json())

    create_2: SampleCreate = SampleCreate(
        username=f"user-2-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
    )
    create_2_response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(create_2)
    )
    assert_that(create_2_response.status_code).is_equal_to(200)
    sample_2: Sample = Sample(**create_2_response.json())

    http_read_all_response = test_client.get(SAMPLE_ORM_ENDPOINT)
    assert_that(http_read_all_response.status_code).is_equal_to(200)

    all_samples = [Sample(**item) for item in http_read_all_response.json()]

    assert_that(
        [sample for sample in all_samples if sample.id == sample_1.id]
    ).contains_only(sample_1)
    assert_that(
        [sample for sample in all_samples if sample.id == sample_2.id]
    ).contains_only(sample_2)
    assert_that(all_samples).is_length(2)

    delete_all_samples(test_client)

    http_read_all_after_delete = test_client.get(SAMPLE_ORM_ENDPOINT)
    assert_that(http_read_all_after_delete.status_code).is_equal_to(200)

    empty_samples = [Sample(**item) for item in http_read_all_after_delete.json()]
    assert_that(empty_samples).is_empty()


def test_sample_orm_update(test_client: TestClient):
    delete_all_samples(test_client)

    create_request: SampleCreate = SampleCreate(
        username=f"user-1-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.8,
        decimal_field=Decimal("0.5"),
    )
    create_response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(create_request)
    )
    assert_that(create_response.status_code).is_equal_to(200)
    created_sample: Sample = Sample(**create_response.json())
    assert_created_response_entity(created_sample, create_request)

    update_request: SampleUpdate = SampleUpdate(
        id=created_sample.id,
        old_version=created_sample.version,
        new_version=created_sample.version + 1,
        username=f"user-2-{uuid.uuid4()}",
        bool_field=None,
        float_field=None,
        decimal_field=None,
    )
    update_response = test_client.post(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(update_request)
    )
    assert_that(update_response.status_code).is_equal_to(200)
    updated_sample: Sample = Sample(**update_response.json())
    assert_updated_response_entity(updated_sample, created_sample, update_request)


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


def assert_updated_response_entity(
    actual: Sample, original: Sample, update: SampleUpdate
) -> None:
    assert_that(actual.id).is_equal_to(original.id)
    assert_that(actual.created_datetime).is_equal_to(original.created_datetime)
    now = datetime.now(timezone.utc)
    one_minute_ago = now - timedelta(minutes=1)
    one_minute_hence = now + timedelta(minutes=1)
    assert_that(actual.updated_datetime).is_between(one_minute_ago, one_minute_hence)
    assert_that(actual.version).is_equal_to(update.new_version)
    assert_that(actual.username).is_equal_to(update.username)
    assert_that(actual.bool_field).is_equal_to(update.bool_field)
    assert_that(actual.float_field).is_equal_to(update.float_field)
    assert_that(actual.decimal_field).is_equal_to(update.decimal_field)
