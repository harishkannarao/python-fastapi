import uuid
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pprint import pprint
from typing import Generator

import pytest
from assertpy import assert_that
from deepdiff import DeepDiff
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
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=tuple(["tag1", "tag2"])),
        secondary_json_dict={"key": "value"},
    )
    http_response = test_client.put(
        SAMPLE_JSONB_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_response.status_code).is_equal_to(200)
    response_entity: SampleDocument = SampleDocument(**http_response.json())
    assert_created_response_entity(response_entity, request_entity)


@pytest.mark.parametrize(
    "raise_server_exceptions_fixture, expected_status",
    [(False, 500)],
    indirect=["raise_server_exceptions_fixture"],
)
def test_sample_jsonb_orm_create_with_duplicate_json_id(
    raise_server_exceptions_fixture: bool,
    delete_all_fixture: None,
    test_client: TestClient,
    expected_status: int,
):
    sample = create_random_sample(test_client)

    request_entity: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample.id,
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=tuple(["tag1", "tag2"])),
        secondary_json_dict={"key": "value"},
    )
    http_response = test_client.put(
        SAMPLE_JSONB_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_response.status_code).is_equal_to(200)
    request_entity_with_duplicate_id: SampleDocumentCreate = SampleDocumentCreate(
        sample_id=sample.id,
        json_data=DocumentMetadata(
            id=request_entity.json_data.id, tags=tuple(["tag1", "tag2"])
        ),
        secondary_json_dict={"key": "value"},
    )
    http_response_with_duplicate_id = test_client.put(
        SAMPLE_JSONB_ORM_ENDPOINT,
        json=jsonable_encoder(request_entity_with_duplicate_id),
    )
    assert_that(http_response_with_duplicate_id.status_code).is_equal_to(
        expected_status
    )


def test_sample_jsonb_orm_read_all(delete_all_fixture: None, test_client: TestClient):
    sample1 = create_random_sample(test_client)
    sample2 = create_random_sample(test_client)

    sample_document_1 = create_random_sample_document(test_client, sample1.id)
    sample_document_2 = create_random_sample_document(test_client, sample2.id)
    http_response = test_client.get(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(http_response.status_code).is_equal_to(200)
    all_documents = [SampleDocument(**item) for item in http_response.json()]
    expected = [sample_document_1, sample_document_2]
    assert_that(DeepDiff(expected, all_documents, ignore_order=True)).is_empty()


def test_sample_jsonb_orm_by_sample_id(
    delete_all_fixture: None, test_client: TestClient
):
    sample1 = create_random_sample(test_client)
    sample2 = create_random_sample(test_client)

    sample_document_1 = create_random_sample_document(test_client, sample1.id)
    create_random_sample_document(test_client, sample2.id)
    http_response = test_client.get(
        f"{SAMPLE_JSONB_ORM_ENDPOINT}/{sample_document_1.id}"
    )
    assert_that(http_response.status_code).is_equal_to(200)
    actual = SampleDocument(**http_response.json())
    assert_that(DeepDiff(sample_document_1, actual, ignore_order=True)).is_empty()


def test_sample_jsonb_orm_by_json_id(delete_all_fixture: None, test_client: TestClient):
    sample1 = create_random_sample(test_client)
    sample2 = create_random_sample(test_client)

    create_random_sample_document(test_client, sample1.id)
    sample_document_2 = create_random_sample_document(test_client, sample2.id)
    http_response = test_client.get(
        f"{SAMPLE_JSONB_ORM_ENDPOINT}/json_id/{sample_document_2.json_data.id}"
    )
    assert_that(http_response.status_code).is_equal_to(200)
    actual = SampleDocument(**http_response.json())
    diff = DeepDiff(sample_document_2, actual, ignore_order=True)
    assert_that(diff).described_as(pprint(diff)).is_empty()


def test_sample_jsonb_orm_delete_all(delete_all_fixture: None, test_client: TestClient):
    sample1 = create_random_sample(test_client)
    sample2 = create_random_sample(test_client)

    create_random_sample_document(test_client, sample1.id)
    create_random_sample_document(test_client, sample2.id)

    initial_read_all_response = test_client.get(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(initial_read_all_response.status_code).is_equal_to(200)
    initial_all_documents = [
        SampleDocument(**item) for item in initial_read_all_response.json()
    ]
    assert_that(initial_all_documents).is_length(2)

    http_delete_all_response = test_client.delete(f"{SAMPLE_JSONB_ORM_ENDPOINT}")
    assert_that(http_delete_all_response.status_code).is_equal_to(204)

    final_read_all_response = test_client.get(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(final_read_all_response.status_code).is_equal_to(200)
    final_all_documents = [
        SampleDocument(**item) for item in final_read_all_response.json()
    ]
    assert_that(final_all_documents).is_length(0)


def delete_all(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def delete_all_samples(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def create_random_sample_document(
    test_client: TestClient, sample_id: uuid.UUID
) -> SampleDocument:
    request_entity = SampleDocumentCreate(
        sample_id=sample_id,
        json_data=DocumentMetadata(
            id=uuid.uuid4(), tags=tuple([f"tag-{uuid.uuid4()}"])
        ),
        secondary_json_dict={"key": f"value-{uuid.uuid4()}"},
    )
    http_response = test_client.put(
        SAMPLE_JSONB_ORM_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_response.status_code).is_equal_to(200)
    return SampleDocument(**http_response.json())


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
