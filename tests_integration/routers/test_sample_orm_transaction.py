import uuid
from typing import Generator

import pytest
from assertpy import assert_that
from fastapi.encoders import jsonable_encoder
from starlette.responses import Response
from starlette.testclient import TestClient

from app.model.request.sample import SampleCreateWithDocuments, SampleCreate, SampleDocumentInlineCreate
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


def test_sample_jsonb_orm_create(delete_all_fixture: None, test_client: TestClient):
    document1 = SampleDocumentInlineCreate(
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=tuple([])),
        secondary_json_dict={})
    document2 = SampleDocumentInlineCreate(
        json_data=DocumentMetadata(id=uuid.uuid4(), tags=tuple([])),
        secondary_json_dict={})
    request_entity: SampleCreateWithDocuments = SampleCreateWithDocuments(
        sample=SampleCreate(
            username=f"user-{uuid.uuid4()}",
            bool_field=None,
            float_field=None,
            decimal_field=None
        ),
        documents=tuple([
            document1,
            document2
        ])
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


def delete_all(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_JSONB_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)


def delete_all_samples(test_client: TestClient) -> None:
    delete_all_response: Response = test_client.delete(SAMPLE_ORM_ENDPOINT)
    assert_that(delete_all_response.status_code).is_equal_to(204)
