import uuid
from typing import Generator

import pytest
from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response
from starlette.testclient import TestClient

from app.model.request.sample import (
    SampleCreateWithDocuments,
    SampleCreate,
    SampleDocumentInlineCreate,
)
from app.model.response.sample import Sample
from app.model.response.sample_document import DocumentMetadata

SAMPLE_ORM_ENDPOINT = "/context/samples/orm"
SAMPLE_JSONB_ORM_ENDPOINT = "/context/samples/jsonb/orm"
SAMPLE_TRANSACTION_PROPAGATED_ENDPOINT = "/context/samples/orm/transaction/propagated"


@pytest.fixture
def delete_all_fixture(test_client: TestClient) -> Generator[None, None, None]:
    delete_all(test_client)
    delete_all_samples(test_client)
    yield
    delete_all(test_client)
    delete_all_samples(test_client)


def test_successful_creation_of_sample_with_documents(
    delete_all_fixture: None, test_client: TestClient
):
    document1 = SampleDocumentInlineCreate(
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=tuple([])),
        secondary_json_dict={},
    )
    document2 = SampleDocumentInlineCreate(
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=tuple([])),
        secondary_json_dict={},
    )
    request_entity: SampleCreateWithDocuments = SampleCreateWithDocuments(
        sample=SampleCreate(
            username=f"user-{uuid.uuid4()}",
            bool_field=None,
            float_field=None,
            decimal_field=None,
        ),
        documents=tuple([document1, document2]),
    )
    http_create_with_document_response = test_client.put(
        SAMPLE_TRANSACTION_PROPAGATED_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_create_with_document_response.status_code).is_equal_to(200)
    created_sample: Sample = Sample(**http_create_with_document_response.json())

    http_read_by_sample_id_response = test_client.get(
        f"{SAMPLE_ORM_ENDPOINT}/{created_sample.id}"
    )
    assert_that(http_read_by_sample_id_response.status_code).is_equal_to(200)

    http_document_1_response = test_client.get(
        f"{SAMPLE_JSONB_ORM_ENDPOINT}/json_id/{document1.json_data.id}"
    )
    assert_that(http_document_1_response.status_code).is_equal_to(200)

    http_document_2_response = test_client.get(
        f"{SAMPLE_JSONB_ORM_ENDPOINT}/json_id/{document2.json_data.id}"
    )
    assert_that(http_document_2_response.status_code).is_equal_to(200)


@pytest.mark.parametrize(
    "raise_server_exceptions",
    [False],
    indirect=True,
)
def test_complete_rollback_of_create_sample_with_documents(
    raise_server_exceptions: bool, delete_all_fixture: None, test_client: TestClient
):
    json_id = uuid.uuid4()
    document1 = SampleDocumentInlineCreate(
        json_data=DocumentMetadata(id=json_id, tags=tuple([])), secondary_json_dict={}
    )
    document2 = SampleDocumentInlineCreate(
        json_data=DocumentMetadata(id=json_id, tags=tuple([])), secondary_json_dict={}
    )
    request_entity: SampleCreateWithDocuments = SampleCreateWithDocuments(
        sample=SampleCreate(
            username=f"user-{uuid.uuid4()}",
            bool_field=None,
            float_field=None,
            decimal_field=None,
        ),
        documents=tuple([document1, document2]),
    )
    http_create_with_document_response = test_client.put(
        SAMPLE_TRANSACTION_PROPAGATED_ENDPOINT, json=jsonable_encoder(request_entity)
    )
    assert_that(http_create_with_document_response.status_code).is_equal_to(500)

    http_read_all_response = test_client.get(SAMPLE_ORM_ENDPOINT)
    assert_that(http_read_all_response.status_code).is_equal_to(200)
    all_samples = [Sample(**item) for item in http_read_all_response.json()]
    assert_that(all_samples).is_empty()

    http_document_response = test_client.get(
        f"{SAMPLE_JSONB_ORM_ENDPOINT}/json_id/{json_id}"
    )
    assert_that(http_document_response.status_code).is_equal_to(404)


def delete_all(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def delete_all_samples(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)
