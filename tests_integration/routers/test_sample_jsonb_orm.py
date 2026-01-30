import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Generator

import pytest
from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from httpx import Response

from app.model.request.sample import SampleCreate
from app.model.request.sample_document import SampleDocumentCreate
from app.model.response.sample import Sample
from app.model.response.sample_document import DocumentMetadata, SampleDocument

SAMPLE_ORM_ENDPOINT = "/context/samples/orm"
SAMPLE_JSONB_ORM_ENDPOINT = "/context/samples/jsonb/orm"


@pytest.fixture
def delete_all_fixture(test_client: TestClient) -> Generator[None, None, None]:
    delete_all(test_client)
    delete_all_samples(test_client)
    yield
    delete_all(test_client)
    delete_all_samples(test_client)


def test_sample_jsonb_orm_create(delete_all_fixture: None, test_client: TestClient):
    sample = create_random_sample(test_client)

    request_entity: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample.id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=["tag1", "tag2"]),
        secondary_json_dict={"key": "value"},
    )
    http_response = test_client.put(
        SAMPLE_JSONB_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_response.status_code).is_equal_to(200)
    response_entity: SampleDocument = SampleDocument(**http_response.json())
    assert_created_response_entity(response_entity, request_entity)


def delete_all(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def delete_all_samples(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def create_random_sample(test_client: TestClient) -> Sample:
    request_entity: SampleCreate = SampleCreate(
        username=f"user-{uuid.uuid4()}",
        bool_field=True,
        float_field=0.8,
        decimal_field=Decimal("0.5"),
    )
    response = test_client.put(
        SAMPLE_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(response.status_code).is_equal_to(200)
    return Sample(**response.json())


def assert_created_response_entity(
    actual: SampleDocument, expected: SampleDocumentCreate
) -> None:
    assert_that(actual.id).is_not_none()
    now = datetime.now(timezone.utc)
    one_minute_ago = now - timedelta(minutes=1)
    one_minute_hence = now + timedelta(minutes=1)
    assert_that(actual.created_datetime).is_between(one_minute_ago, one_minute_hence)
    assert_that(actual.sample_id).is_equal_to(expected.sample_id)
    assert_that(actual.json_data).is_equal_to(expected.json_data)
    assert_that(actual.secondary_json_dict).is_equal_to(expected.secondary_json_dict)
